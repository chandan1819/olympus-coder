"""
Code quality assessment tools for Olympus-Coder-v1.

Provides comprehensive code quality analysis including style compliance,
documentation quality, and best practices adherence.
"""

import re
import ast
from typing import Dict, Any, List, Optional, Tuple
from code_validator import PythonValidator, JavaScriptValidator


class DocumentationAnalyzer:
    """Analyzes code documentation and comment quality."""
    
    def analyze_python_documentation(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code documentation quality.
        
        Args:
            code: Python code string to analyze
            
        Returns:
            Dict with documentation analysis results
        """
        result = {
            "score": 0.0,
            "has_module_docstring": False,
            "function_docstrings": 0,
            "class_docstrings": 0,
            "total_functions": 0,
            "total_classes": 0,
            "comment_lines": 0,
            "total_lines": len(code.splitlines()),
            "issues": [],
            "suggestions": []
        }
        
        lines = code.splitlines()
        
        try:
            tree = ast.parse(code)
            
            # Check for module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                result["has_module_docstring"] = True
            
            # Analyze functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result["total_functions"] += 1
                    if ast.get_docstring(node):
                        result["function_docstrings"] += 1
                    else:
                        result["issues"].append(f"Function '{node.name}' missing docstring")
                
                elif isinstance(node, ast.ClassDef):
                    result["total_classes"] += 1
                    if ast.get_docstring(node):
                        result["class_docstrings"] += 1
                    else:
                        result["issues"].append(f"Class '{node.name}' missing docstring")
        
        except SyntaxError:
            result["issues"].append("Cannot analyze documentation due to syntax errors")
        
        # Count comment lines
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                result["comment_lines"] += 1
        
        # Calculate documentation score
        doc_score = 0.0
        
        # Module docstring (20 points)
        if result["has_module_docstring"]:
            doc_score += 0.2
        
        # Function docstrings (40 points)
        if result["total_functions"] > 0:
            func_ratio = result["function_docstrings"] / result["total_functions"]
            doc_score += 0.4 * func_ratio
        else:
            doc_score += 0.4  # No functions to document
        
        # Class docstrings (30 points)
        if result["total_classes"] > 0:
            class_ratio = result["class_docstrings"] / result["total_classes"]
            doc_score += 0.3 * class_ratio
        else:
            doc_score += 0.3  # No classes to document
        
        # Comment density (10 points)
        if result["total_lines"] > 0:
            comment_ratio = result["comment_lines"] / result["total_lines"]
            doc_score += 0.1 * min(1.0, comment_ratio * 10)  # Cap at 10% comment ratio
        
        result["score"] = doc_score
        
        # Generate suggestions
        if not result["has_module_docstring"]:
            result["suggestions"].append("Add module docstring to describe file purpose")
        
        if result["total_functions"] > result["function_docstrings"]:
            result["suggestions"].append("Add docstrings to all functions")
        
        if result["total_classes"] > result["class_docstrings"]:
            result["suggestions"].append("Add docstrings to all classes")
        
        if result["comment_lines"] / max(1, result["total_lines"]) < 0.05:
            result["suggestions"].append("Consider adding more inline comments")
        
        return result
    
    def analyze_javascript_documentation(self, code: str) -> Dict[str, Any]:
        """
        Analyze JavaScript code documentation quality.
        
        Args:
            code: JavaScript code string to analyze
            
        Returns:
            Dict with documentation analysis results
        """
        result = {
            "score": 0.0,
            "jsdoc_functions": 0,
            "total_functions": 0,
            "jsdoc_classes": 0,
            "total_classes": 0,
            "comment_lines": 0,
            "total_lines": len(code.splitlines()),
            "issues": [],
            "suggestions": []
        }
        
        lines = code.splitlines()
        
        # Count functions and classes
        function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\(.*?\)\s*=>))'
        class_pattern = r'class\s+(\w+)'
        jsdoc_pattern = r'/\*\*[\s\S]*?\*/'
        
        # Find JSDoc blocks and their positions
        jsdoc_blocks = []
        code_text = '\n'.join(lines)
        for match in re.finditer(jsdoc_pattern, code_text):
            start_line = code_text[:match.start()].count('\n')
            end_line = code_text[:match.end()].count('\n')
            jsdoc_blocks.append((start_line, end_line))
        
        # Find all functions
        for i, line in enumerate(lines):
            func_matches = re.findall(function_pattern, line)
            for match in func_matches:
                func_name = match[0] or match[1]
                if func_name:
                    result["total_functions"] += 1
                    
                    # Check if there's a JSDoc block immediately before this function
                    has_jsdoc = False
                    for start, end in jsdoc_blocks:
                        if end < i and i - end <= 2:  # JSDoc within 2 lines before function
                            has_jsdoc = True
                            break
                    
                    if has_jsdoc:
                        result["jsdoc_functions"] += 1
                    else:
                        result["issues"].append(f"Function '{func_name}' missing JSDoc documentation")
            
            # Find classes
            class_matches = re.findall(class_pattern, line)
            for class_name in class_matches:
                result["total_classes"] += 1
                
                # Check if there's a JSDoc block immediately before this class
                has_jsdoc = False
                for start, end in jsdoc_blocks:
                    if end < i and i - end <= 2:  # JSDoc within 2 lines before class
                        has_jsdoc = True
                        break
                
                if has_jsdoc:
                    result["jsdoc_classes"] += 1
                else:
                    result["issues"].append(f"Class '{class_name}' missing JSDoc documentation")
        
        # Count comment lines
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                result["comment_lines"] += 1
        
        # Calculate documentation score
        doc_score = 0.0
        
        # Function documentation (50 points)
        if result["total_functions"] > 0:
            func_ratio = result["jsdoc_functions"] / result["total_functions"]
            doc_score += 0.5 * func_ratio
        else:
            doc_score += 0.5  # No functions to document
        
        # Class documentation (30 points)
        if result["total_classes"] > 0:
            class_ratio = result["jsdoc_classes"] / result["total_classes"]
            doc_score += 0.3 * class_ratio
        else:
            doc_score += 0.3  # No classes to document
        
        # Comment density (20 points)
        if result["total_lines"] > 0:
            comment_ratio = result["comment_lines"] / result["total_lines"]
            doc_score += 0.2 * min(1.0, comment_ratio * 10)
        
        result["score"] = doc_score
        
        # Generate suggestions
        if result["total_functions"] > result["jsdoc_functions"]:
            result["suggestions"].append("Add JSDoc comments to all functions")
        
        if result["total_classes"] > result["jsdoc_classes"]:
            result["suggestions"].append("Add JSDoc comments to all classes")
        
        if result["comment_lines"] / max(1, result["total_lines"]) < 0.05:
            result["suggestions"].append("Consider adding more inline comments")
        
        return result


class CodeQualityAssessor:
    """Comprehensive code quality assessment tool."""
    
    def __init__(self):
        self.python_validator = PythonValidator()
        self.js_validator = JavaScriptValidator()
        self.doc_analyzer = DocumentationAnalyzer()
    
    def assess_python_quality(self, code: str) -> Dict[str, Any]:
        """
        Comprehensive Python code quality assessment.
        
        Args:
            code: Python code string to assess
            
        Returns:
            Dict with comprehensive quality assessment
        """
        result = {
            "overall_score": 0.0,
            "syntax_valid": False,
            "style_compliant": False,
            "well_documented": False,
            "assessments": {},
            "recommendations": [],
            "grade": "F"
        }
        
        # Syntax validation (25% weight)
        syntax_result = self.python_validator.validate_syntax(code)
        result["assessments"]["syntax"] = syntax_result
        result["syntax_valid"] = syntax_result["is_valid"]
        syntax_score = 1.0 if syntax_result["is_valid"] else 0.0
        
        # Style validation (35% weight)
        style_result = self.python_validator.validate_style(code)
        result["assessments"]["style"] = style_result
        result["style_compliant"] = style_result["is_compliant"]
        style_score = style_result["score"]
        
        # Documentation analysis (40% weight)
        doc_result = self.doc_analyzer.analyze_python_documentation(code)
        result["assessments"]["documentation"] = doc_result
        result["well_documented"] = doc_result["score"] >= 0.7
        doc_score = doc_result["score"]
        
        # Calculate overall score
        result["overall_score"] = (
            syntax_score * 0.25 +
            style_score * 0.35 +
            doc_score * 0.40
        )
        
        # Assign grade
        if result["overall_score"] >= 0.9:
            result["grade"] = "A"
        elif result["overall_score"] >= 0.8:
            result["grade"] = "B"
        elif result["overall_score"] >= 0.7:
            result["grade"] = "C"
        elif result["overall_score"] >= 0.6:
            result["grade"] = "D"
        else:
            result["grade"] = "F"
        
        # Generate recommendations
        if not syntax_result["is_valid"]:
            result["recommendations"].append("Fix syntax errors before proceeding")
        
        if not style_result["is_compliant"]:
            result["recommendations"].extend([
                f"Address PEP 8 violations: {len(style_result['violations'])} issues found",
                "Consider using autopep8 or black for automatic formatting"
            ])
        
        if doc_result["score"] < 0.7:
            result["recommendations"].extend(doc_result["suggestions"])
        
        return result
    
    def assess_javascript_quality(self, code: str) -> Dict[str, Any]:
        """
        Comprehensive JavaScript code quality assessment.
        
        Args:
            code: JavaScript code string to assess
            
        Returns:
            Dict with comprehensive quality assessment
        """
        result = {
            "overall_score": 0.0,
            "syntax_valid": False,
            "style_compliant": False,
            "well_documented": False,
            "assessments": {},
            "recommendations": [],
            "grade": "F"
        }
        
        # Syntax validation (25% weight)
        syntax_result = self.js_validator.validate_syntax(code)
        result["assessments"]["syntax"] = syntax_result
        result["syntax_valid"] = syntax_result["is_valid"]
        syntax_score = 1.0 if syntax_result["is_valid"] else 0.0
        
        # Style validation (35% weight)
        style_result = self.js_validator.validate_style(code)
        result["assessments"]["style"] = style_result
        result["style_compliant"] = style_result["is_compliant"]
        style_score = style_result["score"]
        
        # Documentation analysis (40% weight)
        doc_result = self.doc_analyzer.analyze_javascript_documentation(code)
        result["assessments"]["documentation"] = doc_result
        result["well_documented"] = doc_result["score"] >= 0.7
        doc_score = doc_result["score"]
        
        # Calculate overall score
        result["overall_score"] = (
            syntax_score * 0.25 +
            style_score * 0.35 +
            doc_score * 0.40
        )
        
        # Assign grade
        if result["overall_score"] >= 0.9:
            result["grade"] = "A"
        elif result["overall_score"] >= 0.8:
            result["grade"] = "B"
        elif result["overall_score"] >= 0.7:
            result["grade"] = "C"
        elif result["overall_score"] >= 0.6:
            result["grade"] = "D"
        else:
            result["grade"] = "F"
        
        # Generate recommendations
        if not syntax_result["is_valid"]:
            result["recommendations"].append("Fix syntax errors before proceeding")
        
        if not style_result["is_compliant"]:
            result["recommendations"].extend([
                f"Address style violations: {len(style_result['violations'])} issues found",
                "Consider using ESLint and Prettier for automatic formatting"
            ])
        
        if doc_result["score"] < 0.7:
            result["recommendations"].extend(doc_result["suggestions"])
        
        return result
    
    def assess_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """
        Assess code quality for any supported language.
        
        Args:
            code: Code string to assess
            language: Programming language
            
        Returns:
            Dict with quality assessment results
        """
        language = language.lower()
        
        if language in ['python', 'py']:
            return self.assess_python_quality(code)
        elif language in ['javascript', 'js']:
            return self.assess_javascript_quality(code)
        else:
            return {
                "overall_score": 0.0,
                "error": f"Unsupported language: {language}",
                "grade": "F"
            }


def generate_quality_report(assessment: Dict[str, Any], language: str) -> str:
    """
    Generate a human-readable quality report.
    
    Args:
        assessment: Quality assessment results
        language: Programming language
        
    Returns:
        Formatted quality report string
    """
    if "error" in assessment:
        return f"Error: {assessment['error']}"
    
    report = f"""
Code Quality Assessment Report ({language.title()})
{'=' * 50}

Overall Grade: {assessment['grade']} ({assessment['overall_score']:.1%})

Syntax: {'✓ Valid' if assessment['syntax_valid'] else '✗ Invalid'}
Style: {'✓ Compliant' if assessment['style_compliant'] else '✗ Non-compliant'}
Documentation: {'✓ Well documented' if assessment['well_documented'] else '✗ Needs improvement'}

"""
    
    if assessment.get("recommendations"):
        report += "Recommendations:\n"
        for i, rec in enumerate(assessment["recommendations"], 1):
            report += f"{i}. {rec}\n"
    
    return report