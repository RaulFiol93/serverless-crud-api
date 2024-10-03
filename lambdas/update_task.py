import json
import boto3
import uuid
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

def handler(event, context):
    """
    Lambda function to update a task in a DynamoDB table.
    Parameters:
    event (dict): The event dictionary containing the request data.
        - pathParameters (dict): Dictionary containing path parameters.
            - taskId (str): The ID of the task to be updated.
        - body (str): JSON string containing the task details to be updated.
            - title (str): The new title of the task.
            - description (str): The new description of the task.
            - status (str): The new status of the task.
    context (object): The context in which the function is called.
    Returns:
    dict: A dictionary containing the status code and response body.
        - 200: If the task was successfully updated.
        - 400: If missing key or invalid.
        - 404: If the task was not found.
        - 500: If an internal server error occurred.
    """

    try:
        # Check if taskId is provided
        if 'pathParameters' not in event or 'taskId' not in event['pathParameters']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing taskId in path parameters'})
            }

        task_id = event['pathParameters']['taskId']
        body = json.loads(event['body'])

        # Validate taskId format (assuming UUID format)
        try:
            uuid.UUID(task_id)
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid taskId format'})
            }

        # Check if the task exists
        response = table.get_item(Key={'taskId': task_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Task not found'})
            }

        # Update the task
        update_expression = "set title=:t, description=:d, #s=:s"
        expression_attribute_values = {
            ':t': body['title'],
            ':d': body['description'],
            ':s': body['status']
        }
        expression_attribute_names = {
            '#s': 'status'
        }
        response = table.update_item(
            Key={'taskId': task_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="UPDATED_NEW"
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing key: {e}'})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': e.response['Error']['Message']})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }