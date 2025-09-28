"""
Example Usage of Olympus-Coder-v1 Integration Layer

Demonstrates how to use the integration components for agentic framework
integration, including basic usage patterns and advanced features.
"""

import os
import time
from pathlib import Path

from ollama_client import OllamaClient, create_client_from_config
from agentic_adapter import (
    AgenticAdapter, AgentContext, create_default_adapter, 
    create_context_from_task
)
from logging_tools import create_agent_logger, DebugSession
from utils import setup_logging, format_model_options


def basic_usage_example():
    """
    Basic usage example showing simple task execution.
    """
    print("=== Basic Usage Example ===")
    
    # Create client and adapter
    client = OllamaClient(model_name="olympus-coder-v1")
    adapter = AgenticAdapter(client)
    
    # Create context
    context = create_context_from_task(
        task_id="example-1",
        task_description="Write a Python function to calculate fibonacci numbers"
    )
    
    # Execute task
    prompt = "Please write a Python function that calculates the nth Fibonacci number using recursion."
    
    try:
        response = adapter.execute_task(context, prompt)
        
        if response.is_successful():
            print("Task completed successfully!")
            print(f"Response: {response.content}")
            
            if response.has_tool_request():
                print(f"Tool request: {response.tool_request.tool_name}")
        else:
            print(f"Task failed: {response.error}")
            
    except Exception as e:
        print(f"Error: {e}")


