# Test Scenarios and Benchmarks

This directory contains comprehensive test scenarios for evaluating Olympus-Coder-v1 model performance across different coding tasks.

## Test Categories

### 1. Code Generation Tests (`code_generation_tests.py`)
- **Purpose**: Evaluate the model's ability to generate high-quality Python and JavaScript code
- **Coverage**: Function generation, class creation, edge cases, complex requirements
- **Requirements Tested**: 1.1, 1.2, 1.6
- **Test Runner**: `test_code_generation.py`

### 2. Debugging and Analysis Tests (`debugging_tests.py`)
- **Purpose**: Evaluate error identification, code fixing, and improvement suggestions
- **Coverage**: Syntax errors, runtime errors, logic errors, code review scenarios
- **Requirements Tested**: 2.1, 2.2, 2.3
- **Test Runner**: `test_debugging.py`

### 3. Tool Usage Decision Tests (`tool_usage_tests.py`)
- **Purpose**: Evaluate appropriate tool selection and JSON formatting accuracy
- **Coverage**: File operations, code execution, analysis tools, ambiguous scenarios
- **Requirements Tested**: 3.1, 3.2, 3.5, 3.6
- **Test Runner**: `test_tool_usage.py`

### 4. Context Awareness Tests (`context_awareness_tests.py`)
- **Purpose**: Evaluate project understanding and consistency maintenance
- **Coverage**: File referencing, naming conventions, architecture patterns, imports
- **Requirements Tested**: 4.1, 4.2, 4.5
- **Test Runner**: `test_context_awareness.py`

## Usage

### Running Individual Test Categories

```bash
# Run code generation tests
python test_code_generation.py

# Run debugging tests
python test_debugging.py

# Run tool usage tests
python test_tool_usage.py

# Run context awareness tests
python test_context_awareness.py
```

### Running Comprehensive Test Suite

```bash
# Run all test categories with comprehensive reporting
python run_all_tests.py
```

This will generate:
- Detailed JSON results file
- Human-readable text report
- Requirements compliance analysis
- Performance metrics

### Test Structure

Each test category follows a consistent structure:

1. **Test Case Definition**: Dataclass defining test parameters and expectations
2. **Test Collection**: Organized test cases by difficulty and type
3. **Test Runner**: Validation logic and result compilation
4. **Mock Responses**: Framework testing with realistic mock responses

### Validation Criteria

Tests validate multiple aspects:
- **Syntax Correctness**: Code compiles/parses without errors
- **Style Compliance**: Follows language-specific best practices
- **Feature Completeness**: Contains expected functionality elements
- **Format Accuracy**: Proper markdown formatting and JSON structure
- **Context Consistency**: Maintains project patterns and conventions

### Expected Performance Targets

Based on requirements:
- **Code Generation**: 75% success rate for autonomous completion
- **Tool Usage**: >95% accuracy in JSON formatting
- **Overall Performance**: 75% autonomous completion rate
- **Context Accuracy**: Accurate file references without hallucination

### Extending Tests

To add new test cases:

1. Add test case to appropriate test collection class
2. Update validation criteria as needed
3. Add mock response generation for framework testing
4. Run tests to verify new cases work correctly

### Integration with Model

In production, replace mock response generation with actual Ollama API calls:

```python
# Replace mock responses with actual model calls
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "olympus-coder-v1",
        "prompt": test_prompt,
        "stream": False
    }
)
```

## Files Overview

- `code_generation_tests.py` - Test case definitions for code generation
- `test_code_generation.py` - Test runner for code generation scenarios
- `debugging_tests.py` - Test case definitions for debugging scenarios
- `test_debugging.py` - Test runner for debugging scenarios
- `tool_usage_tests.py` - Test case definitions for tool usage decisions
- `test_tool_usage.py` - Test runner for tool usage scenarios
- `context_awareness_tests.py` - Test case definitions for context awareness
- `test_context_awareness.py` - Test runner for context awareness scenarios
- `run_all_tests.py` - Comprehensive test suite runner and reporter