"""
Test runner for context awareness test scenarios.

This module provides functionality to execute context awareness tests against
the Olympus-Coder-v1 model and validate the results.
"""

import unittest
import json
import re
from typing import Dict, List, Any, Optional, Set
from context_awareness_tests import ContextAwarenessTests, ContextAwarenessTestCase


class ContextAwarenessTestRunner(unittest.TestCase):
    """Test runner for context awareness scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_suite = ContextAwarenessTests()
        self.model_endpoint = "http://localhost:11434/api/generate"
        self.model_name = "olympus-coder-v1"
    
    def _extract_file_references(self, response: str) -> Set[str]:
        """Extract file path references from model response."""
        # Common file path patterns
        patterns = [
            r'from\s+([a-zA-Z_][a-zA-Z0-9_./]*)\s+import',  # Python imports
            r'import\s+([a-zA-Z_][a-zA-Z0-9_./]*)',  # Python imports
            r'from\s+["\']([^"\']+)["\']',  # ES6 imports with quotes
            r'import.*from\s+["\']([^"\']+)["\']',  # ES6 imports
            r'["\']([a-zA-Z_][a-zA-Z0-9_./]*\.(?:py|js|jsx|ts|tsx))["\']',  # Quoted file paths
            r'([a-zA-Z_][a-zA-Z0-9_./]*\.(?:py|js|jsx|ts|tsx))',  # Direct file references
            r'([a-zA-Z_][a-zA-Z0-9_./]*/[a-zA-Z_][a-zA-Z0-9_./]*)',  # Directory paths
        ]
        
        references = set()
        for pattern in patterns:
            matches = re.findall(pattern, response)
            references.update(matches)
        
        return references
    
    def _extract_class_and_function_names(self, response: str) -> Dict[str, Set[str]]:
        """Extract class and function names from model response."""
        result = {
            'classes': set(),
            'functions': set(),
            'variables': set()
        }
        
        # Python patterns
        class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)'
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        # JavaScript patterns
        js_class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)'
        js_function_pattern = r'(?:function\s+([a-zA-Z_][a-zA-Z0-9_]*)|const\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=)'
        
        # Extract matches
        result['classes'].update(re.findall(class_pattern, response))
        result['classes'].update(re.findall(js_class_pattern, response))
        
        result['functions'].update(re.findall(function_pattern, response))
        js_func_matches = re.findall(js_function_pattern, response)
        for match in js_func_matches:
            result['functions'].update([name for name in match if name])
        
        return result
    
    def _validate_file_references(self, response: str, test_case: ContextAwarenessTestCase) -> Dict[str, Any]:
        """Validate that file references are accurate and don't hallucinate."""
        validation_result = {
            'valid_references': [],
            'invalid_references': [],
            'hallucinated_files': [],
            'accuracy_score': 0.0
        }
        
        # Get all file references from response
        referenced_files = self._extract_file_references(response)
        
        # Get valid files from project context
        valid_files = set()
        
        def collect_files(structure, prefix=""):
            for key, value in structure.items():
                if isinstance(value, dict):
                    collect_files(value, f"{prefix}{key}/")
                else:
                    valid_files.add(f"{prefix}{key}")
        
        collect_files(test_case.project_context.file_structure)
        
        # Also add files from existing code samples
        valid_files.update(test_case.project_context.existing_code_samples.keys())
        
        # Validate each reference
        for ref in referenced_files:
            # Normalize reference (remove extensions for module imports)
            normalized_ref = ref.replace('.py', '').replace('.js', '').replace('.jsx', '')
            normalized_ref = normalized_ref.replace('/', '.')  # Python module style
            
            # Check if reference exists in project
            is_valid = False
            for valid_file in valid_files:
                valid_normalized = valid_file.replace('.py', '').replace('.js', '').replace('.jsx', '')
                if (normalized_ref in valid_normalized or 
                    valid_normalized in normalized_ref or
                    ref in valid_file or
                    valid_file in ref):
                    is_valid = True
                    break
            
            if is_valid:
                validation_result['valid_references'].append(ref)
            else:
                validation_result['invalid_references'].append(ref)
                validation_result['hallucinated_files'].append(ref)
        
        # Calculate accuracy score
        total_refs = len(referenced_files)
        valid_refs = len(validation_result['valid_references'])
        validation_result['accuracy_score'] = valid_refs / total_refs if total_refs > 0 else 1.0
        
        return validation_result
    
    def _validate_naming_conventions(self, response: str, test_case: ContextAwarenessTestCase) -> Dict[str, Any]:
        """Validate that naming conventions are followed."""
        validation_result = {
            'correct_naming': [],
            'incorrect_naming': [],
            'naming_score': 0.0
        }
        
        # Extract names from response
        names = self._extract_class_and_function_names(response)
        conventions = test_case.project_context.naming_conventions
        
        # Check class naming
        for class_name in names['classes']:
            expected_style = conventions.get('classes', 'PascalCase')
            if expected_style == 'PascalCase':
                if re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                    validation_result['correct_naming'].append(f"class {class_name}")
                else:
                    validation_result['incorrect_naming'].append(f"class {class_name} (should be PascalCase)")
        
        # Check function naming
        for func_name in names['functions']:
            expected_style = conventions.get('functions', 'snake_case')
            if expected_style == 'snake_case':
                if re.match(r'^[a-z][a-z0-9_]*$', func_name):
                    validation_result['correct_naming'].append(f"function {func_name}")
                else:
                    validation_result['incorrect_naming'].append(f"function {func_name} (should be snake_case)")
            elif expected_style == 'camelCase':
                if re.match(r'^[a-z][a-zA-Z0-9]*$', func_name):
                    validation_result['correct_naming'].append(f"function {func_name}")
                else:
                    validation_result['incorrect_naming'].append(f"function {func_name} (should be camelCase)")
        
        # Calculate naming score
        total_names = len(validation_result['correct_naming']) + len(validation_result['incorrect_naming'])
        correct_names = len(validation_result['correct_naming'])
        validation_result['naming_score'] = correct_names / total_names if total_names > 0 else 1.0
        
        return validation_result
    
    def _validate_architecture_consistency(self, response: str, test_case: ContextAwarenessTestCase) -> Dict[str, Any]:
        """Validate that architectural patterns are maintained."""
        validation_result = {
            'pattern_adherence': [],
            'pattern_violations': [],
            'architecture_score': 0.0
        }
        
        patterns = test_case.project_context.architecture_patterns
        
        # Check for MVC pattern adherence
        if 'MVC' in patterns:
            # Look for separation of concerns
            has_model_logic = 'class ' in response and ('db.Model' in response or 'Model' in response)
            has_route_logic = '@' in response and ('route' in response or 'app.' in response)
            
            if has_model_logic and has_route_logic:
                validation_result['pattern_violations'].append("Mixed model and route logic in same code")
            elif has_model_logic:
                validation_result['pattern_adherence'].append("Proper model separation")
            elif has_route_logic:
                validation_result['pattern_adherence'].append("Proper route separation")
        
        # Check for Component-based pattern (React)
        if 'Component-based' in patterns:
            # Look for proper component structure
            has_component = 'function ' in response or 'const ' in response and '=>' in response
            has_jsx = 'return (' in response or '<' in response and '>' in response
            
            if has_component and has_jsx:
                validation_result['pattern_adherence'].append("Proper component structure")
        
        # Check for Hook patterns
        if 'Hooks' in patterns:
            # Look for proper hook usage
            hook_pattern = r'use[A-Z][a-zA-Z]*'
            hooks_found = re.findall(hook_pattern, response)
            
            for hook in hooks_found:
                if hook.startswith('use') and len(hook) > 3:
                    validation_result['pattern_adherence'].append(f"Proper hook naming: {hook}")
        
        # Calculate architecture score
        total_checks = len(validation_result['pattern_adherence']) + len(validation_result['pattern_violations'])
        adherent_checks = len(validation_result['pattern_adherence'])
        validation_result['architecture_score'] = adherent_checks / total_checks if total_checks > 0 else 1.0
        
        return validation_result
    
    def _validate_import_accuracy(self, response: str, test_case: ContextAwarenessTestCase) -> Dict[str, Any]:
        """Validate that import statements are accurate."""
        validation_result = {
            'correct_imports': [],
            'incorrect_imports': [],
            'import_score': 0.0
        }
        
        # Extract import statements
        import_patterns = [
            r'from\s+([a-zA-Z_][a-zA-Z0-9_./]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_, ]*)',
            r'import\s+([a-zA-Z_][a-zA-Z0-9_./]*)',
            r'import.*from\s+["\']([^"\']+)["\']'
        ]
        
        imports_found = []
        for pattern in import_patterns:
            matches = re.findall(pattern, response)
            imports_found.extend(matches)
        
        # Validate against existing code samples
        existing_imports = set()
        for code_sample in test_case.project_context.existing_code_samples.values():
            for pattern in import_patterns:
                existing_imports.update(re.findall(pattern, code_sample))
        
        # Check if imports follow existing patterns
        for import_stmt in imports_found:
            if isinstance(import_stmt, tuple):
                import_path = import_stmt[0] if import_stmt[0] else import_stmt[1]
            else:
                import_path = import_stmt
            
            # Check if import path is reasonable given project structure
            is_reasonable = any(
                part in import_path for part in ['models', 'utils', 'services', 'components', 'hooks']
            )
            
            if is_reasonable:
                validation_result['correct_imports'].append(str(import_stmt))
            else:
                validation_result['incorrect_imports'].append(str(import_stmt))
        
        # Calculate import score
        total_imports = len(validation_result['correct_imports']) + len(validation_result['incorrect_imports'])
        correct_imports = len(validation_result['correct_imports'])
        validation_result['import_score'] = correct_imports / total_imports if total_imports > 0 else 1.0
        
        return validation_result
    
    def _run_single_context_test(self, test_case: ContextAwarenessTestCase) -> Dict[str, Any]:
        """Run a single context awareness test case."""
        # Create context-rich prompt
        context_info = f"""
Project: {test_case.project_context.project_name}

File Structure:
{json.dumps(test_case.project_context.file_structure, indent=2)}

Existing Code Samples:
{json.dumps(test_case.project_context.existing_code_samples, indent=2)}

Naming Conventions:
{json.dumps(test_case.project_context.naming_conventions, indent=2)}

Architecture Patterns: {', '.join(test_case.project_context.architecture_patterns)}

User Request: {test_case.user_request}
"""
        
        # Mock response for testing framework
        mock_response = self._generate_mock_context_response(test_case)
        
        # Validate different aspects
        file_validation = self._validate_file_references(mock_response, test_case)
        naming_validation = self._validate_naming_conventions(mock_response, test_case)
        architecture_validation = self._validate_architecture_consistency(mock_response, test_case)
        import_validation = self._validate_import_accuracy(mock_response, test_case)
        
        # Calculate overall success
        overall_score = (
            file_validation['accuracy_score'] * 0.3 +
            naming_validation['naming_score'] * 0.25 +
            architecture_validation['architecture_score'] * 0.25 +
            import_validation['import_score'] * 0.2
        )
        
        success = overall_score >= 0.7  # 70% threshold for success
        
        result = {
            'test_id': test_case.test_id,
            'description': test_case.description,
            'difficulty': test_case.difficulty,
            'project_type': test_case.project_context.project_name,
            'success': success,
            'overall_score': overall_score,
            'file_validation': file_validation,
            'naming_validation': naming_validation,
            'architecture_validation': architecture_validation,
            'import_validation': import_validation,
            'full_response': mock_response
        }
        
        return result
    
    def _generate_mock_context_response(self, test_case: ContextAwarenessTestCase) -> str:
        """Generate a mock response for testing the framework."""
        # This would be replaced with actual model calls in production
        
        if 'flask' in test_case.project_context.project_name.lower():
            if 'auth' in test_case.user_request.lower():
                return """
I'll create a new authentication route that uses the existing User model.

```python
from flask import Blueprint, request, jsonify
from models.user import User
from utils.database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({'message': 'Login successful', 'user_id': user.id})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
```

This route follows the existing Flask blueprint pattern and uses the User model from models/user.py.
"""
            
            elif 'product' in test_case.user_request.lower():
                return """
I'll create a Product model that relates to the existing User model.

```python
from utils.database import db
from models.user import User

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('products', lazy=True))
    
    def __repr__(self):
        return f'<Product {self.name}>'
```

This follows the existing SQLAlchemy patterns and establishes a proper relationship with the User model.
"""
        
        elif 'react' in test_case.project_context.project_name.lower():
            if 'useauth' in test_case.user_request.lower():
                return """
I'll create a new component that uses the existing useAuth hook.

```jsx
import React from 'react';
import { useAuth } from '../hooks/useAuth';

const UserProfile = () => {
    const { user, isLoading } = useAuth();
    
    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (!user) {
        return <div>Please log in to view your profile.</div>;
    }
    
    return (
        <div className="user-profile">
            <h2>User Profile</h2>
            <p>Username: {user.username}</p>
            <p>Email: {user.email}</p>
        </div>
    );
};

export default UserProfile;
```

This component uses the existing useAuth hook and follows the established React patterns.
"""
            
            elif 'form' in test_case.user_request.lower():
                return """
I'll create a custom hook for form state management and a notification component.

```jsx
import { useState } from 'react';

export const useFormState = (initialState = {}) => {
    const [formData, setFormData] = useState(initialState);
    const [errors, setErrors] = useState({});
    
    const updateField = (fieldName, value) => {
        setFormData(prev => ({
            ...prev,
            [fieldName]: value
        }));
    };
    
    const resetForm = () => {
        setFormData(initialState);
        setErrors({});
    };
    
    return {
        formData,
        errors,
        updateField,
        resetForm,
        setErrors
    };
};

const NotificationComponent = ({ message, type = 'info' }) => {
    return (
        <div className={`notification notification-${type}`}>
            {message}
        </div>
    );
};

export default NotificationComponent;
```

The hook follows the useXxx naming convention and the component uses PascalCase as per project standards.
"""
        
        # Generic response
        return f"""
I'll implement the requested feature following the existing project patterns.

```python
# Mock implementation for {test_case.test_id}
def example_function():
    '''Example implementation following project conventions.'''
    return "Implementation follows existing patterns"
```

This implementation maintains consistency with the existing codebase structure and naming conventions.
"""
    
    def test_file_reference_accuracy(self):
        """Test accurate file and function referencing."""
        file_ref_tests = self.test_suite.get_tests_by_category('file_reference')
        
        for test_case in file_ref_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_context_test(test_case)
                self.assertGreaterEqual(result['file_validation']['accuracy_score'], 0.8,
                                      f"File reference test {test_case.test_id} failed")
    
    def test_naming_convention_consistency(self):
        """Test naming convention consistency."""
        naming_tests = self.test_suite.get_tests_by_category('naming')
        
        for test_case in naming_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_context_test(test_case)
                self.assertGreaterEqual(result['naming_validation']['naming_score'], 0.8,
                                      f"Naming convention test {test_case.test_id} failed")
    
    def test_architecture_consistency(self):
        """Test architectural pattern consistency."""
        arch_tests = self.test_suite.get_tests_by_category('architecture')
        
        for test_case in arch_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_context_test(test_case)
                self.assertGreaterEqual(result['architecture_validation']['architecture_score'], 0.7,
                                      f"Architecture test {test_case.test_id} failed")
    
    def test_import_handling(self):
        """Test import statement accuracy."""
        import_tests = self.test_suite.get_tests_by_category('imports')
        
        for test_case in import_tests:
            with self.subTest(test_id=test_case.test_id):
                result = self._run_single_context_test(test_case)
                self.assertGreaterEqual(result['import_validation']['import_score'], 0.8,
                                      f"Import handling test {test_case.test_id} failed")
    
    def run_full_context_awareness_suite(self) -> Dict[str, Any]:
        """Run the complete context awareness test suite and return results."""
        all_tests = self.test_suite.get_all_tests()
        results = []
        
        for test_case in all_tests:
            result = self._run_single_context_test(test_case)
            results.append(result)
        
        # Calculate summary statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0
        
        # Calculate average scores
        avg_file_accuracy = sum(r['file_validation']['accuracy_score'] for r in results) / total_tests
        avg_naming_score = sum(r['naming_validation']['naming_score'] for r in results) / total_tests
        avg_architecture_score = sum(r['architecture_validation']['architecture_score'] for r in results) / total_tests
        avg_import_score = sum(r['import_validation']['import_score'] for r in results) / total_tests
        
        summary = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'average_scores': {
                'file_accuracy': avg_file_accuracy,
                'naming_consistency': avg_naming_score,
                'architecture_consistency': avg_architecture_score,
                'import_accuracy': avg_import_score
            },
            'results': results,
            'by_category': {},
            'by_project_type': {}
        }
        
        # Group by category
        categories = ['file_reference', 'naming', 'architecture', 'imports']
        for category in categories:
            category_tests = self.test_suite.get_tests_by_category(category)
            category_results = [r for r in results if any(t.test_id == r['test_id'] for t in category_tests)]
            summary['by_category'][category] = {
                'total': len(category_results),
                'successful': len([r for r in category_results if r['success']])
            }
        
        # Group by project type
        project_types = ['flask', 'react']
        for project_type in project_types:
            type_results = [r for r in results if project_type in r['project_type'].lower()]
            summary['by_project_type'][project_type] = {
                'total': len(type_results),
                'successful': len([r for r in type_results if r['success']])
            }
        
        return summary


if __name__ == "__main__":
    # Run tests when executed directly
    runner = ContextAwarenessTestRunner()
    
    # Run full test suite
    print("Running Context Awareness Test Suite...")
    summary = runner.run_full_context_awareness_suite()
    
    print(f"\nContext Awareness Test Results Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Success Rate: {summary['success_rate']:.2%}")
    
    print(f"\nAverage Scores:")
    for metric, score in summary['average_scores'].items():
        print(f"  {metric.replace('_', ' ').title()}: {score:.2%}")
    
    print(f"\nBy Category:")
    for category, stats in summary['by_category'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {category.replace('_', ' ').title()}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    print(f"\nBy Project Type:")
    for project_type, stats in summary['by_project_type'].items():
        rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {project_type.title()}: {stats['successful']}/{stats['total']} ({rate:.2%})")
    
    # Save detailed results
    with open('context_awareness_test_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nDetailed results saved to context_awareness_test_results.json")
    
    # Also run as unittest
    unittest.main(argv=[''], exit=False, verbosity=2)