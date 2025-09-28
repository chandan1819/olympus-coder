"""
Integration Utilities

Utility functions for request formatting, response parsing, logging setup,
and common integration tasks.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolRequest:
    """Represents a parsed tool request from model response"""
    tool_name: str
    parameters: Dict[str, Any]
    confidence: float = 1.0
    raw_response: str = ""


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for integration components.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        format_string: Custom log format string
        
    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[]
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_string))
    
    # Add file handler if specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_string))
        handlers.append(file_handler)
    
    # Get logger for integration module
    logger = logging.getLogger("olympus_coder_integration")
    logger.handlers = handlers
    logger.setLevel(getattr(logging, level.upper()))
    
    return logger


def format_context(
    files: Optional[List[Dict[str, str]]] = None,
    project_structure: Optional[Dict[str, Any]] = None,
    current_task: Optional[str] = None,
    error_context: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Format context information for model input.
    
    Args:
        files: List of file objects with 'path' and 'content'
        project_structure: Project directory structure
        current_task: Current task description
        error_context: Error traceback or context
        conversation_history: Previous conversation messages
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    # Add current task
    if current_task:
        context_parts.append(f"## Current Task\n{current_task}\n")
    
    # Add project structure
    if project_structure:
        context_parts.append("## Project Structure")
        context_parts.append(_format_project_structure(project_structure))
        context_parts.append("")
    
    # Add file contents
    if files:
        context_parts.append("## Relevant Files")
        for file_info in files:
            path = file_info.get("path", "unknown")
            content = file_info.get("content", "")
            language = _detect_language(path)
            
            context_parts.append(f"### {path}")
            context_parts.append(f"```{language}")
            context_parts.append(content)
            context_parts.append("```")
            context_parts.append("")
    
    # Add error context
    if error_context:
        context_parts.append("## Error Context")
        context_parts.append("```")
        context_parts.append(error_context)
        context_parts.append("```")
        context_parts.append("")
    
    # Add conversation history (last few messages)
    if conversation_history:
        context_parts.append("## Recent Context")
        # Include last 3 messages to maintain context
        recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            context_parts.append(f"**{role.title()}:** {content[:200]}...")
        context_parts.append("")
    
    return "\n".join(context_parts)


def parse_tool_response(response_text: str) -> Tuple[Optional[ToolRequest], str]:
    """
    Parse model response to extract tool requests and remaining content.
    
    Args:
        response_text: Raw response text from model
        
    Returns:
        Tuple of (ToolRequest object or None, remaining text content)
    """
    # Look for JSON tool request patterns
    json_patterns = [
        r'```json\s*(\{[^`]+\})\s*```',  # JSON in code blocks
        r'(\{[^{}]*"tool_name"[^{}]*\})',  # Direct JSON objects
        r'Tool:\s*(\{[^{}]+\})',  # Tool: prefix
    ]
    
    tool_request = None
    cleaned_text = response_text
    
    for pattern in json_patterns:
        matches = re.finditer(pattern, response_text, re.DOTALL | re.IGNORECASE)
        for match in matches:
            try:
                json_str = match.group(1)
                tool_data = json.loads(json_str)
                
                # Validate tool request structure
                if "tool_name" in tool_data and "parameters" in tool_data:
                    tool_request = ToolRequest(
                        tool_name=tool_data["tool_name"],
                        parameters=tool_data["parameters"],
                        confidence=tool_data.get("confidence", 1.0),
                        raw_response=json_str
                    )
                    
                    # Remove the tool request from text
                    cleaned_text = response_text.replace(match.group(0), "").strip()
                    break
                    
            except (json.JSONDecodeError, KeyError):
                continue
        
        if tool_request:
            break
    
    return tool_request, cleaned_text


def validate_tool_request(tool_request: ToolRequest) -> Tuple[bool, List[str]]:
    """
    Validate a tool request for completeness and correctness.
    
    Args:
        tool_request: ToolRequest object to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check tool name
    if not tool_request.tool_name:
        errors.append("Tool name is required")
    elif not isinstance(tool_request.tool_name, str):
        errors.append("Tool name must be a string")
    
    # Check parameters
    if not isinstance(tool_request.parameters, dict):
        errors.append("Parameters must be a dictionary")
    
    # Check confidence
    if not (0.0 <= tool_request.confidence <= 1.0):
        errors.append("Confidence must be between 0.0 and 1.0")
    
    # Tool-specific validation
    tool_validations = {
        "read_file": ["file_path"],
        "write_file": ["file_path", "content"],
        "execute_command": ["command"],
        "list_directory": ["path"],
        "search_files": ["query"],
    }
    
    if tool_request.tool_name in tool_validations:
        required_params = tool_validations[tool_request.tool_name]
        for param in required_params:
            if param not in tool_request.parameters:
                errors.append(f"Missing required parameter: {param}")
    
    return len(errors) == 0, errors


