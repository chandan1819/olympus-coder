#!/usr/bin/env python3
"""
Olympus-Coder-v1 Performance Benchmarking Tool

Comprehensive performance testing and metrics collection for model evaluation.
"""

import json
import sys
import time
import requests
import argparse
import statistics
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class PerformanceBenchmark:
    """Comprehensive performance benchmarking for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        self.benchmark_results = {}
        
        # Test scenarios for benchmarking
        self.test_scenarios = {
            "simple_response": {
                "prompt": "Hello, respond with 'Benchmark test successful'",
                "expected_keywords": ["benchmark", "test", "successful"],
                "timeout": 10
            },
            "code_generation": {
                "prompt": "Generate a Python function that calculates the factorial of a number",
                "expected_keywords": ["def", "factorial", "return"],
                "timeout": 30
            },
            "json_output": {
                "prompt": "I need to read a file. Provide a JSON tool request with tool_name and parameters.",
                "expected_keywords": ["tool_name", "parameters", "{", "}"],
                "timeout": 20
            },
            "complex_code": {
                "prompt": "Create a Python class for managing a simple database connection with methods for connect, disconnect, and execute query",
                "expected_keywords": ["class", "def", "connect", "disconnect", "execute"],
                "timeout": 45
            },
            "debugging_analysis": {
                "prompt": "Analyze this Python error: 'TypeError: unsupported operand type(s) for +: 'int' and 'str''. Explain the cause and provide a fix.",
                "expected_keywords": ["TypeError", "int", "str", "fix"],
                "timeout": 25
            }
        }
    
    def send_request(self, prompt: str, timeout: int = 30) -> Tuple[bool, str, float, Dict]:
        """Send a request to the model and measure performance"""
        start_time = time.time()
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.api_url, json=payload, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Calculate additional metrics
                metrics = {
                    "response_length": len(response_text),
                    "word_count": len(response_text.split()),
                    "line_count": len(response_text.split('\n')),
                    "has_code_blocks": "```" in response_text,
                    "has_json": "{" in response_text and "}" in response_text
                }
                
                return True, response_text, response_time, metrics
            else:
                return False, f"HTTP {response.status_code}: {response.text}", response_time, {}
                
        except requests.exceptions.Timeout:
            response_time = timeout
            return False, "Request timed out", response_time, {}
        except Exception as e:
            response_time = time.time() - start_time
            return False, f"Request error: {str(e)}", response_time, {}
    
    def validate_response_quality(self, response_text: str, expected_keywords: List[str]) -> Dict[str, Any]:
        """Validate response quality based on expected keywords"""
        response_lower = response_text.lower()
        
        found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
        keyword_coverage = len(found_keywords) / len(expected_keywords) if expected_keywords else 1.0
        
        return {
            "keyword_coverage": keyword_coverage,
            "found_keywords": found_keywords,
            "missing_keywords": [kw for kw in expected_keywords if kw.lower() not in response_lower],
            "quality_score": keyword_coverage
        }
    
    def run_single_scenario_benchmark(self, scenario_name: str, iterations: int = 5) -> Dict[str, Any]:
        """Run benchmark for a single scenario multiple times"""
        scenario = self.test_scenarios[scenario_name]
        prompt = scenario["prompt"]
        expected_keywords = scenario["expected_keywords"]
        timeout = scenario["timeout"]
        
        print(f"  📊 Benchmarking: {scenario_name} ({iterations} iterations)")
        
        results = {
            "scenario_name": scenario_name,
            "iterations": iterations,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "quality_scores": [],
            "response_metrics": [],
            "errors": []
        }
        
        for i in range(iterations):
            success, response_text, response_time, metrics = self.send_request(prompt, timeout)
            
            if success:
                results["successful_requests"] += 1
                results["response_times"].append(response_time)
                results["response_metrics"].append(metrics)
                
                # Validate quality
                quality = self.validate_response_quality(response_text, expected_keywords)
                results["quality_scores"].append(quality["quality_score"])
                
            else:
                results["failed_requests"] += 1
                results["errors"].append(response_text)
            
            # Brief pause between requests
            time.sleep(0.5)
        
        # Calculate statistics
        if results["response_times"]:
            results["performance_stats"] = {
                "avg_response_time": statistics.mean(results["response_times"]),
                "min_response_time": min(results["response_times"]),
                "max_response_time": max(results["response_times"]),
                "median_response_time": statistics.median(results["response_times"]),
                "std_dev_response_time": statistics.stdev(results["response_times"]) if len(results["response_times"]) > 1 else 0.0
            }
        
        if results["quality_scores"]:
            results["quality_stats"] = {
                "avg_quality_score": statistics.mean(results["quality_scores"]),
                "min_quality_score": min(results["quality_scores"]),
                "max_quality_score": max(results["quality_scores"])
            }
        
        # Calculate success rate
        results["success_rate"] = results["successful_requests"] / iterations
        
        return results
    
    def run_concurrent_benchmark(self, scenario_name: str, concurrent_requests: int = 3, 
                                total_requests: int = 10) -> Dict[str, Any]:
        """Run concurrent requests benchmark"""
        scenario = self.test_scenarios[scenario_name]
        prompt = scenario["prompt"]
        timeout = scenario["timeout"]
        
        print(f"  🔄 Concurrent benchmark: {scenario_name} ({concurrent_requests} concurrent, {total_requests} total)")
        
        results = {
            "scenario_name": scenario_name,
            "concurrent_requests": concurrent_requests,
            "total_requests": total_requests,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "start_times": [],
            "end_times": [],
            "errors": []
        }
        
        def make_request(request_id: int) -> Tuple[int, bool, float, str]:
            start_time = time.time()
            success, response_text, response_time, _ = self.send_request(prompt, timeout)
            end_time = time.time()
            return request_id, success, response_time, response_text, start_time, end_time
        
        # Execute concurrent requests
        benchmark_start = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(total_requests)]
            
            for future in as_completed(futures):
                try:
                    request_id, success, response_time, response_text, start_time, end_time = future.result()
                    
                    if success:
                        results["successful_requests"] += 1
                        results["response_times"].append(response_time)
                    else:
                        results["failed_requests"] += 1
                        results["errors"].append(f"Request {request_id}: {response_text}")
                    
                    results["start_times"].append(start_time)
                    results["end_times"].append(end_time)
                    
                except Exception as e:
                    results["failed_requests"] += 1
                    results["errors"].append(f"Execution error: {str(e)}")
        
        benchmark_end = time.time()
        
        # Calculate concurrent performance metrics
        results["total_benchmark_time"] = benchmark_end - benchmark_start
        results["requests_per_second"] = total_requests / results["total_benchmark_time"]
        results["success_rate"] = results["successful_requests"] / total_requests
        
        if results["response_times"]:
            results["performance_stats"] = {
                "avg_response_time": statistics.mean(results["response_times"]),
                "min_response_time": min(results["response_times"]),
                "max_response_time": max(results["response_times"]),
                "median_response_time": statistics.median(results["response_times"])
            }
        
        return results
    
    def run_load_test(self, duration_seconds: int = 60, requests_per_second: int = 2) -> Dict[str, Any]:
        """Run sustained load test"""
        print(f"  ⚡ Load test: {duration_seconds}s duration, {requests_per_second} req/s")
        
        # Use simple response scenario for load testing
        scenario = self.test_scenarios["simple_response"]
        prompt = scenario["prompt"]
        timeout = scenario["timeout"]
        
        results = {
            "duration_seconds": duration_seconds,
            "target_requests_per_second": requests_per_second,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "timestamps": [],
            "errors": []
        }
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        request_interval = 1.0 / requests_per_second
        
        request_count = 0
        
        while time.time() < end_time:
            request_start = time.time()
            
            success, response_text, response_time, _ = self.send_request(prompt, timeout)
            
            if success:
                results["successful_requests"] += 1
                results["response_times"].append(response_time)
            else:
                results["failed_requests"] += 1
                results["errors"].append(response_text)
            
            results["timestamps"].append(time.time())
            request_count += 1
            
            # Wait for next request interval
            elapsed = time.time() - request_start
            sleep_time = max(0, request_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Calculate load test metrics
        actual_duration = time.time() - start_time
        results["actual_duration"] = actual_duration
        results["actual_requests_per_second"] = request_count / actual_duration
        results["total_requests"] = request_count
        results["success_rate"] = results["successful_requests"] / request_count if request_count > 0 else 0.0
        
        if results["response_times"]:
            results["performance_stats"] = {
                "avg_response_time": statistics.mean(results["response_times"]),
                "min_response_time": min(results["response_times"]),
                "max_response_time": max(results["response_times"]),
                "p95_response_time": statistics.quantiles(results["response_times"], n=20)[18] if len(results["response_times"]) >= 20 else max(results["response_times"]),
                "p99_response_time": statistics.quantiles(results["response_times"], n=100)[98] if len(results["response_times"]) >= 100 else max(results["response_times"])
            }
        
        return results
    
    def run_comprehensive_benchmark(self, iterations: int = 5, include_concurrent: bool = True, 
                                  include_load_test: bool = False) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        print(f"🚀 Starting comprehensive performance benchmark for {self.model_name}")
        print("=" * 60)
        
        benchmark_start = time.time()
        
        results = {
            "benchmark_info": {
                "model_name": self.model_name,
                "endpoint": f"{self.host}:{self.port}",
                "start_time": datetime.now().isoformat(),
                "iterations_per_scenario": iterations
            },
            "scenario_benchmarks": {},
            "concurrent_benchmarks": {},
            "load_test_results": {},
            "summary": {}
        }
        
        # Run individual scenario benchmarks
        print("\n📊 Running scenario benchmarks...")
        for scenario_name in self.test_scenarios:
            try:
                scenario_results = self.run_single_scenario_benchmark(scenario_name, iterations)
                results["scenario_benchmarks"][scenario_name] = scenario_results
            except Exception as e:
                print(f"  ❌ Scenario {scenario_name} failed: {str(e)}")
                results["scenario_benchmarks"][scenario_name] = {"error": str(e)}
        
        # Run concurrent benchmarks
        if include_concurrent:
            print("\n🔄 Running concurrent benchmarks...")
            concurrent_scenarios = ["simple_response", "code_generation"]
            
            for scenario_name in concurrent_scenarios:
                if scenario_name in self.test_scenarios:
                    try:
                        concurrent_results = self.run_concurrent_benchmark(scenario_name, 
                                                                         concurrent_requests=3, 
                                                                         total_requests=10)
                        results["concurrent_benchmarks"][scenario_name] = concurrent_results
                    except Exception as e:
                        print(f"  ❌ Concurrent {scenario_name} failed: {str(e)}")
                        results["concurrent_benchmarks"][scenario_name] = {"error": str(e)}
        
        # Run load test
        if include_load_test:
            print("\n⚡ Running load test...")
            try:
                load_results = self.run_load_test(duration_seconds=30, requests_per_second=1)
                results["load_test_results"] = load_results
            except Exception as e:
                print(f"  ❌ Load test failed: {str(e)}")
                results["load_test_results"] = {"error": str(e)}
        
        # Calculate summary statistics
        benchmark_end = time.time()
        results["benchmark_info"]["end_time"] = datetime.now().isoformat()
        results["benchmark_info"]["total_duration"] = benchmark_end - benchmark_start
        
        results["summary"] = self.calculate_summary_stats(results)
        
        return results
    
    def calculate_summary_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from benchmark results"""
        summary = {
            "overall_success_rate": 0.0,
            "avg_response_time": 0.0,
            "avg_quality_score": 0.0,
            "scenario_performance": {},
            "performance_grade": "F"
        }
        
        # Collect metrics from scenario benchmarks
        scenario_success_rates = []
        scenario_response_times = []
        scenario_quality_scores = []
        
        for scenario_name, scenario_results in results["scenario_benchmarks"].items():
            if "error" not in scenario_results:
                success_rate = scenario_results.get("success_rate", 0.0)
                scenario_success_rates.append(success_rate)
                
                perf_stats = scenario_results.get("performance_stats", {})
                if "avg_response_time" in perf_stats:
                    scenario_response_times.append(perf_stats["avg_response_time"])
                
                quality_stats = scenario_results.get("quality_stats", {})
                if "avg_quality_score" in quality_stats:
                    scenario_quality_scores.append(quality_stats["avg_quality_score"])
                
                # Store individual scenario performance
                summary["scenario_performance"][scenario_name] = {
                    "success_rate": success_rate,
                    "avg_response_time": perf_stats.get("avg_response_time", 0.0),
                    "quality_score": quality_stats.get("avg_quality_score", 0.0)
                }
        
        # Calculate overall metrics
        if scenario_success_rates:
            summary["overall_success_rate"] = statistics.mean(scenario_success_rates)
        
        if scenario_response_times:
            summary["avg_response_time"] = statistics.mean(scenario_response_times)
        
        if scenario_quality_scores:
            summary["avg_quality_score"] = statistics.mean(scenario_quality_scores)
        
        # Calculate performance grade
        success_rate = summary["overall_success_rate"]
        response_time = summary["avg_response_time"]
        quality_score = summary["avg_quality_score"]
        
        # Grading criteria
        if success_rate >= 0.95 and response_time <= 5.0 and quality_score >= 0.8:
            summary["performance_grade"] = "A"
        elif success_rate >= 0.9 and response_time <= 10.0 and quality_score >= 0.7:
            summary["performance_grade"] = "B"
        elif success_rate >= 0.8 and response_time <= 15.0 and quality_score >= 0.6:
            summary["performance_grade"] = "C"
        elif success_rate >= 0.7 and response_time <= 20.0 and quality_score >= 0.5:
            summary["performance_grade"] = "D"
        else:
            summary["performance_grade"] = "F"
        
        return summary
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 55)
        
        info = results["benchmark_info"]
        report.append(f"Model: {info['model_name']}")
        report.append(f"Endpoint: {info.get('endpoint', 'N/A')}")
        report.append(f"Start Time: {info['start_time']}")
        report.append(f"End Time: {info['end_time']}")
        report.append(f"Total Duration: {info['total_duration']:.2f}s")
        report.append("")
        
        # Summary
        summary = results["summary"]
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 20)
        report.append(f"Overall Success Rate: {summary['overall_success_rate']:.2%}")
        report.append(f"Average Response Time: {summary['avg_response_time']:.3f}s")
        report.append(f"Average Quality Score: {summary['avg_quality_score']:.2%}")
        report.append(f"Performance Grade: {summary['performance_grade']}")
        report.append("")
        
        # Scenario Performance
        report.append("SCENARIO PERFORMANCE")
        report.append("-" * 20)
        
        for scenario, perf in summary["scenario_performance"].items():
            report.append(f"{scenario.replace('_', ' ').title()}:")
            report.append(f"  Success Rate: {perf['success_rate']:.2%}")
            report.append(f"  Avg Response Time: {perf['avg_response_time']:.3f}s")
            report.append(f"  Quality Score: {perf['quality_score']:.2%}")
            report.append("")
        
        # Detailed Results
        report.append("DETAILED SCENARIO RESULTS")
        report.append("-" * 28)
        
        for scenario_name, scenario_results in results["scenario_benchmarks"].items():
            if "error" in scenario_results:
                report.append(f"{scenario_name}: ERROR - {scenario_results['error']}")
                continue
            
            report.append(f"{scenario_name.replace('_', ' ').title()}:")
            report.append(f"  Iterations: {scenario_results['iterations']}")
            report.append(f"  Successful: {scenario_results['successful_requests']}")
            report.append(f"  Failed: {scenario_results['failed_requests']}")
            
            perf_stats = scenario_results.get("performance_stats", {})
            if perf_stats:
                report.append(f"  Response Time - Avg: {perf_stats['avg_response_time']:.3f}s, "
                             f"Min: {perf_stats['min_response_time']:.3f}s, "
                             f"Max: {perf_stats['max_response_time']:.3f}s")
            
            quality_stats = scenario_results.get("quality_stats", {})
            if quality_stats:
                report.append(f"  Quality Score - Avg: {quality_stats['avg_quality_score']:.2%}")
            
            report.append("")
        
        # Concurrent Results
        if results["concurrent_benchmarks"]:
            report.append("CONCURRENT PERFORMANCE")
            report.append("-" * 22)
            
            for scenario_name, concurrent_results in results["concurrent_benchmarks"].items():
                if "error" in concurrent_results:
                    report.append(f"{scenario_name}: ERROR - {concurrent_results['error']}")
                    continue
                
                report.append(f"{scenario_name.replace('_', ' ').title()}:")
                report.append(f"  Concurrent Requests: {concurrent_results['concurrent_requests']}")
                report.append(f"  Total Requests: {concurrent_results['total_requests']}")
                report.append(f"  Success Rate: {concurrent_results['success_rate']:.2%}")
                report.append(f"  Requests/Second: {concurrent_results['requests_per_second']:.2f}")
                
                perf_stats = concurrent_results.get("performance_stats", {})
                if perf_stats:
                    report.append(f"  Avg Response Time: {perf_stats['avg_response_time']:.3f}s")
                
                report.append("")
        
        # Load Test Results
        if results["load_test_results"] and "error" not in results["load_test_results"]:
            load_results = results["load_test_results"]
            report.append("LOAD TEST RESULTS")
            report.append("-" * 17)
            report.append(f"Duration: {load_results['actual_duration']:.1f}s")
            report.append(f"Total Requests: {load_results['total_requests']}")
            report.append(f"Success Rate: {load_results['success_rate']:.2%}")
            report.append(f"Requests/Second: {load_results['actual_requests_per_second']:.2f}")
            
            perf_stats = load_results.get("performance_stats", {})
            if perf_stats:
                report.append(f"Avg Response Time: {perf_stats['avg_response_time']:.3f}s")
                if "p95_response_time" in perf_stats:
                    report.append(f"95th Percentile: {perf_stats['p95_response_time']:.3f}s")
                if "p99_response_time" in perf_stats:
                    report.append(f"99th Percentile: {perf_stats['p99_response_time']:.3f}s")
            
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        grade = summary["performance_grade"]
        if grade == "A":
            report.append("✅ Excellent performance! Model exceeds all benchmarks.")
        elif grade == "B":
            report.append("✅ Good performance! Model meets most requirements.")
        elif grade == "C":
            report.append("⚠️  Acceptable performance with room for improvement.")
        elif grade == "D":
            report.append("⚠️  Below average performance. Consider optimization.")
        else:
            report.append("❌ Poor performance. Significant improvements needed.")
        
        if summary["avg_response_time"] > 10.0:
            report.append("⚠️  Response times are high. Consider model optimization or hardware upgrade.")
        
        if summary["overall_success_rate"] < 0.9:
            report.append("⚠️  Success rate is below 90%. Review model configuration and prompts.")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Performance Benchmark")
    parser.add_argument("--model", default="olympus-coder-v1",
                       help="Model name to benchmark")
    parser.add_argument("--host", default="localhost",
                       help="Ollama host")
    parser.add_argument("--port", type=int, default=11434,
                       help="Ollama port")
    parser.add_argument("--iterations", type=int, default=5,
                       help="Iterations per scenario")
    parser.add_argument("--no-concurrent", action="store_true",
                       help="Skip concurrent benchmarks")
    parser.add_argument("--load-test", action="store_true",
                       help="Include load testing")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark(args.model, args.host, args.port)
    
    # Run benchmark
    results = benchmark.run_comprehensive_benchmark(
        iterations=args.iterations,
        include_concurrent=not args.no_concurrent,
        include_load_test=args.load_test
    )
    
    # Generate and display report
    report = benchmark.generate_report(results)
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print(report)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {args.output}")
    
    # Exit with appropriate code based on performance grade
    grade = results["summary"]["performance_grade"]
    success = grade in ["A", "B", "C"]
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()