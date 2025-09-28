"""
Debugging and Analysis Test Cases for Olympus-Coder-v1

This module contains test scenarios for evaluating the model's ability to identify
and fix errors in code according to requirements 2.1, 2.2, and 2.3.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class DebuggingTestCase:
    """Represents a single debugging test scenario."""
    test_id: str
    description: str
    language: str
    buggy_code: str
    error_traceback: Optional[str]
    expected_fix_type: str
    expected_explanation_elements: List[str]
    validation_criteria: List[str]
    difficulty: str


class DebuggingTests:
    """Collection of debugging and analysis test scenarios."""
    
    def __init__(self):
        self.python_debugging_tests = self._create_python_debugging_tests()
        self.javascript_debugging_tests = self._create_javascript_debugging_tests()
        self.code_review_tests = self._create_code_review_tests()
    
    def _create_python_debugging_tests(self) -> List[DebuggingTestCase]:
        """Create Python debugging test cases with common errors."""
        return [
            DebuggingTestCase(
                test_id="py_debug_syntax_001",
                description="Fix Python syntax error - missing colon",
                language="python",
                buggy_code="""def calculate_sum(numbers)
    total = 0
    for num in numbers:
        total += num
    return total""",
                error_traceback="""  File "example.py", line 1
    def calculate_sum(numbers)
                              ^
SyntaxError: invalid syntax""",
                expected_fix_type="syntax_fix",
                expected_explanation_elements=[
                    "missing colon after function definition",
                    "function definition syntax",
                    "corrected code snippet"
                ],
                validation_criteria=[
                    "identifies missing colon",
                    "provides corrected code",
                    "explains the syntax rule",
                    "maintains original functionality"
                ],
                difficulty="basic"
            ),
            
            DebuggingTestCase(
                test_id="py_debug_indentation_002",
                description="Fix Python indentation error",
                language="python",
                buggy_code="""def process_data(items):
    result = []
    for item in items:
    if item > 0:
        result.append(item * 2)
    return result""",
                error_traceback="""  File "example.py", line 4
    if item > 0:
    ^
IndentationError: expected an indented block""",
                expected_fix_type="indentation_fix",
                expected_explanation_elements=[
                    "indentation error",
                    "Python indentation rules",
                    "proper code structure"
                ],
                validation_criteria=[
                    "identifies indentation issue",
                    "provides properly indented code",
                    "explains Python indentation requirements",
                    "preserves logic flow"
                ],
                difficulty="basic"
            ),
            
            DebuggingTestCase(
                test_id="py_debug_name_error_003",
                description="Fix Python NameError - undefined variable",
                language="python",
                buggy_code="""def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return avg""",
                error_traceback="""Traceback (most recent call last):
  File "example.py", line 5, in calculate_average
    return avg
NameError: name 'avg' is not defined""",
                expected_fix_type="variable_fix",
                expected_explanation_elements=[
                    "undefined variable",
                    "variable name mismatch",
                    "return statement correction"
                ],
                validation_criteria=[
                    "identifies undefined variable",
                    "corrects variable name",
                    "explains the naming issue",
                    "maintains function logic"
                ],
                difficulty="basic"
            ),
            
            DebuggingTestCase(
                test_id="py_debug_type_error_004",
                description="Fix Python TypeError - string concatenation with integer",
                language="python",
                buggy_code="""def format_message(name, age):
    message = "Hello " + name + ", you are " + age + " years old."
    return message""",
                error_traceback="""Traceback (most recent call last):
  File "example.py", line 2, in format_message
    message = "Hello " + name + ", you are " + age + " years old."
TypeError: can only concatenate str (not "int") to str""",
                expected_fix_type="type_conversion_fix",
                expected_explanation_elements=[
                    "type mismatch error",
                    "string concatenation rules",
                    "type conversion solution"
                ],
                validation_criteria=[
                    "identifies type mismatch",
                    "provides type conversion solution",
                    "explains string concatenation rules",
                    "offers alternative formatting methods"
                ],
                difficulty="intermediate"
            ),
            
            DebuggingTestCase(
                test_id="py_debug_index_error_005",
                description="Fix Python IndexError - list index out of range",
                language="python",
                buggy_code="""def get_first_and_last(items):
    first = items[0]
    last = items[len(items)]
    return first, last""",
                error_traceback="""Traceback (most recent call last):
  File "example.py", line 3, in get_first_and_last
    last = items[len(items)]
