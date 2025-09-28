"""Debug test for documentation analyzer."""

from quality_assessor import DocumentationAnalyzer

analyzer = DocumentationAnalyzer()

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

from quality_assessor import CodeQualityAssessor

assessor = CodeQualityAssessor()

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

print("Non-compliant code style assessment:")
for key, value in style_result.items():
    print(f"  {key}: {value}")