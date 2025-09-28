#!/usr/bin/env python3
"""
Olympus-Coder-v1 Comprehensive Test Runner

Master test runner that executes all testing and validation components
and generates a unified report.
"""

import json
import sys
import os
import time
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class ComprehensiveTestRunner:
    """Master test runner for all Olympus-Coder-v1 testing components"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.start_time = datetime.now()
        
        # Set up results directory
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Test components and their scripts
        self.test_components = {
            "validation_framework": {
                "script": "validation/test_all_validation.py",
                "description": "Core validation framework tests",
                "timeout": 120,
                "required": True
            },
            "scenario_tests": {
                "script": "tests/scenarios/run_all_tests.py", 
                "description": "Comprehensive scenario-based tests",
                "timeout": 300,
                "required": True
            },
            "health_check": {
                "script": "scripts/health_check.py",
                "description": "Model health and functionality verification",
                "timeout": 180,
                "required": True
            },
            "deployment_verification": {
                "script": "scripts/deployment_verification.py",
                "description": "Deployment readiness verification",
                "timeout": 120,
                "required": True
            },
            "performance_benchmark": {
                "script": "scripts/performance_benchmark.py",
                "description": "Performance benchmarking and metrics",
                "timeout": 600,
                "required": False
            },
            "accuracy_measurement": {
                "script": "scripts/accuracy_measurement.py",
                "description": "Comprehensive accuracy assessment",
                "timeout": 400,
                "required": True
            }
        }
        
        self.test_results = {}
        self.execution_summary = {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_test_component(self, component_name: str, component_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test component"""
        script_path = component_config["script"]
        timeout = component_config["timeout"]
        description = component_config["description"]
        
        self.log(f"🧪 Running {component_name}: {description}")
        
        # Prepare command
        command = ["python3", script_path, "--model", self.model_name]
        
        # Add host and port for components that support it
        if component_name in ["health_check", "deployment_verification", "performance_benchmark", "accuracy_measurement"]:
            command.extend(["--host", self.host, "--port", str(self.port)])
        
        # Add component-specific arguments
        if component_name == "performance_benchmark":
            command.extend(["--iterations", "3", "--no-concurrent"])  # Faster execution
        
        try:
            start_time = time.time()
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd()
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            # Parse output for metrics
            output = result.stdout if success else result.stderr
            
            component_result = {
                "component_name": component_name,
                "description": description,
                "success": success,
                "execution_time": execution_time,
                "output": output,
                "error": result.stderr if not success else "",
                "metrics": self.extract_metrics(component_name, output)
            }
            
            if success:
                self.log(f"✅ {component_name} completed successfully ({execution_time:.1f}s)")
            else:
                self.log(f"❌ {component_name} failed ({execution_time:.1f}s)")
            
            return component_result
            
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {component_name} timed out after {timeout}s")
            return {
                "component_name": component_name,
                "description": description,
                "success": False,
                "execution_time": timeout,
                "output": "",
                "error": f"Component timed out after {timeout} seconds",
                "metrics": {}
            }
        except Exception as e:
            self.log(f"❌ {component_name} failed with exception: {str(e)}")
            return {
                "component_name": component_name,
                "description": description,
                "success": False,
                "execution_time": 0.0,
                "output": "",
                "error": f"Execution error: {str(e)}",
                "metrics": {}
            }
    
    def extract_metrics(self, component_name: str, output: str) -> Dict[str, Any]:
        """Extract key metrics from component output"""
        metrics = {}
        
        try:
            if component_name == "validation_framework":
                # Count passed/failed tests
                passed = output.count("✅")
                failed = output.count("❌")
                if passed + failed > 0:
                    metrics["success_rate"] = passed / (passed + failed)
                    metrics["passed_tests"] = passed
                    metrics["failed_tests"] = failed
            
            elif component_name == "scenario_tests":
                # Look for overall success rate
                for line in output.split('\n'):
                    if "Overall Success Rate:" in line:
                        try:
                            rate_str = line.split(':')[1].strip().replace('%', '')
                            metrics["overall_success_rate"] = float(rate_str) / 100.0
                        except (ValueError, IndexError):
                            pass
                    elif "Requirements Compliance:" in line:
                        try:
                            rate_str = line.split(':')[1].strip().replace('%', '')
                            metrics["requirements_compliance"] = float(rate_str) / 100.0
                        except (ValueError, IndexError):
                            pass
            
            elif component_name == "health_check":
                # Extract health metrics
                passed_checks = output.count("✅ PASS")
                failed_checks = output.count("❌ FAIL")
                if passed_checks + failed_checks > 0:
                    metrics["health_rate"] = passed_checks / (passed_checks + failed_checks)
                    metrics["passed_checks"] = passed_checks
                    metrics["failed_checks"] = failed_checks
                
                metrics["overall_healthy"] = "✅ HEALTHY" in output
            
            elif component_name == "deployment_verification":
                # Extract verification metrics
                passed_verifications = output.count("✅ VERIFIED")
                failed_verifications = output.count("❌ FAILED")
                if passed_verifications + failed_verifications > 0:
                    metrics["verification_rate"] = passed_verifications / (passed_verifications + failed_verifications)
                    metrics["passed_verifications"] = passed_verifications
                    metrics["failed_verifications"] = failed_verifications
                
                metrics["deployment_ready"] = "✅ READY" in output
            
            elif component_name == "performance_benchmark":
                # Extract performance metrics
                for line in output.split('\n'):
                    if "Overall Success Rate:" in line:
                        try:
                            rate_str = line.split(':')[1].strip().replace('%', '')
                            metrics["success_rate"] = float(rate_str) / 100.0
                        except (ValueError, IndexError):
                            pass
                    elif "Average Response Time:" in line:
                        try:
                            time_str = line.split(':')[1].strip().replace('s', '')
                            metrics["avg_response_time"] = float(time_str)
                        except (ValueError, IndexError):
                            pass
                    elif "Performance Grade:" in line:
                        try:
                            grade = line.split(':')[1].strip()
                            metrics["performance_grade"] = grade
                        except IndexError:
                            pass
            
            elif component_name == "accuracy_measurement":
                # Extract accuracy metrics
                for line in output.split('\n'):
                    if "Accuracy Score:" in line:
                        try:
                            rate_str = line.split(':')[1].strip().replace('%', '')
                            metrics["accuracy_score"] = float(rate_str) / 100.0
                        except (ValueError, IndexError):
                            pass
                    elif "Accuracy Grade:" in line:
                        try:
                            grade = line.split(':')[1].strip()
                            metrics["accuracy_grade"] = grade
                        except IndexError:
                            pass
                    elif "Meets Target" in line:
                        metrics["meets_target"] = "✅ YES" in line
        
        except Exception as e:
            self.log(f"⚠️  Could not extract metrics from {component_name}: {str(e)}")
        
        return metrics
    
    def run_all_tests(self, skip_optional: bool = False) -> Dict[str, Any]:
        """Run all test components"""
        self.log(f"🚀 Starting comprehensive test suite for {self.model_name}")
        self.log("=" * 70)
        
        suite_start = time.time()
        
        # Run each test component
        for component_name, component_config in self.test_components.items():
            # Skip optional components if requested
            if skip_optional and not component_config["required"]:
                self.log(f"⏭️  Skipping optional component: {component_name}")
                continue
            
            try:
                component_result = self.run_test_component(component_name, component_config)
                self.test_results[component_name] = component_result
                
            except Exception as e:
                self.log(f"❌ Component {component_name} failed with exception: {str(e)}")
                self.test_results[component_name] = {
                    "component_name": component_name,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0.0,
                    "metrics": {}
                }
            
            # Brief pause between components
            time.sleep(2)
        
        # Calculate execution summary
        suite_end = time.time()
        self.execution_summary = self.calculate_execution_summary(suite_end - suite_start)
        
        # Compile final results
        final_results = {
            "test_suite_info": {
                "model_name": self.model_name,
                "endpoint": f"{self.host}:{self.port}",
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_execution_time": suite_end - suite_start,
                "components_run": list(self.test_results.keys())
            },
            "component_results": self.test_results,
            "execution_summary": self.execution_summary,
            "overall_assessment": self.calculate_overall_assessment()
        }
        
        return final_results
    
    def calculate_execution_summary(self, total_time: float) -> Dict[str, Any]:
        """Calculate execution summary statistics"""
        successful_components = sum(1 for result in self.test_results.values() 
                                  if result.get("success", False))
        total_components = len(self.test_results)
        
        # Calculate component execution times
        execution_times = {name: result.get("execution_time", 0.0) 
                          for name, result in self.test_results.items()}
        
        return {
            "total_execution_time": total_time,
            "successful_components": successful_components,
            "failed_components": total_components - successful_components,
            "total_components": total_components,
            "component_success_rate": successful_components / total_components if total_components > 0 else 0.0,
            "execution_times": execution_times,
            "suite_status": "SUCCESS" if successful_components == total_components else 
                           "PARTIAL" if successful_components > 0 else "FAILED"
        }
    
    def calculate_overall_assessment(self) -> Dict[str, Any]:
        """Calculate overall model assessment"""
        assessment = {
            "model_readiness": "UNKNOWN",
            "key_metrics": {},
            "compliance_status": {},
            "recommendations": []
        }
        
        # Extract key metrics from component results
        key_metrics = {}
        
        # Scenario tests metrics
        if "scenario_tests" in self.test_results:
            st_metrics = self.test_results["scenario_tests"].get("metrics", {})
            if "overall_success_rate" in st_metrics:
                key_metrics["scenario_success_rate"] = st_metrics["overall_success_rate"]
            if "requirements_compliance" in st_metrics:
                key_metrics["requirements_compliance"] = st_metrics["requirements_compliance"]
        
        # Accuracy measurement metrics
        if "accuracy_measurement" in self.test_results:
            am_metrics = self.test_results["accuracy_measurement"].get("metrics", {})
            if "accuracy_score" in am_metrics:
                key_metrics["accuracy_score"] = am_metrics["accuracy_score"]
            if "meets_target" in am_metrics:
                key_metrics["meets_accuracy_target"] = am_metrics["meets_target"]
        
        # Performance benchmark metrics
        if "performance_benchmark" in self.test_results:
            pb_metrics = self.test_results["performance_benchmark"].get("metrics", {})
            if "performance_grade" in pb_metrics:
                key_metrics["performance_grade"] = pb_metrics["performance_grade"]
            if "avg_response_time" in pb_metrics:
                key_metrics["avg_response_time"] = pb_metrics["avg_response_time"]
        
        # Health check metrics
        if "health_check" in self.test_results:
            hc_metrics = self.test_results["health_check"].get("metrics", {})
            if "overall_healthy" in hc_metrics:
                key_metrics["model_healthy"] = hc_metrics["overall_healthy"]
        
        # Deployment verification metrics
        if "deployment_verification" in self.test_results:
            dv_metrics = self.test_results["deployment_verification"].get("metrics", {})
            if "deployment_ready" in dv_metrics:
                key_metrics["deployment_ready"] = dv_metrics["deployment_ready"]
        
        assessment["key_metrics"] = key_metrics
        
        # Determine overall model readiness
        readiness_score = 0
        max_score = 0
        
        # Check critical metrics
        if key_metrics.get("model_healthy", False):
            readiness_score += 1
        max_score += 1
        
        if key_metrics.get("deployment_ready", False):
            readiness_score += 1
        max_score += 1
        
        if key_metrics.get("scenario_success_rate", 0.0) >= 0.75:
            readiness_score += 1
        max_score += 1
        
        if key_metrics.get("accuracy_score", 0.0) >= 0.75:
            readiness_score += 1
        max_score += 1
        
        # Determine readiness level
        readiness_ratio = readiness_score / max_score if max_score > 0 else 0.0
        
        if readiness_ratio >= 0.9:
            assessment["model_readiness"] = "PRODUCTION_READY"
        elif readiness_ratio >= 0.75:
            assessment["model_readiness"] = "READY"
        elif readiness_ratio >= 0.5:
            assessment["model_readiness"] = "NEEDS_IMPROVEMENT"
        else:
            assessment["model_readiness"] = "NOT_READY"
        
        # Generate recommendations
        recommendations = []
        
        if not key_metrics.get("model_healthy", True):
            recommendations.append("Address model health issues before deployment")
        
        if key_metrics.get("accuracy_score", 1.0) < 0.75:
            recommendations.append("Improve model accuracy to meet 75% target requirement")
        
        if key_metrics.get("scenario_success_rate", 1.0) < 0.75:
            recommendations.append("Enhance scenario test performance for better reliability")
        
        if key_metrics.get("avg_response_time", 0.0) > 10.0:
            recommendations.append("Optimize model for faster response times")
        
        performance_grade = key_metrics.get("performance_grade", "A")
        if performance_grade in ["D", "F"]:
            recommendations.append("Significant performance improvements needed")
        
        if not recommendations:
            recommendations.append("Model meets all requirements and is ready for deployment")
        
        assessment["recommendations"] = recommendations
        
        return assessment
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test suite report"""
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 COMPREHENSIVE TEST SUITE REPORT")
        report.append("=" * 60)
        
        info = results["test_suite_info"]
        report.append(f"Model: {info['model_name']}")
        report.append(f"Endpoint: {info['endpoint']}")
        report.append(f"Test Duration: {info['total_execution_time']:.1f}s")
        report.append(f"Components Run: {len(info['components_run'])}")
        report.append("")
        
        # Overall Assessment
        assessment = results["overall_assessment"]
        report.append("OVERALL ASSESSMENT")
        report.append("-" * 19)
        report.append(f"Model Readiness: {assessment['model_readiness']}")
        report.append("")
        
        # Key Metrics Summary
        key_metrics = assessment["key_metrics"]
        report.append("KEY METRICS SUMMARY")
        report.append("-" * 20)
        
        if "scenario_success_rate" in key_metrics:
            report.append(f"Scenario Success Rate: {key_metrics['scenario_success_rate']:.2%}")
        if "accuracy_score" in key_metrics:
            report.append(f"Accuracy Score: {key_metrics['accuracy_score']:.2%}")
        if "performance_grade" in key_metrics:
            report.append(f"Performance Grade: {key_metrics['performance_grade']}")
        if "avg_response_time" in key_metrics:
            report.append(f"Avg Response Time: {key_metrics['avg_response_time']:.3f}s")
        if "model_healthy" in key_metrics:
            health_status = "HEALTHY" if key_metrics["model_healthy"] else "UNHEALTHY"
            report.append(f"Model Health: {health_status}")
        if "deployment_ready" in key_metrics:
            deploy_status = "READY" if key_metrics["deployment_ready"] else "NOT READY"
            report.append(f"Deployment Status: {deploy_status}")
        
        report.append("")
        
        # Execution Summary
        summary = results["execution_summary"]
        report.append("EXECUTION SUMMARY")
        report.append("-" * 17)
        report.append(f"Suite Status: {summary['suite_status']}")
        report.append(f"Successful Components: {summary['successful_components']}/{summary['total_components']}")
        report.append(f"Component Success Rate: {summary['component_success_rate']:.2%}")
        report.append("")
        
        # Component Results
        report.append("COMPONENT RESULTS")
        report.append("-" * 17)
        
        for component_name, component_result in results["component_results"].items():
            status = "✅ SUCCESS" if component_result["success"] else "❌ FAILED"
            exec_time = component_result["execution_time"]
            
            report.append(f"{component_name.replace('_', ' ').title()}: {status} ({exec_time:.1f}s)")
            
            # Add key metrics for each component
            metrics = component_result.get("metrics", {})
            if metrics:
                for metric_name, metric_value in metrics.items():
                    if isinstance(metric_value, float):
                        if metric_name.endswith("_rate") or metric_name.endswith("_score"):
                            report.append(f"  {metric_name.replace('_', ' ').title()}: {metric_value:.2%}")
                        else:
                            report.append(f"  {metric_name.replace('_', ' ').title()}: {metric_value:.3f}")
                    else:
                        report.append(f"  {metric_name.replace('_', ' ').title()}: {metric_value}")
            
            if not component_result["success"] and component_result.get("error"):
                report.append(f"  Error: {component_result['error']}")
            
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        for i, recommendation in enumerate(assessment["recommendations"], 1):
            report.append(f"{i}. {recommendation}")
        
        report.append("")
        
        # Next Steps
        report.append("NEXT STEPS")
        report.append("-" * 10)
        
        readiness = assessment["model_readiness"]
        if readiness == "PRODUCTION_READY":
            report.append("🎉 Model is ready for production deployment!")
            report.append("• Deploy to production environment")
            report.append("• Set up monitoring and logging")
            report.append("• Begin integration with agentic frameworks")
        elif readiness == "READY":
            report.append("✅ Model is ready for deployment with minor considerations")
            report.append("• Address any remaining recommendations")
            report.append("• Deploy to staging environment for final testing")
            report.append("• Prepare production deployment plan")
        elif readiness == "NEEDS_IMPROVEMENT":
            report.append("⚠️  Model needs improvement before deployment")
            report.append("• Address failed test components")
            report.append("• Improve accuracy and performance metrics")
            report.append("• Re-run comprehensive tests after improvements")
        else:
            report.append("❌ Model is not ready for deployment")
            report.append("• Review and fix critical issues")
            report.append("• Consider model retraining or configuration changes")
            report.append("• Run individual test components to identify specific problems")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any]) -> Tuple[str, str]:
        """Save comprehensive results"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"comprehensive_test_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save text report
        report = self.generate_comprehensive_report(results)
        txt_file = self.results_dir / f"comprehensive_test_report_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write(report)
        
        return str(json_file), str(txt_file)

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Comprehensive Test Suite")
    parser.add_argument("--model", default="olympus-coder-v1",
                       help="Model name to test")
    parser.add_argument("--host", default="localhost",
                       help="Ollama host")
    parser.add_argument("--port", type=int, default=11434,
                       help="Ollama port")
    parser.add_argument("--skip-optional", action="store_true",
                       help="Skip optional test components")
    parser.add_argument("--output-dir", default="test_results",
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    # Create test runner
    runner = ComprehensiveTestRunner(args.model, args.host, args.port)
    runner.results_dir = Path(args.output_dir)
    runner.results_dir.mkdir(exist_ok=True)
    
    # Run comprehensive tests
    results = runner.run_all_tests(args.skip_optional)
    
    # Generate and display report
    report = runner.generate_comprehensive_report(results)
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUITE COMPLETE")
    print("=" * 70)
    print(report)
    
    # Save results
    json_file, txt_file = runner.save_results(results)
    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Report: {txt_file}")
    
    # Exit with appropriate code
    readiness = results["overall_assessment"]["model_readiness"]
    success = readiness in ["PRODUCTION_READY", "READY"]
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()