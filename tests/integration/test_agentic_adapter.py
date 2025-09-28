"""
Test suite for Agentic Framework Integration Adapter.

Tests the AgenticAdapter functionality including context management,
tool execution, and framework integration patterns.
"""

import json
import pytest
import time
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from integration.agentic_adapter import (
    AgenticAdapter, AgentContext, AgentResponse, AgentState,
    create_default_adapter, create_context_from_task
)
from integration.ollama_client import OllamaClient, ModelResponse
from integration.utils import ToolRequest


class TestAgentContext:
    """Test cases for AgentContext class"""
    
    def test_create_context(self):
        """Test creating agent context"""
        context = AgentContext(
            task_id="test-task-1",
            task_description="Test task description"
        )
        
        assert context.task_id == "test-task-1"
        assert context.task_description == "Test task description"
        assert len(context.files) == 0
        assert len(context.conversation_history) == 0
        assert context.error_context is None
    
    def test_add_message(self):
        """Test adding message to conversation history"""
        context = AgentContext("test-task", "Test task")
        
        context.add_message("user", "Hello")
        context.add_message("assistant", "Hi there!")
        
        assert len(context.conversation_history) == 2
        assert context.conversation_history[0]["role"] == "user"
        assert context.conversation_history[0]["content"] == "Hello"
        assert context.conversation_history[1]["role"] == "assistant"
        assert context.conversation_history[1]["content"] == "Hi there!"
    
    def test_add_file(self):
        """Test adding file to context"""
        context = AgentContext("test-task", "Test task")
        
        context.add_file("test.py", "print('hello')", "python")
        
        assert len(context.files) == 1
        assert context.files[0]["path"] == "test.py"
        assert context.files[0]["content"] == "print('hello')"
        assert context.files[0]["language"] == "python"
    
    def test_set_error(self):
        """Test setting error context"""
        context = AgentContext("test-task", "Test task")
        
        context.set_error("Test error", "Traceback info")
        
        assert "Test error" in context.error_context
        assert "Traceback info" in context.error_context
    
    def test_clear_error(self):
        """Test clearing error context"""
        context = AgentContext("test-task", "Test task")
        context.set_error("Test error")
        
        context.clear_error()
        
        assert context.error_context is None
    
    def test_to_dict_from_dict(self):
        """Test serialization and deserialization"""
        context = AgentContext("test-task", "Test task")
        context.add_message("user", "Hello")
        context.add_file("test.py", "print('hello')")
        
        # Convert to dict and back
        data = context.to_dict()
        restored_context = AgentContext.from_dict(data)
        
        assert restored_context.task_id == context.task_id
        assert restored_context.task_description == context.task_description
        assert len(restored_context.files) == len(context.files)
        assert len(restored_context.conversation_history) == len(context.conversation_history)


class TestAgentResponse:
    """Test cases for AgentResponse class"""
    
    def test_create_response(self):
        """Test creating agent response"""
        response = AgentResponse(
            content="Generated content",
            confidence=0.95,
            execution_time=1.5
        )
        
        assert response.content == "Generated content"
        assert response.confidence == 0.95
        assert response.execution_time == 1.5
        assert response.state == AgentState.COMPLETE
    
    def test_has_tool_request(self):
        """Test tool request detection"""
        # Response without tool request
        response1 = AgentResponse(content="Just text")
        assert response1.has_tool_request() is False
        
        # Response with tool request
        tool_request = ToolRequest("read_file", {"path": "test.py"})
        response2 = AgentResponse(content="Text", tool_request=tool_request)
        assert response2.has_tool_request() is True
    
    def test_is_successful(self):
        """Test success detection"""
        # Successful response
        response1 = AgentResponse(content="Success")
        assert response1.is_successful() is True
        
        # Error response
        response2 = AgentResponse(content="", error="Something went wrong")
        assert response2.is_successful() is False
        
        # Error state
        response3 = AgentResponse(content="", state=AgentState.ERROR)
        assert response3.is_successful() is False


