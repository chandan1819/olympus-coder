"""
Context validation framework for Olympus-Coder-v1.

Validates file path accuracy, import statements, and naming consistency
against provided project context.
"""

import os
import re
import ast
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path


class ProjectContext:
    """Represents the project structure and context information."""
    
    def __init__(self, file_paths: List[str] = None, directory_structure: Dict[str, Any] = None):
        """
        Initialize project context.
        
        Args:
            file_paths: List of valid file paths in the project
            directory_structure: Nested dict representing directory structure
        """
        self.file_paths = set(file_paths or [])
        self.directory_structure = directory_structure or {}
        
        # Extract directory paths from file paths
        self.directory_paths = set()
        for file_path in self.file_paths:
            path_parts = Path(file_path).parts
            for i in range(1, len(path_parts)):
                dir_path = str(Path(*path_parts[:i]))
                self.directory_paths.add(dir_path)
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file path exists in the project context."""
        return file_path in self.file_paths
    
    def directory_exists(self, dir_path: str) -> bool:
        """Check if a directory path exists in the project context."""
        return dir_path in self.directory_paths
    
    def get_python_modules(self) -> Set[str]:
        """Get all Python module names from the project."""
        modules = set()
        for file_path in self.file_paths:
            if file_path.endswith('.py'):
                # Convert file path to module name
                module_path = file_path.replace('/', '.').replace('\\', '.')
                if module_path.endswith('.py'):
                    module_path = module_path[:-3]  # Remove .py extension
                modules.add(module_path)
        return modules
    
    def get_javascript_modules(self) -> Set[str]:
        """Get all JavaScript module names from the project."""
        modules = set()
        for file_path in self.file_paths:
            if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                modules.add(file_path)
        return modules


class ContextValidator:
    """Validates code against project context for consistency and accuracy."""
    
    def __init__(self, project_context: ProjectContext = None):
        """
        Initialize context validator.
        
        Args:
            project_context: ProjectContext instance with project information
        """
        self.project_context = project_context or ProjectContext()
    
    def validate_file_references(self, code: str, language: str) -> Dict[str, Any]:
        """
        Validate file path references in code against project context.
        
        Args:
            code: Code string to validate
            language: Programming language ('python', 'javascript', etc.)
            
        Returns:
            Dict with validation results
        """
        result = {
            "is_valid": True,
            "file_references": [],
            "invalid_references": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Extract file references based on language
        if language.lower() in ['python', 'py']:
            references = self._extract_python_file_references(code)
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            references = self._extract_javascript_file_references(code)
        else:
            result["warnings"].append(f"File reference validation not supported for {language}")
            return result
        
        result["file_references"] = references
        
        # Validate each reference
        for ref in references:
            if not self.project_context.file_exists(ref):
                result["invalid_references"].append(ref)
                result["is_valid"] = False
        
        # Generate suggestions for invalid references
        for invalid_ref in result["invalid_references"]:
            similar_files = self._find_similar_files(invalid_ref)
            if similar_files:
                result["suggestions"].append(
                    f"'{invalid_ref}' not found. Did you mean: {', '.join(similar_files[:3])}?"
                )
        
        return result
    
    def validate_import_statements(self, code: str, language: str) -> Dict[str, Any]:
        """
        Validate import statements against project structure.
        
        Args:
            code: Code string to validate
            language: Programming language
            
        Returns:
            Dict with import validation results
        """
        result = {
            "is_valid": True,
            "imports": [],
            "invalid_imports": [],
            "circular_imports": [],
            "warnings": [],
            "suggestions": []
        }
        
        if language.lower() in ['python', 'py']:
            imports = self._extract_python_imports(code)
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            imports = self._extract_javascript_imports(code)
        else:
            result["warnings"].append(f"Import validation not supported for {language}")
            return result
        
        result["imports"] = imports
        
        # Validate imports against project context
        available_modules = (self.project_context.get_python_modules() 
                           if language.lower() in ['python', 'py'] 
                           else self.project_context.get_javascript_modules())
        
        for import_info in imports:
            module_name = import_info["module"]
            
            # Skip standard library and external packages for now
            if self._is_external_module(module_name, language):
                continue
            
            # Check if module exists in project
            if not self._module_exists_in_project(module_name, available_modules):
                result["invalid_imports"].append(import_info)
                result["is_valid"] = False
        
        return result
    
    def validate_naming_consistency(self, code: str, language: str, 
                                  existing_patterns: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """
        Validate naming conventions consistency with existing codebase.
        
        Args:
            code: Code string to validate
            language: Programming language
            existing_patterns: Dict of existing naming patterns in codebase
            
        Returns:
            Dict with naming consistency validation results
        """
        result = {
            "is_consistent": True,
            "naming_patterns": {},
            "inconsistencies": [],
            "suggestions": []
        }
        
        existing_patterns = existing_patterns or {}
        
        if language.lower() in ['python', 'py']:
            patterns = self._extract_python_naming_patterns(code)
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            patterns = self._extract_javascript_naming_patterns(code)
        else:
            result["suggestions"].append(f"Naming validation not supported for {language}")
            return result
        
        result["naming_patterns"] = patterns
        
        # Check consistency with existing patterns
        for pattern_type, names in patterns.items():
            if pattern_type in existing_patterns:
                existing_names = existing_patterns[pattern_type]
                inconsistencies = self._find_naming_inconsistencies(
                    names, existing_names, pattern_type
                )
                if inconsistencies:
                    result["inconsistencies"].extend(inconsistencies)
                    result["is_consistent"] = False
        
        return result
    
    def _extract_python_file_references(self, code: str) -> List[str]:
        """Extract file path references from Python code."""
        references = []
        
        # Look for string literals that might be file paths
        file_patterns = [
            r'["\']([^"\']*\.py)["\']',  # .py files
            r'["\']([^"\']*\.txt)["\']',  # .txt files
            r'["\']([^"\']*\.json)["\']',  # .json files
            r'["\']([^"\']*\.csv)["\']',  # .csv files
            r'["\']([^"\']*\.yaml)["\']',  # .yaml files
            r'["\']([^"\']*\.yml)["\']',  # .yml files
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, code)
            references.extend(matches)
        
        return references
    
    def _extract_javascript_file_references(self, code: str) -> List[str]:
        """Extract file path references from JavaScript/TypeScript code."""
        references = []
        
        # Look for import/require statements and string literals
        file_patterns = [
            r'["\']([^"\']*\.js)["\']',  # .js files
            r'["\']([^"\']*\.ts)["\']',  # .ts files
            r'["\']([^"\']*\.jsx)["\']',  # .jsx files
            r'["\']([^"\']*\.tsx)["\']',  # .tsx files
            r'["\']([^"\']*\.json)["\']',  # .json files
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, code)
            references.extend(matches)
        
        return references
    
    def _extract_python_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from Python code."""
        imports = []
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append({
                            "type": "from_import",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
        except SyntaxError:
            # If code has syntax errors, try regex fallback
            import_patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, code)
                for match in matches:
                    imports.append({
                        "type": "import",
                        "module": match,
                        "alias": None,
                        "line": 0
                    })
        
        return imports
    
    def _extract_javascript_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from JavaScript/TypeScript code."""
        imports = []
        
        # ES6 imports
        import_patterns = [
            r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
            r'import\s+["\']([^"\']+)["\']',
            r'require\s*\(\s*["\']([^"\']+)["\']\s*\)'
        ]
        
        lines = code.splitlines()
        for i, line in enumerate(lines, 1):
            for pattern in import_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    imports.append({
                        "type": "import",
                        "module": match,
                        "line": i
                    })
        
        return imports
    
    def _extract_python_naming_patterns(self, code: str) -> Dict[str, List[str]]:
        """Extract naming patterns from Python code."""
        patterns = {
            "functions": [],
            "classes": [],
            "variables": [],
            "constants": []
        }
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    patterns["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    patterns["classes"].append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            if name.isupper():
                                patterns["constants"].append(name)
                            else:
                                patterns["variables"].append(name)
        except SyntaxError:
            pass
        
        return patterns
    
    def _extract_javascript_naming_patterns(self, code: str) -> Dict[str, List[str]]:
        """Extract naming patterns from JavaScript/TypeScript code."""
        patterns = {
            "functions": [],
            "classes": [],
            "variables": [],
            "constants": []
        }
        
        lines = code.splitlines()
        
        # Function patterns
        func_patterns = [
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:function|\(.*?\)\s*=>)'
        ]
        
        # Class pattern
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        # Variable patterns
        var_patterns = [
            r'(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*='
        ]
        
        for line in lines:
            # Extract functions
            for pattern in func_patterns:
                matches = re.findall(pattern, line)
                patterns["functions"].extend(matches)
            
            # Extract classes
            matches = re.findall(class_pattern, line)
            patterns["classes"].extend(matches)
            
            # Extract variables
            for pattern in var_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if match.isupper():
                        patterns["constants"].append(match)
                    else:
                        patterns["variables"].append(match)
        
        return patterns
    
    def _find_similar_files(self, target_file: str) -> List[str]:
        """Find files similar to the target file name."""
        similar = []
        target_name = os.path.basename(target_file).lower()
        
        for file_path in self.project_context.file_paths:
            file_name = os.path.basename(file_path).lower()
            
            # Simple similarity check
            if target_name in file_name or file_name in target_name:
                similar.append(file_path)
            elif self._calculate_similarity(target_name, file_name) > 0.15:
                similar.append(file_path)
        
        return similar[:5]  # Return top 5 similar files
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity."""
        if not str1 or not str2:
            return 0.0
        
        # Simple Jaccard similarity using character bigrams
        bigrams1 = set(str1[i:i+2] for i in range(len(str1)-1))
        bigrams2 = set(str2[i:i+2] for i in range(len(str2)-1))
        
        if not bigrams1 and not bigrams2:
            return 1.0
        if not bigrams1 or not bigrams2:
            return 0.0
        
        intersection = len(bigrams1 & bigrams2)
        union = len(bigrams1 | bigrams2)
        
        return intersection / union
    
    def _is_external_module(self, module_name: str, language: str) -> bool:
        """Check if a module is external (standard library or third-party)."""
        if language.lower() in ['python', 'py']:
            # Common Python standard library modules
            stdlib_modules = {
                'os', 'sys', 'json', 'datetime', 'collections', 'itertools',
                'functools', 'operator', 'pathlib', 'typing', 're', 'math',
                'random', 'urllib', 'http', 'email', 'html', 'xml', 'csv',
                'sqlite3', 'logging', 'unittest', 'pytest', 'numpy', 'pandas'
            }
            return module_name.split('.')[0] in stdlib_modules
        
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            # Common Node.js modules and relative imports
            return (module_name.startswith('node:') or 
                   not module_name.startswith('.') and '/' not in module_name)
        
        return False
    
    def _module_exists_in_project(self, module_name: str, available_modules: Set[str]) -> bool:
        """Check if a module exists in the project."""
        # Direct match
        if module_name in available_modules:
            return True
        
        # Check for partial matches (e.g., 'utils.helpers' matches 'utils/helpers.py')
        for available in available_modules:
            if module_name.replace('.', '/') in available:
                return True
            if available.replace('/', '.').replace('\\', '.').startswith(module_name):
                return True
        
        return False
    
    def _find_naming_inconsistencies(self, new_names: List[str], 
                                   existing_names: List[str], 
                                   pattern_type: str) -> List[Dict[str, Any]]:
        """Find naming inconsistencies between new and existing names."""
        inconsistencies = []
        
        if not existing_names:
            return inconsistencies
        
        # Analyze existing naming patterns
        existing_patterns = self._analyze_naming_patterns(existing_names, pattern_type)
        
        for name in new_names:
            if not self._matches_naming_pattern(name, existing_patterns, pattern_type):
                inconsistencies.append({
                    "name": name,
                    "type": pattern_type,
                    "issue": f"Naming style inconsistent with existing {pattern_type}",
                    "suggestion": self._suggest_consistent_name(name, existing_patterns, pattern_type)
                })
        
        return inconsistencies
    
    def _analyze_naming_patterns(self, names: List[str], pattern_type: str) -> Dict[str, Any]:
        """Analyze naming patterns in a list of names."""
        patterns = {
            "snake_case": 0,
            "camelCase": 0,
            "PascalCase": 0,
            "UPPER_CASE": 0
        }
        
        for name in names:
            if re.match(r'^[a-z_][a-z0-9_]*$', name):
                patterns["snake_case"] += 1
            elif re.match(r'^[a-z][a-zA-Z0-9]*$', name):
                patterns["camelCase"] += 1
            elif re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
                patterns["PascalCase"] += 1
            elif re.match(r'^[A-Z_][A-Z0-9_]*$', name):
                patterns["UPPER_CASE"] += 1
        
        # Find dominant pattern
        dominant_pattern = max(patterns, key=patterns.get)
        return {
            "dominant": dominant_pattern,
            "counts": patterns
        }
    
    def _matches_naming_pattern(self, name: str, patterns: Dict[str, Any], pattern_type: str) -> bool:
        """Check if a name matches the dominant naming pattern."""
        dominant = patterns["dominant"]
        
        if dominant == "snake_case":
            return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None
        elif dominant == "camelCase":
            return re.match(r'^[a-z][a-zA-Z0-9]*$', name) is not None
        elif dominant == "PascalCase":
            return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
        elif dominant == "UPPER_CASE":
            return re.match(r'^[A-Z_][A-Z0-9_]*$', name) is not None
        
        return True  # If no clear pattern, accept anything
    
    def _suggest_consistent_name(self, name: str, patterns: Dict[str, Any], pattern_type: str) -> str:
        """Suggest a name that's consistent with existing patterns."""
        dominant = patterns["dominant"]
        
        if dominant == "snake_case":
            # Convert to snake_case
            return re.sub(r'([A-Z])', r'_\1', name).lower().strip('_')
        elif dominant == "camelCase":
            # Convert to camelCase
            words = re.split(r'[_\s]+', name.lower())
            return words[0] + ''.join(word.capitalize() for word in words[1:])
        elif dominant == "PascalCase":
            # Convert to PascalCase
            words = re.split(r'[_\s]+', name.lower())
            return ''.join(word.capitalize() for word in words)
        elif dominant == "UPPER_CASE":
            # Convert to UPPER_CASE
            return re.sub(r'([A-Z])', r'_\1', name).upper().strip('_')
        
        return name  # Return original if no clear pattern