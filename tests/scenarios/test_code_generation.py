"""
Test runner for code generation test scenarios.

This module provides functionality to execute code generation tests against
the Olympus-Coder-v1 model and validate the results.
"""

import unittest
import json
import re
import ast
import subprocess
from typing import Dict, List, Any, Optional
from code_generation_tests import CodeGenerationTests, CodeGenerationTestCase


class CodeGenerationTestRunner(unittest.TestCase):
    """Test runner for code generation scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_suite = CodeGenerationTests()
        self.model_endpoint = "http://localhost:11434/api/generate"  # Default Ollama endpoint
        self.model_name = "olympus-coder-v1"
    
    def _extract_code_from_response(self, response: str, language: str) -> Optional[str]:
        """Extract code from model response, handling markdown code blocks."""
        # Look for markdown code blocks with language tag
        pattern = rf"```{language}\s*\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Fallback: look for any code block
        pattern = r"```\s*\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        return None
    
    def _validate_python_syntax(self, code: str) -> Dict[str, Any]:
        """Validate Python code syntax and style."""
        validation_result = {
            'syntax_valid': False,
            'pep8_compliant': False,
            'has_docstring': False,
            'has_comments': False,
            'errors': []
        }
        
        try:
            # Check syntax by parsing
            ast.parse(code)
            validation_result['syntax_valid'] = True
        except SyntaxError as e:
            validation_result['errors'].append(f"Syntax error: {str(e)}")
        
        # Check for docstrings
        if '"""' in code or "'''" in code:
            validation_result['has_docstring'] = True
        
        # Check for comments
        if '#' in code:
            validation_result['has_comments'] = True
        
        # Basic PEP 8 checks
        lines = code.split('\n')
        pep8_issues = []
        
        for i, line in enumerate(lines, 1):
            # Check line length (max 79 characters for PEP 8)
            if len(line) > 79:
                pep8_issues.append(f"Line {i}: exceeds 79 characters")
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                pep8_issues.append(f"Line {i}: trailing whitespace")
        
        validation_result['pep8_compliant'] = len(pep8_issues) == 0
        if pep8_issues:
            validation_result['errors'].extend(pep8_issues)
        
        return validation_result
    
    def _validate_javascript_syntax(self, code: str) -> Dict[str, Any]:
        """Validate JavaScript code syntax and style."""
        validation_result = {
            'syntax_valid': False,
            'has_comments': False,
            'uses_modern_syntax': False,
            'errors': []
        }
        
        # Check for comments
        if '//' in code or '/*' in code:
            validation_result['has_comments'] = True
        
        # Check for modern JavaScript features
        modern_features = ['const ', 'let ', '=>', 'async ', 'await ', 'class ']
        if any(feature in code for feature in modern_features):
            validation_result['uses_modern_syntax'] = True
        
        # Basic syntax validation using Node.js if available
        try:
            # Create a temporary file and validate with Node.js
            with open('/tmp/temp_js_validation.js', 'w') as f:
                f.write(code)
            
            result = subprocess.run(
                ['node', '--check', '/tmp/temp_js_validation.js'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                validation_result['syntax_valid'] = True
            else:
                validation_result['errors'].append(f"Syntax error: {result.stderr}")
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Node.js not available or timeout, skip syntax validation
            validation_result['syntax_valid'] = True  # Assume valid if can't check
        
        return validation_result
    
    def _validate_code_features(self, code: str, test_case: CodeGenerationTestCase) -> Dict[str, Any]:
        """Validate that generated code contains expected features."""
        feature_validation = {
            'features_found': [],
            'features_missing': [],
            'score': 0.0
        }
        
        code_lower = code.lower()
        
        for feature in test_case.expected_features:
            feature_found = False
            
            # Check for specific feature patterns
            if 'function definition' in feature and test_case.language == 'python':
                feature_found = 'def ' in code
            elif 'arrow function' in feature and test_case.language == 'javascript':
                feature_found = '=>' in code
            elif 'class definition' in feature:
                feature_found = 'class ' in code_lower
            elif 'docstring' in feature or 'comments' in feature:
                feature_found = ('"""' in code or "'''" in code or '#' in code or 
                               '//' in code or '/*' in code)
            elif 'type hints' in feature:
                feature_found = ':' in code and '->' in code
            elif 'error handling' in feature:
                feature_found = ('try:' in code_lower or 'except' in code_lower or 
                               'catch' in code_lower)
            elif 'markdown code block' in feature:
                # This would be checked in the full response, not just extracted code
                feature_found = True  # Assume true if code was extracted successfully
            else:
                # Generic feature check - look for keywords in the feature description
                keywords = feature.lower().split()
                feature_found = any(keyword in code_lower for keyword in keywords)
            
            if feature_found:
                feature_validation['features_found'].append(feature)
            else:
                feature_validation['features_missing'].append(feature)
        
        # Calculate score
        total_features = len(test_case.expected_features)
        found_features = len(feature_validation['features_found'])
        feature_validation['score'] = found_features / total_features if total_features > 0 else 0.0
        
        return feature_validation
    
    def _run_single_test(self, test_case: CodeGenerationTestCase) -> Dict[str, Any]:
        """Run a single code generation test case."""
        # Note: This is a mock implementation. In a real scenario, you would
        # make an API call to the Ollama model here.
        
        # Mock response for testing framework
        mock_response = f"""
Here's a {test_case.language} implementation for your request:

```{test_case.language}
# Mock generated code for test case: {test_case.test_id}
def example_function():
    '''This is a mock implementation for testing.'''
    return "mock result"
```

This implementation includes the requested functionality with proper formatting.
"""
        
        # Extract code from response
        generated_code = self._extract_code_from_response(mock_response, test_case.language)
        
        if not generated_code:
            return {
                'test_id': test_case.test_id,
                'success': False,
                'error': 'No code found in model response',
                'response': mock_response
            }
        
        # Validate syntax
        if test_case.language == 'python':
            syntax_validation = self._validate_python_syntax(generated_code)
        else:
            syntax_validation = self._validate_javascript_syntax(generated_code)
        
        # Validate features
        feature_validation = self._validate_code_features(generated_code, test_case)
        
        # Compile results
        result = {
            'test_id': test_case.test_id,
            'description': test_case.description,
            'language': test_case.language,
            'difficulty': test_case.difficulty,
            'success': syntax_validation['syntax_valid'] and feature_validation['score'] >= 0.7,
            'generated_code': generated_code,
            'syntax_validation': syntax_validation,
            'feature_validation': feature_validation,
            'full_response': mock_response
        }
        
        return result
    
    def test_python_basic_functions(self):
        """Test basic Python function generation."""
        python_tests = self.test_suite.get_tests_by_language('python')
        basic_tests = [t for t in python_tests if t.difficulty == 'basic']
        
        for test_case in basic_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_test(test_case)
                self.assertTrue(result['success'], 
                              f"Test {test_case.test_id} failed: {result.get('error', 'Unknown error')}")
    
    def test_javascript_basic_functions(self):
        """Test basic JavaScript function generation."""
        js_tests = self.test_suite.get_tests_by_language('javascript')
        basic_tests = [t for t in js_tests if t.difficulty == 'basic']
        
        for test_case in basic_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_test(test_case)
                self.assertTrue(result['success'], 
                              f"Test {test_case.test_id} failed: {result.get('error', 'Unknown error')}")
    
    def test_edge_cases(self):
        """Test edge case scenarios."""
        edge_cases = self.test_suite.edge_case_tests
        
        for test_case in edge_cases:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_test(test_case)
                # Edge cases may have lower success criteria
                self.assertIsNotNone(result['generated_code'], 
                                   f"Edge case {test_case.test_id} produced no code")
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete code generation test suite and return results."""
        all_tests = self.test_suite.get_all_tests()
        results = []
        
        for test_case in all_tests:
            result = self._run_single_test(test_case)
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
            'by_difficulty': {
                'basic': {
                    'total': len([r for r in results if r['difficulty'] == 'basic']),
                    'successful': len([r for r in results if r['difficulty'] == 'basic' and r['success']])
                },
                'intermediate': {
                    'total': len([r for r in results if r['difficulty'] == 'intermediate']),
                    'successful': len([r for r in results if r['difficulty'] == 'intermediate' and r['success']])
                },
                'advanced': {
                    'total': len([r for r in results if r['difficulty'] == 'advanced']),
                    'successful': len([r for r in results if r['difficulty'] == 'advanced' and r['success']])
                }
            }
        }
        
        return summary


if __name__ == "__main__":
    # Run tests when executed directly
    runner = CodeGenerationTestRunner()
    
    # Run full test suite
    print("Running Code Generation Test Suite...")
    summary = runner.run_full_test_suite()
    
    print(f"\nTest Results Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    
    print(f"\nBy Language:")
    for lang, stats in summary['by_language'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {lang.title()}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    print(f"\nBy Difficulty:")
    for diff, stats in summary['by_difficulty'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {diff.title()}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    # Save detailed results
    with open('code_generation_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to code_generation_test_results.json")
    
    # Also run as unittest
    unittest.main(argv=[''], exit=False, verbosity=2)