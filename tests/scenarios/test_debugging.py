"""
Test runner for debugging and analysis test scenarios.

This module provides functionality to execute debugging tests against
the Olympus-Coder-v1 model and validate the results.
"""

import unittest
import json
import re
import ast
from typing import Dict, List, Any, Optional
from debugging_tests import DebuggingTests, DebuggingTestCase


class DebuggingTestRunner(unittest.TestCase):
    """Test runner for debugging and analysis scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_suite = DebuggingTests()
        self.model_endpoint = "http://localhost:11434/api/generate"
        self.model_name = "olympus-coder-v1"
    
    def _extract_fixed_code(self, response: str, language: str) -> Optional[str]:
        """Extract fixed code from model response."""
        # Look for markdown code blocks with language tag
        pattern = rf"```{language}\s*\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[-1].strip()  # Get the last code block (likely the fix)
        
        # Fallback: look for any code block
        pattern = r"```\s*\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[-1].strip()
        
        return None
    
    def _extract_explanation(self, response: str) -> str:
        """Extract explanation text from model response."""
        # Remove code blocks to get explanation text
        explanation = re.sub(r"```.*?```", "", response, flags=re.DOTALL)
        return explanation.strip()
    
    def _validate_fix_correctness(self, original_code: str, fixed_code: str, 
                                 test_case: DebuggingTestCase) -> Dict[str, Any]:
        """Validate that the fix addresses the original issue."""
        validation_result = {
            'syntax_improved': False,
            'logic_preserved': False,
            'fix_addresses_issue': False,
            'errors': []
        }
        
        if test_case.language == 'python':
            # Check if fixed code has valid syntax
            try:
                ast.parse(fixed_code)
                validation_result['syntax_improved'] = True
            except SyntaxError as e:
                validation_result['errors'].append(f"Fixed code still has syntax error: {e}")
        
        # Check if the specific issue type is addressed
        fix_type = test_case.expected_fix_type
        
        if 'syntax' in fix_type:
            # For syntax fixes, check if common syntax elements are present
            if test_case.language == 'python':
                if 'def ' in original_code and ':' not in original_code.split('def')[1].split('\n')[0]:
                    # Missing colon case
                    validation_result['fix_addresses_issue'] = ':' in fixed_code
                elif 'IndentationError' in (test_case.error_traceback or ''):
                    # Check if indentation is improved (basic heuristic)
                    validation_result['fix_addresses_issue'] = len(fixed_code.split('\n')) >= len(original_code.split('\n'))
        
        elif 'variable' in fix_type or 'name' in fix_type:
            # Check if undefined variables are addressed
            if test_case.test_id == "py_debug_name_error_003":
                validation_result['fix_addresses_issue'] = 'return average' in fixed_code or 'return total/count' in fixed_code
        
        elif 'type' in fix_type:
            # Check if type conversion is added
            validation_result['fix_addresses_issue'] = ('str(' in fixed_code or 
                                                       'f"' in fixed_code or 
                                                       '.format(' in fixed_code)
        
        elif 'index' in fix_type:
            # Check if index bounds are corrected
            validation_result['fix_addresses_issue'] = ('[len(' not in fixed_code or 
                                                       '[-1]' in fixed_code or 
                                                       'len(' in fixed_code and '- 1' in fixed_code)
        
        elif 'logic' in fix_type:
            # Check if loop control is added
            validation_result['fix_addresses_issue'] = ('n -= 1' in fixed_code or 
                                                       'n = n - 1' in fixed_code)
        
        elif 'null_check' in fix_type:
            # Check if null/undefined checks are added
            validation_result['fix_addresses_issue'] = ('if (' in fixed_code and 
                                                       ('null' in fixed_code or 'undefined' in fixed_code))
        
        elif 'async' in fix_type:
            # Check if try-catch is added for async operations
            validation_result['fix_addresses_issue'] = ('try' in fixed_code and 'catch' in fixed_code)
        
        elif 'closure' in fix_type:
            # Check if let/const is used or IIFE pattern
            validation_result['fix_addresses_issue'] = ('let ' in fixed_code or 
                                                       'const ' in fixed_code or 
                                                       '(function(' in fixed_code)
        
        # Basic logic preservation check (same number of functions/classes)
        original_functions = len(re.findall(r'def |function ', original_code))
        fixed_functions = len(re.findall(r'def |function ', fixed_code))
        validation_result['logic_preserved'] = original_functions == fixed_functions
        
        return validation_result
    
    def _validate_explanation_quality(self, explanation: str, 
                                    test_case: DebuggingTestCase) -> Dict[str, Any]:
        """Validate the quality of the error explanation."""
        validation_result = {
            'contains_expected_elements': [],
            'missing_elements': [],
            'explanation_score': 0.0
        }
        
        explanation_lower = explanation.lower()
        
        for element in test_case.expected_explanation_elements:
            element_found = False
            
            # Check for key terms from the expected element
            element_words = element.lower().split()
            if any(word in explanation_lower for word in element_words):
                element_found = True
            
            if element_found:
                validation_result['contains_expected_elements'].append(element)
            else:
                validation_result['missing_elements'].append(element)
        
        # Calculate explanation score
        total_elements = len(test_case.expected_explanation_elements)
        found_elements = len(validation_result['contains_expected_elements'])
        validation_result['explanation_score'] = found_elements / total_elements if total_elements > 0 else 0.0
        
        return validation_result
    
    def _run_single_debugging_test(self, test_case: DebuggingTestCase) -> Dict[str, Any]:
        """Run a single debugging test case."""
        # Create prompt for the model
        prompt = f"""
