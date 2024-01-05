from PIL import Image
import jwt
from hashlib import sha256
import pymongo
import bson
import json
import boto3
import io
import os


secret = os.environ["SECRET"]   # JWT secret key
root_URL = os.environ["ROOT_URL"]   # S3 bucket URL
db_uri = os.environ["DB_URI"]  # Mongo URI with credentials

file_client = boto3.client("s3")

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))
db = dbclient["artCollections"]

class Request():
    def __init__(self, event):
        self.path = event["path"].split("/")[1:]
        self.method = event["httpMethod"]
        self.headers = event.get("headers")
        self.args = event.get("queryStringParameters")

def response(body=None, status=200, headers=None):
    response = {
        "statusCode": status
    }

    if body != None:
        response["body"] = body

    if headers != None:
        response["headers"] = headers

    return response

def login(request):
    auth = request.headers["Authorization"].split(":")
    username = auth[0]
    password = auth[1]
    try:
        user = db["users"].find_one({"username" : username},{"_id":0})
        if sha256(password.encode('utf-8')).hexdigest() == user["password"]:
            token = jwt.encode(
                {
                "artist": user["name"],
                }, secret, algorithm="HS256")
            return response(token)
        else:
            return response("Password does not match username", 401)
    except:
        return response("Username not found", 401)

def all_images(request):
    image_collection = db[request.args.get("artist")]
    image_list_return = []
    image_list = image_collection.find().sort("sequence", -1)
    for image in image_list:
        image["_id"] = str(image["_id"])
        image["srcFull"] = f"{root_URL}/{image['srcFull']}"
        image["srcThumb"] = f"{root_URL}/{image['srcThumb']}"
        image_list_return.append(image)
    return response(image_list_return)

def all_images_by_series(request):
    image_collection = db[request.args.get("artist")]
    image_list_return = {}
    image_list = image_collection.find().sort("sequence", -1)
    for image in image_list:
        image["_id"] = str(image["_id"])
        image["srcFull"] = f"{root_URL}/{image['srcFull']}"
        image["srcThumb"] = f"{root_URL}/{image['srcThumb']}"
        
        if image["series"] in image_list_return:
            image_list_return[image["series"]].append(image)
        else:
            image_list_return[image["series"]] = [image]

    return response(image_list_return)

def new_image(request, artist_name):
    all_keys = ['name', 'caption', 'series']
    for key in request.form.keys():
        if key in all_keys:
            all_keys.remove(key)
            continue
        else:
            return response("Unexpected form field(s) found", 422)
    if all_keys != []:
        return response("Unexpected form field(s) found or missing", 422)

    name = request.form["name"]
    caption = request.form["caption"]
    series = request.form["series"]
    
    if len(request.files) == 2:
        try:
            image_file = request.files["file"]
            thumb_file = request.files["thumb"]
        except:
            return response("File upload failed", 422)
        
        if (thumb_file.content_type != "image/jpeg") or (image_file.content_type != "image/jpeg"):
            return response("File must be jpeg", 422)
        
    elif len(request.files) == 1:
        try:
            image_file = request.files["file"]
        except:
            return response("File upload failed", 422)
        
        if (image_file.content_type != "image/jpeg"):
            return response("File must be jpeg", 422)
        
        thumb_file = io.BytesIO()
        thumb = Image.open(image_file)
        thumb.thumbnail((360, 360))
        thumb.save(thumb_file, "JPEG")
        thumb_file.seek(0)
    else:
        return response("Incorrect number of files", 422)


    existing_images = db[artist_name].find({"series" : series})
    max_index = 0
    for image in existing_images:
        if image["sequence"] > max_index:
            max_index = image["sequence"]
        if (image["name"] == name):
            return response("Image name already used")
        else:
            continue
    sequence = max_index + 1

    url = name
    for char in url:
        if char.isspace():
            url = url.replace(" ", "_")
        elif not (char.isalnum() or (char == "-")):
            url = url.replace(char, "-")

    file_client.upload_fileobj(image_file, 
                               "artist-api", 
                               f"{artist_name}/{series}/full/{url}.jpg")


    file_client.upload_fileobj(thumb_file, 
                               "artist-api", 
                               f"{artist_name}/{series}/thumb/{url}.jpg")

    image_file.close()
    thumb_file.close()

    image_data = {
        "url": f"/{series}/{url}",
        "name": name,
        "srcThumb": f"{artist_name}/{series}/thumb/{url}.jpg",
        "srcFull": f"{artist_name}/{series}/full/{url}.jpg",
        "caption": caption,
        "series": series,
        "sequence" : sequence,
        "s3KeyFull" : f"{artist_name}/{series}/full/{url}.jpg",
        "s3KeyThumb" : f"{artist_name}/{series}/thumb/{url}.jpg",
    }

    db[artist_name].insert_one(image_data)

    image_data["_id"] = str(image_data["_id"])
    image_data["srcFull"] = f"{root_URL}/{image_data['srcFull']}"
    image_data["srcThumb"] = f"{root_URL}/{image_data['srcThumb']}"

    return response(image_data)

