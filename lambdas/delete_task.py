import json
import boto3
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

def handler(event, context):
    """
    Lambda function to handle the deletion of a task from a DynamoDB table.
    Parameters:
    event (dict): The event dictionary containing the request data. It must include 'pathParameters' with 'taskId'.
    context (object): The context in which the Lambda function is called.
    Returns:
    dict: A dictionary containing the HTTP status code and a response body.
        - 400: If 'taskId' is missing or invalid.
        - 204: If the task was successfully deleted.
        - 404: If the task was not found.
        - 500: If an internal server error occurred.
    """

    try:
        # Check if taskId is provided
        if 'pathParameters' not in event or 'taskId' not in event['pathParameters']:
            return {
                # Return a 400 status code and an error message if not provided
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing taskId in path parameters'})
            }

        # If taskId is provided, extract it
        task_id = event['pathParameters']['taskId']
        # Validate taskId format (assuming UUID format)
        try:
            uuid.UUID(task_id)
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid taskId format'})
            }

        # Delete item from DynamoDB
        response = table.delete_item(
            Key={'taskId': task_id},
            ConditionExpression="attribute_exists(taskId)"
        )

        # Check if the item was deleted
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            return {
                # Return a 204 status code if the item was deleted
                'statusCode': 204,
                'body': ''
            }
        else:
            return {
                # Return a 404 status code if the item was not found
                'statusCode': 404,
                'body': json.dumps({'error': 'Task not found'})
            }

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Task not found'})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }