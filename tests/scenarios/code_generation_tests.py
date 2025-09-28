"""
Code Generation Test Cases for Olympus-Coder-v1

This module contains test scenarios for evaluating the model's ability to generate
high-quality Python and JavaScript code according to requirements 1.1, 1.2, and 1.6.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CodeGenerationTestCase:
    """Represents a single code generation test scenario."""
    test_id: str
    description: str
    language: str
    prompt: str
    expected_features: List[str]
    validation_criteria: List[str]
    difficulty: str  # 'basic', 'intermediate', 'advanced'


class CodeGenerationTests:
    """Collection of code generation test scenarios."""
    
    def __init__(self):
        self.python_tests = self._create_python_tests()
        self.javascript_tests = self._create_javascript_tests()
        self.edge_case_tests = self._create_edge_case_tests()
    
    def _create_python_tests(self) -> List[CodeGenerationTestCase]:
        """Create Python function and class generation test cases."""
        return [
            CodeGenerationTestCase(
                test_id="py_func_basic_001",
                description="Generate a simple Python function with parameters and return value",
                language="python",
                prompt="Create a Python function called 'calculate_area' that takes width and height as parameters and returns the area of a rectangle.",
                expected_features=[
                    "function definition with correct syntax",
                    "appropriate parameter names",
                    "return statement",
                    "docstring or comments",
                    "markdown code block with python tag"
                ],
                validation_criteria=[
                    "syntactically correct Python code",
                    "follows PEP 8 naming conventions",
                    "includes explanatory comments",
                    "proper code block formatting"
                ],
                difficulty="basic"
            ),
            
            CodeGenerationTestCase(
                test_id="py_func_intermediate_002",
                description="Generate Python function with error handling and type hints",
                language="python",
                prompt="Create a Python function 'safe_divide' that divides two numbers with proper error handling for division by zero and includes type hints.",
                expected_features=[
                    "type hints for parameters and return",
                    "try-except block for error handling",
                    "appropriate exception handling",
                    "docstring with parameter descriptions",
                    "return type annotation"
                ],
                validation_criteria=[
                    "correct type hint syntax",
                    "proper exception handling",
                    "PEP 8 compliant formatting",
                    "comprehensive docstring"
                ],
                difficulty="intermediate"
            ),
            
            CodeGenerationTestCase(
                test_id="py_class_basic_003",
                description="Generate a simple Python class with constructor and methods",
                language="python",
                prompt="Create a Python class 'BankAccount' with constructor that takes account_number and initial_balance, and methods for deposit, withdraw, and get_balance.",
                expected_features=[
                    "class definition with __init__ method",
                    "instance variables initialization",
                    "public methods with appropriate logic",
                    "proper method signatures",
                    "class and method docstrings"
                ],
                validation_criteria=[
                    "correct class syntax",
                    "proper method definitions",
                    "appropriate use of self parameter",
                    "follows Python naming conventions"
                ],
                difficulty="basic"
            ),
            
            CodeGenerationTestCase(
                test_id="py_class_advanced_004",
                description="Generate Python class with inheritance and property decorators",
                language="python",
                prompt="Create a Python class 'Employee' that inherits from 'Person' with properties for salary using @property decorator and a method to calculate annual bonus.",
                expected_features=[
                    "class inheritance syntax",
                    "property decorator usage",
                    "getter and setter methods",
                    "super() call in constructor",
                    "method overriding if applicable"
                ],
                validation_criteria=[
                    "correct inheritance implementation",
                    "proper property decorator usage",
                    "appropriate super() usage",
                    "maintains encapsulation principles"
                ],
                difficulty="advanced"
            ),
            
            CodeGenerationTestCase(
                test_id="py_func_data_processing_005",
                description="Generate Python function for data processing with list comprehensions",
                language="python",
                prompt="Create a Python function 'process_student_grades' that takes a list of dictionaries containing student data and returns average grades by subject using list comprehensions.",
                expected_features=[
                    "list comprehension usage",
                    "dictionary manipulation",
                    "data aggregation logic",
                    "proper function structure",
                    "handling of nested data structures"
                ],
                validation_criteria=[
                    "efficient list comprehension syntax",
                    "correct dictionary operations",
                    "proper data type handling",
                    "readable and maintainable code"
                ],
                difficulty="intermediate"
            )
        ]
    
    def _create_javascript_tests(self) -> List[CodeGenerationTestCase]:
        """Create JavaScript component and utility function test cases."""
        return [
            CodeGenerationTestCase(
                test_id="js_func_basic_001",
                description="Generate a simple JavaScript function with arrow syntax",
                language="javascript",
                prompt="Create a JavaScript arrow function called 'formatCurrency' that takes a number and returns it formatted as USD currency.",
                expected_features=[
                    "arrow function syntax",
                    "parameter handling",
                    "return statement",
                    "appropriate variable naming",
                    "markdown code block with javascript tag"
                ],
                validation_criteria=[
                    "correct arrow function syntax",
                    "proper JavaScript formatting",
                    "follows JavaScript naming conventions",
                    "includes explanatory comments"
                ],
                difficulty="basic"
            ),
            
            CodeGenerationTestCase(
                test_id="js_func_async_002",
                description="Generate JavaScript async function with error handling",
                language="javascript",
                prompt="Create an async JavaScript function 'fetchUserData' that makes an API call and handles both success and error cases with proper async/await syntax.",
                expected_features=[
                    "async/await syntax",
                    "try-catch error handling",
                    "fetch API usage",
                    "proper promise handling",
                    "JSDoc comments"
                ],
                validation_criteria=[
                    "correct async/await implementation",
                    "proper error handling",
                    "appropriate API call structure",
                    "good JavaScript practices"
                ],
                difficulty="intermediate"
            ),
            
            CodeGenerationTestCase(
                test_id="js_class_component_003",
                description="Generate JavaScript ES6 class with methods and properties",
                language="javascript",
                prompt="Create a JavaScript ES6 class 'TaskManager' with methods to add, remove, and list tasks, using private fields and getter methods.",
                expected_features=[
                    "ES6 class syntax",
                    "private field declarations",
                    "getter methods",
                    "constructor with parameters",
                    "method implementations"
                ],
                validation_criteria=[
                    "correct ES6 class structure",
                    "proper private field usage",
                    "appropriate method definitions",
                    "follows modern JavaScript patterns"
                ],
                difficulty="intermediate"
            ),
            
            CodeGenerationTestCase(
                test_id="js_utility_advanced_004",
                description="Generate JavaScript utility function with complex data manipulation",
                language="javascript",
                prompt="Create a JavaScript utility function 'deepMergeObjects' that recursively merges two objects, handling nested objects and arrays properly.",
                expected_features=[
                    "recursive function logic",
                    "object and array type checking",
                    "deep cloning mechanisms",
                    "edge case handling",
                    "comprehensive parameter validation"
                ],
                validation_criteria=[
                    "correct recursive implementation",
                    "proper type checking",
                    "handles edge cases appropriately",
                    "efficient and readable code"
                ],
                difficulty="advanced"
            ),
            
            CodeGenerationTestCase(
                test_id="js_module_export_005",
                description="Generate JavaScript module with multiple exports",
                language="javascript",
                prompt="Create a JavaScript module 'mathUtils.js' that exports multiple utility functions for mathematical operations using both named and default exports.",
                expected_features=[
                    "module export syntax",
                    "named exports",
                    "default export",
                    "multiple function definitions",
                    "proper module structure"
                ],
                validation_criteria=[
                    "correct ES6 module syntax",
                    "proper export declarations",
                    "consistent function implementations",
                    "follows module best practices"
                ],
                difficulty="intermediate"
            )
        ]
    
    def _create_edge_case_tests(self) -> List[CodeGenerationTestCase]:
        """Create edge cases for complex code generation requirements."""
        return [
            CodeGenerationTestCase(
                test_id="edge_case_001",
                description="Generate code with ambiguous requirements",
                language="python",
                prompt="Create a function that processes data efficiently.",
                expected_features=[
                    "reasonable assumptions documented",
                    "generic but functional implementation",
                    "clear parameter definitions",
                    "explanatory comments about assumptions"
                ],
                validation_criteria=[
                    "makes reasonable assumptions",
                    "documents assumptions clearly",
                    "provides working implementation",
                    "maintains code quality standards"
                ],
                difficulty="advanced"
            ),
            
            CodeGenerationTestCase(
                test_id="edge_case_002",
                description="Generate code with conflicting style requirements",
                language="javascript",
                prompt="Create a JavaScript function using both functional and object-oriented programming paradigms to solve a data transformation problem.",
                expected_features=[
                    "hybrid programming approach",
                    "appropriate use of both paradigms",
                    "clear separation of concerns",
                    "justification for approach choice"
                ],
                validation_criteria=[
                    "successfully combines paradigms",
                    "maintains code readability",
                    "appropriate design decisions",
                    "explains approach rationale"
                ],
                difficulty="advanced"
            ),
            
            CodeGenerationTestCase(
                test_id="edge_case_003",
                description="Generate code with performance constraints",
                language="python",
                prompt="Create a Python function to find duplicates in a large list with O(n) time complexity requirement.",
                expected_features=[
                    "efficient algorithm implementation",
                    "appropriate data structure usage",
                    "complexity analysis comments",
                    "performance-optimized code"
                ],
                validation_criteria=[
                    "meets time complexity requirement",
                    "uses appropriate algorithms",
                    "includes performance analysis",
                    "maintains code clarity"
                ],
                difficulty="advanced"
            ),
            
            CodeGenerationTestCase(
                test_id="edge_case_004",
                description="Generate code with multiple language features",
                language="javascript",
                prompt="Create a JavaScript function that uses destructuring, spread operator, template literals, and default parameters to process user configuration objects.",
                expected_features=[
                    "destructuring assignment",
                    "spread operator usage",
                    "template literal strings",
                    "default parameter values",
                    "modern JavaScript features"
                ],
                validation_criteria=[
                    "correctly uses all specified features",
                    "appropriate feature application",
                    "maintains code readability",
                    "follows modern JavaScript patterns"
                ],
                difficulty="advanced"
            )
        ]
    
    def get_all_tests(self) -> List[CodeGenerationTestCase]:
        """Return all code generation test cases."""
        return self.python_tests + self.javascript_tests + self.edge_case_tests
    
    def get_tests_by_language(self, language: str) -> List[CodeGenerationTestCase]:
        """Return test cases for a specific language."""
        all_tests = self.get_all_tests()
        return [test for test in all_tests if test.language.lower() == language.lower()]
    
    def get_tests_by_difficulty(self, difficulty: str) -> List[CodeGenerationTestCase]:
        """Return test cases for a specific difficulty level."""
        all_tests = self.get_all_tests()
        return [test for test in all_tests if test.difficulty.lower() == difficulty.lower()]
    
    def export_to_json(self, filepath: str) -> None:
        """Export all test cases to JSON format for external tools."""
        all_tests = self.get_all_tests()
        test_data = []
        
        for test in all_tests:
            test_data.append({
                'test_id': test.test_id,
                'description': test.description,
                'language': test.language,
                'prompt': test.prompt,
                'expected_features': test.expected_features,
                'validation_criteria': test.validation_criteria,
                'difficulty': test.difficulty
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage and basic validation
    test_suite = CodeGenerationTests()
    
    print(f"Total test cases: {len(test_suite.get_all_tests())}")
    print(f"Python tests: {len(test_suite.get_tests_by_language('python'))}")
    print(f"JavaScript tests: {len(test_suite.get_tests_by_language('javascript'))}")
    print(f"Basic difficulty: {len(test_suite.get_tests_by_difficulty('basic'))}")
    print(f"Intermediate difficulty: {len(test_suite.get_tests_by_difficulty('intermediate'))}")
    print(f"Advanced difficulty: {len(test_suite.get_tests_by_difficulty('advanced'))}")
    
    # Export to JSON for external validation tools
    test_suite.export_to_json('code_generation_test_cases.json')
    print("Test cases exported to code_generation_test_cases.json")