def update_image(request, artist_name, id):
    image_collection = db[artist_name]
    updates = {"$set" : request["body"]}
    image_collection.update_one({"_id" : bson.ObjectId(id)}, updates)
    return response("complete")

def reorder_images(request, artist_name):
    image_collection = db[artist_name]
    updates = request["body"]
    print(updates)
    for image in updates:
        update = {"$set" : image["newSequence"]}
        print(update)
        image_collection.update_one({"_id": bson.ObjectId(image["_id"])}, update)
    return "complete"

def delete_image(artist_name, id):
    image_collection = db[artist_name]
    print(artist_name)
    image = image_collection.find_one({"_id" : bson.ObjectId(id)})
    print(image)
    
    file_client.delete_object(Bucket="artist-api",
                              Key=image["s3KeyFull"])

    file_client.delete_object(Bucket="artist-api",
                              Key=image["s3KeyThumb"])

    image_collection.delete_one({"_id" : bson.ObjectId(id)})

    return response("complete")

def lambda_handler(event, context):
    request = Request(event)
    
    if request.path == ["login"] and request.method == "POST":
        return login(request)

    if request.headers != None and "Authorization" in request.headers:
        try:
            artist = jwt.decode(request.headers["Authorization"], secret, algorithms="HS256")["artist"]
            
            if request.path == ["image"] and request.method == "POST":
                return new_image(request, artist)
            
            if request.path[0] == ["image"] and len(request.path) == 1 and request.method == "PUT":
                return update_image(request, artist, request.path[1])
            
            if request.path[0] == ["reorder"] and request.method == "PUT":
                return reorder_images(request, artist)
            
            if request.path[0] == ["image"] and len(request.path) == 1 and request.method == "DELETE":
                return delete_image(artist, request.path[1])
        
        except jwt.exceptions.InvalidSignatureError:
            return response("Invalid signature", 401)
        
        except:
            return response("other error", 401)
        
    if request.path == ["all-images"] and request.method == "GET":
        return all_images(request)
    
    if request.path == ["all-images-by-series"] and request.method == "GET":
        return all_images_by_series(request)
    



    else:
        return response("No matching path found", 404)


if __name__ == "__main__":
    def test_passed(event):
        result = lambda_handler(event["request"], None)
        if result == event["expected"]:
            return True
        else:
            print(f"""
{event['name']} test failed
Expected:
{event['expected']}
Received:
{result}
""")
            return False
    
    with open("./tests.json", "r") as file:
        test_events = json.load(file)

    failed_tests = 0
    for event in test_events:
        if test_passed(event):
            continue

        else:
            failed_tests += 1

    if failed_tests == 0:
        print("All tests passed")
    
    else:
        print(f"{failed_tests} tests failed")
    

