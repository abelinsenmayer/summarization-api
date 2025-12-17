# Summarization API

A serverless text summarization API built with AWS Lambda and API Gateway, deployed using AWS CDK.

## Architecture

- **AWS Lambda**: Serverless compute for the API logic
- **API Gateway**: RESTful API endpoint with CORS support
- **Amazon Bedrock**: AI service for text summarization
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

### 3. Configure AWS CDK

If you haven't already, bootstrap AWS CDK:
```bash
cdk bootstrap
```

## Deployment

### Deploy the Stack

```bash
cdk deploy
```

The deployment will:
- Create a Lambda function with the summarization logic
- Set up API Gateway with the `/summarize` and `/health` endpoints
- Configure logging and monitoring
- Set up the necessary IAM permissions including Bedrock runtime access

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

### Summarize Endpoint

```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text to summarize goes here..."
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "summary": "The summarized text...",
    "original_length": 1234,
    "summary_length": 156
  }
}
```

#### Request Body
- `text` (required): The text to be summarized. Maximum length is configurable via the `MAX_TEXT_LENGTH` environment variable (default: 1000 characters).

#### Error Responses
Missing text field:
```json
{
  "error": "Missing required field: text"
}
```

Text exceeds maximum length:
```json
{
  "error": "Text exceeds maximum length of 1000 characters"
}
```

#### Bedrock Integration
The summarization endpoint uses Amazon Bedrock with the following configuration:
- **Model**: Anthropic Claude 3.5 Haiku (`us.anthropic.claude-3-5-haiku-20241022-v1:0`)
- **Region**: us-east-1
- **API**: Bedrock Converse API

The service sends a prompt to Claude requesting a concise and clear summary of the provided text. The response includes the summary along with metadata about the original and summary text lengths.

## Development

### Local Development

To run the Lambda function locally for testing:

```bash
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

## Cost Considerations

- Lambda: Charged per request and execution time
- API Gateway: Charged per request
- CloudWatch Logs: Charged per GB ingested and stored

## Security

- Lambda function has minimal required permissions including Bedrock runtime access
- API Gateway has CORS enabled (configure specific origins for production)
- All traffic is encrypted via HTTPS
- Input validation prevents abuse (configurable text length limits)

## Cleanup

To remove all deployed resources:

```bash
cdk destroy
```

## License

This project is licensed under the MIT License.
