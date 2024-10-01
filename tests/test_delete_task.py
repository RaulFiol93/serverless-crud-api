import unittest
import uuid
from lambdas.delete_task import handler
from test_create_task import TestCreateTask

class TestDeleteTask(unittest.TestCase):

    def test_delete_task_success(self):
        event = {
            "pathParameters": {"taskId": TestCreateTask.created_task_id}
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 204)

    def test_delete_task_invalid(self):
        event = {
            "pathParameters": {"taskId": "invalid-task-id"}
        }
        context = {}
        response = handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', response['body'])

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