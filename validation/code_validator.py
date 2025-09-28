"""
Code syntax validation functions for Python and JavaScript.

Validates code syntax, formatting, and basic quality checks.
"""

import ast
import re
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class CodeValidator(ABC):
    """Abstract base class for code validators."""
    
    @abstractmethod
    def validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate code syntax."""
        pass
    
    @abstractmethod
    def validate_style(self, code: str) -> Dict[str, Any]:
        """Validate code style and formatting."""
        pass


class PythonValidator(CodeValidator):
    """Validates Python code syntax and PEP 8 compliance."""
    
    def validate_syntax(self, code: str) -> Dict[str, Any]:
        """
        Validate Python code syntax using AST parsing.
        
        Args:
            code: Python code string to validate
            
        Returns:
            Dict with validation results
        """
        result = {
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "line_count": len(code.splitlines()),
            "has_functions": False,
            "has_classes": False
        }
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            result["is_valid"] = True
            
            # Analyze AST for structure
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result["has_functions"] = True
                elif isinstance(node, ast.ClassDef):
                    result["has_classes"] = True
            
        except SyntaxError as e:
            result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            result["errors"].append(f"Parse error: {str(e)}")
        
        return result
    
    def validate_style(self, code: str) -> Dict[str, Any]:
        """
        Validate Python code style against PEP 8 guidelines.
        
        Args:
            code: Python code string to validate
            
        Returns:
            Dict with style validation results
        """
        result = {
            "is_compliant": True,
            "violations": [],
            "score": 1.0,
            "checks": {
                "line_length": True,
                "indentation": True,
                "imports": True,
                "naming": True,
                "whitespace": True
            }
        }
        
        lines = code.splitlines()
        violations = []
        
        # Check line length (PEP 8: max 79 characters)
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                violations.append(f"Line {i}: Line too long ({len(line)} > 79 characters)")
                result["checks"]["line_length"] = False
        
        # Check indentation (should be 4 spaces)
        for i, line in enumerate(lines, 1):
            if line.strip() and line.startswith(' '):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces % 4 != 0:
                    violations.append(f"Line {i}: Indentation should be multiple of 4 spaces")
                    result["checks"]["indentation"] = False
        
        # Check import organization
        import_lines = [line for line in lines if line.strip().startswith(('import ', 'from '))]
        if import_lines:
            # Check for imports after code
            code_started = False
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith(('#', 'import ', 'from ', '"""', "'''")):
                    code_started = True
                elif code_started and stripped.startswith(('import ', 'from ')):
                    violations.append(f"Line {i}: Import should be at top of file")
                    result["checks"]["imports"] = False
        
        # Check function/class naming conventions
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]'
        
        for i, line in enumerate(lines, 1):
            # Check function names (should be snake_case)
            func_matches = re.findall(function_pattern, line)
            for func_name in func_matches:
                if not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
                    violations.append(f"Line {i}: Function '{func_name}' should use snake_case")
                    result["checks"]["naming"] = False
            
            # Check class names (should be PascalCase)
            class_matches = re.findall(class_pattern, line)
            for class_name in class_matches:
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                    violations.append(f"Line {i}: Class '{class_name}' should use PascalCase")
                    result["checks"]["naming"] = False
        
        # Check whitespace around operators
        operator_pattern = r'[a-zA-Z0-9_]\s*[+\-*/=<>!]+\s*[a-zA-Z0-9_]'
        for i, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                # Simple check for spaces around assignment
                if re.search(r'[a-zA-Z0-9_]=[a-zA-Z0-9_]', line):
                    violations.append(f"Line {i}: Missing spaces around assignment operator")
                    result["checks"]["whitespace"] = False
        
        result["violations"] = violations
        result["is_compliant"] = len(violations) == 0
        
        # Calculate score based on violations
        if violations:
            result["score"] = max(0.0, 1.0 - (len(violations) * 0.1))
        
        return result


