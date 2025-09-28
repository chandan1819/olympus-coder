#!/usr/bin/env python3
"""
Olympus-Coder-v1 Automated Testing and Validation Pipeline

Comprehensive test runner that executes all test scenarios, measures performance,
and generates detailed accuracy reports.
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
import statistics

class TestPipeline:
    """Automated testing and validation pipeline for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 config_path: str = "config/build_config.json"):
        self.model_name = model_name
        self.config = self.load_config(config_path)
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = datetime.now()
        
        # Set up results directory
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Test categories and their scripts
        self.test_categories = {
            "validation_framework": {
                "script": "validation/test_all_validation.py",
                "description": "Core validation framework tests",
                "timeout": 120
            },
            "scenario_tests": {
                "script": "tests/scenarios/run_all_tests.py",
                "description": "Comprehensive scenario tests",
                "timeout": 300
            },
            "health_check": {
                "script": "scripts/health_check.py",
                "description": "Model health and functionality check",
                "timeout": 180
            },
            "deployment_verification": {
                "script": "scripts/deployment_verification.py",
                "description": "Deployment readiness verification",
                "timeout": 120
            }
        }
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Configuration file not found: {config_path}")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "validation_tests": {
                "basic_response": {"enabled": True, "timeout": 30},
                "code_generation": {"enabled": True, "timeout": 45},
                "json_output": {"enabled": True, "timeout": 30},
                "context_awareness": {"enabled": True, "timeout": 60}
            },
            "performance": {
                "response_time_threshold": 10.0,
                "memory_limit_mb": 8192,
                "concurrent_requests": 1
            }
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_test_script(self, script_path: str, args: List[str] = None, 
                       timeout: int = 120) -> Tuple[bool, str, float]:
        """Run a test script and return success, output, and execution time"""
        if args is None:
            args = []
        
        # Add model name to args if not present
        if "--model" not in args:
            args.extend(["--model", self.model_name])
        
        command = ["python3", script_path] + args
        
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
            output = result.stdout if success else result.stderr
            
            return success, output, execution_time
            
        except subprocess.TimeoutExpired:
            execution_time = timeout
            return False, f"Test timed out after {timeout} seconds", execution_time
        except Exception as e:
            return False, f"Test execution error: {str(e)}", 0.0
    
    def run_validation_framework_tests(self) -> Dict[str, Any]:
        """Run validation framework tests"""
        self.log("🧪 Running validation framework tests...")
        
        script_path = "validation/test_all_validation.py"
        success, output, exec_time = self.run_test_script(script_path, timeout=120)
        
        # Parse output for detailed results
        passed_tests = output.count("✅")
        failed_tests = output.count("❌")
        total_tests = passed_tests + failed_tests
        
        return {
            "success": success,
            "execution_time": exec_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "output": output
        }
    
    def run_scenario_tests(self) -> Dict[str, Any]:
        """Run comprehensive scenario tests"""
        self.log("🎯 Running scenario tests...")
        
        script_path = "tests/scenarios/run_all_tests.py"
        success, output, exec_time = self.run_test_script(script_path, timeout=300)
        
        # Try to parse JSON output if available
        results = {
            "success": success,
            "execution_time": exec_time,
            "output": output
        }
        
        # Look for JSON results in output
        try:
            # Find JSON content in output
            lines = output.split('\n')
            json_start = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('{') and '"test_run_info"' in line:
                    json_start = i
                    break
            
            if json_start >= 0:
                json_content = '\n'.join(lines[json_start:])
                # Try to find the end of JSON
                brace_count = 0
                json_end = len(json_content)
                for i, char in enumerate(json_content):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                json_data = json.loads(json_content[:json_end])
                results.update(json_data.get('overall_summary', {}))
                results['requirements_compliance'] = json_data.get('requirements_validation', {})
                
        except (json.JSONDecodeError, KeyError, IndexError):
            # Fallback to parsing text output
            self.log("⚠️  Could not parse JSON results, using text parsing")
            
            # Parse text output for basic metrics
            if "Overall Success Rate:" in output:
                try:
                    rate_line = [line for line in output.split('\n') if "Overall Success Rate:" in line][0]
                    rate_str = rate_line.split(':')[1].strip().replace('%', '')
                    results['overall_success_rate'] = float(rate_str) / 100.0
                except (ValueError, IndexError):
                    results['overall_success_rate'] = 0.0
        
        return results
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run health check tests"""
        self.log("🏥 Running health check...")
        
        script_path = "scripts/health_check.py"
        args = ["--no-performance"]  # Skip performance tests for faster execution
        success, output, exec_time = self.run_test_script(script_path, args, timeout=180)
        
        # Parse health check results
        passed_checks = output.count("✅ PASS")
        failed_checks = output.count("❌ FAIL")
        total_checks = passed_checks + failed_checks
        
        overall_health = "✅ HEALTHY" in output
        
        return {
            "success": success,
            "execution_time": exec_time,
            "overall_health": overall_health,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "health_rate": passed_checks / total_checks if total_checks > 0 else 0.0,
            "output": output
        }
    
    def run_deployment_verification(self) -> Dict[str, Any]:
        """Run deployment verification tests"""
        self.log("🔍 Running deployment verification...")
        
        script_path = "scripts/deployment_verification.py"
        success, output, exec_time = self.run_test_script(script_path, timeout=120)
        
        # Parse verification results
        passed_verifications = output.count("✅ VERIFIED")
        failed_verifications = output.count("❌ FAILED")
        total_verifications = passed_verifications + failed_verifications
        
        deployment_ready = "✅ READY" in output
        
        return {
            "success": success,
            "execution_time": exec_time,
            "deployment_ready": deployment_ready,
            "total_verifications": total_verifications,
            "passed_verifications": passed_verifications,
            "failed_verifications": failed_verifications,
            "verification_rate": passed_verifications / total_verifications if total_verifications > 0 else 0.0,
            "output": output
        }
    
    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarking tests"""
        self.log("⚡ Running performance benchmarks...")
        
        # Run health check with performance tests
        script_path = "scripts/health_check.py"
        success, output, exec_time = self.run_test_script(script_path, timeout=300)
        
        # Parse performance metrics from output
        performance_data = {
            "benchmark_execution_time": exec_time,
            "benchmark_success": success
        }
        
        # Extract response times if available
        response_times = []
        for line in output.split('\n'):
            if "Response time:" in line:
                try:
                    time_str = line.split("Response time:")[1].strip().replace('s', '')
                    response_times.append(float(time_str))
                except (ValueError, IndexError):
                    continue
        
        if response_times:
            performance_data.update({
                "response_times": response_times,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "response_time_std": statistics.stdev(response_times) if len(response_times) > 1 else 0.0
            })
        
        return performance_data
    
    def calculate_accuracy_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive accuracy metrics"""
        self.log("📊 Calculating accuracy metrics...")
        
        accuracy_metrics = {}
        
        # Validation framework accuracy
        if "validation_framework" in self.test_results:
            vf_results = self.test_results["validation_framework"]
            accuracy_metrics["validation_framework_accuracy"] = vf_results.get("success_rate", 0.0)
        
        # Scenario tests accuracy
        if "scenario_tests" in self.test_results:
            st_results = self.test_results["scenario_tests"]
            accuracy_metrics["overall_scenario_accuracy"] = st_results.get("overall_success_rate", 0.0)
            
            # Requirements compliance
            compliance = st_results.get("requirements_compliance", {})
            if compliance:
                overall_compliance = compliance.get("overall_compliance", {})
                accuracy_metrics["requirements_compliance_rate"] = overall_compliance.get("compliance_rate", 0.0)
        
        # Health check accuracy
        if "health_check" in self.test_results:
            hc_results = self.test_results["health_check"]
            accuracy_metrics["health_check_accuracy"] = hc_results.get("health_rate", 0.0)
        
        # Deployment verification accuracy
        if "deployment_verification" in self.test_results:
            dv_results = self.test_results["deployment_verification"]
            accuracy_metrics["deployment_verification_accuracy"] = dv_results.get("verification_rate", 0.0)
        
        # Calculate composite accuracy score
        accuracy_values = [v for v in accuracy_metrics.values() if isinstance(v, (int, float))]
        if accuracy_values:
            accuracy_metrics["composite_accuracy_score"] = statistics.mean(accuracy_values)
        else:
            accuracy_metrics["composite_accuracy_score"] = 0.0
        
        return accuracy_metrics
    
    def run_full_pipeline(self, include_performance: bool = True) -> Dict[str, Any]:
        """Run the complete testing pipeline"""
        self.log(f"🚀 Starting comprehensive test pipeline for {self.model_name}")
        self.log("=" * 60)
        
        pipeline_start = time.time()
        
        # Run all test categories
        test_runners = {
            "validation_framework": self.run_validation_framework_tests,
            "scenario_tests": self.run_scenario_tests,
            "health_check": self.run_health_check,
            "deployment_verification": self.run_deployment_verification
        }
        
        for category, runner in test_runners.items():
            try:
                self.log(f"📋 Running {category.replace('_', ' ').title()}...")
                self.test_results[category] = runner()
                
                # Log summary
                result = self.test_results[category]
                if result.get("success", False):
                    self.log(f"✅ {category} completed successfully")
                else:
                    self.log(f"⚠️  {category} completed with issues")
                
            except Exception as e:
                self.log(f"❌ {category} failed: {str(e)}")
                self.test_results[category] = {
                    "success": False,
                    "error": str(e),
                    "execution_time": 0.0
                }
        
        # Run performance benchmarks if requested
        if include_performance:
            try:
                self.performance_metrics = self.run_performance_benchmarks()
            except Exception as e:
                self.log(f"⚠️  Performance benchmarks failed: {str(e)}")
                self.performance_metrics = {"error": str(e)}
        
        # Calculate accuracy metrics
        accuracy_metrics = self.calculate_accuracy_metrics()
        
        # Calculate total execution time
        total_execution_time = time.time() - pipeline_start
        
        # Compile final results
        final_results = {
            "pipeline_info": {
                "model_name": self.model_name,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_execution_time": total_execution_time
            },
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
            "accuracy_metrics": accuracy_metrics,
            "summary": self.generate_summary()
        }
        
        return final_results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate pipeline execution summary"""
        successful_categories = sum(1 for result in self.test_results.values() 
                                  if result.get("success", False))
        total_categories = len(self.test_results)
        
        # Calculate overall success rate
        overall_success_rate = successful_categories / total_categories if total_categories > 0 else 0.0
        
        # Get key metrics
        summary = {
            "successful_categories": successful_categories,
            "total_categories": total_categories,
            "category_success_rate": overall_success_rate,
            "pipeline_status": "SUCCESS" if overall_success_rate >= 0.75 else "PARTIAL" if overall_success_rate > 0 else "FAILED"
        }
        
        # Add specific metrics if available
        if "scenario_tests" in self.test_results:
            st_results = self.test_results["scenario_tests"]
            summary["model_accuracy"] = st_results.get("overall_success_rate", 0.0)
            
            compliance = st_results.get("requirements_compliance", {})
            if compliance:
                overall_compliance = compliance.get("overall_compliance", {})
                summary["requirements_compliance"] = overall_compliance.get("compliance_rate", 0.0)
        
        return summary
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive text report"""
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 AUTOMATED TEST PIPELINE REPORT")
        report.append("=" * 60)
        report.append(f"Model: {results['pipeline_info']['model_name']}")
        report.append(f"Start Time: {results['pipeline_info']['start_time']}")
        report.append(f"End Time: {results['pipeline_info']['end_time']}")
        report.append(f"Total Execution Time: {results['pipeline_info']['total_execution_time']:.2f}s")
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append("PIPELINE SUMMARY")
        report.append("-" * 20)
        report.append(f"Pipeline Status: {summary['pipeline_status']}")
        report.append(f"Successful Categories: {summary['successful_categories']}/{summary['total_categories']}")
        report.append(f"Category Success Rate: {summary['category_success_rate']:.2%}")
        
        if "model_accuracy" in summary:
            report.append(f"Model Accuracy: {summary['model_accuracy']:.2%}")
        if "requirements_compliance" in summary:
            report.append(f"Requirements Compliance: {summary['requirements_compliance']:.2%}")
        report.append("")
        
        # Test Category Results
        report.append("TEST CATEGORY RESULTS")
        report.append("-" * 25)
        
        for category, result in results["test_results"].items():
            status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
            exec_time = result.get("execution_time", 0.0)
            
            report.append(f"{category.replace('_', ' ').title()}: {status} ({exec_time:.2f}s)")
            
            # Add specific metrics for each category
            if category == "validation_framework":
                if "success_rate" in result:
                    report.append(f"  Success Rate: {result['success_rate']:.2%}")
                if "total_tests" in result:
                    report.append(f"  Tests: {result['passed_tests']}/{result['total_tests']}")
            
            elif category == "scenario_tests":
                if "overall_success_rate" in result:
                    report.append(f"  Overall Success Rate: {result['overall_success_rate']:.2%}")
            
            elif category == "health_check":
                if "health_rate" in result:
                    report.append(f"  Health Rate: {result['health_rate']:.2%}")
                if "overall_health" in result:
                    health_status = "HEALTHY" if result["overall_health"] else "UNHEALTHY"
                    report.append(f"  Overall Health: {health_status}")
            
            elif category == "deployment_verification":
                if "verification_rate" in result:
                    report.append(f"  Verification Rate: {result['verification_rate']:.2%}")
                if "deployment_ready" in result:
                    ready_status = "READY" if result["deployment_ready"] else "NOT READY"
                    report.append(f"  Deployment Status: {ready_status}")
            
            report.append("")
        
        # Accuracy Metrics
        accuracy = results["accuracy_metrics"]
        report.append("ACCURACY METRICS")
        report.append("-" * 18)
        
        for metric, value in accuracy.items():
            if isinstance(value, (int, float)):
                report.append(f"{metric.replace('_', ' ').title()}: {value:.2%}")
        report.append("")
        
        # Performance Metrics
        if results["performance_metrics"] and "error" not in results["performance_metrics"]:
            perf = results["performance_metrics"]
            report.append("PERFORMANCE METRICS")
            report.append("-" * 20)
            
            if "avg_response_time" in perf:
                report.append(f"Average Response Time: {perf['avg_response_time']:.3f}s")
                report.append(f"Min Response Time: {perf['min_response_time']:.3f}s")
                report.append(f"Max Response Time: {perf['max_response_time']:.3f}s")
                if "response_time_std" in perf:
                    report.append(f"Response Time Std Dev: {perf['response_time_std']:.3f}s")
            
            report.append(f"Benchmark Execution Time: {perf['benchmark_execution_time']:.2f}s")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        if summary["category_success_rate"] >= 0.9:
            report.append("✅ Excellent performance! Model is ready for production use.")
        elif summary["category_success_rate"] >= 0.75:
            report.append("✅ Good performance! Model meets basic requirements.")
        elif summary["category_success_rate"] >= 0.5:
            report.append("⚠️  Moderate performance. Consider additional training or tuning.")
        else:
            report.append("❌ Poor performance. Significant improvements needed.")
        
        if "model_accuracy" in summary:
            if summary["model_accuracy"] < 0.75:
                report.append("⚠️  Model accuracy below target (75%). Review training data and prompts.")
        
        if "requirements_compliance" in summary:
            if summary["requirements_compliance"] < 0.8:
                report.append("⚠️  Requirements compliance below target (80%). Review implementation.")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any]) -> Tuple[str, str]:
        """Save results to files"""
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"pipeline_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save text report
        report = self.generate_report(results)
        txt_file = self.results_dir / f"pipeline_report_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write(report)
        
        return str(json_file), str(txt_file)

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Test Pipeline")
    parser.add_argument("--model", default="olympus-coder-v1",
                       help="Model name to test")
    parser.add_argument("--config", default="config/build_config.json",
                       help="Configuration file")
    parser.add_argument("--no-performance", action="store_true",
                       help="Skip performance benchmarks")
    parser.add_argument("--output-dir", default="test_results",
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    # Create pipeline
    pipeline = TestPipeline(args.model, args.config)
    pipeline.results_dir = Path(args.output_dir)
    pipeline.results_dir.mkdir(exist_ok=True)
    
    # Run pipeline
    results = pipeline.run_full_pipeline(not args.no_performance)
    
    # Generate and display report
    report = pipeline.generate_report(results)
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 60)
    print(report)
    
    # Save results
    json_file, txt_file = pipeline.save_results(results)
    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Report: {txt_file}")
    
    # Exit with appropriate code
    summary = results["summary"]
    success = summary["pipeline_status"] in ["SUCCESS", "PARTIAL"]
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()