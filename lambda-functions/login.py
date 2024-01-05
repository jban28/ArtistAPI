import json

def lambda_handler(event, context):
    # TODO implement testing again and again and again and again
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