IndexError: list index out of range""",
                expected_fix_type="index_bounds_fix",
                expected_explanation_elements=[
                    "index out of range",
                    "zero-based indexing",
                    "proper last element access"
                ],
                validation_criteria=[
                    "identifies index error",
                    "corrects index calculation",
                    "explains zero-based indexing",
                    "adds bounds checking if appropriate"
                ],
                difficulty="intermediate"
            ),
            
            DebuggingTestCase(
                test_id="py_debug_logic_error_006",
                description="Fix Python logic error - infinite loop",
                language="python",
                buggy_code="""def countdown(n):
    while n > 0:
        print(n)
        # Missing decrement
    print("Done!")""",
                error_traceback=None,  # Logic errors don't always have tracebacks
                expected_fix_type="logic_fix",
                expected_explanation_elements=[
                    "infinite loop",
                    "missing loop variable update",
                    "loop termination condition"
                ],
                validation_criteria=[
                    "identifies infinite loop",
                    "adds missing decrement",
                    "explains loop control",
                    "ensures proper termination"
                ],
                difficulty="intermediate"
            )
        ]
    
    def _create_javascript_debugging_tests(self) -> List[DebuggingTestCase]:
        """Create JavaScript debugging test cases with common errors."""
        return [
            DebuggingTestCase(
                test_id="js_debug_syntax_001",
                description="Fix JavaScript syntax error - missing bracket",
                language="javascript",
                buggy_code="""function calculateTotal(prices) {
    let total = 0;
    for (let price of prices) {
        total += price;
    }
    return total;
""",
                error_traceback="""SyntaxError: Unexpected end of input""",
                expected_fix_type="syntax_fix",
                expected_explanation_elements=[
                    "missing closing bracket",
                    "function syntax",
                    "bracket matching"
                ],
                validation_criteria=[
                    "identifies missing bracket",
                    "provides corrected code",
                    "explains bracket matching",
                    "maintains function structure"
                ],
                difficulty="basic"
            ),
            
            DebuggingTestCase(
                test_id="js_debug_reference_error_002",
                description="Fix JavaScript ReferenceError - undefined variable",
                language="javascript",
                buggy_code="""function processUser(userData) {
    const name = userData.name;
    const email = userData.email;
    
    console.log(`Processing user: ${userName}`);
    return { name, email };
}""",
                error_traceback="""ReferenceError: userName is not defined
    at processUser (example.js:5:37)""",
                expected_fix_type="variable_reference_fix",
                expected_explanation_elements=[
                    "undefined variable reference",
                    "variable name mismatch",
                    "template literal correction"
                ],
                validation_criteria=[
                    "identifies undefined variable",
                    "corrects variable reference",
                    "explains variable scoping",
                    "maintains template literal syntax"
                ],
                difficulty="basic"
            ),
            
            DebuggingTestCase(
                test_id="js_debug_type_error_003",
                description="Fix JavaScript TypeError - calling method on null",
                language="javascript",
                buggy_code="""function getStringLength(input) {
    return input.length;
}

// Usage that causes error
const result = getStringLength(null);""",
                error_traceback="""TypeError: Cannot read property 'length' of null
    at getStringLength (example.js:2:17)""",
                expected_fix_type="null_check_fix",
                expected_explanation_elements=[
                    "null reference error",
                    "defensive programming",
                    "input validation"
                ],
                validation_criteria=[
                    "identifies null reference issue",
                    "adds null/undefined checks",
                    "explains defensive programming",
                    "provides graceful error handling"
                ],
                difficulty="intermediate"
            ),
            
            DebuggingTestCase(
                test_id="js_debug_async_error_004",
                description="Fix JavaScript async/await error handling",
                language="javascript",
                buggy_code="""async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    const userData = await response.json();
    return userData;
}""",
                error_traceback="""UnhandledPromiseRejectionWarning: SyntaxError: Unexpected token < in JSON at position 0""",
                expected_fix_type="async_error_handling_fix",
                expected_explanation_elements=[
                    "unhandled promise rejection",
                    "HTTP response validation",
                    "async error handling patterns"
                ],
                validation_criteria=[
                    "identifies missing error handling",
                    "adds try-catch blocks",
                    "validates HTTP responses",
                    "explains async error patterns"
                ],
                difficulty="advanced"
            ),
            
            DebuggingTestCase(
                test_id="js_debug_closure_error_005",
                description="Fix JavaScript closure variable capture issue",
                language="javascript",
                buggy_code="""function createCounters() {
    const counters = [];
    for (var i = 0; i < 3; i++) {
        counters.push(function() {
            return i;
        });
    }
    return counters;
}

