import unittest
import uuid
from lambdas.update_task import handler
from test_create_task import TestCreateTask

class TestUpdateTask(unittest.TestCase):

    def test_update_task_success(self):
        event = {
            "pathParameters": {"taskId": TestCreateTask.created_task_id},
            "body": '{"title": "Updated Task", "description": "Updated description", "status": "completed"}'
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('title', response['body'])

    def test_update_task_invalid(self):
        event = {
            "pathParameters": {"taskId": "invalid-task-id"},
            "body": '{"title": "Updated Task", "description": "Updated description", "status": "completed"}'
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', response['body'])

    def test_get_task_not_found(self):
        event = {
            "pathParameters": {"taskId": str(uuid.uuid4())},
            "body": '{"title": "Updated Task", "description": "Updated description", "status": "completed"}'
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('error', response['body'])

if __name__ == '__main__':
    unittest.main()