class TestAgenticAdapter:
    """Test cases for AgenticAdapter class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_client = Mock(spec=OllamaClient)
        self.adapter = AgenticAdapter(self.mock_client)
        
        # Mock model response
        self.mock_model_response = ModelResponse(
            content="Generated response content",
            model="test-model",
            created_at="2024-01-01T00:00:00Z",
            done=True,
            eval_count=50
        )
    
    def test_execute_task_success(self):
        """Test successful task execution"""
        # Setup
        self.mock_client.generate.return_value = self.mock_model_response
        
        context = AgentContext("test-task", "Write a hello world function")
        prompt = "Please write a hello world function in Python"
        
        # Execute
        response = self.adapter.execute_task(context, prompt)
        
        # Verify
        assert response.is_successful()
        assert response.content == "Generated response content"
        assert response.execution_time is not None
        assert response.token_count == 50
        
        # Verify client was called
        self.mock_client.generate.assert_called_once()
        
        # Verify context was updated
        assert len(context.conversation_history) == 2
        assert context.conversation_history[0]["role"] == "user"
        assert context.conversation_history[1]["role"] == "assistant"
    
    def test_execute_task_with_tool_request(self):
        """Test task execution that returns tool request"""
        # Setup model response with tool request
        tool_response_content = '''
        I need to read a file first.
        
        ```json
        {
            "tool_name": "read_file",
            "parameters": {
                "file_path": "test.py"
            }
        }
        ```
        '''
        
        self.mock_model_response.content = tool_response_content
        self.mock_client.generate.return_value = self.mock_model_response
        
        context = AgentContext("test-task", "Analyze the test.py file")
        prompt = "What does the test.py file contain?"
        
        # Execute
        response = self.adapter.execute_task(context, prompt)
        
        # Verify
        assert response.is_successful()
        assert response.has_tool_request()
        assert response.tool_request.tool_name == "read_file"
        assert response.tool_request.parameters["file_path"] == "test.py"
    
    def test_execute_task_error(self):
        """Test task execution with error"""
        # Setup
        self.mock_client.generate.side_effect = Exception("Model error")
        
        context = AgentContext("test-task", "Test task")
        prompt = "Test prompt"
        
        # Execute
        response = self.adapter.execute_task(context, prompt)
        
        # Verify
        assert not response.is_successful()
        assert response.state == AgentState.ERROR
        assert response.error == "Model error"
        assert context.error_context is not None
    
    def test_register_tool_handler(self):
        """Test registering tool handler"""
        def mock_handler(params, context):
            return {"result": "success"}
        
        self.adapter.register_tool_handler("test_tool", mock_handler)
        
        assert "test_tool" in self.adapter.tool_handlers
        assert self.adapter.tool_handlers["test_tool"] == mock_handler
    
    def test_execute_tool_request_success(self):
        """Test successful tool execution"""
        # Register handler
        def mock_handler(params, context):
            return {"file_content": "print('hello')"}
        
        self.adapter.register_tool_handler("read_file", mock_handler)
        
        # Create tool request
        tool_request = ToolRequest("read_file", {"file_path": "test.py"})
        context = AgentContext("test-task", "Test task")
        
        # Execute
        result = self.adapter.execute_tool_request(tool_request, context)
        
        # Verify
        assert result["success"] is True
        assert result["error"] is None
        assert result["result"]["file_content"] == "print('hello')"
    
    def test_execute_tool_request_no_handler(self):
        """Test tool execution with no registered handler"""
        tool_request = ToolRequest("unknown_tool", {})
        context = AgentContext("test-task", "Test task")
        
        result = self.adapter.execute_tool_request(tool_request, context)
        
        assert result["success"] is False
        assert "No handler registered" in result["error"]
    
    def test_execute_tool_request_handler_error(self):
        """Test tool execution with handler error"""
        def failing_handler(params, context):
            raise Exception("Handler failed")
        
        self.adapter.register_tool_handler("failing_tool", failing_handler)
        
        tool_request = ToolRequest("failing_tool", {})
        context = AgentContext("test-task", "Test task")
        
        result = self.adapter.execute_tool_request(tool_request, context)
        
        assert result["success"] is False
        assert "Handler failed" in result["error"]
    
    def test_context_management(self):
        """Test context storage and retrieval"""
        context = AgentContext("test-task", "Test task")
        
        # Store context (happens automatically in execute_task)
        self.adapter.active_contexts[context.task_id] = context
        
        # Retrieve context
        retrieved = self.adapter.get_context("test-task")
        assert retrieved is not None
        assert retrieved.task_id == "test-task"
        
        # Non-existent context
        missing = self.adapter.get_context("missing-task")
        assert missing is None
    
    def test_save_load_context(self):
        """Test context persistence"""
        context = AgentContext("test-task", "Test task")
        context.add_message("user", "Hello")
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Test save
            self.adapter.save_context(context, "test_context.json")
            mock_open.assert_called_with("test_context.json", 'w')
            mock_file.write.assert_called()
    
    def test_execution_hooks(self):
        """Test pre and post execution hooks"""
        pre_hook_called = False
        post_hook_called = False
        
        def pre_hook(context, prompt):
            nonlocal pre_hook_called
            pre_hook_called = True
        
        def post_hook(context, response):
            nonlocal post_hook_called
            post_hook_called = True
        
        self.adapter.add_pre_execution_hook(pre_hook)
        self.adapter.add_post_execution_hook(post_hook)
        
        # Setup mock
        self.mock_client.generate.return_value = self.mock_model_response
        
        # Execute task
        context = AgentContext("test-task", "Test task")
        self.adapter.execute_task(context, "Test prompt")
        
        # Verify hooks were called
        assert pre_hook_called
        assert post_hook_called
    
    def test_get_execution_stats(self):
        """Test execution statistics"""
        # Initially empty
        stats = self.adapter.get_execution_stats()
        assert stats["total_executions"] == 0
        
        # Add some execution history
        self.adapter.execution_history = [
            {"success": True, "execution_time": 1.0},
            {"success": False, "execution_time": 2.0},
            {"success": True, "execution_time": 1.5}
        ]
        
        stats = self.adapter.get_execution_stats()
        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 2
        assert stats["success_rate"] == 2/3
        assert stats["average_execution_time"] == 1.5


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_create_default_adapter(self):
        """Test creating default adapter"""
        with patch('integration.agentic_adapter.OllamaClient') as mock_client_class:
            adapter = create_default_adapter()
            
            # Verify client was created with defaults
            mock_client_class.assert_called_once_with(
                base_url="http://localhost:11434",
                model_name="olympus-coder-v1"
            )
            
            assert isinstance(adapter, AgenticAdapter)
    
    def test_create_context_from_task(self):
        """Test creating context from task info"""
        context = create_context_from_task(
            task_id="task-123",
            task_description="Write unit tests",
            project_root="/path/to/project"
        )
        
        assert context.task_id == "task-123"
        assert context.task_description == "Write unit tests"
        assert context.project_root == "/path/to/project"
        assert len(context.files) == 0
        assert len(context.conversation_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])