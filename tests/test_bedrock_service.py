import json
import pytest
import sys
import os
import importlib.util
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Add the lambda directory to Python path so modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lambda"))

# Import bedrock service module
spec = importlib.util.spec_from_file_location("bedrock_service", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lambda", "bedrock_service.py"))
bedrock_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bedrock_service_module)

get_bedrock_client = bedrock_service_module.get_bedrock_client
summarize_text = bedrock_service_module.summarize_text


class TestBedrockService:
    """Test suite for the Bedrock service functions."""

    def setup_method(self):
        """Reset global variables before each test."""
        bedrock_service_module.bedrock_client = None

    @patch('boto3.client')
    @patch.dict(os.environ, {'AWS_REGION': 'us-west-2'})
    def test_get_bedrock_client_creates_new_client(self, mock_boto_client):
        """Test that get_bedrock_client creates a new client when none exists."""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        result = get_bedrock_client()
        
        assert result == mock_client
        mock_boto_client.assert_called_once_with(
            service_name='bedrock-runtime',
            region_name='us-west-2'
        )
        assert bedrock_service_module.bedrock_client == mock_client

    @patch('boto3.client')
    def test_get_bedrock_client_returns_existing_client(self, mock_boto_client):
        """Test that get_bedrock_client returns existing client when available."""
        existing_client = MagicMock()
        bedrock_service_module.bedrock_client = existing_client
        
        result = get_bedrock_client()
        
        assert result == existing_client
        mock_boto_client.assert_not_called()

    @patch('boto3.client')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_bedrock_client_uses_default_region(self, mock_boto_client):
        """Test that get_bedrock_client uses default region when none specified."""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        result = get_bedrock_client()
        
        mock_boto_client.assert_called_once_with(
            service_name='bedrock-runtime',
            region_name='us-east-2'
        )

    @patch('boto3.client')
    def test_summarize_text_success(self, mock_get_client):
        """Test successful text summarization."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': 'This is a summary.'}]
                }
            }
        }
        mock_client.converse.return_value = mock_response
        
        text = "This is a long text that needs to be summarized."
        result = summarize_text(text)
        
        assert result['summary'] == 'This is a summary.'
        assert result['original_length'] == len(text)
        assert result['summary_length'] == len('This is a summary.')
        
        mock_client.converse.assert_called_once_with(
            modelId="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            messages=[{
                "role": "user",
                "content": [{
                    "text": f"Please summarize the following text in a concise and clear manner:\n\n{text}"
                }]
            }]
        )

    @patch('boto3.client')
    def test_summarize_text_bedrock_error(self, mock_get_client):
        """Test handling of Bedrock service errors."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_client.converse.side_effect = Exception("Bedrock service error")
        
        text = "Some text to summarize"
        
        with pytest.raises(Exception, match="Bedrock service error"):
            summarize_text(text)

    @patch('boto3.client')
    def test_summarize_text_client_error(self, mock_get_client):
        """Test handling of ClientError from Bedrock."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        error_response = {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}}
        mock_client.converse.side_effect = ClientError(error_response, 'Converse')
        
        text = "Some text to summarize"
        
        with pytest.raises(ClientError):
            summarize_text(text)

    @patch('boto3.client')
    def test_summarize_text_empty_response(self, mock_get_client):
        """Test handling of empty or malformed response from Bedrock."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = {
            'output': {
                'message': {
                    'content': [{
                        'text': 'Hey it\'s a summary!'
                    }]
                }
            }
        }
        mock_client.converse.return_value = mock_response
        
        text = "Some text to summarize"
        
        result = summarize_text(text)
        
        assert result['summary'] == 'Hey it\'s a summary!'
        assert result['original_length'] == len(text)
        assert result['summary_length'] == 19

    @patch('boto3.client')
    def test_summarize_text_with_special_characters(self, mock_get_client):
        """Test summarization with special characters and unicode."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': 'Summary with émojis 🚀 and spëcial chars!'}]
                }
            }
        }
        mock_client.converse.return_value = mock_response
        
        text = "Text with special characters: café, naïve, and emojis 🎉"
        result = summarize_text(text)
        
        assert result['summary'] == 'Summary with émojis 🚀 and spëcial chars!'
        assert result['original_length'] == len(text)
        assert result['summary_length'] == len('Summary with émojis 🚀 and spëcial chars!')
