import json
import logging
import os
from bedrock_service import summarize_text

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Lambda handler for the API
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse HTTP request
        http_method = event['requestContext']['http']['method']
        path = event['requestContext']['http']['path']
        
        # Health check endpoint
        if http_method == 'GET' and path == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'message': 'API is running'
                })
            }
        
        # Summarize endpoint
        if http_method == 'POST' and path == '/summarize':
            try:
                # Parse request body
                body = json.loads(event.get('body', '{}'))
                text_to_summarize = body.get('text', '')
                
                if not text_to_summarize:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'error': 'Missing required field: text'
                        })
                    }
                
                # Validate input length to prevent abuse
                max_input_length = int(os.environ.get('MAX_TEXT_LENGTH', '1000'))
                if len(text_to_summarize) > max_input_length:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({
                            'error': f'Text exceeds maximum length of {max_input_length} characters'
                        })
                    }
                
                # Call summarization function
                result = summarize_text(text_to_summarize)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'data': result
                    })
                }
                
            except Exception as e:
                logger.error(f"Error in summarize endpoint: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Failed to summarize text',
                        'details': str(e)
                    })
                }
        
        # 404 for other endpoints
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Endpoint not found'
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
