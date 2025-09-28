# Code Generation Guidelines

## General Code Generation Rules

### Output Formatting Requirements
- ALWAYS wrap code in markdown code blocks with appropriate language tags
- Use ```python for Python code and ```javascript for JavaScript code
- Include file paths as comments at the top of code blocks when relevant
- Ensure proper indentation and formatting within code blocks

### Code Quality Standards
- Generate syntactically correct code that can be executed immediately
- Include comprehensive error handling for all critical operations
- Write self-documenting code with clear variable and function names
- Implement proper input validation and boundary checking

## Python Code Generation

### Style Guidelines (PEP 8 Compliance)
- Use 4 spaces for indentation (never tabs)
- Limit lines to 79 characters for code, 72 for comments
- Use snake_case for variables and functions, PascalCase for classes
- Add blank lines: 2 before top-level functions/classes, 1 before methods

### Syntax Rules
```python
# Function definition with type hints
def process_data(input_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Process input data and return summary statistics.
    
    Args:
        input_data: List of dictionaries containing data records
        
    Returns:
        Dictionary with processed statistics
        
    Raises:
        ValueError: If input_data is empty or invalid
    """
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Implementation here
    return result
```

### Commenting Standards
- Include docstrings for all functions, classes, and modules
- Use Google-style docstrings with Args, Returns, and Raises sections
- Add inline comments for complex logic or non-obvious operations
- Document any assumptions or limitations in the code

### Import Organization
```python
# Standard library imports
import os
import sys
from typing import List, Dict, Any, Optional

# Third-party imports
import requests
import pandas as pd

# Local application imports
from .utils import helper_function
from .models import DataModel
```

### Error Handling Patterns
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return default_value
finally:
    cleanup_resources()
```

## JavaScript Code Generation

### Style Guidelines
- Use 2 spaces for indentation
- Use camelCase for variables and functions, PascalCase for classes
- Use const for immutable values, let for variables, avoid var
- Add semicolons at the end of statements

### Syntax Rules
```javascript
/**
 * Process user data and return formatted results
 * @param {Array<Object>} userData - Array of user objects
 * @param {Object} options - Processing options
 * @returns {Promise<Object>} Formatted results
 * @throws {Error} When userData is invalid
 */
async function processUserData(userData, options = {}) {
  if (!Array.isArray(userData) || userData.length === 0) {
    throw new Error('userData must be a non-empty array');
  }
  
  // Implementation here
  return result;
}
```

### Commenting Standards
- Use JSDoc format for function and class documentation
- Include @param, @returns, and @throws tags where applicable
- Add inline comments for complex algorithms or business logic
- Document any browser compatibility requirements

### Modern JavaScript Features
```javascript
// Use arrow functions for simple operations
const filterActive = users => users.filter(user => user.active);

// Use destructuring for object/array manipulation
const { name, email, ...otherProps } = user;
const [first, second, ...rest] = items;

// Use template literals for string formatting
const message = `Hello ${name}, you have ${count} messages`;

// Use async/await for asynchronous operations
async function fetchUserData(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    throw error;
  }
}
```

### Error Handling Patterns
```javascript
// Promise-based error handling
function apiCall(endpoint) {
  return fetch(endpoint)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .catch(error => {
      console.error('API call failed:', error);
      throw error;
    });
}

// Async/await error handling
async function safeOperation() {
  try {
    const result = await riskyOperation();
    return result;
  } catch (error) {
    if (error instanceof SpecificError) {
      // Handle specific error type
      return defaultValue;
    }
    // Re-throw unexpected errors
    throw error;
  }
}
```

## Code Block Formatting Requirements

### Language Tag Specification
- Always include the correct language identifier
- Use lowercase language names: `python`, `javascript`, `json`, `bash`
- For configuration files, use appropriate tags: `yaml`, `toml`, `ini`

### File Context Information
```python
# File: src/utils/data_processor.py
def process_data(data):
    """Process the input data according to business rules."""
    # Implementation here
    pass
```

### Multi-file Code Generation
When generating multiple related files, clearly separate them:

```python
# File: models/user.py
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

```python
# File: services/user_service.py
from models.user import User

class UserService:
    def create_user(self, name, email):
        return User(name, email)
```

## Contextual Code Generation

### Project Integration
- Analyze existing code patterns and maintain consistency
- Use established naming conventions from the project
- Follow existing architectural patterns and design decisions
- Integrate with existing error handling and logging systems

### Dependency Management
- Only import modules that are available in the project context
- Use relative imports appropriately for local modules
- Avoid introducing new dependencies without explicit requirements
- Check for existing utility functions before creating new ones

### Testing Considerations
- Write testable code with clear separation of concerns
- Include docstrings and type hints to facilitate testing
- Avoid hard-coded values that would make testing difficult
- Consider edge cases and error conditions in the implementation