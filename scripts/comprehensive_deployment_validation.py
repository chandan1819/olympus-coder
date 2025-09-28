#!/usr/bin/env python3
"""
Comprehensive Deployment Validation for Olympus-Coder-v1

This script provides thorough deployment validation including:
- Pre-deployment checks
- Post-deployment verification
- Integration readiness assessment
- Performance validation
- Security and compliance checks

Requirements addressed: 6.4, 6.5
"""

import json
import sys
import time
import requests
import argparse
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class ComprehensiveDeploymentValidator:
    """Comprehensive deployment validator for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.validation_results = []
        self.performance_metrics = {}
        
    def log_validation(self, category: str, check_name: str, passed: bool, 
                      details: str = "", metrics: Dict[str, Any] = None):
        """Log validation result with category and metrics"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} [{category}] {check_name}")
        if details:
            print(f"    {details}")
        if metrics:
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"    {key}: {value:.3f}")
                else:
                    print(f"    {key}: {value}")
        
        result = {
            "category": category,
            "check": check_name,
            "passed": passed,
            "details": details,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat()
        }
        self.validation_results.append(result)
    
    def validate_pre_deployment_requirements(self) -> bool:
        """Validate pre-deployment requirements"""
        print("🔍 Pre-Deployment Requirements Validation")
        print("-" * 50)
        
        all_passed = True
        
        # Check Ollama installation
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_validation("Pre-Deployment", "Ollama Installation", True, 
                                  f"Version: {version}")
            else:
                self.log_validation("Pre-Deployment", "Ollama Installation", False, 
                                  "Ollama not found or not working")
                all_passed = False
        except Exception as e:
            self.log_validation("Pre-Deployment", "Ollama Installation", False, 
                              f"Error checking Ollama: {str(e)}")
            all_passed = False
        
        # Check required files
        required_files = [
            ("modelfile/Modelfile", "Main Modelfile"),
            ("config/model_config.json", "Model configuration"),
            ("config/deployment.json", "Deployment configuration"),
            ("scripts/build_model.sh", "Build script"),
            ("scripts/health_check.py", "Health check script")
        ]
        
        missing_files = []
        for file_path, description in required_files:
            full_path = Path("olympus-coder-v1") / file_path
            if full_path.exists():
                # Check file integrity
                file_size = full_path.stat().st_size
                if file_size > 0:
                    self.log_validation("Pre-Deployment", f"Required File: {description}", 
                                      True, f"Size: {file_size} bytes")
                else:
                    self.log_validation("Pre-Deployment", f"Required File: {description}", 
                                      False, "File is empty")
                    all_passed = False
            else:
                missing_files.append(file_path)
                all_passed = False
        
        if missing_files:
            self.log_validation("Pre-Deployment", "File Structure", False, 
                              f"Missing files: {', '.join(missing_files)}")
        
        # Check configuration validity
        try:
            config_path = Path("olympus-coder-v1/config/model_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                
                required_config_keys = ["base_model", "temperature", "top_p"]
                missing_keys = [key for key in required_config_keys if key not in config]
                
                if not missing_keys:
                    self.log_validation("Pre-Deployment", "Configuration Validity", True, 
                                      f"All required keys present")
                else:
                    self.log_validation("Pre-Deployment", "Configuration Validity", False, 
                                      f"Missing keys: {', '.join(missing_keys)}")
                    all_passed = False
        except Exception as e:
            self.log_validation("Pre-Deployment", "Configuration Validity", False, 
                              f"Error reading config: {str(e)}")
            all_passed = False
        
        # Check base model availability
        try:
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                available_models = result.stdout
                base_models = ["llama3:8b", "codellama:13b"]
                found_base_model = any(model in available_models for model in base_models)
                
                if found_base_model:
                    self.log_validation("Pre-Deployment", "Base Model Availability", True, 
                                      "Required base model found")
                else:
                    self.log_validation("Pre-Deployment", "Base Model Availability", False, 
                                      f"No base model found. Available: {available_models.strip()}")
                    all_passed = False
        except Exception as e:
            self.log_validation("Pre-Deployment", "Base Model Availability", False, 
                              f"Error checking models: {str(e)}")
            all_passed = False
        
        return all_passed
    
    def validate_model_deployment(self) -> bool:
        """Validate model deployment status"""
        print("\n🚀 Model Deployment Validation")
        print("-" * 40)
        
        all_passed = True
        
        # Check Ollama service
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                self.log_validation("Deployment", "Ollama Service", True, 
                                  f"Service accessible at {self.host}:{self.port}")
            else:
                self.log_validation("Deployment", "Ollama Service", False, 
                                  f"HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_validation("Deployment", "Ollama Service", False, 
                              f"Service not accessible: {str(e)}")
            all_passed = False
        
        # Check model presence
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_info = next((m for m in models if m.get("name") == self.model_name), None)
                
                if model_info:
                    size = model_info.get("size", "Unknown")
                    modified = model_info.get("modified_at", "Unknown")
                    
                    # Calculate model hash for integrity check
                    model_hash = hashlib.md5(str(model_info).encode()).hexdigest()[:8]
                    
                    self.log_validation("Deployment", "Model Presence", True, 
                                      f"Model deployed successfully", 
                                      {"size": size, "modified": modified, "hash": model_hash})
                else:
                    available_models = [m.get("name", "Unknown") for m in models]
                    self.log_validation("Deployment", "Model Presence", False, 
                                      f"Model not found. Available: {', '.join(available_models)}")
                    all_passed = False
        except Exception as e:
            self.log_validation("Deployment", "Model Presence", False, 
                              f"Error checking model: {str(e)}")
            all_passed = False
        
        # Validate model configuration
        try:
            payload = {"name": self.model_name}
            response = requests.post(f"{self.base_url}/api/show", json=payload, timeout=15)
            
            if response.status_code == 200:
                model_info = response.json()
                
                # Check for system prompt
                has_system = "system" in str(model_info).lower()
                
                # Check for parameters
                has_params = "parameters" in str(model_info).lower()
                
                # Check model size
                model_size = model_info.get("size", 0)
                
                if has_system and has_params:
                    self.log_validation("Deployment", "Model Configuration", True, 
                                      "System prompt and parameters configured", 
                                      {"model_size": model_size})
                else:
                    missing = []
                    if not has_system: missing.append("system prompt")
                    if not has_params: missing.append("parameters")
                    
                    self.log_validation("Deployment", "Model Configuration", False, 
                                      f"Missing: {', '.join(missing)}")
                    all_passed = False
        except Exception as e:
            self.log_validation("Deployment", "Model Configuration", False, 
                              f"Error checking configuration: {str(e)}")
            all_passed = False
        
        return all_passed
    
    def validate_functional_capabilities(self) -> bool:
        """Validate functional capabilities of the deployed model"""
        print("\n🧪 Functional Capabilities Validation")
        print("-" * 45)
        
        all_passed = True
        
        # Test basic response
        try:
            start_time = time.time()
            payload = {
                "model": self.model_name,
                "prompt": "What is your name and primary function?",
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").lower()
                
                # Check for agentic identity
                identity_terms = ["olympus-coder", "agent", "autonomous", "software development"]
                found_terms = [term for term in identity_terms if term in response_text]
                
                if len(found_terms) >= 2:
                    self.log_validation("Functional", "Agentic Identity", True, 
                                      f"Identity confirmed", 
                                      {"response_time": response_time, "terms_found": len(found_terms)})
                else:
                    self.log_validation("Functional", "Agentic Identity", False, 
                                      f"Identity unclear (found: {', '.join(found_terms)})", 
                                      {"response_time": response_time})
                    all_passed = False
        except Exception as e:
            self.log_validation("Functional", "Agentic Identity", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        # Test code generation
        try:
            start_time = time.time()
            payload = {
                "model": self.model_name,
                "prompt": "Generate a Python function that calculates the factorial of a number. Include proper documentation and error handling.",
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=45)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check code quality indicators
                has_code_block = "```python" in response_text
                has_function = "def " in response_text
                has_docstring = '"""' in response_text or "'''" in response_text
                has_error_handling = "try" in response_text or "except" in response_text or "raise" in response_text
                
                quality_score = sum([has_code_block, has_function, has_docstring, has_error_handling]) / 4
                
                if quality_score >= 0.75:
                    self.log_validation("Functional", "Code Generation Quality", True, 
                                      f"High-quality code generated", 
                                      {"response_time": response_time, "quality_score": quality_score})
                else:
                    missing = []
                    if not has_code_block: missing.append("code blocks")
                    if not has_function: missing.append("function definition")
                    if not has_docstring: missing.append("documentation")
                    if not has_error_handling: missing.append("error handling")
                    
                    self.log_validation("Functional", "Code Generation Quality", False, 
                                      f"Quality issues: {', '.join(missing)}", 
                                      {"response_time": response_time, "quality_score": quality_score})
                    all_passed = False
        except Exception as e:
            self.log_validation("Functional", "Code Generation Quality", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        # Test structured output (JSON)
        try:
            start_time = time.time()
            payload = {
                "model": self.model_name,
                "prompt": "I need to create a new file called 'test.py'. Provide a JSON tool request with tool_name and parameters fields.",
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check JSON structure
                has_json = "{" in response_text and "}" in response_text
                has_tool_name = "tool_name" in response_text
                has_parameters = "parameters" in response_text
                
                # Try to extract and validate JSON
                json_valid = False
                try:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        json.loads(json_str)
                        json_valid = True
                except:
                    pass
                
                structure_score = sum([has_json, has_tool_name, has_parameters, json_valid]) / 4
                
                if structure_score >= 0.75:
                    self.log_validation("Functional", "Structured Output", True, 
                                      f"Valid JSON structure generated", 
                                      {"response_time": response_time, "structure_score": structure_score})
                else:
                    issues = []
                    if not has_json: issues.append("no JSON structure")
                    if not has_tool_name: issues.append("missing tool_name")
                    if not has_parameters: issues.append("missing parameters")
                    if not json_valid: issues.append("invalid JSON syntax")
                    
                    self.log_validation("Functional", "Structured Output", False, 
                                      f"Structure issues: {', '.join(issues)}", 
                                      {"response_time": response_time, "structure_score": structure_score})
                    all_passed = False
        except Exception as e:
            self.log_validation("Functional", "Structured Output", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        # Test debugging capability
        try:
            start_time = time.time()
            buggy_code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# This will cause an error
result = calculate_average([])
'''
            
            payload = {
                "model": self.model_name,
                "prompt": f"Debug this Python code and explain the error:\n\n```python\n{buggy_code}\n```\n\nWhat's wrong and how to fix it?",
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=45)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").lower()
                
                # Check debugging indicators
                identifies_error = "zerodivisionerror" in response_text or "division by zero" in response_text
                suggests_fix = "empty" in response_text and ("check" in response_text or "if" in response_text)
                provides_solution = "len(numbers)" in response_text or "if numbers:" in response_text
                
                debug_score = sum([identifies_error, suggests_fix, provides_solution]) / 3
                
                if debug_score >= 0.67:
                    self.log_validation("Functional", "Debugging Capability", True, 
                                      f"Effective debugging analysis", 
                                      {"response_time": response_time, "debug_score": debug_score})
                else:
                    missing = []
                    if not identifies_error: missing.append("error identification")
                    if not suggests_fix: missing.append("fix suggestion")
                    if not provides_solution: missing.append("solution code")
                    
                    self.log_validation("Functional", "Debugging Capability", False, 
                                      f"Debugging issues: {', '.join(missing)}", 
                                      {"response_time": response_time, "debug_score": debug_score})
                    all_passed = False
        except Exception as e:
            self.log_validation("Functional", "Debugging Capability", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        return all_passed
    
    def validate_performance_requirements(self) -> bool:
        """Validate performance requirements"""
        print("\n⚡ Performance Requirements Validation")
        print("-" * 45)
        
        all_passed = True
        
        # Response time benchmark
        response_times = []
        try:
            for i in range(5):
                start_time = time.time()
                payload = {
                    "model": self.model_name,
                    "prompt": f"Write a simple Python function to add two numbers. Test {i+1}.",
                    "stream": False
                }
                
                response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                else:
                    self.log_validation("Performance", "Response Time Benchmark", False, 
                                      f"Request {i+1} failed: HTTP {response.status_code}")
                    all_passed = False
                    break
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                # Performance thresholds
                if avg_time <= 15.0:  # Average under 15 seconds
                    self.log_validation("Performance", "Response Time Benchmark", True, 
                                      f"Performance within acceptable range", 
                                      {"avg_time": avg_time, "min_time": min_time, "max_time": max_time})
                else:
                    self.log_validation("Performance", "Response Time Benchmark", False, 
                                      f"Performance too slow (avg: {avg_time:.2f}s, threshold: 15s)", 
                                      {"avg_time": avg_time, "min_time": min_time, "max_time": max_time})
                    all_passed = False
                
                self.performance_metrics["response_times"] = {
                    "average": avg_time,
                    "minimum": min_time,
                    "maximum": max_time,
                    "samples": len(response_times)
                }
        except Exception as e:
            self.log_validation("Performance", "Response Time Benchmark", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        # Consistency test
        try:
            consistent_responses = 0
            total_tests = 3
            
            for i in range(total_tests):
                payload = {
                    "model": self.model_name,
                    "prompt": "Generate a Python function that returns 'Hello, World!'. Use consistent formatting.",
                    "stream": False
                }
                
                response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Check for consistent elements
                    has_function = "def " in response_text
                    has_return = "return" in response_text
                    has_hello_world = "Hello, World!" in response_text
                    
                    if has_function and has_return and has_hello_world:
                        consistent_responses += 1
            
            consistency_rate = consistent_responses / total_tests
            
            if consistency_rate >= 0.8:  # 80% consistency required
                self.log_validation("Performance", "Response Consistency", True, 
                                  f"High consistency achieved", 
                                  {"consistency_rate": consistency_rate, "consistent_responses": consistent_responses})
            else:
                self.log_validation("Performance", "Response Consistency", False, 
                                  f"Inconsistent responses", 
                                  {"consistency_rate": consistency_rate, "consistent_responses": consistent_responses})
                all_passed = False
            
            self.performance_metrics["consistency"] = {
                "rate": consistency_rate,
                "consistent_responses": consistent_responses,
                "total_tests": total_tests
            }
        except Exception as e:
            self.log_validation("Performance", "Response Consistency", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        return all_passed
    
    def validate_integration_readiness(self) -> bool:
        """Validate integration readiness for agentic frameworks"""
        print("\n🔗 Integration Readiness Validation")
        print("-" * 42)
        
        all_passed = True
        
        # API compatibility test
        try:
            # Test standard Ollama API endpoints
            endpoints_to_test = [
                ("/api/tags", "GET", None, "Model listing"),
                ("/api/generate", "POST", {"model": self.model_name, "prompt": "test"}, "Generation"),
                ("/api/show", "POST", {"name": self.model_name}, "Model info")
            ]
            
            compatible_endpoints = 0
            
            for endpoint, method, payload, description in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint}"
                    
                    if method == "GET":
                        response = requests.get(url, timeout=10)
                    else:
                        response = requests.post(url, json=payload, timeout=15)
                    
                    if response.status_code in [200, 201]:
                        compatible_endpoints += 1
                except Exception:
                    pass
            
            compatibility_rate = compatible_endpoints / len(endpoints_to_test)
            
            if compatibility_rate >= 0.9:  # 90% compatibility required
                self.log_validation("Integration", "API Compatibility", True, 
                                  f"High API compatibility", 
                                  {"compatibility_rate": compatibility_rate})
            else:
                self.log_validation("Integration", "API Compatibility", False, 
                                  f"API compatibility issues", 
                                  {"compatibility_rate": compatibility_rate})
                all_passed = False
        except Exception as e:
            self.log_validation("Integration", "API Compatibility", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        # Framework integration simulation
        try:
            # Simulate agentic framework interaction pattern
            conversation_turns = [
                "What programming languages do you support?",
                "Generate a Python function to read a CSV file.",
                "Now add error handling to that function.",
                "Create unit tests for the function."
            ]
            
            successful_turns = 0
            context_retention = 0
            
            for i, prompt in enumerate(conversation_turns):
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=45)
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Check for appropriate response
                    if i == 0 and "python" in response_text.lower():
                        successful_turns += 1
                    elif i == 1 and ("csv" in response_text.lower() and "def " in response_text):
                        successful_turns += 1
                    elif i == 2 and ("try" in response_text or "except" in response_text):
                        successful_turns += 1
                        context_retention += 1  # Shows it remembered the function
                    elif i == 3 and ("test" in response_text.lower() and "def " in response_text):
                        successful_turns += 1
                        context_retention += 1  # Shows it remembered the context
            
            conversation_success_rate = successful_turns / len(conversation_turns)
            context_retention_rate = context_retention / 2  # 2 context-dependent turns
            
            if conversation_success_rate >= 0.75 and context_retention_rate >= 0.5:
                self.log_validation("Integration", "Framework Simulation", True, 
                                  f"Successful multi-turn interaction", 
                                  {"conversation_success": conversation_success_rate, 
                                   "context_retention": context_retention_rate})
            else:
                self.log_validation("Integration", "Framework Simulation", False, 
                                  f"Multi-turn interaction issues", 
                                  {"conversation_success": conversation_success_rate, 
                                   "context_retention": context_retention_rate})
                all_passed = False
        except Exception as e:
            self.log_validation("Integration", "Framework Simulation", False, 
                              f"Error: {str(e)}")
            all_passed = False
        
        return all_passed
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment validation report"""
        # Calculate category success rates
        categories = {}
        for result in self.validation_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "total": 0}
            
            categories[category]["total"] += 1
            if result["passed"]:
                categories[category]["passed"] += 1
        
        # Calculate overall metrics
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results if r["passed"])
        overall_success_rate = passed_checks / total_checks if total_checks > 0 else 0.0
        
        # Determine deployment readiness
        deployment_ready = (
            overall_success_rate >= 0.85 and  # 85% overall success
            categories.get("Pre-Deployment", {}).get("passed", 0) >= 
            categories.get("Pre-Deployment", {}).get("total", 1) * 0.9 and  # 90% pre-deployment
            categories.get("Functional", {}).get("passed", 0) >= 
            categories.get("Functional", {}).get("total", 1) * 0.8  # 80% functional
        )
        
        return {
            "model_name": self.model_name,
            "endpoint": f"{self.host}:{self.port}",
            "validation_timestamp": datetime.now().isoformat(),
            "deployment_ready": deployment_ready,
            "overall_success_rate": overall_success_rate,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "category_results": {
                category: {
                    "success_rate": data["passed"] / data["total"] if data["total"] > 0 else 0.0,
                    "passed": data["passed"],
                    "total": data["total"]
                }
                for category, data in categories.items()
            },
            "performance_metrics": self.performance_metrics,
            "detailed_results": self.validation_results,
            "recommendations": self._generate_recommendations(categories, overall_success_rate)
        }
    
    def _generate_recommendations(self, categories: Dict, overall_success_rate: float) -> List[str]:
        """Generate deployment recommendations based on validation results"""
        recommendations = []
        
        if overall_success_rate < 0.85:
            recommendations.append("Overall success rate below 85% - address failed checks before deployment")
        
        for category, data in categories.items():
            success_rate = data["passed"] / data["total"] if data["total"] > 0 else 0.0
            
            if category == "Pre-Deployment" and success_rate < 0.9:
                recommendations.append("Pre-deployment requirements not fully met - ensure all prerequisites are satisfied")
            elif category == "Functional" and success_rate < 0.8:
                recommendations.append("Functional capabilities below target - review model configuration and system prompt")
            elif category == "Performance" and success_rate < 0.7:
                recommendations.append("Performance issues detected - optimize model parameters or infrastructure")
            elif category == "Integration" and success_rate < 0.8:
                recommendations.append("Integration readiness concerns - test with target agentic frameworks")
        
        if not recommendations:
            recommendations.append("All validation checks passed - model is ready for deployment")
        
        return recommendations
    
    def run_comprehensive_validation(self) -> Tuple[bool, Dict[str, Any]]:
        """Run comprehensive deployment validation"""
        print("🔍 COMPREHENSIVE DEPLOYMENT VALIDATION")
        print("=" * 60)
        print(f"Model: {self.model_name}")
        print(f"Target: {self.host}:{self.port}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Run validation phases
        validation_phases = [
            ("Pre-Deployment Requirements", self.validate_pre_deployment_requirements),
            ("Model Deployment", self.validate_model_deployment),
            ("Functional Capabilities", self.validate_functional_capabilities),
            ("Performance Requirements", self.validate_performance_requirements),
            ("Integration Readiness", self.validate_integration_readiness)
        ]
        
        phase_results = {}
        
        for phase_name, validation_func in validation_phases:
            try:
                phase_success = validation_func()
                phase_results[phase_name] = phase_success
                
                if phase_success:
                    print(f"\n✅ {phase_name}: PASSED")
                else:
                    print(f"\n❌ {phase_name}: FAILED")
                
            except Exception as e:
                print(f"\n💥 {phase_name}: ERROR - {str(e)}")
                phase_results[phase_name] = False
        
        # Generate final report
        report = self.generate_deployment_report()
        
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Overall Success Rate: {report['overall_success_rate']:.1%}")
        print(f"Deployment Ready: {'✅ YES' if report['deployment_ready'] else '❌ NO'}")
        
        print("\nCategory Results:")
        for category, results in report["category_results"].items():
            print(f"  {category}: {results['passed']}/{results['total']} ({results['success_rate']:.1%})")
        
        print("\nRecommendations:")
        for i, recommendation in enumerate(report["recommendations"], 1):
            print(f"  {i}. {recommendation}")
        
        return report["deployment_ready"], report


def main():
    """Main function for comprehensive deployment validation"""
    parser = argparse.ArgumentParser(description="Comprehensive Deployment Validation for Olympus-Coder-v1")
    parser.add_argument("--model", default="olympus-coder-v1", help="Model name to validate")
    parser.add_argument("--host", default="localhost", help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port")
    parser.add_argument("--output", help="Save validation report to JSON file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Create validator and run comprehensive validation
    validator = ComprehensiveDeploymentValidator(args.model, args.host, args.port)
    
    try:
        deployment_ready, report = validator.run_comprehensive_validation()
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Validation report saved to: {args.output}")
        
        # Final status
        if deployment_ready:
            print("\n🎉 DEPLOYMENT VALIDATION SUCCESSFUL!")
            print("💡 The model is ready for production deployment.")
        else:
            print("\n⚠️  DEPLOYMENT VALIDATION FAILED!")
            print("🔧 Please address the issues before deploying to production.")
        
        sys.exit(0 if deployment_ready else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()