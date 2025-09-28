"""
Test suite for response validation utilities.
"""

import json
from response_validator import ResponseValidator, ToolRequestValidator
from code_validator import validate_code_block, PythonValidator, JavaScriptValidator


def test_tool_request_validator():
    """Test tool request JSON validation."""
    validator = ToolRequestValidator()
    
    # Test valid tool request
    valid_request = '{"tool_name": "read_file", "parameters": {"file_path": "test.py"}}'
    result = validator.validate_tool_request(valid_request)
    assert result["is_valid"] == True
    assert result["confidence_score"] > 0.8
    print("✓ Valid tool request validation passed")
    
    # Test invalid JSON
    invalid_json = '{"tool_name": "read_file", "parameters": {'
    result = validator.validate_tool_request(invalid_json)
    assert result["is_valid"] == False
    assert "Invalid JSON" in result["errors"][0]
    print("✓ Invalid JSON detection passed")
    
    # Test missing required fields
    missing_params = '{"tool_name": "read_file"}'
    result = validator.validate_tool_request(missing_params)
    assert result["is_valid"] == False
    print("✓ Missing parameters detection passed")
    
    # Test empty tool name
    empty_name = '{"tool_name": "", "parameters": {}}'
    result = validator.validate_tool_request(empty_name)
    assert result["is_valid"] == False
    print("✓ Empty tool name detection passed")


def test_response_validator():
    """Test overall response format validation."""
    validator = ResponseValidator()
    
    # Test code response
    code_response = """Here's the Python function:

```python
def hello_world():
    print("Hello, World!")
    return True
```

This function prints a greeting."""
    
    result = validator.validate_response_format(code_response)
    assert result["has_code_blocks"] == True
    assert result["response_type"] == "code"
    assert len(result["code_blocks"]) == 1
    assert result["code_blocks"][0]["language"] == "python"
    print("✓ Code response validation passed")
    
    # Test tool request response
    tool_response = 'I need to read the file: {"tool_name": "read_file", "parameters": {"file_path": "test.py"}}'
    result = validator.validate_response_format(tool_response)
    assert result["has_tool_requests"] == True
    assert result["response_type"] == "tool_request"
    print("✓ Tool request response validation passed")
    
    # Test empty response
    empty_response = ""
    result = validator.validate_response_format(empty_response)
    assert result["is_valid"] == False
    assert "Empty response" in result["errors"]
    print("✓ Empty response detection passed")


def test_code_validators():
    """Test code syntax and style validation."""
    
    # Test Python validation
    python_code = """
def calculate_sum(a, b):
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
    """
    
    result = validate_code_block(python_code, "python")
    assert result["is_valid"] == True
    assert result["syntax_result"]["has_functions"] == True
    assert result["syntax_result"]["has_classes"] == True
    print("✓ Python code validation passed")
    
    # Test JavaScript validation
    js_code = """
function calculateSum(a, b) {
    return a + b;
}

class Calculator {
    constructor() {
        this.result = 0;
    }
}
"""
    
    result = validate_code_block(js_code, "javascript")
    assert result["is_valid"] == True
    assert result["syntax_result"]["has_functions"] == True
    assert result["syntax_result"]["has_classes"] == True
    print("✓ JavaScript code validation passed")
    
    # Test invalid Python syntax
    invalid_python = """
def broken_function(
    print("Missing closing parenthesis")
"""
    
    result = validate_code_block(invalid_python, "python")
    assert result["is_valid"] == False
    assert len(result["errors"]) > 0
    print("✓ Invalid Python syntax detection passed")


def test_structured_response_accuracy():
    """Test structured response accuracy calculation."""
    validator = ResponseValidator()
    
    responses = [
        '{"tool_name": "read_file", "parameters": {"file_path": "test.py"}}',
        'Here is some code: ```python\nprint("hello")\n```',
        '{"tool_name": "write_file", "parameters": {"file_path": "output.txt", "content": "test"}}',
        'Invalid response without proper format',
        '{"tool_name": "execute", "parameters": {"command": "ls -la"}}'
    ]
    
    accuracy = validator.check_structured_response_accuracy(responses)
    print(f"✓ Structured response accuracy: {accuracy:.2%}")
    
    # Should be 80% (4 out of 5 valid responses)
    assert accuracy >= 0.75  # Allow some tolerance


if __name__ == "__main__":
    print("Running response validation tests...")
    
    test_tool_request_validator()
    test_response_validator()
    test_code_validators()
    test_structured_response_accuracy()
    
    print("\n✅ All response validation tests passed!")