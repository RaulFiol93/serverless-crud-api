import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

def handler(event, context):
    """
    Lambda function handler to retrieve a task by its taskId from a DynamoDB table.
    Parameters:
    event (dict): The event dictionary containing request data. Expected to have 'pathParameters' with 'taskId'.
    context (object): The context in which the Lambda function is called.
    Returns:
    dict: A dictionary containing the HTTP status code and the response body.
        - 200: Task found, returns the task item.
        - 400: Missing or invalid taskId in path parameters.
        - 404: Task not found.
        - 500: Internal server error.
    """

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
            # Return a 200 status code and the task item
            'statusCode': 200,
            'body': json.dumps(item)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }