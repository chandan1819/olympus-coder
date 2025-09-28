#!/usr/bin/env python3
"""
Olympus-Coder-v1 Validation and Testing Script

This script validates the model's functionality and runs comprehensive tests
to ensure it meets the specified requirements.
"""

import json
import sys
import argparse
import requests
import time
from typing import Dict, List, Any, Optional

class ModelValidator:
    """Validates Olympus-Coder-v1 model functionality"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        
    def check_model_availability(self) -> bool:
        """Check if the model is available in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model.get("name") == self.model_name for model in models)
            return False
        except Exception as e:
            print(f"❌ Error checking model availability: {e}")
            return False
    
    def send_prompt(self, prompt: str, stream: bool = False) -> Optional[Dict]:
        """Send a prompt to the model and return the response"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": stream
            }
            
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error sending prompt: {e}")
            return None
    
    def test_basic_functionality(self) -> bool:
        """Test basic model response functionality"""
        print("🧪 Testing basic functionality...")
        
        response = self.send_prompt("Hello, can you respond?")
        if response and "response" in response:
            print("✅ Basic functionality test passed")
            return True
        else:
            print("❌ Basic functionality test failed")
            return False
    
    def test_code_generation(self) -> bool:
        """Test code generation capabilities"""
        print("🧪 Testing code generation...")
        
        prompt = "Generate a simple Python function that adds two numbers"
        response = self.send_prompt(prompt)
        
        if response and "response" in response:
            response_text = response["response"]
            # Check for code block formatting
            if "```python" in response_text and "def " in response_text:
                print("✅ Code generation test passed")
                return True
        
        print("❌ Code generation test failed")
        return False
    
    def test_json_output(self) -> bool:
        """Test structured JSON output for tool usage"""
        print("🧪 Testing JSON output formatting...")
        
        prompt = """I need to read a file called 'config.json'. 
        Please provide the appropriate tool request in JSON format."""
        
        response = self.send_prompt(prompt)
        
        if response and "response" in response:
            response_text = response["response"]
            # Look for JSON-like structure
            if "{" in response_text and "tool_name" in response_text:
                print("✅ JSON output test passed")
                return True
        
        print("❌ JSON output test failed")
        return False
    
    def run_quick_tests(self) -> bool:
        """Run a quick validation suite"""
        print(f"🚀 Running quick validation for {self.model_name}...")
        
        if not self.check_model_availability():
            print(f"❌ Model {self.model_name} not found")
            return False
        
        print(f"✅ Model {self.model_name} is available")
        
        tests = [
            self.test_basic_functionality,
            self.test_code_generation,
            self.test_json_output
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        success_rate = passed / len(tests)
        print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            print("🎉 Validation successful!")
            return True
        else:
            print("⚠️  Validation completed with issues")
            return False
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive test suite (placeholder for future implementation)"""
        print("🧪 Comprehensive testing not yet implemented")
        print("This will be implemented in tasks 5.1-5.4 of the implementation plan")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate Olympus-Coder-v1 model")
    parser.add_argument("--model", default="olympus-coder-v1", 
                       help="Model name to validate")
    parser.add_argument("--host", default="localhost", 
                       help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, 
                       help="Ollama port")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick validation only")
    parser.add_argument("--comprehensive", action="store_true", 
                       help="Run comprehensive test suite")
    
    args = parser.parse_args()
    
    validator = ModelValidator(args.model, args.host, args.port)
    
    if args.quick:
        success = validator.run_quick_tests()
    elif args.comprehensive:
        success = validator.run_comprehensive_tests()
    else:
        # Default to quick tests
        success = validator.run_quick_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()