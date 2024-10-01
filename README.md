# Serverless CRUD API

This project is a Serverless CRUD API built using AWS Lambda, API Gateway, and DynamoDB. It allows you to create, read, update, and delete tasks.

The CDK code creates the following infrastructure resources:

- API Gateway: An API Gateway is created to serve as the entry point for the CRUD operations. It routes HTTP requests to the appropriate Lambda functions.

- Lambda Functions: Four Lambda functions are created to handle the CRUD operations:

    - `create_task`: Handles the creation of a new task.
    - `get_task`: Retrieves a task by its ID.
    - `update_task`: Updates an existing task.
    - `delete_task`: Deletes a task by its ID.

- DynamoDB Table: A DynamoDB table named `TasksTable` is created to store the tasks. The table uses `taskId` as the primary key.

- AWS Distro for OpenTelemetry (ADOT): ADOT is enabled for tracing. This allows you to collect and visualize traces for the Lambda functions, providing insights into the performance and behavior of your application.

## Prerequisites

- Python 3.x
- AWS CLI configured with appropriate permissions
- Node.js (for AWS CDK)
- AWS CDK

## Setup

### Create a Virtual Environment

You need to create a virtual environment for running this CDK Python project. To manually create a virtual environment on MacOS and Linux:

```sh
$ python3 -m venv .venv
```

After the init process completes and the virtual environment is created, you can use the following step to activate your virtual environment.

```sh
$ source .venv/bin/activate
```

If you are on a Windows platform, you would activate the virtual environment like this:

```sh
% .venv\Scripts\activate.bat
```

### Install Dependencies

Once the virtual environment is activated, you can install the required dependencies.

```sh
$ pip install -r requirements.txt -r requirements-dev.txt
```

### Synthesize the CloudFormation Template

At this point, you can now synthesize the CloudFormation template for this code.

```sh
$ cdk synth
```

### If it is the first time running CDK in an AWS account, probably bootstrapping might be needed

```sh
$ cdk bootstrap
```

### Deploy the Stack

To deploy the stack to your AWS account, run:

```sh
$ cdk deploy
```

## Usage

### Create a Task

To create a task, send a POST request to the API Gateway endpoint with the following JSON body:

```json
{
    "title": "Task 1",
    "description": "This is task 1",
    "status": "pending"
}
```

```sh
curl -X POST https://your-api-gateway-endpoint/tasks \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Task 1",
        "description": "This is task 1",
        "status": "pending"
    }'
```



### Get a Task

To get a task, send a GET request to the API Gateway endpoint with the task ID as a path parameter:

```sh
curl -X GET https://your-api-gateway-endpoint/tasks/{taskId}
```

### Update a Task

To update a task, send a PUT request to the API Gateway endpoint with the task ID as a path parameter and the following JSON body:

```json
{
    "title": "Updated Task",
    "description": "Updated description",
    "status": "completed"
}
```

```sh
curl -X PUT https://your-api-gateway-endpoint/tasks/{taskId} \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Updated Task",
        "description": "Updated description",
        "status": "completed"
    }'
```

### Delete a Task

To delete a task, send a DELETE request to the API Gateway endpoint with the task ID as a path parameter:

```sh
curl -X DELETE https://your-api-gateway-endpoint/tasks/{taskId}
```

## Testing

### Running Unit Tests

To run the unit tests, use the following command:

```sh
$ python -m unittest discover tests/lambdas
```

### Test Cases

- **Create Task Success**: Tests if a task is successfully created.
- **Create Task Missing Body**: Tests if the appropriate error is returned when the request body is missing.
- **Get Task Success**: Tests if a task is successfully retrieved.
- **Get Task Not Found**: Tests if the appropriate error is returned when the task is not found.
- **Update Task Success**: Tests if a task is successfully updated.
- **Update Task Not Found**: Tests if the appropriate error is returned when the task is not found.
- **Delete Task Success**: Tests if a task is successfully deleted.
- **Delete Task Not Found**: Tests if the appropriate error is returned when the task is not found.

## Cleanup

To delete the stack and all resources created by the deployment, run:

```sh
$ cdk destroy
```