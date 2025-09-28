# Debugging and Analysis Instructions

## Error Identification Methodology

### Traceback Analysis Process
1. **Locate the Error Source**: Identify the exact line number and file where the error occurred
2. **Understand the Error Type**: Classify the error (SyntaxError, TypeError, ValueError, etc.)
3. **Trace the Call Stack**: Follow the execution path that led to the error
4. **Identify Root Cause**: Determine the underlying issue causing the error
5. **Propose Solution**: Provide a specific fix that addresses the root cause

### Python Error Analysis

#### Syntax Errors
```python
# Error: SyntaxError: invalid syntax
def calculate_sum(a, b
    return a + b  # Missing closing parenthesis

# Fix:
def calculate_sum(a, b):
    return a + b
```

#### Type Errors
```python
# Error: TypeError: unsupported operand type(s) for +: 'int' and 'str'
def add_numbers(a, b):
    return a + b

result = add_numbers(5, "10")  # Mixing int and str

# Fix:
def add_numbers(a, b):
    # Convert inputs to ensure consistent types
    return int(a) + int(b)

# Or with proper validation:
def add_numbers(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a + b
```

#### Value Errors
```python
# Error: ValueError: invalid literal for int() with base 10: 'abc'
user_input = "abc"
number = int(user_input)  # Cannot convert 'abc' to integer

# Fix:
def safe_int_conversion(value):
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to integer")

# Or with default handling:
def safe_int_conversion(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default
```

### JavaScript Error Analysis

#### Reference Errors
```javascript
// Error: ReferenceError: undefinedVariable is not defined
function processData() {
    return undefinedVariable.length;  // Variable not declared
}

// Fix:
function processData(data) {
    if (!data) {
        throw new Error("Data parameter is required");
    }
    return data.length;
}
```

#### Type Errors
```javascript
// Error: TypeError: Cannot read property 'length' of null
function getLength(arr) {
    return arr.length;  // arr might be null/undefined
}

// Fix:
function getLength(arr) {
    if (!Array.isArray(arr)) {
        throw new TypeError("Expected an array");
    }
    return arr.length;
}

// Or with defensive programming:
function getLength(arr) {
    return arr?.length ?? 0;
}
```

## Code Analysis Framework

### Static Analysis Checklist
- **Syntax Validation**: Check for proper syntax and formatting
- **Type Consistency**: Verify variable types match expected usage
- **Null/Undefined Checks**: Ensure proper handling of null values
- **Boundary Conditions**: Validate input ranges and edge cases
- **Resource Management**: Check for proper cleanup of resources

### Performance Analysis
```python
# Inefficient code example
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

# Optimized version
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

### Security Analysis
```python
# Vulnerable code
def execute_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return database.execute(query)  # SQL injection risk

# Secure version
def execute_query(user_input):
    query = "SELECT * FROM users WHERE name = ?"
    return database.execute(query, (user_input,))  # Parameterized query
```

## Solution Formatting Requirements

### Error Explanation Format
```
**Error Type**: [Specific error class/type]
**Location**: [File:line_number]
**Root Cause**: [Clear explanation of why the error occurred]
**Impact**: [What functionality is affected]
**Solution**: [Step-by-step fix]
```

### Code Fix Documentation
```python
# BEFORE (problematic code)
def problematic_function(data):
    # Explain what's wrong with this approach
    return data.split()  # Assumes data is always a string

# AFTER (corrected code)
def fixed_function(data):
    """
    Process input data safely with proper type checking.
    
    Args:
        data: Input data to process (expected: str)
        
    Returns:
        List of processed elements
        
    Raises:
        TypeError: If data is not a string
    """
    if not isinstance(data, str):
        raise TypeError(f"Expected string, got {type(data).__name__}")
    
    return data.split()

# EXPLANATION: Added type checking to prevent runtime errors
# when non-string data is passed to the function
```

## Debugging Methodology

### Systematic Debugging Approach
1. **Reproduce the Error**: Understand the exact conditions that cause the error
2. **Isolate the Problem**: Narrow down the scope to the specific problematic code
3. **Analyze Dependencies**: Check if the error is caused by external factors
4. **Test the Fix**: Verify that the solution resolves the issue without breaking other functionality
5. **Document the Solution**: Explain the fix and why it works

### Debug Information Collection
```python
# Add debugging information to understand program state
def debug_function(data):
    print(f"DEBUG: Input data type: {type(data)}")
    print(f"DEBUG: Input data value: {repr(data)}")
    
    try:
        result = process_data(data)
        print(f"DEBUG: Processing successful, result: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: Error occurred: {type(e).__name__}: {e}")
        print(f"DEBUG: Error at line: {e.__traceback__.tb_lineno}")
        raise
```

### Testing Fixes
```python
# Create test cases to verify the fix
def test_fixed_function():
    # Test normal case
    assert fixed_function("hello world") == ["hello", "world"]
    
    # Test edge cases
    assert fixed_function("") == []
    assert fixed_function("single") == ["single"]
    
    # Test error cases
    try:
        fixed_function(None)
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected behavior
    
    try:
        fixed_function(123)
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected behavior
```

## Common Error Patterns and Solutions

### Python Common Issues

#### Import Errors
```python
# Error: ModuleNotFoundError: No module named 'custom_module'
from custom_module import helper_function

# Solution: Check import path and module structure
# Ensure __init__.py files exist in package directories
from .utils.custom_module import helper_function  # Relative import
# OR
import sys
sys.path.append('/path/to/module')
from custom_module import helper_function
```

#### Indentation Errors
```python
# Error: IndentationError: expected an indented block
def my_function():
return "hello"  # Missing indentation

# Fix:
def my_function():
    return "hello"  # Proper 4-space indentation
```

### JavaScript Common Issues

#### Async/Await Errors
```javascript
// Error: Cannot use await outside async function
function fetchData() {
    const result = await fetch('/api/data');  // Missing async
    return result.json();
}

// Fix:
async function fetchData() {
    const result = await fetch('/api/data');
    return result.json();
}
```

#### Scope Issues
```javascript
// Error: Variables not accessible due to scope
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);  // Prints 3, 3, 3
}

// Fix:
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);  // Prints 0, 1, 2
}
```

## Error Prevention Guidelines

### Defensive Programming
- Always validate input parameters
- Handle null/undefined values explicitly
- Use try-catch blocks for risky operations
- Implement proper error logging and reporting

### Code Review Checklist
- Check for proper error handling in all functions
- Verify input validation and sanitization
- Ensure resource cleanup (file handles, connections)
- Validate edge cases and boundary conditions
- Review for potential security vulnerabilities

### Testing Strategy
- Write unit tests for all error conditions
- Test with invalid inputs and edge cases
- Verify error messages are helpful and accurate
- Ensure fixes don't introduce new issues