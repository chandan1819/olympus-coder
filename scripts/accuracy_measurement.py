#!/usr/bin/env python3
"""
Olympus-Coder-v1 Accuracy Measurement and Reporting Tool

Comprehensive accuracy assessment against requirements and benchmarks.
"""

import json
import sys
import time
import requests
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class AccuracyMeasurement:
    """Comprehensive accuracy measurement for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        
        # Accuracy test cases mapped to requirements
        self.accuracy_tests = {
            "code_generation_accuracy": {
                "requirement": "1.1-1.6",
                "description": "Generate high-quality code with proper formatting",
                "tests": [
                    {
                        "prompt": "Generate a Python function that calculates the area of a circle",
                        "expected_elements": ["def", "pi", "radius", "return", "```python"],
                        "validation_criteria": {
                            "has_function_def": True,
                            "has_docstring": False,  # Optional
                            "has_return_statement": True,
                            "has_code_block": True,
                            "syntax_valid": True
                        }
                    },
                    {
                        "prompt": "Create a JavaScript function that validates an email address",
                        "expected_elements": ["function", "email", "return", "@", "```javascript"],
                        "validation_criteria": {
                            "has_function_def": True,
                            "has_return_statement": True,
                            "has_code_block": True,
                            "syntax_valid": True
                        }
                    },
                    {
                        "prompt": "Write a Python class for a simple calculator with add and subtract methods",
                        "expected_elements": ["class", "def", "add", "subtract", "self", "```python"],
                        "validation_criteria": {
                            "has_class_def": True,
                            "has_methods": True,
                            "has_code_block": True,
                            "syntax_valid": True
                        }
                    }
                ]
            },
            "debugging_accuracy": {
                "requirement": "2.1-2.5",
                "description": "Analyze and debug existing code effectively",
                "tests": [
                    {
                        "prompt": "Debug this Python code: 'def add(a, b): return a + b; result = add(5, '10'); print(result)'. What's wrong and how to fix it?",
                        "expected_elements": ["TypeError", "string", "int", "str()", "int()"],
                        "validation_criteria": {
                            "identifies_error_type": True,
                            "explains_cause": True,
                            "provides_solution": True
                        }
                    },
                    {
                        "prompt": "Fix this JavaScript error: 'Cannot read property 'length' of undefined' in the code: 'function getLength(arr) { return arr.length; }'",
                        "expected_elements": ["undefined", "null", "check", "if", "||"],
                        "validation_criteria": {
                            "identifies_error_type": True,
                            "explains_cause": True,
                            "provides_solution": True
                        }
                    }
                ]
            },
            "tool_usage_accuracy": {
                "requirement": "3.1-3.6",
                "description": "Determine when to use tools and format requests properly (>95% accuracy)",
                "tests": [
                    {
                        "prompt": "I need to read the contents of a file called 'config.json'. What should I do?",
                        "expected_elements": ["tool_name", "parameters", "read_file", "file_path"],
                        "validation_criteria": {
                            "has_json_structure": True,
                            "has_tool_name": True,
                            "has_parameters": True,
                            "correct_tool_selection": True
                        }
                    },
                    {
                        "prompt": "I want to create a new directory called 'output'. Provide the appropriate tool request.",
                        "expected_elements": ["tool_name", "parameters", "create_directory", "mkdir"],
                        "validation_criteria": {
                            "has_json_structure": True,
                            "has_tool_name": True,
                            "has_parameters": True,
                            "correct_tool_selection": True
                        }
                    },
                    {
                        "prompt": "Execute this Python script: 'print(\"Hello World\")'. What tool should I use?",
                        "expected_elements": ["tool_name", "parameters", "execute", "run", "python"],
                        "validation_criteria": {
                            "has_json_structure": True,
                            "has_tool_name": True,
                            "has_parameters": True,
                            "correct_tool_selection": True
                        }
                    }
                ]
            },
            "context_awareness_accuracy": {
                "requirement": "4.1-4.5",
                "description": "Understand project context accurately",
                "tests": [
                    {
                        "prompt": "Given this project structure: src/main.py, src/utils/helpers.py, config/settings.json - write an import statement to use helpers from main.py",
                        "expected_elements": ["from src.utils.helpers import", "import src.utils.helpers"],
                        "validation_criteria": {
                            "correct_import_path": True,
                            "no_hallucinated_files": True,
                            "follows_project_structure": True
                        }
                    },
                    {
                        "prompt": "In a project with files: app.js, package.json, src/components/Button.js - how would you import Button in app.js?",
                        "expected_elements": ["import", "from", "./src/components/Button", "require"],
                        "validation_criteria": {
                            "correct_import_path": True,
                            "no_hallucinated_files": True,
                            "follows_project_structure": True
                        }
                    }
                ]
            },
            "autonomous_completion_accuracy": {
                "requirement": "5.1-5.5",
                "description": "Complete coding tasks autonomously with high reliability (75% target)",
                "tests": [
                    {
                        "prompt": "Create a complete Python script that reads a CSV file, processes the data, and saves results to a new file. Include error handling.",
                        "expected_elements": ["import csv", "try", "except", "with open", "def"],
                        "validation_criteria": {
                            "complete_solution": True,
                            "has_error_handling": True,
                            "follows_best_practices": True,
                            "executable_code": True
                        }
                    },
                    {
                        "prompt": "Build a JavaScript function that fetches data from an API, handles errors, and returns formatted results.",
                        "expected_elements": ["async", "fetch", "try", "catch", "return", "json"],
                        "validation_criteria": {
                            "complete_solution": True,
                            "has_error_handling": True,
                            "follows_best_practices": True,
                            "executable_code": True
                        }
                    }
                ]
            }
        }
    
    def send_request(self, prompt: str, timeout: int = 45) -> Tuple[bool, str]:
        """Send request to model"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                return True, result.get("response", "")
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, f"Request error: {str(e)}"
    
    def validate_code_generation(self, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code generation response"""
        validation_results = {}
        
        # Check for function definition
        if criteria.get("has_function_def", False):
            validation_results["has_function_def"] = bool(re.search(r'\b(def|function)\s+\w+', response))
        
        # Check for class definition
        if criteria.get("has_class_def", False):
            validation_results["has_class_def"] = bool(re.search(r'\bclass\s+\w+', response))
        
        # Check for return statement
        if criteria.get("has_return_statement", False):
            validation_results["has_return_statement"] = "return" in response.lower()
        
        # Check for code block formatting
        if criteria.get("has_code_block", False):
            validation_results["has_code_block"] = "```" in response
        
        # Check for methods (in class context)
        if criteria.get("has_methods", False):
            validation_results["has_methods"] = bool(re.search(r'def\s+\w+\s*\(.*self', response))
        
        # Basic syntax validation (simplified)
        if criteria.get("syntax_valid", False):
            # Look for common syntax patterns
            has_proper_indentation = bool(re.search(r'\n    ', response))  # 4-space indentation
            has_colons = ":" in response
            validation_results["syntax_valid"] = has_proper_indentation and has_colons
        
        return validation_results
    
    def validate_debugging(self, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate debugging response"""
        validation_results = {}
        
        # Check if error type is identified
        if criteria.get("identifies_error_type", False):
            error_types = ["TypeError", "ValueError", "SyntaxError", "NameError", "AttributeError", "undefined", "null"]
            validation_results["identifies_error_type"] = any(error_type.lower() in response.lower() for error_type in error_types)
        
        # Check if cause is explained
        if criteria.get("explains_cause", False):
            explanation_keywords = ["because", "due to", "caused by", "reason", "problem is"]
            validation_results["explains_cause"] = any(keyword in response.lower() for keyword in explanation_keywords)
        
        # Check if solution is provided
        if criteria.get("provides_solution", False):
            solution_keywords = ["fix", "solution", "correct", "change", "modify", "should be"]
            validation_results["provides_solution"] = any(keyword in response.lower() for keyword in solution_keywords)
        
        return validation_results
    
    def validate_tool_usage(self, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool usage response"""
        validation_results = {}
        
        # Check for JSON structure
        if criteria.get("has_json_structure", False):
            validation_results["has_json_structure"] = "{" in response and "}" in response
        
        # Check for tool_name field
        if criteria.get("has_tool_name", False):
            validation_results["has_tool_name"] = "tool_name" in response
        
        # Check for parameters field
        if criteria.get("has_parameters", False):
            validation_results["has_parameters"] = "parameters" in response
        
        # Check for correct tool selection (simplified)
        if criteria.get("correct_tool_selection", False):
            tool_keywords = ["read_file", "write_file", "create_directory", "execute", "run", "mkdir"]
            validation_results["correct_tool_selection"] = any(keyword in response.lower() for keyword in tool_keywords)
        
        return validation_results
    
    def validate_context_awareness(self, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate context awareness response"""
        validation_results = {}
        
        # Check for correct import path
        if criteria.get("correct_import_path", False):
            import_patterns = [r'from\s+[\w./]+\s+import', r'import\s+[\w./]+', r'require\s*\(']
            validation_results["correct_import_path"] = any(re.search(pattern, response) for pattern in import_patterns)
        
        # Check for no hallucinated files (simplified - look for common hallucinations)
        if criteria.get("no_hallucinated_files", False):
            hallucination_indicators = ["lib/", "node_modules/", "dist/", "build/"]
            validation_results["no_hallucinated_files"] = not any(indicator in response for indicator in hallucination_indicators)
        
        # Check if follows project structure
        if criteria.get("follows_project_structure", False):
            structure_keywords = ["src/", "./", "../", "config/"]
            validation_results["follows_project_structure"] = any(keyword in response for keyword in structure_keywords)
        
        return validation_results
    
    def validate_autonomous_completion(self, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate autonomous completion response"""
        validation_results = {}
        
        # Check for complete solution
        if criteria.get("complete_solution", False):
            completeness_indicators = ["def", "function", "import", "return"]
            validation_results["complete_solution"] = sum(indicator in response.lower() for indicator in completeness_indicators) >= 2
        
        # Check for error handling
        if criteria.get("has_error_handling", False):
            error_handling_keywords = ["try", "catch", "except", "error", "throw"]
            validation_results["has_error_handling"] = any(keyword in response.lower() for keyword in error_handling_keywords)
        
        # Check for best practices
        if criteria.get("follows_best_practices", False):
            best_practice_indicators = ["with open", "async", "const", "let", "==="]
            validation_results["follows_best_practices"] = any(indicator in response for indicator in best_practice_indicators)
        
        # Check if code appears executable
        if criteria.get("executable_code", False):
            validation_results["executable_code"] = "```" in response and ("def " in response or "function " in response)
        
        return validation_results
    
    def run_accuracy_test_category(self, category_name: str) -> Dict[str, Any]:
        """Run accuracy tests for a specific category"""
        category = self.accuracy_tests[category_name]
        print(f"  📊 Testing: {category_name} - {category['description']}")
        
        results = {
            "category_name": category_name,
            "requirement": category["requirement"],
            "description": category["description"],
            "total_tests": len(category["tests"]),
            "passed_tests": 0,
            "failed_tests": 0,
            "test_results": [],
            "accuracy_score": 0.0
        }
        
        for i, test in enumerate(category["tests"]):
            print(f"    Test {i+1}/{len(category['tests'])}: {test['prompt'][:50]}...")
            
            # Send request
            success, response = self.send_request(test["prompt"])
            
            test_result = {
                "test_index": i,
                "prompt": test["prompt"],
                "success": success,
                "response": response if success else "",
                "error": response if not success else "",
                "expected_elements": test["expected_elements"],
                "validation_results": {},
                "element_coverage": 0.0,
                "criteria_coverage": 0.0,
                "overall_score": 0.0
            }
            
            if success:
                # Check expected elements
                found_elements = [elem for elem in test["expected_elements"] if elem.lower() in response.lower()]
                test_result["element_coverage"] = len(found_elements) / len(test["expected_elements"]) if test["expected_elements"] else 1.0
                
                # Validate against criteria
                criteria = test["validation_criteria"]
                
                if category_name == "code_generation_accuracy":
                    validation_results = self.validate_code_generation(response, criteria)
                elif category_name == "debugging_accuracy":
                    validation_results = self.validate_debugging(response, criteria)
                elif category_name == "tool_usage_accuracy":
                    validation_results = self.validate_tool_usage(response, criteria)
                elif category_name == "context_awareness_accuracy":
                    validation_results = self.validate_context_awareness(response, criteria)
                elif category_name == "autonomous_completion_accuracy":
                    validation_results = self.validate_autonomous_completion(response, criteria)
                else:
                    validation_results = {}
                
                test_result["validation_results"] = validation_results
                
                # Calculate criteria coverage
                if validation_results:
                    passed_criteria = sum(1 for result in validation_results.values() if result)
                    test_result["criteria_coverage"] = passed_criteria / len(validation_results)
                else:
                    test_result["criteria_coverage"] = 0.0
                
                # Calculate overall test score
                test_result["overall_score"] = (test_result["element_coverage"] + test_result["criteria_coverage"]) / 2
                
                # Determine if test passed (threshold: 70%)
                if test_result["overall_score"] >= 0.7:
                    results["passed_tests"] += 1
                else:
                    results["failed_tests"] += 1
            else:
                results["failed_tests"] += 1
            
            results["test_results"].append(test_result)
            time.sleep(1)  # Brief pause between tests
        
        # Calculate category accuracy score
        if results["test_results"]:
            scores = [test["overall_score"] for test in results["test_results"] if test["success"]]
            results["accuracy_score"] = sum(scores) / len(scores) if scores else 0.0
        
        return results
    
    def run_comprehensive_accuracy_assessment(self) -> Dict[str, Any]:
        """Run comprehensive accuracy assessment"""
        print(f"🎯 Starting comprehensive accuracy assessment for {self.model_name}")
        print("=" * 60)
        
        assessment_start = time.time()
        
        results = {
            "assessment_info": {
                "model_name": self.model_name,
                "start_time": datetime.now().isoformat(),
                "endpoint": f"{self.host}:{self.port}"
            },
            "category_results": {},
            "requirements_compliance": {},
            "overall_accuracy": {}
        }
        
        # Run tests for each category
        for category_name in self.accuracy_tests:
            try:
                category_results = self.run_accuracy_test_category(category_name)
                results["category_results"][category_name] = category_results
                
                # Log category summary
                accuracy = category_results["accuracy_score"]
                passed = category_results["passed_tests"]
                total = category_results["total_tests"]
                print(f"    ✅ {category_name}: {accuracy:.2%} accuracy ({passed}/{total} tests passed)")
                
            except Exception as e:
                print(f"    ❌ {category_name} failed: {str(e)}")
                results["category_results"][category_name] = {"error": str(e)}
        
        # Calculate requirements compliance
        results["requirements_compliance"] = self.calculate_requirements_compliance(results["category_results"])
        
        # Calculate overall accuracy metrics
        results["overall_accuracy"] = self.calculate_overall_accuracy(results["category_results"])
        
        # Finalize assessment info
        assessment_end = time.time()
        results["assessment_info"]["end_time"] = datetime.now().isoformat()
        results["assessment_info"]["total_duration"] = assessment_end - assessment_start
        
        return results
    
    def calculate_requirements_compliance(self, category_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate compliance with specific requirements"""
        compliance = {}
        
        # Requirement 1: Code Generation (target: high quality with proper formatting)
        if "code_generation_accuracy" in category_results:
            cg_results = category_results["code_generation_accuracy"]
            if "error" not in cg_results:
                compliance["requirement_1_code_generation"] = {
                    "target": "Generate high-quality code with proper formatting",
                    "accuracy": cg_results["accuracy_score"],
                    "threshold": 0.75,
                    "compliant": cg_results["accuracy_score"] >= 0.75
                }
        
        # Requirement 2: Debugging (target: effective analysis and debugging)
        if "debugging_accuracy" in category_results:
            db_results = category_results["debugging_accuracy"]
            if "error" not in db_results:
                compliance["requirement_2_debugging"] = {
                    "target": "Analyze and debug existing code effectively",
                    "accuracy": db_results["accuracy_score"],
                    "threshold": 0.70,
                    "compliant": db_results["accuracy_score"] >= 0.70
                }
        
        # Requirement 3: Tool Usage (target: >95% accuracy in structured response formatting)
        if "tool_usage_accuracy" in category_results:
            tu_results = category_results["tool_usage_accuracy"]
            if "error" not in tu_results:
                compliance["requirement_3_tool_usage"] = {
                    "target": "Achieve >95% accuracy in structured response formatting",
                    "accuracy": tu_results["accuracy_score"],
                    "threshold": 0.95,
                    "compliant": tu_results["accuracy_score"] >= 0.95
                }
        
        # Requirement 4: Context Awareness (target: accurate project understanding)
        if "context_awareness_accuracy" in category_results:
            ca_results = category_results["context_awareness_accuracy"]
            if "error" not in ca_results:
                compliance["requirement_4_context_awareness"] = {
                    "target": "Understand project context accurately",
                    "accuracy": ca_results["accuracy_score"],
                    "threshold": 0.70,
                    "compliant": ca_results["accuracy_score"] >= 0.70
                }
        
        # Requirement 5: Autonomous Completion (target: 75% completion rate)
        if "autonomous_completion_accuracy" in category_results:
            ac_results = category_results["autonomous_completion_accuracy"]
            if "error" not in ac_results:
                compliance["requirement_5_autonomous_completion"] = {
                    "target": "Achieve 75% autonomous completion rate",
                    "accuracy": ac_results["accuracy_score"],
                    "threshold": 0.75,
                    "compliant": ac_results["accuracy_score"] >= 0.75
                }
        
        # Calculate overall compliance
        compliant_requirements = sum(1 for req in compliance.values() if req.get("compliant", False))
        total_requirements = len(compliance)
        
        compliance["overall_compliance"] = {
            "compliant_count": compliant_requirements,
            "total_count": total_requirements,
            "compliance_rate": compliant_requirements / total_requirements if total_requirements > 0 else 0.0
        }
        
        return compliance
    
    def calculate_overall_accuracy(self, category_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall accuracy metrics"""
        accuracy_scores = []
        category_accuracies = {}
        
        for category_name, results in category_results.items():
            if "error" not in results and "accuracy_score" in results:
                accuracy_scores.append(results["accuracy_score"])
                category_accuracies[category_name] = results["accuracy_score"]
        
        overall_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        
        return {
            "overall_accuracy_score": overall_accuracy,
            "category_accuracies": category_accuracies,
            "accuracy_grade": self.calculate_accuracy_grade(overall_accuracy),
            "meets_target": overall_accuracy >= 0.75  # 75% target from requirements
        }
    
    def calculate_accuracy_grade(self, accuracy: float) -> str:
        """Calculate letter grade based on accuracy"""
        if accuracy >= 0.95:
            return "A+"
        elif accuracy >= 0.90:
            return "A"
        elif accuracy >= 0.85:
            return "B+"
        elif accuracy >= 0.80:
            return "B"
        elif accuracy >= 0.75:
            return "C+"
        elif accuracy >= 0.70:
            return "C"
        elif accuracy >= 0.65:
            return "D+"
        elif accuracy >= 0.60:
            return "D"
        else:
            return "F"
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive accuracy report"""
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 ACCURACY ASSESSMENT REPORT")
        report.append("=" * 50)
        
        info = results["assessment_info"]
        report.append(f"Model: {info['model_name']}")
        report.append(f"Endpoint: {info['endpoint']}")
        report.append(f"Assessment Time: {info['start_time']}")
        report.append(f"Duration: {info['total_duration']:.2f}s")
        report.append("")
        
        # Overall Accuracy
        overall = results["overall_accuracy"]
        report.append("OVERALL ACCURACY")
        report.append("-" * 17)
        report.append(f"Accuracy Score: {overall['overall_accuracy_score']:.2%}")
        report.append(f"Accuracy Grade: {overall['accuracy_grade']}")
        report.append(f"Meets Target (75%): {'✅ YES' if overall['meets_target'] else '❌ NO'}")
        report.append("")
        
        # Category Breakdown
        report.append("CATEGORY ACCURACY BREAKDOWN")
        report.append("-" * 28)
        
        for category, accuracy in overall["category_accuracies"].items():
            category_display = category.replace("_accuracy", "").replace("_", " ").title()
            report.append(f"{category_display}: {accuracy:.2%}")
        report.append("")
        
        # Requirements Compliance
        compliance = results["requirements_compliance"]
        report.append("REQUIREMENTS COMPLIANCE")
        report.append("-" * 23)
        
        for req_id, req_data in compliance.items():
            if req_id == "overall_compliance":
                continue
            
            status = "✅ COMPLIANT" if req_data["compliant"] else "❌ NON-COMPLIANT"
            report.append(f"{req_id.replace('_', ' ').title()}: {status}")
            report.append(f"  Target: {req_data['target']}")
            report.append(f"  Accuracy: {req_data['accuracy']:.2%} (threshold: {req_data['threshold']:.2%})")
            report.append("")
        
        overall_compliance = compliance["overall_compliance"]
        report.append(f"Overall Compliance: {overall_compliance['compliant_count']}/{overall_compliance['total_count']} "
                     f"({overall_compliance['compliance_rate']:.2%})")
        report.append("")
        
        # Detailed Results
        report.append("DETAILED CATEGORY RESULTS")
        report.append("-" * 27)
        
        for category_name, category_results in results["category_results"].items():
            if "error" in category_results:
                report.append(f"{category_name}: ERROR - {category_results['error']}")
                continue
            
            category_display = category_name.replace("_accuracy", "").replace("_", " ").title()
            report.append(f"{category_display}:")
            report.append(f"  Requirement: {category_results['requirement']}")
            report.append(f"  Tests: {category_results['passed_tests']}/{category_results['total_tests']} passed")
            report.append(f"  Accuracy: {category_results['accuracy_score']:.2%}")
            
            # Show individual test results
            for test_result in category_results["test_results"]:
                if test_result["success"]:
                    score = test_result["overall_score"]
                    status = "✅" if score >= 0.7 else "⚠️"
                    report.append(f"    Test {test_result['test_index']+1}: {status} {score:.2%}")
                else:
                    report.append(f"    Test {test_result['test_index']+1}: ❌ FAILED")
            
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        overall_accuracy = overall["overall_accuracy_score"]
        
        if overall_accuracy >= 0.90:
            report.append("🎉 Excellent accuracy! Model exceeds expectations.")
        elif overall_accuracy >= 0.75:
            report.append("✅ Good accuracy! Model meets requirements.")
        elif overall_accuracy >= 0.60:
            report.append("⚠️  Moderate accuracy. Some improvements needed.")
        else:
            report.append("❌ Poor accuracy. Significant improvements required.")
        
        # Specific recommendations based on category performance
        for category, accuracy in overall["category_accuracies"].items():
            if accuracy < 0.70:
                category_display = category.replace("_accuracy", "").replace("_", " ")
                report.append(f"⚠️  Improve {category_display} performance (current: {accuracy:.2%})")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Accuracy Measurement")
    parser.add_argument("--model", default="olympus-coder-v1",
                       help="Model name to assess")
    parser.add_argument("--host", default="localhost",
                       help="Ollama host")
    parser.add_argument("--port", type=int, default=11434,
                       help="Ollama port")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    assessor = AccuracyMeasurement(args.model, args.host, args.port)
    
    # Run assessment
    results = assessor.run_comprehensive_accuracy_assessment()
    
    # Generate and display report
    report = assessor.generate_report(results)
    print("\n" + "=" * 60)
    print("ACCURACY ASSESSMENT COMPLETE")
    print("=" * 60)
    print(report)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {args.output}")
    
    # Exit with appropriate code based on accuracy
    overall_accuracy = results["overall_accuracy"]["overall_accuracy_score"]
    success = overall_accuracy >= 0.75  # 75% target from requirements
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()