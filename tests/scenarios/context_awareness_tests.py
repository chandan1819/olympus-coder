"""
Context Awareness Test Cases for Olympus-Coder-v1

This module contains test scenarios for evaluating the model's ability to understand
project context and maintain consistency according to requirements 4.1, 4.2, and 4.5.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ProjectContext:
    """Represents project structure and context information."""
    project_name: str
    file_structure: Dict[str, Any]
    existing_code_samples: Dict[str, str]
    naming_conventions: Dict[str, str]
    architecture_patterns: List[str]


@dataclass
class ContextAwarenessTestCase:
    """Represents a single context awareness test scenario."""
    test_id: str
    description: str
    project_context: ProjectContext
    user_request: str
    expected_behaviors: List[str]
    validation_criteria: List[str]
    difficulty: str


class ContextAwarenessTests:
    """Collection of context awareness test scenarios."""
    
    def __init__(self):
        self.file_reference_tests = self._create_file_reference_tests()
        self.naming_convention_tests = self._create_naming_convention_tests()
        self.architecture_consistency_tests = self._create_architecture_consistency_tests()
        self.import_handling_tests = self._create_import_handling_tests()
    
    def _create_sample_project_contexts(self) -> Dict[str, ProjectContext]:
        """Create sample project contexts for testing."""
        return {
            'flask_api': ProjectContext(
                project_name="Flask API Project",
                file_structure={
                    'app.py': 'main application file',
                    'models/': {
                        'user.py': 'User model',
                        'product.py': 'Product model',
                        '__init__.py': 'models package init'
                    },
                    'routes/': {
                        'auth.py': 'authentication routes',
                        'api.py': 'API routes',
                        '__init__.py': 'routes package init'
                    },
                    'utils/': {
                        'database.py': 'database utilities',
                        'validators.py': 'validation functions'
                    },
                    'config.py': 'configuration settings',
                    'requirements.txt': 'dependencies'
                },
                existing_code_samples={
                    'models/user.py': '''
from flask_sqlalchemy import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
''',
                    'utils/database.py': '''
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
'''
                },
                naming_conventions={
                    'classes': 'PascalCase',
                    'functions': 'snake_case',
                    'variables': 'snake_case',
                    'constants': 'UPPER_SNAKE_CASE'
                },
                architecture_patterns=['MVC', 'Blueprint', 'Factory Pattern']
            ),
            
            'react_app': ProjectContext(
                project_name="React Application",
                file_structure={
                    'src/': {
                        'components/': {
                            'Header.jsx': 'header component',
                            'Footer.jsx': 'footer component',
                            'UserProfile.jsx': 'user profile component'
                        },
                        'hooks/': {
                            'useAuth.js': 'authentication hook',
                            'useApi.js': 'API hook'
                        },
                        'services/': {
                            'authService.js': 'authentication service',
                            'apiService.js': 'API service'
                        },
                        'utils/': {
                            'helpers.js': 'utility functions',
                            'constants.js': 'application constants'
                        },
                        'App.jsx': 'main app component',
                        'index.js': 'entry point'
                    },
                    'package.json': 'dependencies and scripts',
                    'README.md': 'project documentation'
                },
                existing_code_samples={
                    'src/hooks/useAuth.js': '''
import { useState, useEffect } from 'react';
import { authService } from '../services/authService';

export const useAuth = () => {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    
    useEffect(() => {
        checkAuthStatus();
    }, []);
    
    const checkAuthStatus = async () => {
        try {
            const userData = await authService.getCurrentUser();
            setUser(userData);
        } catch (error) {
            console.error('Auth check failed:', error);
        } finally {
            setIsLoading(false);
        }
    };
    
    return { user, isLoading, checkAuthStatus };
};
''',
                    'src/services/authService.js': '''
const API_BASE_URL = process.env.REACT_APP_API_URL;

export const authService = {
    async login(credentials) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
        });
        return response.json();
    },
    
    async getCurrentUser() {
        const token = localStorage.getItem('authToken');
        if (!token) throw new Error('No token found');
        
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.json();
    }
};
'''
                },
                naming_conventions={
                    'components': 'PascalCase',
                    'functions': 'camelCase',
                    'variables': 'camelCase',
                    'constants': 'UPPER_SNAKE_CASE',
                    'hooks': 'use + PascalCase'
                },
                architecture_patterns=['Component-based', 'Hooks', 'Service Layer']
            )
        }
    
    def _create_file_reference_tests(self) -> List[ContextAwarenessTestCase]:
        """Create test cases for accurate file and function referencing."""
        contexts = self._create_sample_project_contexts()
        
        return [
            ContextAwarenessTestCase(
                test_id="context_file_ref_001",
                description="Reference existing files accurately in Flask project",
                project_context=contexts['flask_api'],
                user_request="Create a new route in the auth module that uses the User model to authenticate users.",
                expected_behaviors=[
                    "references routes/auth.py correctly",
                    "imports from models/user.py",
                    "uses existing User class methods",
                    "follows Flask routing patterns"
                ],
                validation_criteria=[
                    "does not hallucinate non-existent files",
                    "uses correct import paths",
                    "references existing User class",
                    "maintains Flask blueprint structure"
                ],
                difficulty="basic"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_file_ref_002",
                description="Reference existing components in React project",
                project_context=contexts['react_app'],
                user_request="Create a new component that uses the useAuth hook and displays user information.",
                expected_behaviors=[
                    "imports useAuth from correct path",
                    "follows React component patterns",
                    "uses existing hook interface",
                    "places component in appropriate directory"
                ],
                validation_criteria=[
                    "correct import path for useAuth",
                    "does not invent new hook methods",
                    "follows existing component structure",
                    "maintains React patterns"
                ],
                difficulty="basic"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_file_ref_003",
                description="Handle complex file relationships and dependencies",
                project_context=contexts['flask_api'],
                user_request="Create a new Product model that has a relationship with the User model and uses the database utilities.",
                expected_behaviors=[
                    "imports from models/__init__.py or models/user.py",
                    "uses utils/database.py utilities",
                    "follows existing model patterns",
                    "establishes proper relationships"
                ],
                validation_criteria=[
                    "correct database import paths",
                    "references existing User model",
                    "follows SQLAlchemy patterns from existing code",
                    "maintains consistent model structure"
                ],
                difficulty="intermediate"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_file_ref_004",
                description="Avoid hallucinating non-existent files",
                project_context=contexts['react_app'],
                user_request="Add error handling to the authentication flow using existing utilities.",
                expected_behaviors=[
                    "only references existing files",
                    "uses actual utility functions",
                    "works within existing service structure",
                    "maintains current error patterns"
                ],
                validation_criteria=[
                    "does not reference non-existent error utilities",
                    "uses existing authService methods",
                    "maintains current file structure",
                    "follows established patterns"
                ],
                difficulty="intermediate"
            )
        ]
    
    def _create_naming_convention_tests(self) -> List[ContextAwarenessTestCase]:
        """Create test cases for maintaining naming convention consistency."""
        contexts = self._create_sample_project_contexts()
        
        return [
            ContextAwarenessTestCase(
                test_id="context_naming_001",
                description="Follow Python naming conventions in Flask project",
                project_context=contexts['flask_api'],
                user_request="Create a utility function for validating email addresses and a constant for maximum password length.",
                expected_behaviors=[
                    "uses snake_case for function names",
                    "uses UPPER_SNAKE_CASE for constants",
                    "follows existing naming patterns",
                    "maintains consistency with existing code"
                ],
                validation_criteria=[
                    "function names in snake_case",
                    "constants in UPPER_SNAKE_CASE",
                    "consistent with existing utils",
                    "follows Python PEP 8 conventions"
                ],
                difficulty="basic"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_naming_002",
                description="Follow JavaScript naming conventions in React project",
                project_context=contexts['react_app'],
                user_request="Create a new custom hook for managing form state and a component for displaying notifications.",
                expected_behaviors=[
                    "hook name starts with 'use' + PascalCase",
                    "component name in PascalCase",
                    "function names in camelCase",
                    "follows React naming patterns"
                ],
                validation_criteria=[
                    "hook follows useXxx pattern",
                    "component in PascalCase",
                    "internal functions in camelCase",
                    "consistent with existing code style"
                ],
                difficulty="basic"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_naming_003",
                description="Maintain naming consistency across multiple files",
                project_context=contexts['flask_api'],
                user_request="Create a new authentication middleware and corresponding route handlers.",
                expected_behaviors=[
                    "consistent function naming across files",
                    "follows existing middleware patterns",
                    "maintains route naming conventions",
                    "uses consistent variable names"
                ],
                validation_criteria=[
                    "all functions use snake_case",
                    "middleware follows existing patterns",
                    "route names consistent with existing",
                    "variable naming matches project style"
                ],
                difficulty="intermediate"
            )
        ]
    
    def _create_architecture_consistency_tests(self) -> List[ContextAwarenessTestCase]:
        """Create test cases for maintaining architectural patterns."""
        contexts = self._create_sample_project_contexts()
        
        return [
            ContextAwarenessTestCase(
                test_id="context_arch_001",
                description="Follow MVC pattern in Flask project",
                project_context=contexts['flask_api'],
                user_request="Add a new feature for user profile management with CRUD operations.",
                expected_behaviors=[
                    "separates model, view, and controller logic",
                    "follows existing MVC structure",
                    "uses appropriate Flask blueprints",
                    "maintains separation of concerns"
                ],
                validation_criteria=[
                    "model logic in models/ directory",
                    "routes in routes/ directory",
                    "follows existing blueprint pattern",
                    "maintains MVC separation"
                ],
                difficulty="intermediate"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_arch_002",
                description="Follow component-based architecture in React project",
                project_context=contexts['react_app'],
                user_request="Add a new feature for user settings with form handling and API integration.",
                expected_behaviors=[
                    "creates reusable components",
                    "uses existing service layer",
                    "follows hook patterns for state",
                    "maintains component hierarchy"
                ],
                validation_criteria=[
                    "components are properly structured",
                    "uses existing service patterns",
                    "follows hook conventions",
                    "maintains architectural consistency"
                ],
                difficulty="intermediate"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_arch_003",
                description="Maintain service layer pattern consistency",
                project_context=contexts['react_app'],
                user_request="Add new API endpoints for data analytics with proper error handling.",
                expected_behaviors=[
                    "extends existing service structure",
                    "follows established API patterns",
                    "maintains error handling consistency",
                    "uses existing service utilities"
                ],
                validation_criteria=[
                    "follows existing service structure",
                    "consistent error handling patterns",
                    "maintains API abstraction layer",
                    "uses established patterns"
                ],
                difficulty="advanced"
            )
        ]
    
    def _create_import_handling_tests(self) -> List[ContextAwarenessTestCase]:
        """Create test cases for proper import statement handling."""
        contexts = self._create_sample_project_contexts()
        
        return [
            ContextAwarenessTestCase(
                test_id="context_import_001",
                description="Generate correct import statements for Flask project",
                project_context=contexts['flask_api'],
                user_request="Create a new route that uses the User model and database utilities.",
                expected_behaviors=[
                    "imports User from models.user",
                    "imports database utilities correctly",
                    "uses relative imports appropriately",
                    "follows Python import conventions"
                ],
                validation_criteria=[
                    "correct import paths for existing modules",
                    "uses appropriate import style",
                    "no circular import issues",
                    "follows project import patterns"
                ],
                difficulty="basic"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_import_002",
                description="Generate correct import statements for React project",
                project_context=contexts['react_app'],
                user_request="Create a component that uses the useAuth hook and authService.",
                expected_behaviors=[
                    "imports useAuth from correct hook path",
                    "imports authService from services",
                    "uses ES6 import syntax",
                    "follows existing import patterns"
                ],
                validation_criteria=[
                    "correct relative import paths",
                    "uses existing import style",
                    "follows ES6 module conventions",
                    "maintains import consistency"
                ],
                difficulty="basic"
            ),
            
            ContextAwarenessTestCase(
                test_id="context_import_003",
                description="Handle complex import scenarios with multiple dependencies",
                project_context=contexts['flask_api'],
                user_request="Create a comprehensive user management system that integrates models, routes, and utilities.",
                expected_behaviors=[
                    "manages multiple import dependencies",
                    "avoids circular imports",
                    "uses appropriate import levels",
                    "maintains clean import structure"
                ],
                validation_criteria=[
                    "all imports are valid and necessary",
                    "no circular dependency issues",
                    "follows established import hierarchy",
                    "maintains code organization"
                ],
                difficulty="advanced"
            )
        ]
    
    def get_all_tests(self) -> List[ContextAwarenessTestCase]:
        """Return all context awareness test cases."""
        return (self.file_reference_tests + 
                self.naming_convention_tests + 
                self.architecture_consistency_tests + 
                self.import_handling_tests)
    
    def get_tests_by_category(self, category: str) -> List[ContextAwarenessTestCase]:
        """Return test cases for a specific category."""
        category_map = {
            'file_reference': self.file_reference_tests,
            'naming': self.naming_convention_tests,
            'architecture': self.architecture_consistency_tests,
            'imports': self.import_handling_tests
        }
        return category_map.get(category.lower(), [])
    
    def get_tests_by_project_type(self, project_type: str) -> List[ContextAwarenessTestCase]:
        """Return test cases for a specific project type."""
        all_tests = self.get_all_tests()
        return [test for test in all_tests 
                if project_type.lower() in test.project_context.project_name.lower()]
    
    def get_tests_by_difficulty(self, difficulty: str) -> List[ContextAwarenessTestCase]:
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
                'project_context': {
                    'project_name': test.project_context.project_name,
                    'file_structure': test.project_context.file_structure,
                    'existing_code_samples': test.project_context.existing_code_samples,
                    'naming_conventions': test.project_context.naming_conventions,
                    'architecture_patterns': test.project_context.architecture_patterns
                },
                'user_request': test.user_request,
                'expected_behaviors': test.expected_behaviors,
                'validation_criteria': test.validation_criteria,
                'difficulty': test.difficulty
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage and basic validation
    test_suite = ContextAwarenessTests()
    
    print(f"Total context awareness test cases: {len(test_suite.get_all_tests())}")
    print(f"File reference tests: {len(test_suite.get_tests_by_category('file_reference'))}")
    print(f"Naming convention tests: {len(test_suite.get_tests_by_category('naming'))}")
    print(f"Architecture tests: {len(test_suite.get_tests_by_category('architecture'))}")
    print(f"Import handling tests: {len(test_suite.get_tests_by_category('imports'))}")
    
    print(f"\nBy project type:")
    print(f"Flask tests: {len(test_suite.get_tests_by_project_type('flask'))}")
    print(f"React tests: {len(test_suite.get_tests_by_project_type('react'))}")
    
    print(f"\nBy difficulty:")
    for difficulty in ['basic', 'intermediate', 'advanced']:
        count = len(test_suite.get_tests_by_difficulty(difficulty))
        print(f"  {difficulty}: {count}")
    
    # Export to JSON for external validation tools
    test_suite.export_to_json('context_awareness_test_cases.json')
    print("\nContext awareness test cases exported to context_awareness_test_cases.json")