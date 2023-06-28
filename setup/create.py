import pymongo
import json
from hashlib import sha256


dbclient = pymongo.MongoClient("mongodb://localhost:27017/")

db = dbclient["artCollections"]
artist = db["Matt Pagett"]
users = db["users"]

artist.insert_many(json.load(open("bodies.json", "r")))
artist.insert_many(json.load(open("flowers.json", "r")))

matt = {
    "name" : "Matt Pagett",
    "username" : "mattPagett",
    "password" : sha256("password123".encode('utf-8')).hexdigest()
    }

users.insert_one(matt)
