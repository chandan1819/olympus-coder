# Context Awareness Guidelines

## Project Structure Understanding

### Directory Structure Analysis
When provided with directory listings or file trees, analyze the project structure to understand:
- **Project Type**: Web application, CLI tool, library, data science project
- **Framework/Technology**: Django, Flask, React, Node.js, etc.
- **Architecture Pattern**: MVC, microservices, monolithic, etc.
- **Testing Strategy**: Unit tests, integration tests, test frameworks used
- **Build System**: Package managers, build tools, deployment scripts

### File Organization Patterns
```
# Example project structure analysis
project/
├── src/                    # Source code directory
│   ├── models/            # Data models and business logic
│   ├── views/             # Presentation layer
│   ├── controllers/       # Request handling logic
│   └── utils/             # Utility functions and helpers
├── tests/                 # Test files
├── config/                # Configuration files
├── docs/                  # Documentation
└── requirements.txt       # Dependencies
```

**Analysis Output**: This is a Python web application following MVC architecture with separate concerns for models, views, and controllers.

### Technology Stack Identification
- **Python Projects**: Look for requirements.txt, setup.py, pyproject.toml
- **JavaScript Projects**: Look for package.json, node_modules, webpack.config.js
- **Framework Indicators**: 
  - Django: settings.py, manage.py, apps structure
  - Flask: app.py, blueprints
  - React: components, JSX files, public/src structure
  - Express: server.js, routes, middleware

## File Reference Validation

### Absolute Path Validation
```python
# CORRECT: Reference files that exist in provided context
from src.models.user import User  # Only if src/models/user.py exists
from utils.helpers import format_date  # Only if utils/helpers.py exists

# INCORRECT: Never reference files not shown in context
from external.library import SomeClass  # Don't assume external files exist
from ../other_project/module import func  # Don't reference outside project
```

### Relative Import Handling
```python
# When in src/services/user_service.py
from ..models.user import User  # Correct relative import
from .auth_service import authenticate  # Correct same-level import
from src.utils.helpers import format_date  # Correct absolute import

# Validate import paths against provided directory structure
# Only use imports that can be verified from the context
```

### File Existence Verification
Before referencing any file in code:
1. Check if the file exists in the provided directory listing
2. Verify the import path matches the actual file structure
3. Ensure the referenced functions/classes are available
4. Use only imports that can be validated from context

## Import Statement Guidelines

### Python Import Best Practices
```python
# Standard library imports (always available)
import os
import sys
from typing import List, Dict, Optional

# Third-party imports (check requirements.txt or setup.py)
import requests  # Only if in requirements.txt
import pandas as pd  # Only if in requirements.txt

# Local imports (verify file existence)
from .models import User  # Only if models.py or models/__init__.py exists
from ..utils.helpers import format_date  # Verify relative path exists
```

### JavaScript Import Validation
```javascript
// Node.js built-in modules (always available)
const fs = require('fs');
const path = require('path');

// Third-party packages (check package.json)
const express = require('express');  // Only if in package.json
const lodash = require('lodash');    // Only if in package.json

// Local modules (verify file existence)
const User = require('./models/User');  // Only if ./models/User.js exists
const { formatDate } = require('../utils/helpers');  // Verify path exists
```

### Import Error Prevention
- Never assume external libraries are available without verification
- Always check package.json or requirements.txt for dependencies
- Validate relative import paths against directory structure
- Use absolute imports when the full project structure is known

## Consistency Requirements

### Naming Convention Adherence
Analyze existing code to identify and maintain:
- **Variable Naming**: snake_case vs camelCase vs PascalCase
- **Function Naming**: Verb-noun patterns, prefixes/suffixes
- **Class Naming**: Singular vs plural, naming patterns
- **File Naming**: Underscore vs hyphen vs camelCase

```python
# Example: Analyzing existing code patterns
# If existing code uses:
class UserManager:
    def get_user_by_id(self, user_id):
        pass

# New code should follow the same pattern:
class OrderManager:  # PascalCase for classes
    def get_order_by_id(self, order_id):  # snake_case for methods
        pass
```

### Code Style Consistency
```python
# Match existing indentation style
# If existing code uses 4 spaces:
def existing_function():
    if condition:
        return value

# New code should also use 4 spaces:
def new_function():
    if condition:
        return value
```

### Architectural Pattern Consistency
```python
# If existing code follows repository pattern:
class UserRepository:
    def find_by_id(self, user_id):
        pass

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

# New code should follow the same pattern:
class OrderRepository:
    def find_by_id(self, order_id):
        pass

class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
```

## Existing Codebase Integration

### Pattern Recognition
Analyze existing code to identify:
- **Error Handling Patterns**: Try-catch usage, custom exceptions
- **Logging Patterns**: Logger configuration, log levels, message formats
- **Configuration Management**: Environment variables, config files
- **Database Patterns**: ORM usage, connection management
- **API Patterns**: Response formats, error handling, authentication

### Code Integration Strategy
```python
# Example: Integrating with existing error handling
# If existing code uses custom exceptions:
class ValidationError(Exception):
    pass

def validate_user(user_data):
    if not user_data.get('email'):
        raise ValidationError("Email is required")

# New code should use the same exception pattern:
def validate_order(order_data):
    if not order_data.get('customer_id'):
        raise ValidationError("Customer ID is required")
```

### Configuration Integration
```python
# If existing code uses a config module:
from config.settings import DATABASE_URL, API_KEY

# New code should use the same configuration approach:
from config.settings import PAYMENT_API_URL, ENCRYPTION_KEY
```

## Context Validation Checklist

### Before Writing Code
1. **Verify File Structure**: Confirm all referenced files exist in provided context
2. **Check Dependencies**: Validate all imports against available packages
3. **Analyze Patterns**: Identify existing code patterns and conventions
4. **Validate Paths**: Ensure all file paths and imports are accurate
5. **Review Architecture**: Understand the overall system design

### During Code Generation
1. **Maintain Consistency**: Follow established naming and style conventions
2. **Use Existing Utilities**: Leverage existing helper functions and utilities
3. **Follow Patterns**: Implement new features using established architectural patterns
4. **Validate References**: Double-check all file and function references
5. **Integrate Properly**: Ensure new code fits seamlessly with existing codebase

### After Code Generation
1. **Review Integration**: Verify the code integrates properly with existing systems
2. **Check Dependencies**: Confirm all imports and references are valid
3. **Validate Consistency**: Ensure the code follows project conventions
4. **Test Compatibility**: Consider how the code interacts with existing functionality

## Context Limitation Handling

### When Context is Incomplete
- Document assumptions made about missing information
- Use conservative approaches that are likely to be compatible
- Suggest areas where additional context would be helpful
- Implement defensive programming practices

### When Files are Missing
```python
# Instead of assuming a file exists:
try:
    from utils.helpers import format_date
except ImportError:
    # Provide fallback implementation
    def format_date(date_obj):
        return date_obj.strftime('%Y-%m-%d')
```

### When Patterns are Unclear
- Use widely accepted best practices as defaults
- Document the chosen approach and reasoning
- Suggest reviewing with existing codebase for consistency
- Implement flexible solutions that can be easily modified

## Project Context Examples

### Web Application Context
```
project/
├── app/
│   ├── models/
│   ├── views/
│   ├── templates/
│   └── static/
├── tests/
└── requirements.txt
```
**Analysis**: Django-style web application with MVC structure

### Library/Package Context
```
package/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
├── setup.py
└── README.md
```
**Analysis**: Python package with standard distribution structure

### Microservice Context
```
service/
├── src/
│   ├── handlers/
│   ├── services/
│   ├── models/
│   └── middleware/
├── docker/
├── k8s/
└── Dockerfile
```
**Analysis**: Containerized microservice with cloud deployment configuration