import json

def lambda_handler(event, context):
    auth = event['headers']["Authorization"].split(":")
    username = auth[0]
    password = auth[1]

    return {
        'statusCode': 200,
        'body': json.dumps(event),
    }



if __name__ == "__main__":
    test_event = {
        "path": "/test/hello"
    }
    lambda_handler(test_event)