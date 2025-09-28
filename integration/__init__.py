"""
Olympus-Coder-v1 Integration Layer

This module provides integration utilities for the Olympus-Coder-v1 model,
including Ollama API client, agentic framework adapters, and utilities.
"""

from .ollama_client import (
    OllamaClient, OllamaError, ModelNotFoundError, APIConnectionError,
    ModelResponse, GenerateRequest, create_client_from_config
)
from .agentic_adapter import (
    AgenticAdapter, AgentContext, AgentResponse, AgentState,
    create_default_adapter, create_context_from_task
)
from .logging_tools import (
    AgentLogger, DebugSession, LogEntry, create_agent_logger
)
from .utils import (
    setup_logging, format_context, parse_tool_response, ToolRequest,
    validate_tool_request, format_model_options, extract_code_blocks,
    sanitize_file_path, calculate_response_metrics
)

__version__ = "1.0.0"
__all__ = [
    # Ollama Client
    "OllamaClient",
    "OllamaError", 
    "ModelNotFoundError",
    "APIConnectionError",
    "ModelResponse",
    "GenerateRequest",
    "create_client_from_config",
    
    # Agentic Adapter
    "AgenticAdapter",
    "AgentContext",
    "AgentResponse",
    "AgentState",
    "create_default_adapter",
    "create_context_from_task",
    
    # Logging Tools
    "AgentLogger",
    "DebugSession", 
    "LogEntry",
    "create_agent_logger",
    
    # Utilities
    "setup_logging",
    "format_context",
    "parse_tool_response",
    "ToolRequest",
    "validate_tool_request",
    "format_model_options",
    "extract_code_blocks",
    "sanitize_file_path",
    "calculate_response_metrics"
]