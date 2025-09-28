"""
Integration Test Runner

Runs comprehensive tests for the Olympus-Coder-v1 integration layer
including API client, agentic adapter, and utility functions.
"""

import sys
import os
import pytest
import subprocess
from pathlib import Path

# Add integration module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def run_unit_tests():
    """Run unit tests for integration components"""
    print("Running integration unit tests...")
    
    test_files = [
        "test_ollama_client.py",
        "test_agentic_adapter.py"
    ]
    
    test_dir = Path(__file__).parent
    
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            print(f"\nRunning {test_file}...")
            result = pytest.main([str(test_path), "-v", "--tb=short"])
            if result != 0:
                print(f"Tests failed in {test_file}")
                return False
        else:
            print(f"Warning: {test_file} not found")
    
    return True


def test_ollama_connection():
    """Test connection to Ollama server"""
    print("\nTesting Ollama server connection...")
    
    try:
        from integration.ollama_client import OllamaClient
        
        client = OllamaClient(timeout=10)
        health = client.health_check()
        
        if health["server_accessible"]:
            print("✓ Ollama server is accessible")
            
            if health["model_available"]:
                print("✓ Olympus-Coder-v1 model is available")
                return True
            else:
                print("✗ Olympus-Coder-v1 model not found")
                print("  Make sure the model is built and available")
                return False
        else:
            print("✗ Cannot connect to Ollama server")
            print(f"  Error: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


def test_basic_integration():
    """Test basic integration functionality"""
    print("\nTesting basic integration...")
    
    try:
        from integration import (
            OllamaClient, AgenticAdapter, create_context_from_task,
            format_model_options
        )
        
        # Test client creation
        client = OllamaClient(model_name="olympus-coder-v1", timeout=30)
        print("✓ Client created successfully")
        
        # Test adapter creation
        adapter = AgenticAdapter(
            client,
            default_options=format_model_options(temperature=0.1)
        )
        print("✓ Adapter created successfully")
        
        # Test context creation
        context = create_context_from_task(
            "test-integration",
            "Test basic integration functionality"
        )
        print("✓ Context created successfully")
        
        # Test simple task execution (if server is available)
        if test_ollama_connection():
            try:
                response = adapter.execute_task(
                    context,
                    "Say hello in Python code",
                    options={"num_predict": 100}
                )
                
                if response.is_successful():
                    print("✓ Basic task execution successful")
                    print(f"  Response length: {len(response.content)} chars")
                    return True
                else:
                    print(f"✗ Task execution failed: {response.error}")
                    return False
                    
            except Exception as e:
                print(f"✗ Task execution error: {e}")
                return False
        else:
            print("⚠ Skipping task execution (server not available)")
            return True
            
    except Exception as e:
        print(f"✗ Basic integration test failed: {e}")
        return False


def test_tool_integration():
    """Test tool handler integration"""
    print("\nTesting tool integration...")
    
    try:
        from integration import AgenticAdapter, OllamaClient, create_context_from_task
        
        client = OllamaClient(model_name="olympus-coder-v1")
        adapter = AgenticAdapter(client)
        
        # Register test tool handler
        def test_handler(params, context):
            return {"message": f"Tool executed with params: {params}"}
        
        adapter.register_tool_handler("test_tool", test_handler)
        print("✓ Tool handler registered")
        
        # Test tool execution
        from integration.utils import ToolRequest
        
        tool_request = ToolRequest("test_tool", {"param1": "value1"})
        context = create_context_from_task("tool-test", "Test tool execution")
        
        result = adapter.execute_tool_request(tool_request, context)
        
        if result["success"]:
            print("✓ Tool execution successful")
            print(f"  Result: {result['result']}")
            return True
        else:
            print(f"✗ Tool execution failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"✗ Tool integration test failed: {e}")
        return False


def test_logging_integration():
    """Test logging and debugging integration"""
    print("\nTesting logging integration...")
    
    try:
        from integration.logging_tools import create_agent_logger, DebugSession
        from integration import AgentContext, AgentResponse
        
        # Create logger
        logger = create_agent_logger("test_logger")
        print("✓ Logger created successfully")
        
        # Test logging functionality
        context = AgentContext("log-test", "Test logging")
        response = AgentResponse("Test response", execution_time=0.5)
        
        logger.log_task_start(context, "Test prompt")
        logger.log_task_complete(context, response, 0.5)
        print("✓ Logging functions work")
        
        # Test debug session
        debug_session = DebugSession(logger)
        debug_session.set_breakpoint("test_component", "test_event")
        print("✓ Debug session created")
        
        # Test performance stats
        stats = logger.get_performance_stats()
        print(f"✓ Performance stats: {len(stats)} metrics")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging integration test failed: {e}")
        return False


def test_utility_functions():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        from integration.utils import (
            format_context, parse_tool_response, validate_tool_request,
            format_model_options, extract_code_blocks, sanitize_file_path
        )
        
        # Test context formatting
        context_str = format_context(
            files=[{"path": "test.py", "content": "print('hello')"}],
            current_task="Test task"
        )
        assert "Test task" in context_str
        print("✓ Context formatting works")
        
        # Test tool response parsing
        response_with_tool = '''
        Here's the solution:
        
        ```json
        {
            "tool_name": "write_file",
            "parameters": {"path": "test.py", "content": "print('hello')"}
        }
        ```
        '''
        
        tool_request, cleaned_text = parse_tool_response(response_with_tool)
        assert tool_request is not None
        assert tool_request.tool_name == "write_file"
        print("✓ Tool response parsing works")
        
        # Test model options formatting
        options = format_model_options(temperature=0.5, top_p=0.9)
        assert options["temperature"] == 0.5
        print("✓ Model options formatting works")
        
        # Test code block extraction
        text_with_code = '''
        Here's some Python code:
        
        ```python
        def hello():
            print("Hello, World!")
        ```
        '''
        
        code_blocks = extract_code_blocks(text_with_code)
        assert len(code_blocks) == 1
        assert code_blocks[0]["language"] == "python"
        print("✓ Code block extraction works")
        
        # Test file path sanitization
        safe_path = sanitize_file_path("../../../etc/passwd")
        assert not safe_path.startswith("../")
        print("✓ File path sanitization works")
        
        return True
        
    except Exception as e:
        print(f"✗ Utility functions test failed: {e}")
        return False


def run_performance_tests():
    """Run performance tests"""
    print("\nRunning performance tests...")
    
    try:
        import time
        from integration import OllamaClient, AgenticAdapter, create_context_from_task
        
        if not test_ollama_connection():
            print("⚠ Skipping performance tests (server not available)")
            return True
        
        client = OllamaClient(model_name="olympus-coder-v1")
        adapter = AgenticAdapter(client)
        
        # Test response times
        context = create_context_from_task("perf-test", "Performance test")
        
        start_time = time.time()
        response = adapter.execute_task(
            context,
            "Write a simple hello world function",
            options={"num_predict": 50}
        )
        execution_time = time.time() - start_time
        
        if response.is_successful():
            print(f"✓ Task completed in {execution_time:.2f} seconds")
            
            if execution_time < 10.0:  # Reasonable threshold
                print("✓ Performance within acceptable range")
                return True
            else:
                print("⚠ Performance slower than expected")
                return True
        else:
            print(f"✗ Performance test failed: {response.error}")
            return False
            
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("Olympus-Coder-v1 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Unit Tests", run_unit_tests),
        ("Ollama Connection", test_ollama_connection),
        ("Basic Integration", test_basic_integration),
        ("Tool Integration", test_tool_integration),
        ("Logging Integration", test_logging_integration),
        ("Utility Functions", test_utility_functions),
        ("Performance Tests", run_performance_tests)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
                
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)