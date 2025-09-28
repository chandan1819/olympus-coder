"""
Test suite for Ollama API integration client.

Tests the OllamaClient functionality including request formatting,
response parsing, error handling, and retry logic.
"""

import json
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import ConnectionError, Timeout, HTTPError

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from integration.ollama_client import (
    OllamaClient, OllamaError, ModelNotFoundError, APIConnectionError,
    ModelResponse, GenerateRequest, create_client_from_config
)


class TestOllamaClient:
    """Test cases for OllamaClient class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = OllamaClient(
            base_url="http://localhost:11434",
            model_name="olympus-coder-v1-test",
            timeout=30,
            max_retries=2
        )
    
    @patch('requests.Session.request')
    def test_generate_success(self, mock_request):
        """Test successful generate request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "olympus-coder-v1-test",
            "response": "def hello_world():\n    print('Hello, World!')",
            "done": True,
            "created_at": "2024-01-01T00:00:00Z",
            "total_duration": 1000000,
            "eval_count": 50
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Test generate call
        result = self.client.generate(
            prompt="Write a hello world function in Python",
            options={"temperature": 0.1}
        )
        
        # Verify request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"  # method
        assert "/api/generate" in call_args[0][1]  # URL
        
        # Verify request data
        request_data = call_args[1]["json"]
        assert request_data["model"] == "olympus-coder-v1-test"
        assert request_data["prompt"] == "Write a hello world function in Python"
        assert request_data["options"]["temperature"] == 0.1
        
        # Verify response parsing
        assert isinstance(result, ModelResponse)
        assert result.content == "def hello_world():\n    print('Hello, World!')"
        assert result.model == "olympus-coder-v1-test"
        assert result.done is True
        assert result.eval_count == 50
    
    @patch('requests.Session.request')
    def test_generate_with_system_prompt(self, mock_request):
        """Test generate request with system prompt"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "olympus-coder-v1-test",
            "response": "Generated response",
            "done": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        self.client.generate(
            prompt="Test prompt",
            system_prompt="You are a helpful coding assistant"
        )
        
        # Verify system prompt was included
        call_args = mock_request.call_args
        request_data = call_args[1]["json"]
        assert request_data["system"] == "You are a helpful coding assistant"
    
    @patch('requests.Session.request')
    def test_chat_success(self, mock_request):
        """Test successful chat request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "olympus-coder-v1-test",
            "response": "I can help you with that coding task.",
            "done": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        messages = [
            {"role": "user", "content": "Help me write a function"}
        ]
        
        result = self.client.chat(messages=messages)
        
        # Verify request
        call_args = mock_request.call_args
        assert "/api/chat" in call_args[0][1]
        request_data = call_args[1]["json"]
        assert request_data["messages"] == messages
        
        # Verify response
        assert result.content == "I can help you with that coding task."
    
    @patch('requests.Session.request')
    def test_list_models_success(self, mock_request):
        """Test successful list models request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "olympus-coder-v1", "size": 1000000},
                {"name": "llama3:8b", "size": 2000000}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        models = self.client.list_models()
        
        assert len(models) == 2
        assert models[0]["name"] == "olympus-coder-v1"
        assert models[1]["name"] == "llama3:8b"
    
    @patch('requests.Session.request')
    def test_model_exists_true(self, mock_request):
        """Test model_exists returns True when model exists"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "olympus-coder-v1-test", "size": 1000000}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        exists = self.client.model_exists()
        assert exists is True
    
    @patch('requests.Session.request')
    def test_model_exists_false(self, mock_request):
        """Test model_exists returns False when model doesn't exist"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "other-model", "size": 1000000}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        exists = self.client.model_exists()
        assert exists is False
    
    @patch('requests.Session.request')
    def test_show_model_info_success(self, mock_request):
        """Test successful show model info request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "modelfile": "FROM codellama:13b\nSYSTEM ...",
            "parameters": {"temperature": 0.1},
            "template": "{{ .System }}{{ .Prompt }}"
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        info = self.client.show_model_info()
        
        assert "modelfile" in info
        assert "parameters" in info
        assert info["parameters"]["temperature"] == 0.1
    
    @patch('requests.Session.request')
    def test_model_not_found_error(self, mock_request):
        """Test ModelNotFoundError is raised for 404 responses"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        with pytest.raises(ModelNotFoundError):
            self.client.generate("test prompt")
    
    @patch('requests.Session.request')
    def test_connection_error(self, mock_request):
        """Test APIConnectionError is raised for connection errors"""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(APIConnectionError):
            self.client.generate("test prompt")
    
    @patch('requests.Session.request')
    def test_timeout_error(self, mock_request):
        """Test OllamaError is raised for timeout"""
        mock_request.side_effect = Timeout("Request timeout")
        
        with pytest.raises(OllamaError):
            self.client.generate("test prompt")
    
    @patch('requests.Session.request')
    def test_health_check_success(self, mock_request):
        """Test successful health check"""
        # Mock responses for list_models and show_model_info
        list_response = Mock()
        list_response.status_code = 200
        list_response.json.return_value = {
            "models": [{"name": "olympus-coder-v1-test"}]
        }
        list_response.raise_for_status.return_value = None
        
        show_response = Mock()
        show_response.status_code = 200
        show_response.json.return_value = {"modelfile": "test"}
        show_response.raise_for_status.return_value = None
        
        mock_request.side_effect = [list_response, show_response]
        
        health = self.client.health_check()
        
        assert health["server_accessible"] is True
        assert health["model_available"] is True
        assert health["model_info"] is not None
        assert health["response_time"] is not None
        assert health["error"] is None
    
    @patch('requests.Session.request')
    def test_health_check_failure(self, mock_request):
        """Test health check with server failure"""
        mock_request.side_effect = ConnectionError("Connection failed")
        
        health = self.client.health_check()
        
        assert health["server_accessible"] is False
        assert health["model_available"] is False
        assert health["error"] is not None
    
    def test_serialize_request(self):
        """Test request serialization"""
        request = GenerateRequest(
            model="test-model",
            prompt="test prompt",
            system="test system",
            options={"temperature": 0.5}
        )
        
        serialized = self.client._serialize_request(request)
        
        assert serialized["model"] == "test-model"
        assert serialized["prompt"] == "test prompt"
        assert serialized["system"] == "test system"
        assert serialized["options"]["temperature"] == 0.5
        assert serialized["stream"] is False
    
    def test_parse_response_success(self):
        """Test successful response parsing"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "test content",
            "model": "test-model",
            "done": True,
            "created_at": "2024-01-01T00:00:00Z",
            "eval_count": 25
        }
        
        result = self.client._parse_response(mock_response)
        
        assert isinstance(result, ModelResponse)
        assert result.content == "test content"
        assert result.model == "test-model"
        assert result.done is True
        assert result.eval_count == 25
    
    def test_parse_response_invalid_json(self):
        """Test response parsing with invalid JSON"""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with pytest.raises(OllamaError):
            self.client._parse_response(mock_response)


class TestCreateClientFromConfig:
    """Test cases for create_client_from_config function"""
    
    def test_create_client_default_config(self):
        """Test creating client with default configuration"""
        client = create_client_from_config()
        
        assert client.base_url == "http://localhost:11434"
        assert client.model_name == "olympus-coder-v1"
        assert client.timeout == 60
    
    @patch('builtins.open')
    def test_create_client_from_file(self, mock_open):
        """Test creating client from configuration file"""
        config_data = {
            "ollama_client": {
                "base_url": "http://custom:11434",
                "model_name": "custom-model",
                "timeout": 120
            }
        }
        
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(config_data)
        
        with patch('json.load', return_value=config_data):
            client = create_client_from_config("test_config.json")
        
        assert client.base_url == "http://custom:11434"
        assert client.model_name == "custom-model"
        assert client.timeout == 120
    
    @patch('builtins.open')
    def test_create_client_file_not_found(self, mock_open):
        """Test creating client when config file not found"""
        mock_open.side_effect = FileNotFoundError()
        
        # Should fall back to default config
        client = create_client_from_config("nonexistent.json")
        
        assert client.base_url == "http://localhost:11434"
        assert client.model_name == "olympus-coder-v1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])