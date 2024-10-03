import requests
import json
import os
import uuid
import random
import time

API_ENDPOINT = os.getenv("API_GATEWAY") + "/tasks"
ID_TOKEN = os.getenv("ID_TOKEN")

def create_task(task_number):
    task = {
        "title": f"Task {task_number}",
        "description": f"This is task number {task_number}",
        "status": "pending"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": ID_TOKEN
    }
    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(task))
    return response

def get_task(task_id):
    headers = {
        "Authorization": ID_TOKEN
    }
    response = requests.get(f"{API_ENDPOINT}/{task_id}", headers=headers)
    return response

def update_task(task_id):
    updated_task = {
        "title": "Updated Task",
        "description": "Updated description",
        "status": "completed"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": ID_TOKEN
    }
    response = requests.put(f"{API_ENDPOINT}/{task_id}", headers=headers, data=json.dumps(updated_task))
    return response

def delete_task(task_id):
    headers = {
        "Authorization": ID_TOKEN
    }
    response = requests.delete(f"{API_ENDPOINT}/{task_id}", headers=headers)
    return response

def create_invalid_task():
    # Missing required fields to trigger 400 Bad Request
    task = {
        "description": "This is an invalid task"
    }
    response = requests.post(API_ENDPOINT, headers={"Content-Type": "application/json"}, data=json.dumps(task))
    return response

def simulate_server_error():
    # Simulate a server error by sending invalid data that the server cannot process
    task = {
        "title": "Task",
        "description": "This will cause a server error",
        "status": "pending" * 3  # Exaggerated status to cause a server error
    }
    response = requests.post(API_ENDPOINT, headers={"Content-Type": "application/json"}, data=json.dumps(task))
    return response

def generate_traffic():
    task_ids = []

    # Create tasks
    for i in range(15):
        response = create_task(i + 1)
        if response.status_code == 201:
            task_id = response.json().get('taskId')
            task_ids.append(task_id)
        print(f"Create Task Response: {response.status_code}, {response.text}")

    # Generate traffic
    for _ in range(30):
        action = random.choice(["get", "update", "delete", "invalid_get", "invalid_update", "invalid_delete", "invalid_create", "server_error"])
        if action == "get" and task_ids:
            task_id = random.choice(task_ids)
            response = get_task(task_id)
        elif action == "update" and task_ids:
            task_id = random.choice(task_ids)
            response = update_task(task_id)
        elif action == "delete" and task_ids:
            task_id = random.choice(task_ids)
            response = delete_task(task_id)
            if response.status_code == 204:
                task_ids.remove(task_id)
        elif action == "invalid_get":
            response = get_task(str(uuid.uuid4()))
        elif action == "invalid_update":
            response = update_task(str(uuid.uuid4()))
        elif action == "invalid_delete":
            response = delete_task(str(uuid.uuid4()))
        elif action == "invalid_create":
            response = create_invalid_task()
        elif action == "server_error":
            response = simulate_server_error()
        else:
            continue

        print(f"{action.capitalize()} Task Response: {response.status_code}, {response.text}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    generate_traffic()