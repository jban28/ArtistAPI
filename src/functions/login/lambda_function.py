import json
import os
import pymongo
from hashlib import sha256
import jwt

secret = os.environ["secretKey"]
root_URL = os.environ["rootURL"]
db_uri = os.environ["databaseURI"]

dbclient = pymongo.MongoClient(db_uri, server_api=pymongo.server_api.ServerApi('1'))
db = dbclient["artCollections"]

def lambda_handler(event, context):
    # TODO implement
    auth = event["headers"]["Authorization"].split(":")
    username = auth[0]
    password = auth[1]
    try:
        user = db["users"].find_one({"username" : username},{"_id":0})
        if sha256(password.encode('utf-8')).hexdigest() == user["password"]:
            token = jwt.encode(
                {
                "artist": user["name"],
                }, secret, algorithm="HS256")
            return {
                'statusCode': 200,
                'body': json.dumps(token)
            }
        else:
            return {
                'statusCode': 401,
                'body': json.dumps('Password does not match username.')
            }
    except:
        return {
        'statusCode': 401,
        'body': json.dumps('Username not found')
    }