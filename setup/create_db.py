import pymongo
import json
from hashlib import sha256

db_uri = "mongodb+srv://jban28:uRE3qnUHN8htLoMJ@jban28mongodb.zztm45h.mongodb.net/?retryWrites=true&w=majority"

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))

db = dbclient["artCollections"]

artist = db["Matt_Pagett"]
users = db["users"]

artist.insert_many(json.load(open("./setup/images.json", "r")))

matt = {
    "name" : "Matt_Pagett",
    "username" : "mattPagett",
    "password" : sha256("password123".encode('utf-8')).hexdigest()
    }

users.insert_one(matt)
