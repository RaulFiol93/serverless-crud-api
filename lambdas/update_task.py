import json
import boto3
import uuid
# import logging
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TasksTable')

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

def handler(event, context):
    # logger.info("Received event: %s", event)
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
        # logger.error("Missing key: %s", e)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing key: {e}'})
        }
    except ClientError as e:
        # logger.error("ClientError: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': e.response['Error']['Message']})
        }
    except Exception as e:
        # logger.error("Error: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }