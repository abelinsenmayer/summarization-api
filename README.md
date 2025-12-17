# Summarization API

A serverless text summarization API built with AWS Lambda and API Gateway, deployed using AWS CDK.

## Architecture

- **AWS Lambda**: Serverless compute for the API logic
- **API Gateway**: RESTful API endpoint with CORS support
- **CloudWatch Logs**: Centralized logging and monitoring

## Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- Node.js (for AWS CDK)
- Poetry (optional, for dependency management)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd summarization-api
```

### 2. Install Dependencies

Using Poetry (recommended):
```bash
poetry install
poetry shell
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 3. Configure AWS CDK

If you haven't already, bootstrap AWS CDK:
```bash
cdk bootstrap
```

## Deployment

### Deploy the Stack

```bash
cd infrastructure
cdk deploy
```

The deployment will:
- Create a Lambda function with the placeholder code
- Set up API Gateway with the `/summarize` and `/health` endpoints
- Configure logging and monitoring
- Set up the necessary IAM permissions

After deployment, the CDK will output the API URL.

## API Usage

### Health Check

```bash
curl https://your-api-id.execute-api.region.amazonaws.com/prod/health
```

Response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### Summarize Endpoint (Placeholder)

```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/summarize \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{
  "message": "Hello World - Summarization endpoint ready for Bedrock integration"
}
```

## Development

### Local Development

To run the Lambda function locally for testing:

```bash
cd lambda
python -m pytest tests/
```

### Making Changes

1. Update the Lambda code in `lambda/summarization.py`
2. Update the CDK infrastructure in `infrastructure/`
3. Deploy changes:
   ```bash
   cdk diff  # Review changes
   cdk deploy
   ```

### Updating Dependencies

Using Poetry:
```bash
poetry add <package-name>
poetry install
```

Or update `pyproject.toml` manually.

## Future Integration

This API is designed to be integrated with AWS Bedrock for AI summarization. To add Bedrock integration:

1. Update the Lambda function in `lambda/summarization.py`
2. Add necessary AWS SDK dependencies
3. Configure IAM permissions for Bedrock access
4. Update the CDK stack if additional resources are needed

## Monitoring and Troubleshooting

### CloudWatch Logs

View Lambda logs:
```bash
aws logs tail /aws/lambda/SummarizationApiStack-SummarizationFunction --follow
```

View API Gateway logs:
```bash
aws logs tail /aws/apigateway/SummarizationApi --follow
```

### Common Issues

1. **500 Internal Error**: Check CloudWatch logs for detailed error messages
2. **Timeout**: The Lambda has a 5-minute timeout. Adjust as needed for your use case

## Cost Considerations

- Lambda: Charged per request and execution time
- API Gateway: Charged per request
- CloudWatch Logs: Charged per GB ingested and stored

## Security

- Lambda function has minimal required permissions
- API Gateway has CORS enabled (configure specific origins for production)
- All traffic is encrypted via HTTPS

## Cleanup

To remove all deployed resources:

```bash
cd infrastructure
cdk destroy
```

## License

This project is licensed under the MIT License.
