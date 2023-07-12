import pymongo

db_uri = "mongodb+srv://jban28:uRE3qnUHN8htLoMJ@jban28mongodb.zztm45h.mongodb.net/?retryWrites=true&w=majority"

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))

db = dbclient["artCollections"]

artist = db["Matt_Pagett"]

images = artist.find({"series" : "flowers"})

for image in images:
    x = image["sequence"]
    artist.update_one(image, {"$set": {"sequence" : 56-x}})