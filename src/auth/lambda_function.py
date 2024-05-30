import json
import jwt
import os

secret = os.environ["secretKey"]
root_URL = os.environ["rootURL"]
db_uri = os.environ["databaseURI"]

def lambda_handler(event, context):
    token = event['authorizationToken']

    try: 
        auth = event['headers']['Authorization']
        token = jwt.decode(auth, secret, algorithms="HS256")
    except jwt.exceptions.InvalidSignatureError:
        return "Invalid signature"
    except:
        return "other error"
    else:
        return {
            'statusCode': 200,
            'body': {
                'policyDocument': {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": "arn:aws:execute-api:eu-west-2:053630928262:k17ufb7rzg/ESTestInvoke-stage/GET/"
                        }
                    ]
                },
                'context': {
                    'token': token
                }
            }
        }
