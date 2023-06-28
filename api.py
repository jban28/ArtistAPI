from flask import Flask
from flask import request
from flask_cors import CORS
from PIL import Image
import jwt
from hashlib import sha256
import pymongo
import bson
import os

secret = "secret_key"
root_URL = "http://localhost:5000/images"

dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = dbclient["artCollections"]

app = Flask(__name__)
CORS(app)

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

@app.route("/login")
def login():
    username = request.args.get("username")
    password = request.args.get("password")
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

@app.route("/all-images")
def all_images():
    image_collection = db[request.args.get("artist")]
    image_list = []
    for image in image_collection.find():
        image["_id"] = str(image["_id"])
        image["srcFull"] = f"{root_URL}/{image['srcFull']}"
        image["srcThumb"] = f"{root_URL}/{image['srcThumb']}"
        image_list.append(image)
    return image_list

@app.route("/image", methods=["POST"])
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

    try:
        image_file = request.files["file"]
    except:
        return "File upload failed", 422
    
    url = name
    for char in url:
        if char.isspace():
            url = url.replace(" ", "_")
        elif not (char.isalnum() or (char == "-")):
            url = url.replace(char, "")

    if image_file.content_type != "image/jpeg":
        return "File must be jpeg", 422
    

    image_file.save(f"./images/{artist_name}/full/{url}.jpg")
    image_file.close()

    image_file = Image.open(f"./images/{artist_name}/full/{url}.jpg")
    image_file.thumbnail((360, 360))
    image_file.save(f"./images/{artist_name}/thumb/{url}.jpg")
    image_file.close()

    image_data = {
        "url": url,
        "name": name,
        "srcThumb": f"thumb/{url}.jpg",
        "srcFull": f"full/{url}.jpg",
        "caption": caption,
        "series": series
    }
    return "complete"

@app.route("/image/<id>", methods=["DELETE"])
@user_only
def delete_image(artist_name, id):
    image_collection = db[artist_name]
    image_collection.delete_one({"_id" : bson.ObjectId(id)})
    return "complete"

@app.route("/image/<id>", methods=["PUT"])
@user_only
def update_image(artist_name, id):
    image_collection = db[artist_name]
    updates = {"$set" : request.json}
    print(updates)
    image_collection.update_one({"_id" : bson.ObjectId(id)}, updates)
    return "complete"