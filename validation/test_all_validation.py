"""
Comprehensive test runner for all validation components.
"""

import sys
import traceback
from response_validator import ResponseValidator, ToolRequestValidator
from code_validator import validate_code_block, PythonValidator, JavaScriptValidator
from quality_assessor import CodeQualityAssessor, generate_quality_report
from context_validator import ContextValidator, ProjectContext


def run_test_suite():
    """Run comprehensive validation test suite."""
    print("🧪 Running Olympus-Coder-v1 Validation Framework Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Response Validation
    try:
        print("\n1️⃣  Testing Response Validation...")
        validator = ResponseValidator()
        
        # Test tool request validation
        tool_request = '{"tool_name": "read_file", "parameters": {"file_path": "test.py"}}'
        result = validator.validate_response_format(tool_request)
        assert result["has_tool_requests"] == True
        
        # Test code response validation
        code_response = "```python\ndef hello():\n    print('Hello')\n```"
        result = validator.validate_response_format(code_response)
        assert result["has_code_blocks"] == True
        
        print("   ✅ Response validation tests passed")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Response validation tests failed: {e}")
        tests_failed += 1
    
    # Test 2: Code Validation
    try:
        print("\n2️⃣  Testing Code Validation...")
        
        # Test Python validation
        python_code = '''
def calculate_sum(a, b):
    """Calculate sum of two numbers."""
    return a + b
'''
        result = validate_code_block(python_code, "python")
        assert result["is_valid"] == True
        
        # Test JavaScript validation
        js_code = '''
function calculateSum(a, b) {
    return a + b;
}
'''
        result = validate_code_block(js_code, "javascript")
        assert result["is_valid"] == True
        
        print("   ✅ Code validation tests passed")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Code validation tests failed: {e}")
        tests_failed += 1
    
    # Test 3: Quality Assessment
    try:
        print("\n3️⃣  Testing Quality Assessment...")
        assessor = CodeQualityAssessor()
        
        # Test Python quality assessment
        python_code = '''
"""High quality Python module."""

def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers (list): List of numeric values
        
    Returns:
        float: Average of the numbers
    """
    if not numbers:
        return 0.0
    
    return sum(numbers) / len(numbers)
'''
        
        assessment = assessor.assess_python_quality(python_code)
        assert assessment["syntax_valid"] == True
        assert assessment["overall_score"] > 0.7
        
        # Test report generation
        report = generate_quality_report(assessment, "python")
        assert "Code Quality Assessment Report" in report
        
        print("   ✅ Quality assessment tests passed")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Quality assessment tests failed: {e}")
        tests_failed += 1
    
    # Test 4: Context Validation
    try:
        print("\n4️⃣  Testing Context Validation...")
        
        # Set up project context
        file_paths = [
            "src/main.py",
            "src/utils/helpers.py",
            "config/settings.json"
        ]
        
        context = ProjectContext(file_paths)
        validator = ContextValidator(context)
        
        # Test file reference validation
        code_with_refs = '''
import json

def load_config():
    with open("config/settings.json", "r") as f:
        return json.load(f)
'''
        
        result = validator.validate_file_references(code_with_refs, "python")
        assert result["is_valid"] == True
        
        # Test import validation
        code_with_imports = '''
from src.utils.helpers import format_data
import os
'''
        
        result = validator.validate_import_statements(code_with_imports, "python")
        assert result["is_valid"] == True
        
        print("   ✅ Context validation tests passed")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Context validation tests failed: {e}")
        tests_failed += 1
    
    # Test 5: Integration Test
    try:
        print("\n5️⃣  Testing Framework Integration...")
        
        # Simulate a complete validation workflow
        model_response = '''
Here's the implementation:

```python
"""User management utilities."""

import json
from src.models.user import User

def create_user(name, email):
    """
    Create a new user instance.
    
    Args:
        name (str): User's full name
        email (str): User's email address
        
    Returns:
        User: New user instance
    """
    if not name or not email:
        raise ValueError("Name and email are required")
    
    # Load user configuration
    with open("config/user_settings.json", "r") as f:
        config = json.load(f)
    
    return User(name, email, config)
```

This function creates a user with proper validation.
'''
        
        # Set up comprehensive project context
        project_files = [
            "src/models/user.py",
            "config/user_settings.json",
            "src/main.py"
        ]
        
        project_context = ProjectContext(project_files)
        
        # Validate response format
        response_validator = ResponseValidator()
        format_result = response_validator.validate_response_format(model_response)
        assert format_result["has_code_blocks"] == True
        
        # Extract and validate code
        code_block = format_result["code_blocks"][0]
        code = code_block["code"]
        language = code_block["language"]
        
        # Validate code syntax and style
        code_result = validate_code_block(code, language)
        assert code_result["is_valid"] == True
        
        # Assess code quality
        quality_assessor = CodeQualityAssessor()
        quality_result = quality_assessor.assess_code_quality(code, language)
        assert quality_result["syntax_valid"] == True
        
        # Validate context consistency
        context_validator = ContextValidator(project_context)
        file_result = context_validator.validate_file_references(code, language)
        import_result = context_validator.validate_import_statements(code, language)
        
        # All validations should pass
        assert file_result["is_valid"] == True
        assert import_result["is_valid"] == True
        
        print("   ✅ Integration tests passed")
        tests_passed += 1
        
    except Exception as e:
        print(f"   ❌ Integration tests failed: {e}")
        traceback.print_exc()
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed} passed, {tests_failed} failed")
    
    if tests_failed == 0:
        print("🎉 All validation framework tests passed!")
        print("\n✨ The validation framework is ready for use with:")
        print("   • Response format validation (JSON schema, code blocks)")
        print("   • Code syntax and style validation (Python, JavaScript)")
        print("   • Code quality assessment (PEP 8, JSDoc, documentation)")
        print("   • Context validation (file paths, imports, naming consistency)")
        print("   • Comprehensive integration testing")
        return True
    else:
        print("❌ Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)