class JavaScriptValidator(CodeValidator):
    """Validates JavaScript code syntax and style."""
    
    def validate_syntax(self, code: str) -> Dict[str, Any]:
        """
        Validate JavaScript code syntax.
        
        Args:
            code: JavaScript code string to validate
            
        Returns:
            Dict with validation results
        """
        result = {
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "line_count": len(code.splitlines()),
            "has_functions": False,
            "has_classes": False
        }
        
        # Basic syntax checks
        try:
            # Check for balanced braces, brackets, parentheses
            braces = code.count('{') - code.count('}')
            brackets = code.count('[') - code.count(']')
            parens = code.count('(') - code.count(')')
            
            if braces != 0:
                result["errors"].append(f"Unbalanced braces: {braces} extra opening braces")
            if brackets != 0:
                result["errors"].append(f"Unbalanced brackets: {brackets} extra opening brackets")
            if parens != 0:
                result["errors"].append(f"Unbalanced parentheses: {parens} extra opening parentheses")
            
            # Check for function declarations
            if re.search(r'function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\(', code):
                result["has_functions"] = True
            
            # Check for class declarations
            if re.search(r'class\s+\w+', code):
                result["has_classes"] = True
            
            # If no major syntax errors found, consider valid
            if not result["errors"]:
                result["is_valid"] = True
            
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    def validate_style(self, code: str) -> Dict[str, Any]:
        """
        Validate JavaScript code style against common best practices.
        
        Args:
            code: JavaScript code string to validate
            
        Returns:
            Dict with style validation results
        """
        result = {
            "is_compliant": True,
            "violations": [],
            "score": 1.0,
            "checks": {
                "semicolons": True,
                "indentation": True,
                "naming": True,
                "quotes": True,
                "spacing": True
            }
        }
        
        lines = code.splitlines()
        violations = []
        
        # Check for semicolons at end of statements
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
                # Check if line should end with semicolon
                if (stripped.endswith(')') or 
                    stripped.endswith(']') or 
                    re.search(r'[a-zA-Z0-9_]$', stripped)) and not stripped.endswith(';'):
                    # Skip control structures
                    if not re.match(r'^\s*(if|for|while|function|class|else|try|catch|finally)', stripped):
                        violations.append(f"Line {i}: Missing semicolon")
                        result["checks"]["semicolons"] = False
        
        # Check indentation consistency (prefer 2 or 4 spaces)
        indent_sizes = []
        for line in lines:
            if line.strip() and line.startswith(' '):
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0:
                    indent_sizes.append(leading_spaces)
        
        if indent_sizes:
            # Check if indentation is consistent
            base_indent = min(indent_sizes)
            for i, line in enumerate(lines, 1):
                if line.strip() and line.startswith(' '):
                    leading_spaces = len(line) - len(line.lstrip(' '))
                    if leading_spaces % base_indent != 0:
                        violations.append(f"Line {i}: Inconsistent indentation")
                        result["checks"]["indentation"] = False
                        break
        
        # Check naming conventions (camelCase for variables/functions)
        var_pattern = r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        func_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        for i, line in enumerate(lines, 1):
            # Check variable names
            var_matches = re.findall(var_pattern, line)
            for var_name in var_matches:
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', var_name) and var_name.upper() != var_name:
                    violations.append(f"Line {i}: Variable '{var_name}' should use camelCase")
                    result["checks"]["naming"] = False
            
            # Check function names
            func_matches = re.findall(func_pattern, line)
            for func_name in func_matches:
                if not re.match(r'^[a-z][a-zA-Z0-9]*$', func_name):
                    violations.append(f"Line {i}: Function '{func_name}' should use camelCase")
                    result["checks"]["naming"] = False
        
        # Check quote consistency (prefer single quotes)
        double_quotes = code.count('"')
        single_quotes = code.count("'")
        if double_quotes > single_quotes and single_quotes > 0:
            violations.append("Inconsistent quote usage - prefer single quotes")
            result["checks"]["quotes"] = False
        
        result["violations"] = violations
        result["is_compliant"] = len(violations) == 0
        
        # Calculate score based on violations
        if violations:
            result["score"] = max(0.0, 1.0 - (len(violations) * 0.1))
        
        return result


def validate_code_block(code: str, language: str) -> Dict[str, Any]:
    """
    Validate a code block based on its language.
    
    Args:
        code: Code string to validate
        language: Programming language ('python', 'javascript', etc.)
        
    Returns:
        Dict with validation results
    """
    language = language.lower()
    
    if language in ['python', 'py']:
        validator = PythonValidator()
    elif language in ['javascript', 'js']:
        validator = JavaScriptValidator()
    else:
        return {
            "is_valid": False,
            "errors": [f"Unsupported language: {language}"],
            "warnings": [],
            "syntax_result": None,
            "style_result": None
        }
    
    syntax_result = validator.validate_syntax(code)
    style_result = validator.validate_style(code)
    
    return {
        "is_valid": syntax_result["is_valid"],
        "errors": syntax_result["errors"],
        "warnings": syntax_result["warnings"],
        "syntax_result": syntax_result,
        "style_result": style_result
    }