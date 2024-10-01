import json
import boto3
import uuid
# import logging

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

def handler(event, context):
    # logger.info("Received event: %s", event)
    try:
        body = json.loads(event.get('body', '{}'))
        task_id = str(uuid.uuid4())
        item = {
            'taskId': task_id,
            'title': body['title'],
            'description': body['description'],
            'status': body['status']
        }
        table.put_item(Item=item)
        return {
            'statusCode': 201,
            'body': json.dumps({'taskId': task_id})
        }
    except KeyError as e:
        # logger.error("Missing key: %s", e)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing key: {e}'})
        }
    except Exception as e:
        # logger.error("Error: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }