import unittest
import uuid
from lambdas.get_task import handler
from test_create_task import TestCreateTask

class TestGetTask(unittest.TestCase):

    # Test case to check if a task is successfully retrieved
    def test_get_task_success(self):
        event = {
            "pathParameters": {"taskId": TestCreateTask.created_task_id}
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('title', response['body'])

    # Test case to check an error is returned when the task id is not valid
    def test_get_task_invalid(self):
        event = {
            "pathParameters": {"taskId": "invalid-task-id"}
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', response['body'])

    # Test case to check an error is returned when the task is not found
    def test_get_task_not_found(self):
        event = {
            "pathParameters": {"taskId": str(uuid.uuid4())}
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('error', response['body'])

if __name__ == '__main__':
    unittest.main()