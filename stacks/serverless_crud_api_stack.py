from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_iam as iam_,
    aws_apigateway as apigw_,
    aws_s3 as s3,
    aws_iam as iam,
    Duration,
)
from constructs import Construct

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

        # Create the S3 bucket for the static web page
        bucket = s3.Bucket(self, 'StaticWebsiteBucket',
            website_index_document='index.html'
        )

        # Create the IAM role for API Gateway to access S3
        api_gateway_role = iam.Role(self, 'ApiGatewayS3Role',
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com')
        )

        api_gateway_role.add_to_policy(iam.PolicyStatement(
            actions=['s3:GetObject'],
            resources=[f'{bucket.bucket_arn}/*']
        ))

        # Create API Gateway
        api = apigw_.RestApi(self, "TasksApi",
            rest_api_name="Tasks Service",
            description="This service serves tasks.",
            deploy_options=apigw_.StageOptions(tracing_enabled=True)
        )

        tasks = api.root.add_resource("tasks")
        task = tasks.add_resource("{taskId}")

        tasks.add_method("POST", apigw_.LambdaIntegration(create_task_lambda),
                         request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                         method_responses=[apigw_.MethodResponse(status_code="201"),
                                           apigw_.MethodResponse(status_code="400"),
                                           apigw_.MethodResponse(status_code="404")])
        task.add_method("GET", apigw_.LambdaIntegration(get_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="200"),
                                            apigw_.MethodResponse(status_code="400"),
                                          apigw_.MethodResponse(status_code="404")])
        task.add_method("PUT", apigw_.LambdaIntegration(update_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="200"),
                                          apigw_.MethodResponse(status_code="400"),
                                          apigw_.MethodResponse(status_code="404")])
        task.add_method("DELETE", apigw_.LambdaIntegration(delete_task_lambda),
                        request_models={"application/json": apigw_.Model.EMPTY_MODEL},
                        method_responses=[apigw_.MethodResponse(status_code="204"),
                                          apigw_.MethodResponse(status_code="400"),
                                          apigw_.MethodResponse(status_code="404")])
        
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
                            'method.response.header.Content-Type': 'text/html'
                        }
                    )
                ]
            )
        )

        api.root.add_method('GET', s3_integration, method_responses=[
            apigw_.MethodResponse(
                status_code='200',
                response_parameters={
                    'method.response.header.Content-Type': True
                }
            )
        ])

        # Add a bucket policy to allow API Gateway to access the bucket
        bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[f"{bucket.bucket_arn}/*"],
            principals=[iam.ServicePrincipal("apigateway.amazonaws.com")]
        ))