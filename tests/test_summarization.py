import json
import pytest
import sys
import os
import importlib.util
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    def test_summarize_endpoint(self):
        """Test the /summarize endpoint returns correct response."""
        event = {
            'requestContext': {
                'http': {
                    'method': 'POST',
                    'path': '/summarize'
                }
            }
        }
        
        response = handler(event, None)
        
        assert response['statusCode'] == 200
        assert response['headers']['Content-Type'] == 'application/json'
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        
        body = json.loads(response['body'])
        assert body['message'] == 'Hello World - Summarization endpoint is ready!'

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

