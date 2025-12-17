#!/usr/bin/env python3
import os
import aws_cdk as cdk
from summarization_api.summarization_api_stack import SummarizationApiStack

app = cdk.App()

# Get AWS account and region from CDK context
aws_account = app.node.try_get_context("aws_account") or os.getenv('CDK_DEFAULT_ACCOUNT')
aws_region = app.node.try_get_context("aws_region") or os.getenv('CDK_DEFAULT_REGION')

SummarizationApiStack(app, "SummarizationApiStack",
    env=cdk.Environment(
        account=aws_account,
        region=aws_region
    )
)

app.synth()
