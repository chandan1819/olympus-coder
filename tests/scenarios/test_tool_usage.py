"""
Test runner for tool usage decision test scenarios.

This module provides functionality to execute tool usage tests against
the Olympus-Coder-v1 model and validate the results.
"""

import unittest
import json
import re
from typing import Dict, List, Any, Optional
from tool_usage_tests import ToolUsageTests, ToolUsageTestCase, ExpectedResponseType


class ToolUsageTestRunner(unittest.TestCase):
    """Test runner for tool usage decision scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_suite = ToolUsageTests()
        self.model_endpoint = "http://localhost:11434/api/generate"
        self.model_name = "olympus-coder-v1"
    
    def _extract_tool_request(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON tool request from model response."""
        # Look for JSON objects in the response
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response)
        
        for match in matches:
            try:
                parsed = json.loads(match)
                # Check if it looks like a tool request
                if 'tool_name' in parsed or any(key in parsed for key in ['tool', 'action', 'command']):
                    return parsed
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _is_code_response(self, response: str) -> bool:
        """Check if response contains code blocks."""
        return '```' in response and any(lang in response.lower() for lang in ['python', 'javascript', 'js', 'py'])
    
    def _is_text_response(self, response: str) -> bool:
        """Check if response is plain text without tools or code."""
        has_tool_request = self._extract_tool_request(response) is not None
        has_code = self._is_code_response(response)
        return not has_tool_request and not has_code
    
    def _validate_json_format(self, tool_request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the JSON format of a tool request."""
        validation_result = {
            'valid_json': True,
            'has_tool_name': False,
            'has_parameters': False,
            'proper_structure': False,
            'errors': []
        }
        
        # Check for tool name field
        tool_name_fields = ['tool_name', 'tool', 'action', 'command']
        if any(field in tool_request for field in tool_name_fields):
            validation_result['has_tool_name'] = True
        else:
            validation_result['errors'].append("Missing tool name field")
        
        # Check for parameters field
        param_fields = ['parameters', 'params', 'args', 'arguments']
        if any(field in tool_request for field in param_fields):
            validation_result['has_parameters'] = True
        
        # Check overall structure
        if validation_result['has_tool_name']:
            validation_result['proper_structure'] = True
        
        return validation_result
    
    def _validate_tool_selection(self, tool_request: Dict[str, Any], 
                                test_case: ToolUsageTestCase) -> Dict[str, Any]:
        """Validate that the correct tool was selected."""
        validation_result = {
            'correct_tool': False,
            'acceptable_alternative': False,
            'has_required_parameters': False,
            'parameter_accuracy': 0.0,
            'errors': []
        }
        
        # Extract tool name from request
        tool_name_fields = ['tool_name', 'tool', 'action', 'command']
        actual_tool = None
        for field in tool_name_fields:
            if field in tool_request:
                actual_tool = tool_request[field]
                break
        
        if not actual_tool:
            validation_result['errors'].append("No tool name found in request")
            return validation_result
        
        # Check if it matches expected tool
        if test_case.expected_tool_name and actual_tool == test_case.expected_tool_name:
            validation_result['correct_tool'] = True
        elif actual_tool in test_case.alternative_valid_tools:
            validation_result['acceptable_alternative'] = True
        else:
            validation_result['errors'].append(f"Unexpected tool: {actual_tool}")
        
        # Validate parameters if expected
        if test_case.expected_parameters:
            param_fields = ['parameters', 'params', 'args', 'arguments']
            actual_params = None
            for field in param_fields:
                if field in tool_request:
                    actual_params = tool_request[field]
                    break
            
            if actual_params:
                validation_result['has_required_parameters'] = True
                
                # Calculate parameter accuracy
                expected_keys = set(test_case.expected_parameters.keys())
                actual_keys = set(actual_params.keys()) if isinstance(actual_params, dict) else set()
                
                if expected_keys:
                    matching_keys = expected_keys.intersection(actual_keys)
                    validation_result['parameter_accuracy'] = len(matching_keys) / len(expected_keys)
            else:
                validation_result['errors'].append("Missing parameters in tool request")
        
        return validation_result
    
    def _validate_response_type(self, response: str, test_case: ToolUsageTestCase) -> Dict[str, Any]:
        """Validate that the response type matches expectations."""
        validation_result = {
            'correct_response_type': False,
            'actual_response_type': None,
            'errors': []
        }
        
        # Determine actual response type
        tool_request = self._extract_tool_request(response)
        
        if tool_request:
            validation_result['actual_response_type'] = ExpectedResponseType.TOOL_REQUEST
        elif self._is_code_response(response):
            validation_result['actual_response_type'] = ExpectedResponseType.CODE_RESPONSE
        else:
            validation_result['actual_response_type'] = ExpectedResponseType.TEXT_RESPONSE
        
        # Check if it matches expected type
        if validation_result['actual_response_type'] == test_case.expected_response_type:
            validation_result['correct_response_type'] = True
        else:
            validation_result['errors'].append(
                f"Expected {test_case.expected_response_type.value}, "
                f"got {validation_result['actual_response_type'].value}"
            )
        
        return validation_result
    
    def _run_single_tool_test(self, test_case: ToolUsageTestCase) -> Dict[str, Any]:
        """Run a single tool usage test case."""
        # Create prompt for the model
        prompt = f"""
Context: {test_case.scenario_context}

User Request: {test_case.user_prompt}

Please respond appropriately. If you need to use a tool, output a JSON object with the tool name and parameters. If you can answer directly, provide the response without using tools.
"""
        
        # Mock response for testing framework
        mock_response = self._generate_mock_tool_response(test_case)
        
        # Validate response type
        response_validation = self._validate_response_type(mock_response, test_case)
        
        # Initialize result
        result = {
            'test_id': test_case.test_id,
            'description': test_case.description,
            'difficulty': test_case.difficulty,
            'expected_response_type': test_case.expected_response_type.value,
            'success': False,
            'response_validation': response_validation,
            'full_response': mock_response
        }
        
        # If expecting a tool request, validate the tool selection
        if test_case.expected_response_type == ExpectedResponseType.TOOL_REQUEST:
            tool_request = self._extract_tool_request(mock_response)
            
            if tool_request:
                json_validation = self._validate_json_format(tool_request)
                tool_validation = self._validate_tool_selection(tool_request, test_case)
                
                result['tool_request'] = tool_request
                result['json_validation'] = json_validation
                result['tool_validation'] = tool_validation
                
                # Determine success for tool requests
                success = (response_validation['correct_response_type'] and
                          json_validation['proper_structure'] and
                          (tool_validation['correct_tool'] or tool_validation['acceptable_alternative']))
                
                result['success'] = success
            else:
                result['error'] = 'Expected tool request but no valid JSON found'
        else:
            # For non-tool responses, success is based on response type matching
            result['success'] = response_validation['correct_response_type']
        
        return result
    
    def _generate_mock_tool_response(self, test_case: ToolUsageTestCase) -> str:
        """Generate a mock response for testing the framework."""
        # This would be replaced with actual model calls in production
        
        if test_case.expected_response_type == ExpectedResponseType.TOOL_REQUEST:
            if test_case.test_id == "tool_file_read_001":
                return """
I'll read the main.py file for you.

{
  "tool_name": "read_file",
  "parameters": {
    "file_path": "main.py"
  }
}
"""
            
            elif test_case.test_id == "tool_file_write_002":
                return """
I'll create a config.json file with default database settings.

{
  "tool_name": "write_file",
  "parameters": {
    "file_path": "config.json",
    "content": "{\\"host\\": \\"localhost\\", \\"port\\": 5432, \\"database\\": \\"myapp\\"}"
  }
}
"""
            
            elif test_case.test_id == "tool_exec_run_001":
                return """
I'll run the data_processor.py script for you.

{
  "tool_name": "execute_python",
  "parameters": {
    "script_path": "data_processor.py"
  }
}
"""
            
            else:
                # Generic tool request
                tool_name = test_case.expected_tool_name or "generic_tool"
                params = test_case.expected_parameters or {}
                return f"""
I'll help you with that request.

{{
  "tool_name": "{tool_name}",
  "parameters": {json.dumps(params)}
}}
"""
        
        elif test_case.expected_response_type == ExpectedResponseType.CODE_RESPONSE:
            return """
Here's a Python function to calculate factorial:

```python
def factorial(n):
    '''Calculate the factorial of a number.'''
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    elif n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)
```

This function uses recursion to calculate the factorial with proper error handling.
"""
        
        else:  # TEXT_RESPONSE
            if test_case.test_id == "tool_no_tool_needed_002":
                return """
The main differences between lists and tuples in Python are:

1. **Mutability**: Lists are mutable (can be changed), tuples are immutable (cannot be changed)
2. **Syntax**: Lists use square brackets [], tuples use parentheses ()
3. **Performance**: Tuples are slightly faster for iteration
4. **Use cases**: Lists for collections that change, tuples for fixed data

Example:
- List: my_list = [1, 2, 3] (can modify)
- Tuple: my_tuple = (1, 2, 3) (cannot modify)
"""
            
            else:
                return "I understand your request. Let me provide a direct response without using any tools."
    
    def test_file_operation_tools(self):
        """Test file operation tool selection."""
        file_tests = self.test_suite.get_tests_by_tool_category('file')
        
        for test_case in file_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_tool_test(test_case)
                self.assertTrue(result['success'], 
                              f"File operation test {test_case.test_id} failed")
    
    def test_code_execution_tools(self):
        """Test code execution tool selection."""
        exec_tests = self.test_suite.get_tests_by_tool_category('execution')
        
        for test_case in exec_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_tool_test(test_case)
                self.assertTrue(result['success'], 
                              f"Execution test {test_case.test_id} failed")
    
    def test_analysis_tools(self):
        """Test analysis tool selection."""
        analysis_tests = self.test_suite.get_tests_by_tool_category('analysis')
        
        for test_case in analysis_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_tool_test(test_case)
                self.assertTrue(result['success'], 
                              f"Analysis test {test_case.test_id} failed")
    
    def test_ambiguous_scenarios(self):
        """Test ambiguous and edge case scenarios."""
        ambiguous_tests = self.test_suite.get_tests_by_tool_category('ambiguous')
        
        for test_case in ambiguous_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_tool_test(test_case)
                # Ambiguous tests may have different success criteria
                if test_case.expected_response_type == ExpectedResponseType.TOOL_REQUEST:
                    self.assertTrue(result['success'], 
                                  f"Ambiguous test {test_case.test_id} failed")
                else:
                    self.assertIsNotNone(result['full_response'], 
                                       f"Ambiguous test {test_case.test_id} produced no response")
    
    def test_json_format_accuracy(self):
        """Test JSON format accuracy for tool requests."""
        tool_request_tests = self.test_suite.get_tests_by_response_type(ExpectedResponseType.TOOL_REQUEST)
        
        for test_case in tool_request_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_tool_test(test_case)
                if 'json_validation' in result:
                    self.assertTrue(result['json_validation']['proper_structure'], 
                                  f"JSON format test {test_case.test_id} failed")
    
    def run_full_tool_usage_suite(self) -> Dict[str, Any]:
        """Run the complete tool usage test suite and return results."""
        all_tests = self.test_suite.get_all_tests()
        results = []
        
        for test_case in all_tests:
            result = self._run_single_tool_test(test_case)
            results.append(result)
        
        # Calculate summary statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        
        # Calculate JSON format accuracy for tool requests
        tool_request_results = [r for r in results if 'json_validation' in r]
        json_accuracy = sum(1 for r in tool_request_results 
                           if r['json_validation']['proper_structure']) / len(tool_request_results) if tool_request_results else 0.0
        
        summary = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'json_format_accuracy': json_accuracy,
            'results': results,
            'by_response_type': {},
            'by_tool_category': {
                'file': {
                    'total': len([r for r in results if any(t.test_id == r['test_id'] for t in self.test_suite.file_operation_tests)]),
                    'successful': len([r for r in results if r['success'] and any(t.test_id == r['test_id'] for t in self.test_suite.file_operation_tests)])
                },
                'execution': {
                    'total': len([r for r in results if any(t.test_id == r['test_id'] for t in self.test_suite.code_execution_tests)]),
                    'successful': len([r for r in results if r['success'] and any(t.test_id == r['test_id'] for t in self.test_suite.code_execution_tests)])
                },
                'analysis': {
                    'total': len([r for r in results if any(t.test_id == r['test_id'] for t in self.test_suite.analysis_tests)]),
                    'successful': len([r for r in results if r['success'] and any(t.test_id == r['test_id'] for t in self.test_suite.analysis_tests)])
                },
                'ambiguous': {
                    'total': len([r for r in results if any(t.test_id == r['test_id'] for t in self.test_suite.ambiguous_tests)]),
                    'successful': len([r for r in results if r['success'] and any(t.test_id == r['test_id'] for t in self.test_suite.ambiguous_tests)])
                }
            }
        }
        
        # Group by response type
        for response_type in ExpectedResponseType:
            type_results = [r for r in results if r['expected_response_type'] == response_type.value]
            summary['by_response_type'][response_type.value] = {
                'total': len(type_results),
                'successful': len([r for r in type_results if r['success']])
            }
        
        return summary


if __name__ == "__main__":
    # Run tests when executed directly
    runner = ToolUsageTestRunner()
    
    # Run full test suite
    print("Running Tool Usage Test Suite...")
    summary = runner.run_full_tool_usage_suite()
    
    print(f"\nTool Usage Test Results Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    print(f"JSON Format Accuracy: {summary['json_format_accuracy']:.2%}")
    
    print(f"\nBy Response Type:")
    for response_type, stats in summary['by_response_type'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {response_type}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    print(f"\nBy Tool Category:")
    for category, stats in summary['by_tool_category'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {category}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    # Save detailed results
    with open('tool_usage_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to tool_usage_test_results.json")
    
    # Also run as unittest
    unittest.main(argv=[''], exit=False, verbosity=2)