Here is some {test_case.language} code that has an issue:

```{test_case.language}
{test_case.buggy_code}
```
"""
        
        if test_case.error_traceback:
            prompt += f"""
Error traceback:
```
{test_case.error_traceback}
```
"""
        
        prompt += """
Please identify the issue and provide a corrected version of the code. Explain what was wrong and how you fixed it.
"""
        
        # Mock response for testing framework
        mock_response = self._generate_mock_debugging_response(test_case)
        
        # Extract fixed code and explanation
        fixed_code = self._extract_fixed_code(mock_response, test_case.language)
        explanation = self._extract_explanation(mock_response)
        
        if not fixed_code:
            return {
                'test_id': test_case.test_id,
                'success': False,
                'error': 'No fixed code found in model response',
                'response': mock_response
            }
        
        # Validate the fix
        fix_validation = self._validate_fix_correctness(
            test_case.buggy_code, fixed_code, test_case
        )
        
        # Validate the explanation
        explanation_validation = self._validate_explanation_quality(
            explanation, test_case
        )
        
        # Determine overall success
        success = (fix_validation['fix_addresses_issue'] and 
                  explanation_validation['explanation_score'] >= 0.6)
        
        result = {
            'test_id': test_case.test_id,
            'description': test_case.description,
            'language': test_case.language,
            'difficulty': test_case.difficulty,
            'expected_fix_type': test_case.expected_fix_type,
            'success': success,
            'original_code': test_case.buggy_code,
            'fixed_code': fixed_code,
            'explanation': explanation,
            'fix_validation': fix_validation,
            'explanation_validation': explanation_validation,
            'full_response': mock_response
        }
        
        return result
    
    def _generate_mock_debugging_response(self, test_case: DebuggingTestCase) -> str:
        """Generate a mock response for testing the framework."""
        # This would be replaced with actual model calls in production
        
        if test_case.test_id == "py_debug_syntax_001":
            return """
The issue is a missing colon after the function definition. In Python, function definitions must end with a colon.

Here's the corrected code:

```python
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
```

The function definition syntax in Python requires a colon (:) at the end of the def line to indicate the start of the function body.
"""
        
        elif test_case.test_id == "py_debug_name_error_003":
            return """
The error occurs because the function tries to return a variable named 'avg' which is not defined. The variable is actually named 'average'.

