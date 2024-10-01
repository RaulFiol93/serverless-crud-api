import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

def handler(event, context):
    try:
        # Check if taskId is provided
        if 'pathParameters' not in event or 'taskId' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing taskId in path parameters'})
            }

        task_id = event['pathParameters']['taskId']

        # Validate taskId format (assuming UUID format)
        try:
            uuid.UUID(task_id)
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid taskId format'})
            }

        response = table.get_item(Key={'taskId': task_id})
        item = response.get('Item')
        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Task not found'})
            }
        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }