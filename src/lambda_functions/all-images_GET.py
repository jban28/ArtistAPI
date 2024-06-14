import json
import os
import pymongo

db_uri = os.environ["databaseURI"]
root_URL = os.environ["rootURL"]

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))
db = dbclient["artCollections"]


def lambda_handler(event, context):
    artist = event["queryStringParameters"]["artist"]
    return {
        'statusCode': 200,
        'body': json.dumps(all_images(artist))
    }


def all_images(artist):
    image_collection = db[artist]
    image_list_return = []
    image_list = image_collection.find().sort("sequence", -1)
    for image in image_list:
        image["_id"] = str(image["_id"])
        image["srcFull"] = f"{root_URL}/{image['srcFull']}"
        image["srcThumb"] = f"{root_URL}/{image['srcThumb']}"
        image_list_return.append(image)
    return image_list_return

def all_images_by_series(artist):
    image_collection = db[artist]
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