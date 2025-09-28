#!/usr/bin/env python3
"""
Olympus-Coder-v1 Health Check Script

Comprehensive health checks for model deployment verification.
"""

import json
import sys
import time
import requests
import argparse
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class HealthChecker:
    """Comprehensive health checker for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        self.results = []
        
    def log_result(self, test_name: str, passed: bool, details: str = "", 
                   response_time: float = 0.0):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if response_time > 0:
            print(f"    Response time: {response_time:.2f}s")
        
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_ollama_service(self) -> bool:
        """Check if Ollama service is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.log_result("Ollama Service", True, f"Service running on {self.host}:{self.port}")
                return True
            else:
                self.log_result("Ollama Service", False, f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_result("Ollama Service", False, f"Connection failed: {str(e)}")
            return False
    
    def check_model_availability(self) -> bool:
        """Check if the model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_found = any(model.get("name") == self.model_name for model in models)
                
                if model_found:
                    # Get model details
                    model_info = next((m for m in models if m.get("name") == self.model_name), {})
                    size = model_info.get("size", "Unknown")
                    modified = model_info.get("modified_at", "Unknown")
                    
                    self.log_result("Model Availability", True, 
                                  f"Model found (Size: {size}, Modified: {modified})")
                    return True
                else:
                    available_models = [m.get("name", "Unknown") for m in models]
                    self.log_result("Model Availability", False, 
                                  f"Model not found. Available: {', '.join(available_models)}")
                    return False
            else:
                self.log_result("Model Availability", False, f"API error: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Model Availability", False, f"Error: {str(e)}")
            return False
    
    def test_basic_response(self) -> bool:
        """Test basic model response capability"""
        try:
            start_time = time.time()
            
            payload = {
                "model": self.model_name,
                "prompt": "Respond with exactly: 'Health check successful'",
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                if "Health check successful" in response_text:
                    self.log_result("Basic Response", True, 
                                  f"Correct response received", response_time)
                    return True
                else:
                    self.log_result("Basic Response", False, 
                                  f"Unexpected response: {response_text[:100]}...", response_time)
                    return False
            else:
                self.log_result("Basic Response", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Basic Response", False, f"Error: {str(e)}")
            return False
    
    def test_code_generation(self) -> bool:
        """Test code generation capability"""
        try:
            start_time = time.time()
            
            payload = {
                "model": self.model_name,
                "prompt": "Generate a Python function that adds two numbers. Use proper formatting with code blocks.",
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=45)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check for code block formatting
                has_code_block = "```python" in response_text
                has_function = "def " in response_text
                has_return = "return" in response_text
                
                if has_code_block and has_function and has_return:
                    self.log_result("Code Generation", True, 
                                  "Generated properly formatted Python function", response_time)
                    return True
                else:
                    missing = []
                    if not has_code_block: missing.append("code blocks")
                    if not has_function: missing.append("function definition")
                    if not has_return: missing.append("return statement")
                    
                    self.log_result("Code Generation", False, 
                                  f"Missing: {', '.join(missing)}", response_time)
                    return False
            else:
                self.log_result("Code Generation", False, 
                              f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Code Generation", False, f"Error: {str(e)}")
            return False
    
    def test_json_output(self) -> bool:
        """Test structured JSON output capability"""
        try:
            start_time = time.time()
            
            payload = {
                "model": self.model_name,
                "prompt": "I need to read a file. Provide a JSON tool request with tool_name and parameters fields.",
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Look for JSON structure
                has_json_structure = "{" in response_text and "}" in response_text
                has_tool_name = "tool_name" in response_text
                has_parameters = "parameters" in response_text
                
                if has_json_structure and has_tool_name and has_parameters:
                    self.log_result("JSON Output", True, 
                                  "Generated structured JSON response", response_time)
                    return True
                else:
                    missing = []
                    if not has_json_structure: missing.append("JSON structure")
                    if not has_tool_name: missing.append("tool_name field")
                    if not has_parameters: missing.append("parameters field")
                    
                    self.log_result("JSON Output", False, 
                                  f"Missing: {', '.join(missing)}", response_time)
                    return False
            else:
                self.log_result("JSON Output", False, 
                              f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("JSON Output", False, f"Error: {str(e)}")
            return False
    
    def test_performance_benchmark(self) -> bool:
        """Test response time performance"""
        try:
            times = []
            
            for i in range(3):
                start_time = time.time()
                
                payload = {
                    "model": self.model_name,
                    "prompt": f"Count from 1 to 5. Test {i+1}",
                    "stream": False
                }
                
                response = requests.post(self.api_url, json=payload, timeout=20)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    times.append(response_time)
                else:
                    self.log_result("Performance Benchmark", False, 
                                  f"Request {i+1} failed: HTTP {response.status_code}")
                    return False
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            # Performance thresholds (adjustable)
            if avg_time < 10.0:  # Average under 10 seconds
                self.log_result("Performance Benchmark", True, 
                              f"Avg: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s")
                return True
            else:
                self.log_result("Performance Benchmark", False, 
                              f"Too slow - Avg: {avg_time:.2f}s (threshold: 10s)")
                return False
                
        except Exception as e:
            self.log_result("Performance Benchmark", False, f"Error: {str(e)}")
            return False
    
    def run_health_checks(self, include_performance: bool = True) -> Tuple[bool, Dict]:
        """Run all health checks"""
        print(f"🏥 Running health checks for {self.model_name}")
        print(f"🌐 Target: {self.host}:{self.port}")
        print("=" * 50)
        
        # Core health checks
        checks = [
            self.check_ollama_service,
            self.check_model_availability,
            self.test_basic_response,
            self.test_code_generation,
            self.test_json_output
        ]
        
        # Add performance test if requested
        if include_performance:
            checks.append(self.test_performance_benchmark)
        
        # Run all checks
        passed_count = 0
        for check in checks:
            if check():
                passed_count += 1
            time.sleep(0.5)  # Brief pause between tests
        
        # Calculate results
        total_checks = len(checks)
        success_rate = passed_count / total_checks
        overall_health = success_rate >= 0.8  # 80% pass rate required
        
        print("=" * 50)
        print(f"📊 Health Check Results:")
        print(f"   Passed: {passed_count}/{total_checks} ({success_rate:.1%})")
        print(f"   Overall Health: {'✅ HEALTHY' if overall_health else '❌ UNHEALTHY'}")
        
        # Generate report
        report = {
            "model_name": self.model_name,
            "endpoint": f"{self.host}:{self.port}",
            "timestamp": datetime.now().isoformat(),
            "overall_health": overall_health,
            "success_rate": success_rate,
            "passed_count": passed_count,
            "total_checks": total_checks,
            "results": self.results
        }
        
        return overall_health, report

def main():
    parser = argparse.ArgumentParser(description="Health check for Olympus-Coder-v1")
    parser.add_argument("--model", default="olympus-coder-v1", 
                       help="Model name to check")
    parser.add_argument("--host", default="localhost", 
                       help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, 
                       help="Ollama port")
    parser.add_argument("--no-performance", action="store_true", 
                       help="Skip performance benchmarks")
    parser.add_argument("--output", help="Save report to JSON file")
    
    args = parser.parse_args()
    
    checker = HealthChecker(args.model, args.host, args.port)
    healthy, report = checker.run_health_checks(not args.no_performance)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {args.output}")
    
    sys.exit(0 if healthy else 1)

if __name__ == "__main__":
    main()