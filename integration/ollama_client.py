"""
Ollama API Integration Client

Provides functions to interact with the deployed Olympus-Coder-v1 model
through the Ollama API with proper error handling and retry logic.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OllamaError(Exception):
    """Base exception for Ollama API errors"""
    pass


class ModelNotFoundError(OllamaError):
    """Raised when the specified model is not found"""
    pass


class APIConnectionError(OllamaError):
    """Raised when unable to connect to Ollama API"""
    pass


@dataclass
class ModelResponse:
    """Represents a response from the Ollama model"""
    content: str
    model: str
    created_at: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


@dataclass
class GenerateRequest:
    """Request parameters for model generation"""
    model: str
    prompt: str
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[List[int]] = None
    stream: bool = False
    raw: bool = False
    format: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class OllamaClient:
    """
    Client for interacting with Ollama API to communicate with Olympus-Coder-v1 model.
    
    Provides request formatting, response parsing, error handling, and retry logic.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "olympus-coder-v1",
        timeout: int = 60,
        max_retries: int = 3,
        backoff_factor: float = 0.3
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server base URL
            model_name: Name of the deployed Olympus-Coder-v1 model
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retry delays
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST"],
            backoff_factor=backoff_factor
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> ModelResponse:
        """
        Generate response from Olympus-Coder-v1 model.
        
        Args:
            prompt: User prompt/request
            system_prompt: Optional system prompt override
            options: Model parameters (temperature, top_p, etc.)
            stream: Whether to stream the response
            
        Returns:
            ModelResponse object with generated content and metadata
            
        Raises:
            ModelNotFoundError: If model is not found
            APIConnectionError: If unable to connect to API
            OllamaError: For other API errors
        """
        request_data = GenerateRequest(
            model=self.model_name,
            prompt=prompt,
            system=system_prompt,
            stream=stream,
            options=options or {}
        )
        
        try:
            self.logger.debug(f"Sending generate request to {self.model_name}")
            response = self._make_request(
                "POST",
                "/api/generate",
                json=self._serialize_request(request_data)
            )
            
            return self._parse_response(response)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise APIConnectionError(f"Failed to connect to Ollama API: {e}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> ModelResponse:
        """
        Chat with Olympus-Coder-v1 model using conversation format.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            options: Model parameters
            stream: Whether to stream the response
            
        Returns:
            ModelResponse object with generated content and metadata
        """
        request_data = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "options": options or {}
        }
        
        try:
            self.logger.debug(f"Sending chat request to {self.model_name}")
            response = self._make_request("POST", "/api/chat", json=request_data)
            return self._parse_response(response)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Chat request failed: {e}")
            raise APIConnectionError(f"Failed to connect to Ollama API: {e}")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models on the Ollama server.
        
        Returns:
            List of model information dictionaries
        """
        try:
            response = self._make_request("GET", "/api/tags")
            return response.json().get("models", [])
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to list models: {e}")
            raise APIConnectionError(f"Failed to connect to Ollama API: {e}")
    
    def model_exists(self, model_name: Optional[str] = None) -> bool:
        """
        Check if a model exists on the Ollama server.
        
        Args:
            model_name: Model name to check (defaults to self.model_name)
            
        Returns:
            True if model exists, False otherwise
        """
        check_model = model_name or self.model_name
        try:
            models = self.list_models()
            return any(model.get("name") == check_model for model in models)
        except APIConnectionError:
            return False
    
    def show_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model_name: Model name (defaults to self.model_name)
            
        Returns:
            Model information dictionary
        """
        check_model = model_name or self.model_name
        request_data = {"name": check_model}
        
        try:
            response = self._make_request("POST", "/api/show", json=request_data)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if "not found" in str(e).lower():
                raise ModelNotFoundError(f"Model '{check_model}' not found")
            raise APIConnectionError(f"Failed to get model info: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Ollama server and model.
        
        Returns:
            Health status dictionary with server and model status
        """
        health_status = {
            "server_accessible": False,
            "model_available": False,
            "model_info": None,
            "response_time": None,
            "error": None
        }
        
        start_time = time.time()
        
        try:
            # Check server accessibility
            response = self._make_request("GET", "/api/tags", timeout=10)
            health_status["server_accessible"] = True
            
            # Check model availability
            if self.model_exists():
                health_status["model_available"] = True
                health_status["model_info"] = self.show_model_info()
            
            health_status["response_time"] = time.time() - start_time
            
        except Exception as e:
            health_status["error"] = str(e)
            health_status["response_time"] = time.time() - start_time
        
        return health_status
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request to Ollama API with error handling."""
        url = f"{self.base_url}{endpoint}"
        request_timeout = timeout or self.timeout
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=request_timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(f"Model '{self.model_name}' not found")
            raise OllamaError(f"HTTP error {e.response.status_code}: {e}")
        
        except requests.exceptions.Timeout:
            raise OllamaError(f"Request timeout after {request_timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"Connection error: {e}")
    
    def _serialize_request(self, request: GenerateRequest) -> Dict[str, Any]:
        """Serialize GenerateRequest to dictionary."""
        data = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": request.stream
        }
        
        if request.system:
            data["system"] = request.system
        if request.template:
            data["template"] = request.template
        if request.context:
            data["context"] = request.context
        if request.raw:
            data["raw"] = request.raw
        if request.format:
            data["format"] = request.format
        if request.options:
            data["options"] = request.options
            
        return data
    
    def _parse_response(self, response: requests.Response) -> ModelResponse:
        """Parse Ollama API response into ModelResponse object."""
        try:
            data = response.json()
            
            return ModelResponse(
                content=data.get("response", ""),
                model=data.get("model", self.model_name),
                created_at=data.get("created_at", ""),
                done=data.get("done", True),
                total_duration=data.get("total_duration"),
                load_duration=data.get("load_duration"),
                prompt_eval_count=data.get("prompt_eval_count"),
                prompt_eval_duration=data.get("prompt_eval_duration"),
                eval_count=data.get("eval_count"),
                eval_duration=data.get("eval_duration")
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            raise OllamaError(f"Failed to parse response: {e}")


def create_client_from_config(config_path: str = None) -> OllamaClient:
    """
    Create OllamaClient instance from configuration file.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Configured OllamaClient instance
    """
    # Default configuration
    config = {
        "base_url": "http://localhost:11434",
        "model_name": "olympus-coder-v1",
        "timeout": 60,
        "max_retries": 3,
        "backoff_factor": 0.3
    }
    
    # Load from config file if provided
    if config_path:
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get("ollama_client", {}))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Could not load config from {config_path}: {e}")
    
    return OllamaClient(**config)