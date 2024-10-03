import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

def handler(event, context):
    """
    Lambda function handler to create a new task in the DynamoDB table.

    Parameters:
    event (dict): The event dictionary containing the HTTP request details.
                  Expected to have a 'body' key with a JSON string containing 'title', 'description', and 'status'.
    context (object): The context in which the Lambda function is called.

    Returns:
    dict: A dictionary containing the HTTP response with a status code and a body.
          - 201: On success, the body contains the 'taskId' of the created task.
          - 400: If missing key or invalid.
          - 500: On general error, the body contains an error message with the exception details.
    """
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        task_id = str(uuid.uuid4())
        item = {
            'taskId': task_id,
            'title': body['title'],
            'description': body['description'],
            'status': body['status']
        }
        # Insert the item into the DynamoDB table
        table.put_item(Item=item)
        # Return the task ID in the response and a 201 status code
        return {
            'statusCode': 201,
            'body': json.dumps({'taskId': task_id})
        }
    # Handle missing key errors
    except KeyError as e:
        return {
            # Return a 400 status code and an error message with the missing key
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing key: {e}'})
        }
    except Exception as e:
        return {
            # Return a 500 status code and an error message with the exception details
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }