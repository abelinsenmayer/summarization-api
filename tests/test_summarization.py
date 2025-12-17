import json
import pytest
import sys
import os
import importlib.util
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the lambda directory to Python path so bedrock_service can be imported by summarization.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lambda"))

# Import handler from lambda module using importlib to avoid reserved keyword issue
spec = importlib.util.spec_from_file_location("summarization", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lambda", "summarization.py"))
summarization_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarization_module)
handler = summarization_module.handler


class TestSummarizationHandler:
    """Test suite for the summarization Lambda handler."""

    def test_health_check_endpoint(self):
        """Test the /health endpoint returns correct response."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'GET',
                    'path': '/health'
                }
            }
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        
        body = json.loads(response['body'])
        assert body['status'] == 'healthy'
        assert body['message'] == 'API is running'

    def test_summarize_endpoint_success(self):
        """Test the /summarize endpoint with valid input."""
        with patch.object(summarization_module, 'summarize_text') as mock_summarize:
            mock_summarize.return_value = {
                'summary': 'This is a summarized version.',
                'original_length': 100,
                'summary_length': 30
            }
            
            event = {
                'requestContext': {
                    'http': {
                        'method': 'POST',
                        'path': '/summarize'
                    }
                },
                'body': json.dumps({
                    'text': 'This is a long text that needs to be summarized...'
                })
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 200
            assert response['headers']['Content-Type'] == 'application/json'
            assert response['headers']['Access-Control-Allow-Origin'] == '*'
            
            body = json.loads(response['body'])
            assert body['success'] is True
            assert 'data' in body
            assert body['data']['summary'] == 'This is a summarized version.'
            mock_summarize.assert_called_once_with('This is a long text that needs to be summarized...')
    
    def test_summarize_endpoint_missing_text(self):
        """Test the /summarize endpoint with missing text field."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/summarize'
                }
            },
            'body': json.dumps({})
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 400
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        
        body = json.loads(response['body'])
        assert body['error'] == 'Missing required field: text'
    
    def test_summarize_endpoint_empty_text(self):
        """Test the /summarize endpoint with empty text."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/summarize'
                }
            },
            'body': json.dumps({
                'text': ''
            })
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Missing required field: text'
    
    @patch.dict(os.environ, {'MAX_TEXT_LENGTH': '10'})
    def test_summarize_endpoint_text_exceeds_max_length(self):
        """Test the /summarize endpoint with text exceeding max length."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/summarize'
                }
            },
            'body': json.dumps({
                'text': 'This text is definitely longer than 10 characters.'
            })
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 400
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        
        body = json.loads(response['body'])
        assert body['error'] == 'Text exceeds maximum length of 10 characters'
    
    @patch.dict(os.environ, {'MAX_TEXT_LENGTH': '500'})
    def test_summarize_endpoint_text_within_max_length(self):
        """Test the /summarize endpoint with text within max length."""
        with patch.object(summarization_module, 'summarize_text') as mock_summarize:
            mock_summarize.return_value = {
                'summary': 'This is a summary.',
                'original_length': 50,
                'summary_length': 20
            }
            
            event = {
                'requestContext': {
                    'http': {
                        'method': 'POST',
                        'path': '/summarize'
                    }
                },
                'body': json.dumps({
                    'text': 'This text is within the limit.'
                })
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['success'] is True
            mock_summarize.assert_called_once_with('This text is within the limit.')
    
    def test_summarize_endpoint_default_max_length(self):
        """Test the /summarize endpoint with default max text length (1000)."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/summarize'
                }
            },
            'body': json.dumps({
                'text': 'x' * 1001
            })
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Text exceeds maximum length of 1000 characters'
    
    def test_summarize_endpoint_bedrock_error(self):
        """Test the /summarize endpoint when Bedrock fails."""
        with patch.object(summarization_module, 'summarize_text') as mock_summarize:
            mock_summarize.side_effect = Exception("Bedrock service unavailable")
            
            event = {
                'requestContext': {
                    'http': {
                        'method': 'POST',
                        'path': '/summarize'
                    }
                },
                'body': json.dumps({
                    'text': 'Some text to summarize'
                })
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 500
            body = json.loads(response['body'])
            assert body['error'] == 'Failed to summarize text'
            assert 'Bedrock service unavailable' in body['details']

    def test_unknown_endpoint_returns_404(self):
        """Test that unknown endpoints return 404."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'GET',
                    'path': '/unknown'
                }
            }
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 404
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        
        body = json.loads(response['body'])
        assert body['error'] == 'Endpoint not found'


    def test_different_methods_on_health_endpoint(self):
        """Test that non-GET methods on /health return 404."""
        for method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            event = {
                'requestContext': {
                    'http': {
                        'method': method,
                        'path': '/health'
                    }
                }
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 404
            body = json.loads(response['body'])
            assert body['error'] == 'Endpoint not found'

    def test_different_methods_on_summarize_endpoint(self):
        """Test that non-POST methods on /summarize return 404."""
        for method in ['GET', 'PUT', 'DELETE', 'PATCH']:
            event = {
                'requestContext': {
                    'http': {
                        'method': method,
                        'path': '/summarize'
                    }
                }
            }
            
            response = handler(event, None)
            
            assert response['statusCode'] == 404
            body = json.loads(response['body'])
            assert body['error'] == 'Endpoint not found'