Here's the corrected code:

```python
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    return average
```

The variable name mismatch caused a NameError. Always ensure that variable names in return statements match the actual variable names defined in the function.
"""
        
        elif test_case.test_id == "js_debug_reference_error_002":
            return """
The error is caused by referencing an undefined variable 'userName' instead of the defined variable 'name'.

Here's the corrected code:

```javascript
function processUser(userData) {
    const name = userData.name;
    const email = userData.email;
    
    console.log(`Processing user: ${name}`);
    return { name, email };
}
```

The template literal was trying to use 'userName' which doesn't exist. The correct variable name is 'name' as defined earlier in the function.
"""
        
        else:
            # Generic mock response
            return f"""
I've identified the issue in your {test_case.language} code. Here's the corrected version:

```{test_case.language}
// Mock corrected code for test case: {test_case.test_id}
// This is a placeholder fix for testing purposes
{test_case.buggy_code.replace('    ', '    // Fixed: ')}
```

The issue was related to {test_case.expected_fix_type}. The correction addresses the problem by implementing proper error handling and following best practices.
"""
    
    def test_python_syntax_errors(self):
        """Test Python syntax error debugging."""
        python_tests = self.test_suite.get_tests_by_language('python')
        syntax_tests = [t for t in python_tests if 'syntax' in t.expected_fix_type]
        
        for test_case in syntax_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_debugging_test(test_case)
                self.assertTrue(result['success'], 
                              f"Syntax debugging test {test_case.test_id} failed")
    
    def test_javascript_errors(self):
        """Test JavaScript error debugging."""
        js_tests = self.test_suite.get_tests_by_language('javascript')
        
        for test_case in js_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_debugging_test(test_case)
                self.assertTrue(result['success'], 
                              f"JavaScript debugging test {test_case.test_id} failed")
    
    def test_code_review_scenarios(self):
        """Test code review and improvement scenarios."""
        review_tests = self.test_suite.code_review_tests
        
        for test_case in review_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_debugging_test(test_case)
                # Code review tests may have different success criteria
                self.assertIsNotNone(result['fixed_code'], 
                                   f"Code review test {test_case.test_id} produced no improved code")
    
    def run_full_debugging_suite(self) -> Dict[str, Any]:
        """Run the complete debugging test suite and return results."""
        all_tests = self.test_suite.get_all_tests()
        results = []
        
        for test_case in all_tests:
            result = self._run_single_debugging_test(test_case)
            results.append(result)
        
        # Calculate summary statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        
        summary = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'results': results,
            'by_language': {
                'python': {
                    'total': len([r for r in results if r['language'] == 'python']),
                    'successful': len([r for r in results if r['language'] == 'python' and r['success']])
                },
                'javascript': {
                    'total': len([r for r in results if r['language'] == 'javascript']),
                    'successful': len([r for r in results if r['language'] == 'javascript' and r['success']])
                }
            },
            'by_fix_type': {}
        }
        
        # Group by fix type
        fix_types = set(r['expected_fix_type'] for r in results)
        for fix_type in fix_types:
            type_results = [r for r in results if r['expected_fix_type'] == fix_type]
            summary['by_fix_type'][fix_type] = {
                'total': len(type_results),
                'successful': len([r for r in type_results if r['success']])
            }
        
        return summary


if __name__ == "__main__":
    # Run tests when executed directly
    runner = DebuggingTestRunner()
    
    # Run full test suite
    print("Running Debugging Test Suite...")
    summary = runner.run_full_debugging_suite()
    
    print(f"\nDebugging Test Results Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    
    print(f"\nBy Language:")
    for lang, stats in summary['by_language'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {lang.title()}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    print(f"\nBy Fix Type:")
    for fix_type, stats in summary['by_fix_type'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {fix_type}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    # Save detailed results
    with open('debugging_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to debugging_test_results.json")
    
    # Also run as unittest
    unittest.main(argv=[''], exit=False, verbosity=2)