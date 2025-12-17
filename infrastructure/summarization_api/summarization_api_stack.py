from aws_cdk import (
    Stack,
    aws_apigatewayv2 as apigatewayv2,
    aws_apigatewayv2_integrations as apigateway_integrations,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class SummarizationApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function for summarization
        summarization_lambda = _lambda.Function(
            self, "SummarizationFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="summarization.handler",
            code=_lambda.Code.from_asset("./lambda"),
            timeout=Duration.minutes(5),
            memory_size=512,
            dead_letter_queue_enabled=True,
            retry_attempts=2
        )
        
        # Grant permission to invoke Bedrock models
        summarization_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['bedrock:InvokeModel'],
                resources=['*']
            )
        )

        # HTTP API Gateway
        api = apigatewayv2.HttpApi(
            self, "SummarizationApi",
            api_name="Summarization API",
            description="API for AI text summarization",
            cors_preflight=apigatewayv2.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigatewayv2.CorsHttpMethod.POST, apigatewayv2.CorsHttpMethod.GET],
                allow_headers=["*"]
            )
        )

        # Create a route for summarize
        api.add_routes(
            path="/summarize",
            methods=[apigatewayv2.HttpMethod.POST],
            integration=apigateway_integrations.HttpLambdaIntegration(
                "SummarizeIntegration",
                handler=summarization_lambda,
                payload_format_version=apigatewayv2.PayloadFormatVersion.VERSION_2_0
            )
        )

        # Create a route for health check
        api.add_routes(
            path="/health",
            methods=[apigatewayv2.HttpMethod.GET],
            integration=apigateway_integrations.HttpLambdaIntegration(
                "HealthIntegration",
                handler=summarization_lambda,
                payload_format_version=apigatewayv2.PayloadFormatVersion.VERSION_2_0
            )
        )

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="URL of the Summarization API"
        )
