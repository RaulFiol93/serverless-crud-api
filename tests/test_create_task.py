import unittest
import json
from lambdas.create_task import handler

class TestCreateTask(unittest.TestCase):
    created_task_id = None

    # 
    @classmethod
    def setUpClass(cls):
        event = {
            "body": '{"title": "Task 1", "description": "This is task 1", "status": "pending"}'
        }
        context = {}
        response = handler(event, context)
        response_body = json.loads(response['body'])
        cls.created_task_id = response_body['taskId']

    # Test case to check if a task is successfully created
    def test_create_task_success(self):
        self.assertIsNotNone(TestCreateTask.created_task_id)

    # Test case to check an error is returned when body is missing
    def test_create_task_missing_body(self):
        event = {"body": '{}'}
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', response['body'])

if __name__ == '__main__':
    unittest.main()