def format_model_options(
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    repeat_penalty: Optional[float] = None,
    num_ctx: Optional[int] = None,
    num_predict: Optional[int] = None,
    stop_sequences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Format model parameters for Ollama API requests.
    
    Args:
        temperature: Randomness control (0.0-1.0)
        top_p: Nucleus sampling threshold
        top_k: Top-k sampling limit
        repeat_penalty: Repetition penalty
        num_ctx: Context window size
        num_predict: Max tokens to generate
        stop_sequences: List of stop sequences
        
    Returns:
        Dictionary of model options
    """
    options = {}
    
    if temperature is not None:
        options["temperature"] = max(0.0, min(1.0, temperature))
    if top_p is not None:
        options["top_p"] = max(0.0, min(1.0, top_p))
    if top_k is not None:
        options["top_k"] = max(1, int(top_k))
    if repeat_penalty is not None:
        options["repeat_penalty"] = max(1.0, repeat_penalty)
    if num_ctx is not None:
        options["num_ctx"] = max(512, int(num_ctx))
    if num_predict is not None:
        options["num_predict"] = max(1, int(num_predict))
    if stop_sequences:
        options["stop"] = stop_sequences
    
    return options


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from model response text.
    
    Args:
        text: Response text containing code blocks
        
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    code_blocks = []
    
    # Pattern for fenced code blocks
    pattern = r'```(\w+)?\s*\n(.*?)\n```'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        language = match.group(1) or "text"
        code = match.group(2).strip()
        
        code_blocks.append({
            "language": language,
            "code": code
        })
    
    return code_blocks


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitize file path to prevent directory traversal attacks.
    
    Args:
        file_path: Input file path
        
    Returns:
        Sanitized file path
    """
    # Remove any path traversal attempts
    path = Path(file_path)
    
    # Resolve to absolute path and check if it's within allowed directory
    try:
        resolved = path.resolve()
        # Convert back to relative path if possible
        return str(resolved.relative_to(Path.cwd()))
    except ValueError:
        # If path is outside current directory, return just the filename
        return path.name


def _format_project_structure(structure: Dict[str, Any], indent: int = 0) -> str:
    """Format project structure dictionary as tree view."""
    lines = []
    prefix = "  " * indent
    
    for key, value in structure.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}/")
            lines.append(_format_project_structure(value, indent + 1))
        else:
            lines.append(f"{prefix}{key}")
    
    return "\n".join(lines)


def _detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".sh": "bash",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".txt": "text"
    }
    
    path = Path(file_path)
    return extension_map.get(path.suffix.lower(), "text")


def calculate_response_metrics(
    response_time: float,
    token_count: Optional[int] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate performance metrics for model responses.
    
    Args:
        response_time: Total response time in seconds
        token_count: Total tokens in response
        prompt_tokens: Tokens in prompt
        completion_tokens: Tokens in completion
        
    Returns:
        Dictionary of calculated metrics
    """
    metrics = {
        "response_time": response_time,
        "tokens_per_second": None,
        "total_tokens": token_count,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens
    }
    
    if token_count and response_time > 0:
        metrics["tokens_per_second"] = token_count / response_time
    
    return metrics