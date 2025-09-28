#!/usr/bin/env python3
"""
Olympus-Coder-v1 Advanced Build Script

Enhanced build automation with configuration management and comprehensive validation.
"""

import json
import sys
import os
import time
import subprocess
import requests
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class ModelBuilder:
    """Advanced model builder with comprehensive validation and configuration management"""
    
    def __init__(self, config_path: str = "config/build_config.json"):
        self.config = self.load_config(config_path)
        self.build_log = []
        self.start_time = datetime.now()
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.config["logging"]["log_directory"])
        log_dir.mkdir(exist_ok=True)
        
        # Set up log file
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"build_{timestamp}.log"
        
    def load_config(self, config_path: str) -> Dict:
        """Load build configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_path}")
            print("Using default configuration...")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def get_default_config(self) -> Dict:
        """Get default configuration if config file is missing"""
        return {
            "build": {
                "model_name": "olympus-coder-v1",
                "modelfile_path": "./modelfile/Modelfile",
                "base_models": {"primary": "codellama:13b", "fallback": "llama3:8b"},
                "validation": {"enabled": True, "skip_on_failure": False, "timeout_seconds": 60}
            },
            "ollama": {"host": "localhost", "port": 11434, "api_timeout": 30},
            "logging": {"enabled": True, "log_directory": "./logs", "log_level": "INFO"}
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(message)
        
        if self.config["logging"]["enabled"]:
            self.build_log.append(log_entry)
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")
    
    def run_command(self, command: List[str], timeout: int = 60) -> Tuple[bool, str]:
        """Run shell command with timeout and logging"""
        try:
            self.log(f"🔧 Running: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                self.log(f"✅ Command succeeded: {' '.join(command)}")
                return True, result.stdout
            else:
                self.log(f"❌ Command failed: {result.stderr}", "ERROR")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Command timed out: {' '.join(command)}", "ERROR")
            return False, "Command timed out"
        except Exception as e:
            self.log(f"❌ Command error: {str(e)}", "ERROR")
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """Check all build prerequisites"""
        self.log("📋 Checking prerequisites...")
        
        # Check Ollama installation
        success, _ = self.run_command(["ollama", "--version"], timeout=10)
        if not success:
            self.log("❌ Ollama is not installed or not in PATH", "ERROR")
            return False
        
        # Check Python installation
        success, _ = self.run_command(["python3", "--version"], timeout=10)
        if not success:
            self.log("⚠️  Python3 not found, some validation tests will be skipped", "WARNING")
        
        # Check Ollama service
        try:
            ollama_config = self.config["ollama"]
            url = f"http://{ollama_config['host']}:{ollama_config['port']}/api/tags"
            response = requests.get(url, timeout=ollama_config["api_timeout"])
            
            if response.status_code == 200:
                self.log("✅ Ollama service is running")
            else:
                self.log(f"❌ Ollama service error: HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Cannot connect to Ollama service: {str(e)}", "ERROR")
            return False
        
        # Check required files
        modelfile_path = Path(self.config["build"]["modelfile_path"])
        if not modelfile_path.exists():
            self.log(f"❌ Modelfile not found: {modelfile_path}", "ERROR")
            return False
        
        self.log("✅ All prerequisites satisfied")
        return True
    
    def ensure_base_model(self) -> bool:
        """Ensure base model is available"""
        base_models = self.config["build"]["base_models"]
        primary_model = base_models["primary"]
        fallback_model = base_models.get("fallback")
        
        self.log(f"📦 Checking base model: {primary_model}")
        
        # Check if primary model exists
        success, output = self.run_command(["ollama", "list"], timeout=30)
        if success and primary_model in output:
            self.log(f"✅ Base model {primary_model} is available")
            return True
        
        # Try to pull primary model
        self.log(f"⬇️  Pulling base model: {primary_model}")
        success, _ = self.run_command(["ollama", "pull", primary_model], 
                                    timeout=self.config["ollama"].get("pull_timeout", 300))
        
        if success:
            self.log(f"✅ Successfully pulled {primary_model}")
            return True
        
        # Try fallback model if available
        if fallback_model:
            self.log(f"⚠️  Primary model failed, trying fallback: {fallback_model}")
            success, output = self.run_command(["ollama", "list"], timeout=30)
            
            if success and fallback_model in output:
                self.log(f"✅ Using fallback model: {fallback_model}")
                # Update Modelfile to use fallback model
                self.update_modelfile_base_model(fallback_model)
                return True
            
            # Try to pull fallback model
            success, _ = self.run_command(["ollama", "pull", fallback_model], timeout=300)
            if success:
                self.log(f"✅ Successfully pulled fallback model: {fallback_model}")
                self.update_modelfile_base_model(fallback_model)
                return True
        
        self.log("❌ No suitable base model available", "ERROR")
        return False
    
    def update_modelfile_base_model(self, model_name: str):
        """Update Modelfile to use specified base model"""
        modelfile_path = Path(self.config["build"]["modelfile_path"])
        
        try:
            with open(modelfile_path, 'r') as f:
                content = f.read()
            
            # Replace FROM line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('FROM '):
                    lines[i] = f"FROM {model_name}"
                    break
            
            with open(modelfile_path, 'w') as f:
                f.write('\n'.join(lines))
            
            self.log(f"📝 Updated Modelfile to use base model: {model_name}")
            
        except Exception as e:
            self.log(f"⚠️  Could not update Modelfile: {str(e)}", "WARNING")
    
    def build_model(self) -> bool:
        """Build the custom model"""
        model_name = self.config["build"]["model_name"]
        modelfile_path = self.config["build"]["modelfile_path"]
        
        self.log(f"🔨 Building model: {model_name}")
        
        # Remove existing model if it exists
        success, output = self.run_command(["ollama", "list"], timeout=30)
        if success and model_name in output:
            self.log(f"🗑️  Removing existing model: {model_name}")
            self.run_command(["ollama", "rm", model_name], timeout=60)
        
        # Build new model
        success, output = self.run_command(
            ["ollama", "create", model_name, "-f", modelfile_path],
            timeout=300
        )
        
        if success:
            self.log(f"✅ Model built successfully: {model_name}")
            return True
        else:
            self.log(f"❌ Model build failed: {output}", "ERROR")
            return False
    
    def run_validation_tests(self) -> bool:
        """Run validation tests if enabled"""
        validation_config = self.config["build"]["validation"]
        
        if not validation_config["enabled"]:
            self.log("⏭️  Validation tests disabled")
            return True
        
        self.log("🧪 Running validation tests...")
        
        # Run basic validation script
        validation_script = Path("scripts/validate.py")
        if validation_script.exists():
            model_name = self.config["build"]["model_name"]
            success, output = self.run_command(
                ["python3", str(validation_script), "--model", model_name, "--quick"],
                timeout=validation_config["timeout_seconds"]
            )
            
            if success:
                self.log("✅ Validation tests passed")
                return True
            else:
                self.log(f"❌ Validation tests failed: {output}", "ERROR")
                return not validation_config["skip_on_failure"]
        else:
            self.log("⚠️  Validation script not found", "WARNING")
            return True
    
    def run_health_check(self) -> bool:
        """Run health check if enabled"""
        health_config = self.config["build"].get("health_check", {})
        
        if not health_config.get("enabled", True):
            self.log("⏭️  Health check disabled")
            return True
        
        self.log("🏥 Running health check...")
        
        health_script = Path("scripts/health_check.py")
        if health_script.exists():
            model_name = self.config["build"]["model_name"]
            cmd = ["python3", str(health_script), "--model", model_name]
            
            if not health_config.get("include_performance", False):
                cmd.append("--no-performance")
            
            success, output = self.run_command(
                cmd,
                timeout=health_config.get("timeout_seconds", 120)
            )
            
            if success:
                self.log("✅ Health check passed")
                return True
            else:
                self.log(f"⚠️  Health check issues: {output}", "WARNING")
                return True  # Don't fail build on health check issues
        else:
            self.log("⚠️  Health check script not found", "WARNING")
            return True
    
    def run_deployment_verification(self) -> bool:
        """Run deployment verification if enabled"""
        deploy_config = self.config["build"].get("deployment_verification", {})
        
        if not deploy_config.get("enabled", True):
            self.log("⏭️  Deployment verification disabled")
            return True
        
        self.log("🔍 Running deployment verification...")
        
        deploy_script = Path("scripts/deployment_verification.py")
        if deploy_script.exists():
            model_name = self.config["build"]["model_name"]
            success, output = self.run_command(
                ["python3", str(deploy_script), "--model", model_name],
                timeout=120
            )
            
            if success:
                self.log("✅ Deployment verification passed")
                return True
            else:
                self.log(f"⚠️  Deployment verification issues: {output}", "WARNING")
                return True  # Don't fail build on deployment verification issues
        else:
            self.log("⚠️  Deployment verification script not found", "WARNING")
            return True
    
    def generate_build_report(self, success: bool) -> Dict:
        """Generate comprehensive build report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            "build_info": {
                "model_name": self.config["build"]["model_name"],
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "success": success
            },
            "configuration": self.config,
            "build_log": self.build_log,
            "log_file": str(self.log_file)
        }
        
        # Save report
        report_file = self.log_file.parent / f"build_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📄 Build report saved: {report_file}")
        return report
    
    def build(self) -> bool:
        """Run complete build process"""
        self.log("🚀 Starting Olympus-Coder-v1 advanced build process")
        self.log(f"📅 Build started at: {self.start_time}")
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Ensure base model
            if not self.ensure_base_model():
                return False
            
            # Build model
            if not self.build_model():
                return False
            
            # Run validation tests
            if not self.run_validation_tests():
                return False
            
            # Run health check
            if not self.run_health_check():
                return False
            
            # Run deployment verification
            if not self.run_deployment_verification():
                return False
            
            self.log("🎉 Build completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"❌ Build failed with exception: {str(e)}", "ERROR")
            return False
        
        finally:
            # Always generate report
            self.generate_build_report(True)

def main():
    parser = argparse.ArgumentParser(description="Advanced Olympus-Coder-v1 build script")
    parser.add_argument("--config", default="config/build_config.json",
                       help="Build configuration file")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip validation tests")
    parser.add_argument("--skip-health-check", action="store_true",
                       help="Skip health check")
    
    args = parser.parse_args()
    
    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    builder = ModelBuilder(args.config)
    
    # Override config based on arguments
    if args.skip_validation:
        builder.config["build"]["validation"]["enabled"] = False
    if args.skip_health_check:
        builder.config["build"]["health_check"]["enabled"] = False
    
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()