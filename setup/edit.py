import pymongo
import bson

db_uri = "mongodb+srv://jban28:LCEM7Y4bMmgZ@jban28mongodb.zztm45h.mongodb.net/?retryWrites=true&w=majority"

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))

db = dbclient["artCollections"]

artist = db["Matt_Pagett"]

image = artist.update_one({"_id" : bson.ObjectId("64edae6c114cf4ae44da2db1")}, {"$set" : {
    "s3KeyFull": "Matt_Pagett/bodies/full/test.jpg",
    "s3KeyThumb": "Matt_Pagett/bodies/thumb/test.jpg" }
    })