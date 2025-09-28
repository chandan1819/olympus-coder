#!/usr/bin/env python3
"""
Olympus-Coder-v1 Deployment Verification Script

Verifies successful deployment and integration readiness.
"""

import json
import sys
import time
import requests
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class DeploymentVerifier:
    """Verifies Olympus-Coder-v1 deployment and integration readiness"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.verification_results = []
        
    def log_verification(self, check_name: str, passed: bool, details: str = ""):
        """Log verification result"""
        status = "✅ VERIFIED" if passed else "❌ FAILED"
        print(f"{status} {check_name}")
        if details:
            print(f"    {details}")
        
        self.verification_results.append({
            "check": check_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def verify_model_build(self) -> bool:
        """Verify the model was built successfully"""
        try:
            # Check if model exists in Ollama
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_info = next((m for m in models if m.get("name") == self.model_name), None)
                
                if model_info:
                    size = model_info.get("size", "Unknown")
                    modified = model_info.get("modified_at", "Unknown")
                    self.log_verification("Model Build", True, 
                                        f"Model exists (Size: {size}, Modified: {modified})")
                    return True
                else:
                    self.log_verification("Model Build", False, "Model not found in Ollama registry")
                    return False
            else:
                self.log_verification("Model Build", False, f"Cannot access Ollama API: {response.status_code}")
                return False
        except Exception as e:
            self.log_verification("Model Build", False, f"Error checking model: {str(e)}")
            return False
    
    def verify_system_prompt_integration(self) -> bool:
        """Verify the system prompt is properly integrated"""
        try:
            # Test if the model responds with agentic behavior
            payload = {
                "model": self.model_name,
                "prompt": "What is your role and primary function?",
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").lower()
                
                # Check for key terms that should be in the system prompt
                agentic_terms = ["olympus-coder", "agent", "autonomous", "software development"]
                found_terms = [term for term in agentic_terms if term in response_text]
                
                if len(found_terms) >= 2:
                    self.log_verification("System Prompt Integration", True, 
                                        f"Agentic identity confirmed (found: {', '.join(found_terms)})")
                    return True
                else:
                    self.log_verification("System Prompt Integration", False, 
                                        f"Agentic identity not clear (found: {', '.join(found_terms)})")
                    return False
            else:
                self.log_verification("System Prompt Integration", False, 
                                    f"Cannot test system prompt: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_verification("System Prompt Integration", False, f"Error: {str(e)}")
            return False
    
    def verify_api_endpoints(self) -> bool:
        """Verify all required API endpoints are accessible"""
        endpoints = [
            ("/api/tags", "Model listing"),
            ("/api/generate", "Text generation"),
            ("/api/show", "Model information")
        ]
        
        all_accessible = True
        
        for endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                
                if endpoint == "/api/generate":
                    # POST request for generate endpoint
                    payload = {"model": self.model_name, "prompt": "test"}
                    response = requests.post(url, json=payload, timeout=10)
                elif endpoint == "/api/show":
                    # POST request for show endpoint
                    payload = {"name": self.model_name}
                    response = requests.post(url, json=payload, timeout=10)
                else:
                    # GET request for other endpoints
                    response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.log_verification(f"API Endpoint: {description}", True, 
                                        f"{endpoint} accessible")
                else:
                    self.log_verification(f"API Endpoint: {description}", False, 
                                        f"{endpoint} returned {response.status_code}")
                    all_accessible = False
                    
            except Exception as e:
                self.log_verification(f"API Endpoint: {description}", False, 
                                    f"{endpoint} error: {str(e)}")
                all_accessible = False
        
        return all_accessible
    
    def verify_model_parameters(self) -> bool:
        """Verify model parameters are correctly configured"""
        try:
            # Get model information
            payload = {"name": self.model_name}
            response = requests.post(f"{self.base_url}/api/show", json=payload, timeout=15)
            
            if response.status_code == 200:
                model_info = response.json()
                
                # Check if model has expected configuration
                has_system_prompt = "system" in str(model_info).lower()
                has_parameters = "parameters" in str(model_info).lower()
                
                if has_system_prompt and has_parameters:
                    self.log_verification("Model Parameters", True, 
                                        "System prompt and parameters configured")
                    return True
                else:
                    missing = []
                    if not has_system_prompt: missing.append("system prompt")
                    if not has_parameters: missing.append("parameters")
                    
                    self.log_verification("Model Parameters", False, 
                                        f"Missing: {', '.join(missing)}")
                    return False
            else:
                self.log_verification("Model Parameters", False, 
                                    f"Cannot retrieve model info: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_verification("Model Parameters", False, f"Error: {str(e)}")
            return False
    
    def verify_integration_readiness(self) -> bool:
        """Verify the model is ready for agentic framework integration"""
        try:
            # Test structured output capability
            payload = {
                "model": self.model_name,
                "prompt": "I need to create a file. Respond with a JSON tool request containing tool_name and parameters.",
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check for JSON structure and required fields
                try:
                    # Look for JSON-like content
                    if "{" in response_text and "}" in response_text:
                        has_tool_name = "tool_name" in response_text
                        has_parameters = "parameters" in response_text
                        
                        if has_tool_name and has_parameters:
                            self.log_verification("Integration Readiness", True, 
                                                "Structured output capability confirmed")
                            return True
                        else:
                            self.log_verification("Integration Readiness", False, 
                                                "JSON structure incomplete")
                            return False
                    else:
                        self.log_verification("Integration Readiness", False, 
                                            "No JSON structure in response")
                        return False
                except Exception:
                    self.log_verification("Integration Readiness", False, 
                                        "Cannot parse structured output")
                    return False
            else:
                self.log_verification("Integration Readiness", False, 
                                    f"Cannot test integration: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_verification("Integration Readiness", False, f"Error: {str(e)}")
            return False
    
    def verify_file_structure(self) -> bool:
        """Verify required project files are present"""
        required_files = [
            "modelfile/Modelfile",
            "config/model_config.json",
            "scripts/validate.py",
            "scripts/health_check.py"
        ]
        
        missing_files = []
        
        for file_path in required_files:
            full_path = Path("olympus-coder-v1") / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if not missing_files:
            self.log_verification("File Structure", True, 
                                "All required files present")
            return True
        else:
            self.log_verification("File Structure", False, 
                                f"Missing files: {', '.join(missing_files)}")
            return False
    
    def run_deployment_verification(self) -> Tuple[bool, Dict]:
        """Run complete deployment verification"""
        print(f"🔍 Verifying deployment of {self.model_name}")
        print(f"🌐 Target: {self.host}:{self.port}")
        print("=" * 60)
        
        # Run all verification checks
        verifications = [
            ("File Structure", self.verify_file_structure),
            ("Model Build", self.verify_model_build),
            ("System Prompt Integration", self.verify_system_prompt_integration),
            ("API Endpoints", self.verify_api_endpoints),
            ("Model Parameters", self.verify_model_parameters),
            ("Integration Readiness", self.verify_integration_readiness)
        ]
        
        passed_count = 0
        for name, verification_func in verifications:
            try:
                if verification_func():
                    passed_count += 1
            except Exception as e:
                self.log_verification(name, False, f"Verification error: {str(e)}")
            
            time.sleep(0.5)  # Brief pause between checks
        
        # Calculate results
        total_verifications = len(verifications)
        success_rate = passed_count / total_verifications
        deployment_ready = success_rate >= 0.85  # 85% pass rate required for deployment
        
        print("=" * 60)
        print(f"📊 Deployment Verification Results:")
        print(f"   Passed: {passed_count}/{total_verifications} ({success_rate:.1%})")
        print(f"   Deployment Status: {'✅ READY' if deployment_ready else '❌ NOT READY'}")
        
        # Generate verification report
        report = {
            "model_name": self.model_name,
            "endpoint": f"{self.host}:{self.port}",
            "timestamp": datetime.now().isoformat(),
            "deployment_ready": deployment_ready,
            "success_rate": success_rate,
            "passed_count": passed_count,
            "total_verifications": total_verifications,
            "verifications": self.verification_results
        }
        
        return deployment_ready, report

def main():
    parser = argparse.ArgumentParser(description="Verify Olympus-Coder-v1 deployment")
    parser.add_argument("--model", default="olympus-coder-v1", 
                       help="Model name to verify")
    parser.add_argument("--host", default="localhost", 
                       help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, 
                       help="Ollama port")
    parser.add_argument("--output", help="Save verification report to JSON file")
    
    args = parser.parse_args()
    
    verifier = DeploymentVerifier(args.model, args.host, args.port)
    ready, report = verifier.run_deployment_verification()
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 Verification report saved to: {args.output}")
    
    if ready:
        print("\n🎉 Deployment verification successful!")
        print("💡 The model is ready for integration with agentic frameworks.")
    else:
        print("\n⚠️  Deployment verification failed!")
        print("🔧 Please address the failed checks before proceeding.")
    
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()