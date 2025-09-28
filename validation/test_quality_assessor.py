"""
Test suite for code quality assessment tools.
"""

from quality_assessor import CodeQualityAssessor, DocumentationAnalyzer, generate_quality_report


def test_documentation_analyzer():
    """Test documentation analysis functionality."""
    analyzer = DocumentationAnalyzer()
    
    # Test well-documented Python code
    good_python = '''
"""
This module provides utility functions for mathematical operations.
"""

def calculate_sum(a, b):
    """
    Calculate the sum of two numbers.
    
    Args:
        a (int): First number
        b (int): Second number
        
    Returns:
        int: Sum of a and b
    """
    # Add the two numbers
    return a + b

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.result = 0
'''
    
    result = analyzer.analyze_python_documentation(good_python)
    assert result["has_module_docstring"] == True
    assert result["function_docstrings"] == 2  # calculate_sum and __init__
    assert result["class_docstrings"] == 1
    assert result["score"] > 0.8
    print("✓ Well-documented Python code analysis passed")
    
    # Test poorly documented Python code
    poor_python = '''
def calculate_sum(a, b):
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
'''
    
    result = analyzer.analyze_python_documentation(poor_python)
    assert result["has_module_docstring"] == False
    assert result["function_docstrings"] == 0
    assert result["class_docstrings"] == 0
    assert result["score"] < 0.5
    assert len(result["issues"]) > 0
    print("✓ Poorly documented Python code analysis passed")
    
    # Test JavaScript documentation
    good_js = '''
/**
 * Calculate the sum of two numbers.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
function calculateSum(a, b) {
    // Add the two numbers
    return a + b;
}

/**
 * A simple calculator class.
 */
class Calculator {
    constructor() {
        this.result = 0;
    }
}
'''
    
    result = analyzer.analyze_javascript_documentation(good_js)
    assert result["jsdoc_functions"] == 1
    assert result["jsdoc_classes"] == 1
    assert result["score"] > 0.8
    print("✓ Well-documented JavaScript code analysis passed")


def test_code_quality_assessor():
    """Test comprehensive code quality assessment."""
    assessor = CodeQualityAssessor()
    
    # Test high-quality Python code
    excellent_python = '''
"""
Mathematical utility functions module.

This module provides basic mathematical operations with proper error handling.
"""

def calculate_sum(a, b):
    """
    Calculate the sum of two numbers.
    
    Args:
        a (int or float): First number
        b (int or float): Second number
        
    Returns:
        int or float: Sum of a and b
        
    Raises:
        TypeError: If inputs are not numbers
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    
    # Perform addition
    return a + b


class Calculator:
    """
    A simple calculator for basic mathematical operations.
    
    This class provides methods for common mathematical operations
    with proper error handling and validation.
    """
    
    def __init__(self):
        """Initialize the calculator with zero result."""
        self.result = 0
    
    def add(self, value):
        """
        Add a value to the current result.
        
        Args:
            value (int or float): Value to add
            
        Returns:
            float: New result after addition
        """
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be a number")
        
        # Update result
        self.result += value
        return self.result
'''
    
    assessment = assessor.assess_python_quality(excellent_python)
    assert assessment["syntax_valid"] == True
    assert assessment["overall_score"] > 0.8
    assert assessment["grade"] in ["A", "B"]
    print(f"✓ High-quality Python assessment: Grade {assessment['grade']} ({assessment['overall_score']:.1%})")
    
    # Test poor-quality Python code
    poor_python = '''
def bad_function(x,y):
result=x+y
return result

class badClass:
def __init__(self):
self.value=0
'''
    
    assessment = assessor.assess_python_quality(poor_python)
    assert assessment["syntax_valid"] == False  # Indentation errors
    assert assessment["overall_score"] < 0.6  # Adjusted threshold
    assert assessment["grade"] in ["D", "F"]
    print(f"✓ Poor-quality Python assessment: Grade {assessment['grade']} ({assessment['overall_score']:.1%})")
    
    # Test JavaScript quality assessment
    good_js = '''
/**
 * Calculate the sum of two numbers.
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
function calculateSum(a, b) {
    if (typeof a !== 'number' || typeof b !== 'number') {
        throw new Error('Both arguments must be numbers');
    }
    
    // Perform addition
    return a + b;
}

/**
 * A simple calculator class.
 */
class Calculator {
    constructor() {
        this.result = 0;
    }
    
    /**
     * Add a value to the current result.
     * @param {number} value - Value to add
     * @returns {number} New result
     */
    add(value) {
        if (typeof value !== 'number') {
            throw new Error('Value must be a number');
        }
        
        this.result += value;
        return this.result;
    }
}
'''
    
    assessment = assessor.assess_javascript_quality(good_js)
    assert assessment["syntax_valid"] == True
    assert assessment["overall_score"] > 0.7
    print(f"✓ JavaScript quality assessment: Grade {assessment['grade']} ({assessment['overall_score']:.1%})")


def test_quality_report_generation():
    """Test quality report generation."""
    assessor = CodeQualityAssessor()
    
    code = '''
def hello_world():
    print("Hello, World!")
    return True
'''
    
    assessment = assessor.assess_python_quality(code)
    report = generate_quality_report(assessment, "python")
    
    assert "Code Quality Assessment Report" in report
    assert "Overall Grade:" in report
    assert "Recommendations:" in report
    print("✓ Quality report generation passed")


def test_pep8_compliance_checking():
    """Test PEP 8 compliance checking specifically."""
    assessor = CodeQualityAssessor()
    
    # Test PEP 8 compliant code
    compliant_code = '''
"""Module docstring."""


def function_name(param_one, param_two):
    """Function docstring."""
    result = param_one + param_two
    return result


class ClassName:
    """Class docstring."""
    
    def __init__(self):
        """Initialize instance."""
        self.value = 0
'''
    
    assessment = assessor.assess_python_quality(compliant_code)
    style_result = assessment["assessments"]["style"]
    
    # Should have minimal style violations
    assert style_result["score"] > 0.8
    print("✓ PEP 8 compliant code assessment passed")
    
    # Test non-compliant code
    non_compliant_code = '''
def badFunction(paramOne,paramTwo):
result=paramOne+paramTwo
return result

class badClass:
def __init__(self):
self.value=0
'''
    
    assessment = assessor.assess_python_quality(non_compliant_code)
    style_result = assessment["assessments"]["style"]
    
    # Should have many style violations
    assert len(style_result["violations"]) > 0
    assert style_result["score"] < 0.7  # Adjusted threshold
    print("✓ Non-PEP 8 compliant code detection passed")


if __name__ == "__main__":
    print("Running code quality assessment tests...")
    
    test_documentation_analyzer()
    test_code_quality_assessor()
    test_quality_report_generation()
    test_pep8_compliance_checking()
    
    print("\n✅ All code quality assessment tests passed!")