// All counters return 3 instead of 0, 1, 2""",
                error_traceback=None,  # Logic error, no exception
                expected_fix_type="closure_fix",
                expected_explanation_elements=[
                    "closure variable capture",
                    "var vs let scoping",
                    "loop variable binding"
                ],
                validation_criteria=[
                    "identifies closure issue",
                    "explains variable scoping",
                    "provides let/const solution or IIFE",
                    "demonstrates correct behavior"
                ],
                difficulty="advanced"
            )
        ]
    
    def _create_code_review_tests(self) -> List[DebuggingTestCase]:
        """Create code review and improvement test cases."""
        return [
            DebuggingTestCase(
                test_id="review_performance_001",
                description="Identify and fix performance issues in code",
                language="python",
                buggy_code="""def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates""",
                error_traceback=None,
                expected_fix_type="performance_optimization",
                expected_explanation_elements=[
                    "O(n²) time complexity",
                    "inefficient nested loops",
                    "better algorithm suggestion"
                ],
                validation_criteria=[
                    "identifies performance issue",
                    "suggests more efficient algorithm",
                    "explains time complexity",
                    "provides optimized implementation"
                ],
                difficulty="intermediate"
            ),
            
            DebuggingTestCase(
                test_id="review_security_002",
                description="Identify security vulnerability in code",
                language="javascript",
                buggy_code="""function executeUserCommand(command) {
    // Dangerous: directly executing user input
    return eval(command);
}""",
                error_traceback=None,
                expected_fix_type="security_fix",
                expected_explanation_elements=[
                    "code injection vulnerability",
                    "eval() security risks",
                    "safer alternatives"
                ],
                validation_criteria=[
                    "identifies security vulnerability",
                    "explains eval() risks",
                    "suggests safer alternatives",
                    "provides secure implementation"
                ],
                difficulty="advanced"
            ),
            
            DebuggingTestCase(
                test_id="review_maintainability_003",
                description="Improve code maintainability and readability",
                language="python",
                buggy_code="""def p(d):
    r = []
    for i in d:
        if i['s'] > 1000 and i['a'] and len(i['n']) > 0:
            r.append({'n': i['n'], 't': i['s'] * 0.1})
    return r""",
                error_traceback=None,
                expected_fix_type="readability_improvement",
                expected_explanation_elements=[
                    "unclear variable names",
                    "magic numbers",
                    "code documentation needs"
                ],
                validation_criteria=[
                    "identifies readability issues",
                    "suggests descriptive names",
                    "explains magic numbers",
                    "adds documentation"
                ],
                difficulty="intermediate"
            ),
            
            DebuggingTestCase(
                test_id="review_error_handling_004",
                description="Improve error handling in code",
                language="javascript",
                buggy_code="""function parseJsonData(jsonString) {
    const data = JSON.parse(jsonString);
    return data.results.map(item => item.value);
}""",
                error_traceback=None,
                expected_fix_type="error_handling_improvement",
                expected_explanation_elements=[
                    "missing error handling",
                    "potential null reference",
                    "graceful failure patterns"
                ],
                validation_criteria=[
                    "identifies missing error handling",
                    "adds appropriate try-catch",
                    "handles null/undefined cases",
                    "explains error handling best practices"
                ],
                difficulty="intermediate"
            )
        ]
    
    def get_all_tests(self) -> List[DebuggingTestCase]:
        """Return all debugging test cases."""
        return (self.python_debugging_tests + 
                self.javascript_debugging_tests + 
                self.code_review_tests)
    
    def get_tests_by_language(self, language: str) -> List[DebuggingTestCase]:
        """Return test cases for a specific language."""
        all_tests = self.get_all_tests()
        return [test for test in all_tests if test.language.lower() == language.lower()]
    
    def get_tests_by_type(self, fix_type: str) -> List[DebuggingTestCase]:
        """Return test cases for a specific fix type."""
        all_tests = self.get_all_tests()
        return [test for test in all_tests if fix_type.lower() in test.expected_fix_type.lower()]
    
    def get_tests_by_difficulty(self, difficulty: str) -> List[DebuggingTestCase]:
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
                'buggy_code': test.buggy_code,
                'error_traceback': test.error_traceback,
                'expected_fix_type': test.expected_fix_type,
                'expected_explanation_elements': test.expected_explanation_elements,
                'validation_criteria': test.validation_criteria,
                'difficulty': test.difficulty
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage and basic validation
    test_suite = DebuggingTests()
    
    print(f"Total debugging test cases: {len(test_suite.get_all_tests())}")
    print(f"Python debugging tests: {len(test_suite.get_tests_by_language('python'))}")
    print(f"JavaScript debugging tests: {len(test_suite.get_tests_by_language('javascript'))}")
    print(f"Basic difficulty: {len(test_suite.get_tests_by_difficulty('basic'))}")
    print(f"Intermediate difficulty: {len(test_suite.get_tests_by_difficulty('intermediate'))}")
    print(f"Advanced difficulty: {len(test_suite.get_tests_by_difficulty('advanced'))}")
    
    # Export to JSON for external validation tools
    test_suite.export_to_json('debugging_test_cases.json')
    print("Debugging test cases exported to debugging_test_cases.json")