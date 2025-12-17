import json
import logging
import boto3
import os
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables
bedrock_client = None

def get_bedrock_client():
    """
    Initialize and return Bedrock client
    """
    global bedrock_client
    
    if bedrock_client:
        return bedrock_client
    
    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    return bedrock_client


def summarize_text(text_to_summarize):
    """
    Use Amazon Bedrock to summarize text
    """
    try:
        client = get_bedrock_client()
        
        messages = [{
            "role": "user", 
            "content": [{
                "text": f"Please summarize the following text in a concise and clear manner:\n\n{text_to_summarize}"
            }]
        }]
        
        # Call Converse API to summarize the text
        response = client.converse(
            modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            messages=messages,
        )

        logger.info(f"Response: {response}")
        
        # Extract and return the summary
        summary = response['output']['message']['content'][0]['text']
        
        return {
            'summary': summary,
            'original_length': len(text_to_summarize),
            'summary_length': len(summary)
        }

    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise
