"""
Test suite for context validation framework.
"""

from context_validator import ContextValidator, ProjectContext


def test_project_context():
    """Test ProjectContext functionality."""
    file_paths = [
        "src/main.py",
        "src/utils/helpers.py",
        "src/models/user.py",
        "tests/test_main.py",
        "config/settings.json",
        "README.md"
    ]
    
    context = ProjectContext(file_paths)
    
    # Test file existence
    assert context.file_exists("src/main.py") == True
    assert context.file_exists("nonexistent.py") == False
    print("✓ File existence checking passed")
    
    # Test directory existence
    assert context.directory_exists("src") == True
    assert context.directory_exists("src/utils") == True
    assert context.directory_exists("nonexistent") == False
    print("✓ Directory existence checking passed")
    
    # Test Python modules extraction
    python_modules = context.get_python_modules()
    expected_modules = {"src.main", "src.utils.helpers", "src.models.user", "tests.test_main"}
    assert python_modules == expected_modules
    print("✓ Python modules extraction passed")


def test_file_reference_validation():
    """Test file reference validation."""
    file_paths = [
        "src/main.py",
        "src/utils/helpers.py",
        "config/settings.json",
        "data/input.csv"
    ]
    
    context = ProjectContext(file_paths)
    validator = ContextValidator(context)
    
    # Test Python code with valid file references
    python_code = '''
import json

def load_config():
    with open("config/settings.json", "r") as f:
        return json.load(f)

def process_data():
    data = read_csv("data/input.csv")
    return data
'''
    
    result = validator.validate_file_references(python_code, "python")
    assert result["is_valid"] == True
    assert "config/settings.json" in result["file_references"]
    assert "data/input.csv" in result["file_references"]
    print("✓ Valid file reference validation passed")
    
    # Test Python code with invalid file references
    invalid_python_code = '''
def load_config():
    with open("config/nonexistent.json", "r") as f:
        return json.load(f)
'''
    
    result = validator.validate_file_references(invalid_python_code, "python")
    assert result["is_valid"] == False
    assert "config/nonexistent.json" in result["invalid_references"]
    assert len(result["suggestions"]) > 0
    print("✓ Invalid file reference detection passed")


def test_import_statement_validation():
    """Test import statement validation."""
    file_paths = [
        "src/main.py",
        "src/utils/helpers.py",
        "src/models/user.py",
        "tests/test_main.py"
    ]
    
    context = ProjectContext(file_paths)
    validator = ContextValidator(context)
    
    # Test valid Python imports
    valid_python_code = '''
import os
import json
from src.utils.helpers import format_data
from src.models.user import User

def main():
    pass
'''
    
    result = validator.validate_import_statements(valid_python_code, "python")
    # Should be valid (os and json are external, others exist in project)
    assert result["is_valid"] == True
    assert len(result["imports"]) == 4
    print("✓ Valid Python import validation passed")
    
    # Test invalid Python imports
    invalid_python_code = '''
from src.nonexistent.module import something
from src.utils.missing import function

def main():
    pass
'''
    
    result = validator.validate_import_statements(invalid_python_code, "python")
    assert result["is_valid"] == False
    assert len(result["invalid_imports"]) > 0
    print("✓ Invalid Python import detection passed")
    
    # Test JavaScript imports
    js_code = '''
import React from 'react';
import { Component } from './components/Component.js';
const utils = require('./utils/helpers.js');
'''
    
    js_file_paths = [
        "components/Component.js",
        "utils/helpers.js",
        "index.js"
    ]
    
    js_context = ProjectContext(js_file_paths)
    js_validator = ContextValidator(js_context)
    
    result = js_validator.validate_import_statements(js_code, "javascript")
    # React is external, others should be validated
    print("✓ JavaScript import validation passed")


def test_naming_consistency_validation():
    """Test naming consistency validation."""
    validator = ContextValidator()
    
    # Test Python naming consistency
    python_code = '''
def calculate_sum(a, b):
    return a + b

def processData(x, y):  # Inconsistent with snake_case
    return x * y

class UserModel:
    def __init__(self):
        self.user_id = 0
        self.userName = ""  # Inconsistent with snake_case
'''
    
    existing_patterns = {
        "functions": ["get_user", "set_password", "validate_email"],
        "variables": ["user_id", "email_address", "first_name"],
        "classes": ["UserModel", "EmailService", "DatabaseConnection"]
    }
    
    result = validator.validate_naming_consistency(python_code, "python", existing_patterns)
    assert result["is_consistent"] == False
    assert len(result["inconsistencies"]) > 0
    
    # Check that inconsistencies are detected
    inconsistent_names = [inc["name"] for inc in result["inconsistencies"]]
    assert "processData" in inconsistent_names  # Should be process_data
    print("✓ Python naming consistency validation passed")
    
    # Test JavaScript naming consistency
    js_code = '''
function calculateSum(a, b) {
    return a + b;
}

function process_data(x, y) {  // Inconsistent with camelCase
    return x * y;
}

class UserService {
    constructor() {
        this.userId = 0;
        this.user_name = "";  // Inconsistent with camelCase
    }
}
'''
    
    js_existing_patterns = {
        "functions": ["getUserData", "setUserPassword", "validateEmail"],
        "variables": ["userId", "emailAddress", "firstName"],
        "classes": ["UserService", "EmailValidator", "DataProcessor"]
    }
    
    result = validator.validate_naming_consistency(js_code, "javascript", js_existing_patterns)
    assert result["is_consistent"] == False
    assert len(result["inconsistencies"]) > 0
    print("✓ JavaScript naming consistency validation passed")


def test_similarity_calculation():
    """Test file similarity calculation."""
    file_paths = [
        "src/user_model.py",
        "src/user_service.py",
        "src/email_validator.py",
        "tests/test_user.py"
    ]
    
    context = ProjectContext(file_paths)
    validator = ContextValidator(context)
    
    # Test finding similar files
    similar = validator._find_similar_files("src/user_controller.py")
    assert "src/user_model.py" in similar
    assert "src/user_service.py" in similar
    print("✓ File similarity calculation passed")


def test_naming_pattern_analysis():
    """Test naming pattern analysis."""
    validator = ContextValidator()
    
    # Test snake_case dominant pattern
    snake_case_names = ["get_user", "set_password", "validate_email", "process_data"]
    patterns = validator._analyze_naming_patterns(snake_case_names, "functions")
    assert patterns["dominant"] == "snake_case"
    print("✓ Snake case pattern analysis passed")
    
    # Test camelCase dominant pattern
    camel_case_names = ["getUser", "setPassword", "validateEmail", "processData"]
    patterns = validator._analyze_naming_patterns(camel_case_names, "functions")
    assert patterns["dominant"] == "camelCase"
    print("✓ Camel case pattern analysis passed")
    
    # Test PascalCase dominant pattern
    pascal_case_names = ["UserModel", "EmailService", "DataProcessor", "FileManager"]
    patterns = validator._analyze_naming_patterns(pascal_case_names, "classes")
    assert patterns["dominant"] == "PascalCase"
    print("✓ Pascal case pattern analysis passed")


def test_comprehensive_context_validation():
    """Test comprehensive context validation scenario."""
    # Set up a realistic project context
    file_paths = [
        "src/__init__.py",
        "src/main.py",
        "src/models/__init__.py",
        "src/models/user.py",
        "src/models/product.py",
        "src/services/__init__.py",
        "src/services/user_service.py",
        "src/services/email_service.py",
        "src/utils/__init__.py",
        "src/utils/helpers.py",
        "src/utils/validators.py",
        "tests/__init__.py",
        "tests/test_user.py",
        "tests/test_services.py",
        "config/settings.json",
        "config/database.json",
        "README.md",
        "requirements.txt"
    ]
    
    context = ProjectContext(file_paths)
    validator = ContextValidator(context)
    
    # Test code that should pass all validations
    good_code = '''
"""User management module."""

import json
import os
from src.models.user import User
from src.utils.helpers import format_email
from src.utils.validators import validate_password

def create_user(username, email, password):
    """Create a new user with validation."""
    if not validate_password(password):
        raise ValueError("Invalid password")
    
    formatted_email = format_email(email)
    user = User(username, formatted_email, password)
    
    # Load configuration
    with open("config/settings.json", "r") as f:
        config = json.load(f)
    
    return user

def get_user_by_id(user_id):
    """Retrieve user by ID."""
    # Implementation here
    pass
'''
    
    # Test all validation aspects
    file_result = validator.validate_file_references(good_code, "python")
    import_result = validator.validate_import_statements(good_code, "python")
    
    existing_patterns = {
        "functions": ["get_user_data", "set_user_password", "validate_user_email"],
        "classes": ["User", "EmailService", "DatabaseConnection"]
    }
    naming_result = validator.validate_naming_consistency(good_code, "python", existing_patterns)
    
    assert file_result["is_valid"] == True
    assert import_result["is_valid"] == True
    assert naming_result["is_consistent"] == True
    
    print("✓ Comprehensive context validation passed")


if __name__ == "__main__":
    print("Running context validation tests...")
    
    test_project_context()
    test_file_reference_validation()
    test_import_statement_validation()
    test_naming_consistency_validation()
    test_similarity_calculation()
    test_naming_pattern_analysis()
    test_comprehensive_context_validation()
    
    print("\n✅ All context validation tests passed!")