def advanced_usage_example():
    """
    Advanced usage example with tool handlers, context management, and logging.
    """
    print("\n=== Advanced Usage Example ===")
    
    # Set up logging
    logger = create_agent_logger("example_agent", log_dir="logs")
    
    # Create adapter with custom options
    client = OllamaClient(
        model_name="olympus-coder-v1",
        timeout=120
    )
    
    adapter = AgenticAdapter(
        client,
        logger=logger.logger,
        default_options=format_model_options(
            temperature=0.1,
            top_p=0.9,
            num_predict=1024
        )
    )
    
    # Register tool handlers
    def read_file_handler(params, context):
        """Handler for reading files"""
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("file_path parameter required")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return {"content": content, "size": len(content)}
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
    
    def write_file_handler(params, context):
        """Handler for writing files"""
        file_path = params.get("file_path")
        content = params.get("content")
        
        if not file_path or content is None:
            raise ValueError("file_path and content parameters required")
        
        # Create directory if needed
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return {"bytes_written": len(content), "path": file_path}
    
    def list_files_handler(params, context):
        """Handler for listing directory contents"""
        directory = params.get("directory", ".")
        pattern = params.get("pattern", "*")
        
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        files = list(path.glob(pattern))
        return {
            "files": [str(f) for f in files if f.is_file()],
            "directories": [str(f) for f in files if f.is_dir()],
            "count": len(files)
        }
    
    # Register handlers
    adapter.register_tool_handler("read_file", read_file_handler)
    adapter.register_tool_handler("write_file", write_file_handler)
    adapter.register_tool_handler("list_files", list_files_handler)
    
    # Add execution hooks
    def pre_execution_hook(context, prompt):
        logger.log_task_start(context, prompt)
        print(f"Starting task: {context.task_id}")
    
    def post_execution_hook(context, response):
        logger.log_task_complete(context, response, response.execution_time or 0)
        print(f"Task completed: {context.task_id} - Success: {response.is_successful()}")
    
    adapter.add_pre_execution_hook(pre_execution_hook)
    adapter.add_post_execution_hook(post_execution_hook)
    
    # Create context with project information
    context = AgentContext(
        task_id="advanced-example",
        task_description="Analyze project structure and create a summary file",
        project_root="."
    )
    
    # Add some project files to context
    context.add_file("README.md", "# Olympus-Coder-v1\nA specialized LLM for coding tasks.")
    context.add_file("main.py", "def main():\n    print('Hello, World!')")
    
    # Execute multi-step task
    prompts = [
        "First, list all Python files in the current directory.",
        "Now read the content of the main.py file if it exists.",
        "Create a project summary file called 'project_summary.md' with information about the project structure."
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Step {i} ---")
        print(f"Prompt: {prompt}")
        
        try:
            response = adapter.execute_task(context, prompt)
            
            if response.is_successful():
                print(f"Response: {response.content[:200]}...")
                
                # Handle tool requests
                if response.has_tool_request():
                    print(f"Executing tool: {response.tool_request.tool_name}")
                    
                    tool_start = time.time()
                    tool_result = adapter.execute_tool_request(response.tool_request, context)
                    tool_time = time.time() - tool_start
                    
                    logger.log_tool_execution(
                        response.tool_request.tool_name,
                        response.tool_request.parameters,
                        tool_result,
                        tool_time,
                        context.task_id
                    )
                    
                    if tool_result["success"]:
                        print(f"Tool executed successfully: {tool_result['result']}")
                        
                        # Add tool result to context for next iteration
                        context.add_message("system", f"Tool result: {tool_result['result']}")
                    else:
                        print(f"Tool execution failed: {tool_result['error']}")
                        context.set_error(f"Tool execution failed: {tool_result['error']}")
            else:
                print(f"Task failed: {response.error}")
                break
                
        except Exception as e:
            print(f"Error in step {i}: {e}")
            logger.log_error(e, context, "task_execution")
            break
    
    # Print execution statistics
    print("\n=== Execution Statistics ===")
    stats = adapter.get_execution_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Export logs
    logger.export_logs("example_execution_logs.json")
    print("Logs exported to example_execution_logs.json")


def interactive_debugging_example():
    """
    Example of interactive debugging capabilities.
    """
    print("\n=== Interactive Debugging Example ===")
    
    # Set up logger and debug session
    logger = create_agent_logger("debug_agent")
    debug_session = DebugSession(logger)
    
    # Create adapter
    adapter = create_default_adapter()
    
    # Set some breakpoints
    debug_session.set_breakpoint("task_execution", "task_start")
    debug_session.set_breakpoint("tool_execution", "tool_execute")
    
    print("Debug session configured. In a real scenario, you would:")
    print("1. Set breakpoints on specific events")
    print("2. Watch variable values")
    print("3. Step through execution")
    print("4. Analyze logs and performance")
    
    # Simulate some debugging
    context = create_context_from_task("debug-task", "Debug example task")
    debug_session.print_context(context)
    
    # Show recent logs
    print("\n--- Recent Logs ---")
    recent_logs = logger.get_recent_logs(5)
    for log in recent_logs:
        print(f"{log.level}: {log.message}")


def configuration_example():
    """
    Example of different configuration options.
    """
    print("\n=== Configuration Example ===")
    
    # Create client from configuration file
    config_path = "config/integration_config.json"
    
    # Create sample config if it doesn't exist
    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        sample_config = {
            "ollama_client": {
                "base_url": "http://localhost:11434",
                "model_name": "olympus-coder-v1",
                "timeout": 60,
                "max_retries": 3
            },
            "adapter": {
                "max_context_length": 4000,
                "default_options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            }
        }
        
        with open(config_path, 'w') as f:
            import json
            json.dump(sample_config, f, indent=2)
        
        print(f"Created sample config at {config_path}")
    
    try:
        # Load client from config
        client = create_client_from_config(config_path)
        print(f"Client created with model: {client.model_name}")
        
        # Test health check
        health = client.health_check()
        print(f"Health check: {health}")
        
    except Exception as e:
        print(f"Configuration example failed: {e}")
        print("Make sure Ollama is running and the model is available")


def main():
    """
    Run all examples.
    """
    print("Olympus-Coder-v1 Integration Layer Examples")
    print("=" * 50)
    
    # Set up basic logging
    setup_logging("INFO")
    
    try:
        # Run examples
        basic_usage_example()
        advanced_usage_example()
        interactive_debugging_example()
        configuration_example()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nExample execution failed: {e}")


if __name__ == "__main__":
    main()