from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_iam as iam_,
    aws_apigateway as apigw_,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_iam as iam,
    aws_cognito as cognito_,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
import json

TABLE_NAME = "TasksTable"

class ServerlessCrudApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDb Table
        tasks_table = dynamodb_.Table(
            self,
            "TasksTable",
            table_name=TABLE_NAME,
            partition_key=dynamodb_.Attribute(
                name="taskId", type=dynamodb_.AttributeType.STRING),
            billing_mode=dynamodb_.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create IAM Role for Lambda Functions
        lambda_role = iam_.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam_.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam_.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam_.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
            ]
        )

        # Create Task Lambda Function
        create_task_lambda = lambda_.Function(
            self, "CreateTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="create_task.handler",
            code=lambda_.Code.from_asset("lambdas"),
            role=lambda_role,
            adot_instrumentation=lambda_.AdotInstrumentationConfig(
                layer_version=lambda_.AdotLayerVersion.from_python_sdk_layer_version(lambda_.AdotLambdaLayerPythonSdkVersion.LATEST),
                exec_wrapper=lambda_.AdotLambdaExecWrapper.INSTRUMENT_HANDLER
            )
        )
        tasks_table.grant_write_data(create_task_lambda)

        create_task_lambda_version = create_task_lambda.current_version

        # Create Task Lambda Function Alias
        create_task_lambda_alias = lambda_.Alias(
            self, "CreateTaskFunctionAlias",
            alias_name="CreateTaskFunctionProd",
            version=create_task_lambda_version
        )

        # Get Task Lambda Function
        get_task_lambda = lambda_.Function(
            self, "GetTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="get_task.handler",
            code=lambda_.Code.from_asset("lambdas"),
            role=lambda_role,
            adot_instrumentation=lambda_.AdotInstrumentationConfig(
                layer_version=lambda_.AdotLayerVersion.from_python_sdk_layer_version(lambda_.AdotLambdaLayerPythonSdkVersion.LATEST),
                exec_wrapper=lambda_.AdotLambdaExecWrapper.INSTRUMENT_HANDLER
            )
        )
        tasks_table.grant_read_data(get_task_lambda)

        get_task_lambda_version = get_task_lambda.current_version

        # Get Task Lambda Function Alias
        get_task_lambda_alias = lambda_.Alias(
            self, "GetTaskFunctionAlias",
            alias_name="GetTaskFunctionProd",
            version=get_task_lambda_version
        )

        # Update Lambda Function
        update_task_lambda = lambda_.Function(
            self, "UpdateTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="update_task.handler",
            code=lambda_.Code.from_asset("lambdas"),
            role=lambda_role,
            adot_instrumentation=lambda_.AdotInstrumentationConfig(
                layer_version=lambda_.AdotLayerVersion.from_python_sdk_layer_version(lambda_.AdotLambdaLayerPythonSdkVersion.LATEST),
                exec_wrapper=lambda_.AdotLambdaExecWrapper.INSTRUMENT_HANDLER
            )
        )
        tasks_table.grant_write_data(update_task_lambda)

        update_task_lambda_version = update_task_lambda.current_version

        # Update Task Lambda Function Alias
        update_task_lambda_alias = lambda_.Alias(
            self, "UpdateTaskFunctionAlias",
            alias_name="UpdateTaskFunctionProd",
            version=update_task_lambda_version
        )

        # Delete Lambda Function
        delete_task_lambda = lambda_.Function(
            self, "DeleteTaskFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="delete_task.handler",
            code=lambda_.Code.from_asset("lambdas"),
            role=lambda_role,
            adot_instrumentation=lambda_.AdotInstrumentationConfig(
                layer_version=lambda_.AdotLayerVersion.from_python_sdk_layer_version(lambda_.AdotLambdaLayerPythonSdkVersion.LATEST),
                exec_wrapper=lambda_.AdotLambdaExecWrapper.INSTRUMENT_HANDLER
            )
        )
        tasks_table.grant_write_data(delete_task_lambda)

        delete_task_lambda_version = delete_task_lambda.current_version

        # Update Task Lambda Function Alias
        delete_task_lambda_alias = lambda_.Alias(
            self, "DeleteTaskFunctionAlias",
            alias_name="DeleteTaskFunctionProd",
            version=update_task_lambda_version
        )

        # Create the S3 bucket for the static web page
        bucket = s3.Bucket(self, 'StaticWebsiteBucket',
            website_index_document='index.html',
            removal_policy=RemovalPolicy.DESTROY
        )

        # Copy the index.html file to the bucket
        s3_deployment.BucketDeployment(self, 'DeployWebsite',
            sources=[s3_deployment.Source.asset('static')],
            destination_bucket=bucket
        )

        # Create the IAM role for API Gateway to access S3
        api_gateway_role = iam.Role(self, 'ApiGatewayS3Role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com')
        )

        api_gateway_role.add_to_policy(iam.PolicyStatement(
            actions=['s3:GetObject'],
            resources=[f'{bucket.bucket_arn}/*']
        ))

        # Create Cognito User Pool
        user_pool = cognito_.UserPool(self, "UserPool", self_sign_up_enabled=True, removal_policy=RemovalPolicy.DESTROY)
        user_pool_client = user_pool.add_client("ApiGatewayClient", auth_flows=cognito_.AuthFlow(
            user_password=True,
        ),
            supported_identity_providers=[
                cognito_.UserPoolClientIdentityProvider.COGNITO]
        )

        # Create API Gateway
        api = apigw_.RestApi(self, "TasksApi",
            rest_api_name="Tasks Service",
            description="This service serves tasks.",
            deploy_options=apigw_.StageOptions(tracing_enabled=True)
        )

        # Create API Gateway Resources
        tasks = api.root.add_resource("tasks")
        task = tasks.add_resource("{taskId}")
        
        # Create Authorizer
        auth = apigw_.CognitoUserPoolsAuthorizer(self, "TasksAuthorizer", cognito_user_pools=[user_pool])

        # Create API Gateway Methods
        create_method = tasks.add_method("POST", apigw_.LambdaIntegration(create_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="201", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="400", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="404", response_models={"application/json": apigw_.Model.EMPTY_MODEL})],
                        authorization_type=apigw_.AuthorizationType.COGNITO,
                        authorizer=auth,
                        ),
        get_method = task.add_method("GET", apigw_.LambdaIntegration(get_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="200", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="400", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="404", response_models={"application/json": apigw_.Model.EMPTY_MODEL})],
                        authorization_type=apigw_.AuthorizationType.COGNITO,
                        authorizer=auth,
                        ),
        update_method = task.add_method("PUT", apigw_.LambdaIntegration(update_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="200", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="400", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="404", response_models={"application/json": apigw_.Model.EMPTY_MODEL})],
                        authorization_type=apigw_.AuthorizationType.COGNITO,
                        authorizer=auth,
                        ),
        delete_method= task.add_method("DELETE", apigw_.LambdaIntegration(delete_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="204", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="400", response_models={"application/json": apigw_.Model.EMPTY_MODEL}),
                                            apigw_.MethodResponse(status_code="404", response_models={"application/json": apigw_.Model.EMPTY_MODEL})],
                        authorization_type=apigw_.AuthorizationType.COGNITO,
                        authorizer=auth,
                        ),
        
        # Integrate the S3 bucket with the root path
        s3_integration = apigw_.AwsIntegration(
            service='s3',
            integration_http_method='GET',
            path=f'{bucket.bucket_name}/index.html',
            options=apigw_.IntegrationOptions(
                credentials_role=api_gateway_role,
                integration_responses=[
                    apigw_.IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type'
                        }
                    )
                ]
            )
        )
        
        api.root.add_method('GET', s3_integration, authorization_type=apigw_.AuthorizationType.NONE,
            method_responses=[
                apigw_.MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                    }
                )
            ]
        )

        # Add a bucket policy to allow API Gateway to access the bucket
        bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[f"{bucket.bucket_arn}/*"],
            principals=[iam.ServicePrincipal("apigateway.amazonaws.com")]
        ))