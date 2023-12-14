import pymongo
import json
from hashlib import sha256

db_uri = json.load(open("deployment/config.json", "r"))["databaseURI"]

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))

db = dbclient["artCollections"]

artist = db["Matt_Pagett"]
users = db["users"]

artist.insert_many(json.load(open("setup/images.json", "r")))

matt = {
    "name" : "Matt_Pagett",
    "username" : "mattPagett",
    "password" : sha256("GrwNg7KeCL".encode('utf-8')).hexdigest()
    }

users.insert_one(matt)
