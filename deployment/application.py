from flask import Flask
from flask import request
from flask_cors import CORS
from PIL import Image
import jwt
from hashlib import sha256
import pymongo
import bson
import json
import boto3
import io

config = json.load(open("./config.json", "r"))

secret = config["secretKey"]
root_URL = config["rootURL"]
db_uri = config["databaseURI"]


file_client = boto3.client("s3", 
             aws_access_key_id=config["aws_access_key_id"], 
             aws_secret_access_key=config["aws_secret_access_key"]
             )

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))
db = dbclient["artCollections"]

application = Flask(__name__)
CORS(application)

def user_only(endpoint):
    def wrapper(*args, **kwargs):
        try: 
            auth = request.headers["Authorization"]
            token = jwt.decode(auth, secret, algorithms="HS256")
        except jwt.exceptions.InvalidSignatureError:
            return "Invalid signature"
        except:
            return "other error"
        else:
            print(*args)
            return endpoint(token["artist"], *args, **kwargs)
    wrapper.__name__ = endpoint.__name__
    return wrapper

@application.route("/login")
def login():
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
            return token, 200
        else:
            return "Password does not match username", 401
    except:
        return "Username not found", 401

@application.route("/all-images")
def all_images():
    image_collection = db[request.args.get("artist")]
    image_list_return = []
    image_list = image_collection.find().sort("sequence", -1)
    for image in image_list:
        image["_id"] = str(image["_id"])
        image["srcFull"] = f"{root_URL}/{image['srcFull']}"
        image["srcThumb"] = f"{root_URL}/{image['srcThumb']}"
        image_list_return.append(image)
    return image_list_return

@application.route("/all-images-by-series")
def all_images_by_series():
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

    return image_list_return

@application.route("/image", methods=["POST"])
@user_only
def new_image_file(artist_name):
    all_keys = ['name', 'caption', 'series']
    for key in request.form.keys():
        if key in all_keys:
            all_keys.remove(key)
            continue
        else:
            return "Unexpected form field(s) found", 422
    if all_keys != []:
        return "Unexpected form field(s) found or missing", 422

    name = request.form["name"]
    caption = request.form["caption"]
    series = request.form["series"]

    print(series)

    try:
        image_file = request.files["file"]
    except:
        return "File upload failed", 422
    
    if image_file.content_type != "image/jpeg":
        return "File must be jpeg", 422

    existing_images = db[artist_name].find({"series" : series})
    max_index = 0
    for image in existing_images:
        if image["sequence"] > max_index:
            max_index = image["sequence"]
        if (image["name"] == name):
            return "Image name already used"
        else:
            continue
    sequence = max_index + 1

    url = name
    for char in url:
        if char.isspace():
            url = url.replace(" ", "_")
        elif not (char.isalnum() or (char == "-")):
            url = url.replace(char, "-")

    thumb_file = io.BytesIO()
    thumb = Image.open(image_file)
    thumb.thumbnail((360, 360))
    thumb.save(thumb_file, "JPEG")
    thumb_file.seek(0)

    file_client.upload_fileobj(image_file, 
                               "artist-api", 
                               f"{artist_name}/{series}/full/{url}.jpg", 
                               ExtraArgs={'ACL':'public-read'})


    file_client.upload_fileobj(thumb_file, 
                               "artist-api", 
                               f"{artist_name}/{series}/thumb/{url}.jpg", 
                               ExtraArgs={'ACL':'public-read'})

    image_file.close()
    thumb_file.close()

    image_data = {
        "url": f"/{series}/{url}",
        "name": name,
        "srcThumb": f"{artist_name}/{series}/thumb/{url}.jpg",
        "srcFull": f"{artist_name}/{series}/full/{url}.jpg",
        "caption": caption,
        "series": series,
        "sequence" : sequence
    }

    db[artist_name].insert_one(image_data)

    return "complete"

@application.route("/image/<id>", methods=["DELETE"])
@user_only
def delete_image(artist_name, id):
    image_collection = db[artist_name]
    image_collection.delete_one({"_id" : bson.ObjectId(id)})
    return "complete"

@application.route("/image/<id>", methods=["PUT"])
@user_only
def update_image(artist_name, id):
    image_collection = db[artist_name]
    updates = {"$set" : request.json}
    image_collection.update_one({"_id" : bson.ObjectId(id)}, updates)
    return "complete"

@application.route("/reorder", methods=["PUT"])
@user_only
def reorder_images(artist_name):
    image_collection = db[artist_name]
    updates = request.json
    print(updates)
    for image in updates:
        update = {"$set" : image["newSequence"]}
        print(update)
        image_collection.update_one({"_id": bson.ObjectId(image["_id"])}, update)
    return "complete"

if __name__ == "__main__":
    application.run(debug=True)
    

