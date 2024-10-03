import boto3
import sys
import getpass

def set_api_gateway_url(api_name, region):
    # Initialize API Gateway client
    apigateway_client = boto3.client('apigateway')

    # Get the API ID
    response = apigateway_client.get_rest_apis()
    api_id = next(item['id'] for item in response['items'] if item['name'] == api_name)

    # Construct the API Gateway URL
    api_gateway_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"

    # Set the environment variable
    # os.environ['API_GATEWAY'] = api_gateway_url
    print(f"export API_GATEWAY={api_gateway_url}")

def create_user(user_pool_id, username, email, password):
    client = boto3.client('cognito-idp')
    
    # Create the user
    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {'Name': 'email', 'Value': email},
            {'Name': 'email_verified', 'Value': 'true'}
        ],
        TemporaryPassword=password,
        MessageAction='SUPPRESS'
    )
    
    # Set the user's password permanently
    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=username,
        Password=password,
        Permanent=True
    )

def authenticate_user(client_id, username, password):
    client = boto3.client('cognito-idp')
    
    # Authenticate the user
    response = client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        },
        ClientId=client_id
    )
    
    # Extract the id_token from the authentication result
    id_token = response['AuthenticationResult']['IdToken']
    
    # Print the id_token in a format that can be sourced
    print(f"export ID_TOKEN={id_token}")

def change_user_password(user_pool_id, username, new_password):
    client = boto3.client('cognito-idp')
    
    # Change the user's password
    client.admin_set_user_password(
        UserPoolId=user_pool_id,
        Username=username,
        Password=new_password,
        Permanent=True
    )

def get_user_pool_id():
    client = boto3.client('cognito-idp')
    response = client.list_user_pools(MaxResults=10)
    for pool in response['UserPools']:
        if 'UserPool' in pool['Name']:
            return pool['Id']
    return None

def get_client_id(user_pool_id):
    client = boto3.client('cognito-idp')
    response = client.list_user_pool_clients(UserPoolId=user_pool_id, MaxResults=10)
    for client in response['UserPoolClients']:
        if 'UserPoolApiGatewayClient' in client['ClientName']:
            return client['ClientId']
    return None

if __name__ == "__main__":
    user_pool_id = get_user_pool_id()
    if not user_pool_id:
        print("Failed to retrieve USER_POOL_ID.")
        sys.exit(1)
    
    client_id = get_client_id(user_pool_id)
    if not client_id:
        print("Failed to retrieve CLIENT_ID.")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python cognito_helper.py {create-user|username <username>|change-password <username>}")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create-user":
        username = input("Enter the username: ")
        email = input("Enter the email: ")
        password = getpass.getpass("Enter the password: ")
        create_user(user_pool_id, username, email, password)
        authenticate_user(client_id, username, password)
    elif command == "authenticate-user":
        if len(sys.argv) != 3:
            print("Usage: python helper-functions.py auth-user <username>")
            sys.exit(1)
        username = sys.argv[2]
        password = getpass.getpass("Enter the password: ")
        authenticate_user(client_id, username, password)
    elif command == "change-password":
        if len(sys.argv) != 3:
            print("Usage: python cognito_helper.py change-password <username>")
            sys.exit(1)
        username = sys.argv[2]
        new_password = getpass.getpass("Enter the new password: ")
        change_user_password(user_pool_id, username, new_password)
    elif command == "get-api-url":
        # if the user provides arguments, use them
        if len(sys.argv) > 3:
            api_name = sys.argv[2]
            region = sys.argv[3]
            set_api_gateway_url(api_name, region)
        # Otherwise, use the default values or prompt the user
        else:
            try:
                set_api_gateway_url("Tasks Service", "us-east-1")
            # If the API Gateway is not found, the user can provide the API name and region
            except IndexError:
                api_name = input("Enter the API name: ")
                region = input("Enter the region: ")
                set_api_gateway_url(api_name, region)
    else:
        print("Usage: python cognito_helper.py {create-user|username <username>|change-password <username>|get-api-url [api_name region]}")
        sys.exit(1)