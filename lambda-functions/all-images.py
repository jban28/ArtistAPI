import json

def lambda_handler(event, context):
    # TODO implemen
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
