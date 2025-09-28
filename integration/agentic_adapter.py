"""
Agentic Framework Integration Adapter

Provides adapter functions for common agentic framework patterns,
context passing, state management, and logging utilities.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .ollama_client import OllamaClient, ModelResponse
from .utils import format_context, parse_tool_response, ToolRequest, validate_tool_request


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class AgentContext:
    """
    Context object for agent interactions containing task information,
    project state, and conversation history.
    """
    task_id: str
    task_description: str
    project_root: Optional[str] = None
    files: List[Dict[str, str]] = field(default_factory=list)
    project_structure: Optional[Dict[str, Any]] = None
    error_context: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        self.updated_at = time.time()
    
    def add_file(self, path: str, content: str, language: Optional[str] = None):
        """Add file to context"""
        file_info = {
            "path": path,
            "content": content,
            "language": language or self._detect_language(path),
            "added_at": time.time()
        }
        self.files.append(file_info)
        self.updated_at = time.time()
    
    def set_error(self, error_message: str, traceback: Optional[str] = None):
        """Set error context"""
        self.error_context = error_message
        if traceback:
            self.error_context += f"\n\nTraceback:\n{traceback}"
        self.updated_at = time.time()
    
    def clear_error(self):
        """Clear error context"""
        self.error_context = None
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "project_root": self.project_root,
            "files": self.files,
            "project_structure": self.project_structure,
            "error_context": self.error_context,
            "conversation_history": self.conversation_history,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        """Create context from dictionary"""
        return cls(**data)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c"
        }
        return extension_map.get(Path(file_path).suffix, "text")


@dataclass
class AgentResponse:
    """
    Response object from agent containing generated content,
    tool requests, and execution metadata.
    """
    content: str
    tool_request: Optional[ToolRequest] = None
    confidence: float = 1.0
    state: AgentState = AgentState.COMPLETE
    execution_time: Optional[float] = None
    token_count: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_tool_request(self) -> bool:
        """Check if response contains a tool request"""
        return self.tool_request is not None
    
    def is_successful(self) -> bool:
        """Check if response indicates successful execution"""
        return self.error is None and self.state != AgentState.ERROR


class AgenticAdapter:
    """
    Adapter for integrating Olympus-Coder-v1 with agentic frameworks.
    
    Provides high-level interface for agent interactions, context management,
    and tool execution coordination.
    """
    
    def __init__(
        self,
        ollama_client: OllamaClient,
        logger: Optional[logging.Logger] = None,
        max_context_length: int = 4000,
        default_options: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agentic adapter.
        
        Args:
            ollama_client: Configured OllamaClient instance
            logger: Optional logger instance
            max_context_length: Maximum context length in tokens
            default_options: Default model options
        """
        self.client = ollama_client
        self.logger = logger or logging.getLogger(__name__)
        self.max_context_length = max_context_length
        self.default_options = default_options or {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 2048
        }
        
        # State management
        self.active_contexts: Dict[str, AgentContext] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # Tool execution hooks
        self.tool_handlers: Dict[str, Callable] = {}
        self.pre_execution_hooks: List[Callable] = []
        self.post_execution_hooks: List[Callable] = []
    
    def execute_task(
        self,
        context: AgentContext,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute a task using the agent with provided context.
        
        Args:
            context: Agent context with task and project information
            prompt: User prompt/request
            system_prompt: Optional system prompt override
            options: Model generation options
            
        Returns:
            AgentResponse with generated content and tool requests
        """
        start_time = time.time()
        
        try:
            # Store context
            self.active_contexts[context.task_id] = context
            
            # Run pre-execution hooks
            for hook in self.pre_execution_hooks:
                hook(context, prompt)
            
            # Format context for model
            formatted_context = format_context(
                files=context.files,
                project_structure=context.project_structure,
                current_task=context.task_description,
                error_context=context.error_context,
                conversation_history=context.conversation_history
            )
            
            # Combine context with prompt
            full_prompt = f"{formatted_context}\n\n## Request\n{prompt}"
            
            # Truncate if too long
            if len(full_prompt) > self.max_context_length:
                full_prompt = self._truncate_context(full_prompt)
            
            # Generate response
            model_options = {**self.default_options, **(options or {})}
            model_response = self.client.generate(
                prompt=full_prompt,
                system_prompt=system_prompt,
                options=model_options
            )
            
            # Parse response for tool requests
            tool_request, cleaned_content = parse_tool_response(model_response.content)
            
            # Create agent response
            execution_time = time.time() - start_time
            agent_response = AgentResponse(
                content=cleaned_content,
                tool_request=tool_request,
                execution_time=execution_time,
                token_count=model_response.eval_count,
                metadata={
                    "model_response": model_response,
                    "context_length": len(full_prompt)
                }
            )
            
            # Add to conversation history
            context.add_message("user", prompt)
            context.add_message("assistant", model_response.content)
            
            # Run post-execution hooks
            for hook in self.post_execution_hooks:
                hook(context, agent_response)
            
            # Log execution
            self._log_execution(context, prompt, agent_response)
            
            return agent_response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_response = AgentResponse(
                content="",
                state=AgentState.ERROR,
                execution_time=execution_time,
                error=str(e)
            )
            
            self.logger.error(f"Task execution failed: {e}")
            context.set_error(str(e))
            
            return error_response
    
    def execute_tool_request(
        self,
        tool_request: ToolRequest,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Execute a tool request using registered handlers.
        
        Args:
            tool_request: Tool request to execute
            context: Agent context
            
        Returns:
            Tool execution result
        """
        # Validate tool request
        is_valid, errors = validate_tool_request(tool_request)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid tool request: {', '.join(errors)}",
                "result": None
            }
        
        # Check if handler exists
        if tool_request.tool_name not in self.tool_handlers:
            return {
                "success": False,
                "error": f"No handler registered for tool: {tool_request.tool_name}",
                "result": None
            }
        
        try:
            # Execute tool
            handler = self.tool_handlers[tool_request.tool_name]
            result = handler(tool_request.parameters, context)
            
            self.logger.info(f"Tool executed successfully: {tool_request.tool_name}")
            
            return {
                "success": True,
                "error": None,
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Tool execution failed: {tool_request.tool_name} - {e}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    def register_tool_handler(self, tool_name: str, handler: Callable):
        """
        Register a tool handler function.
        
        Args:
            tool_name: Name of the tool
            handler: Function to handle tool execution
        """
        self.tool_handlers[tool_name] = handler
        self.logger.info(f"Registered tool handler: {tool_name}")
    
    def add_pre_execution_hook(self, hook: Callable):
        """Add pre-execution hook"""
        self.pre_execution_hooks.append(hook)
    
    def add_post_execution_hook(self, hook: Callable):
        """Add post-execution hook"""
        self.post_execution_hooks.append(hook)
    
    def get_context(self, task_id: str) -> Optional[AgentContext]:
        """Get context by task ID"""
        return self.active_contexts.get(task_id)
    
    def save_context(self, context: AgentContext, file_path: str):
        """Save context to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
            self.logger.info(f"Context saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")
    
    def load_context(self, file_path: str) -> Optional[AgentContext]:
        """Load context from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            context = AgentContext.from_dict(data)
            self.active_contexts[context.task_id] = context
            self.logger.info(f"Context loaded from {file_path}")
            return context
        except Exception as e:
            self.logger.error(f"Failed to load context: {e}")
            return None
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        total_executions = len(self.execution_history)
        successful_executions = sum(
            1 for exec_info in self.execution_history 
            if exec_info.get("success", False)
        )
        
        total_time = sum(
            exec_info.get("execution_time", 0) 
            for exec_info in self.execution_history
        )
        
        avg_time = total_time / total_executions if total_executions > 0 else 0
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_time,
            "total_execution_time": total_time
        }
    
    def _truncate_context(self, context: str) -> str:
        """Truncate context to fit within max length"""
        if len(context) <= self.max_context_length:
            return context
        
        # Keep the end of the context (most recent information)
        truncated = context[-self.max_context_length:]
        
        # Find a good break point (start of a line)
        newline_pos = truncated.find('\n')
        if newline_pos > 0:
            truncated = truncated[newline_pos + 1:]
        
        return f"[Context truncated...]\n{truncated}"
    
    def _log_execution(
        self,
        context: AgentContext,
        prompt: str,
        response: AgentResponse
    ):
        """Log execution details"""
        execution_info = {
            "task_id": context.task_id,
            "prompt_length": len(prompt),
            "response_length": len(response.content),
            "execution_time": response.execution_time,
            "success": response.is_successful(),
            "has_tool_request": response.has_tool_request(),
            "timestamp": time.time()
        }
        
        self.execution_history.append(execution_info)
        
        # Keep only last 1000 executions
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]


def create_default_adapter(
    base_url: str = "http://localhost:11434",
    model_name: str = "olympus-coder-v1"
) -> AgenticAdapter:
    """
    Create AgenticAdapter with default configuration.
    
    Args:
        base_url: Ollama server URL
        model_name: Model name
        
    Returns:
        Configured AgenticAdapter instance
    """
    client = OllamaClient(base_url=base_url, model_name=model_name)
    return AgenticAdapter(client)


def create_context_from_task(
    task_id: str,
    task_description: str,
    project_root: Optional[str] = None
) -> AgentContext:
    """
    Create AgentContext from basic task information.
    
    Args:
        task_id: Unique task identifier
        task_description: Description of the task
        project_root: Optional project root directory
        
    Returns:
        Initialized AgentContext
    """
    return AgentContext(
        task_id=task_id,
        task_description=task_description,
        project_root=project_root
    )