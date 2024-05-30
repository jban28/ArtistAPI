import json
import jwt
import os

secret = os.environ["secretKey"]
root_URL = os.environ["rootURL"]
db_uri = os.environ["databaseURI"]

def lambda_handler(event, context):
    try: 
        auth = event['authorizationToken']
        token = jwt.decode(auth, secret, algorithms="HS256")
    except jwt.exceptions.InvalidSignatureError:
        return {
            'principalId': token['artist'],
            'policyDocument': {
                "Version": "2012-10-17",
                "Statement": [
                    {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": event['methodArn']
                    }
                ]
            }
        }
    except:
        return "other error"
    else:
        return {
            'principalId': token['artist'],
            'policyDocument': {
                "Version": "2012-10-17",
                "Statement": [
                    {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event['methodArn']
                    }
                ]
            },
            'context': {
                'artist': token['artist']
            }
        }
