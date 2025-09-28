#!/usr/bin/env python3
"""
Olympus-Coder-v1 Enhanced Performance Monitoring Tools

Advanced performance benchmarking with response time analysis, resource usage monitoring,
and comparative analysis vs base model performance as specified in requirement 5.2.
"""

import json
import sys
import time
import psutil
import requests
import argparse
import threading
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

@dataclass
class PerformanceMetrics:
    """Data class for performance metrics"""
    timestamp: datetime
    response_time: float
    cpu_usage: float
    memory_usage: float
    memory_usage_mb: float
    request_size: int
    response_size: int
    success: bool
    error_message: Optional[str] = None

@dataclass
class ResourceSnapshot:
    """Data class for system resource snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float

class PerformanceMonitor:
    """Enhanced performance monitoring for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434,
                 base_model: str = "llama3:8b",
                 db_path: str = "olympus_performance_monitoring.db"):
        self.model_name = model_name
        self.base_model = base_model
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        self.db_path = db_path
        
        # Initialize database
        self.init_database()
        
        # Resource monitoring
        self.monitoring_active = False
        self.resource_snapshots = []
        
        # Performance test scenarios
        self.performance_scenarios = {
            "simple_query": {
                "prompt": "Hello, respond with a simple greeting",
                "expected_response_time": 2.0,
                "category": "basic"
            },
            "code_generation_small": {
                "prompt": "Generate a Python function that adds two numbers",
                "expected_response_time": 5.0,
                "category": "code_generation"
            },
            "code_generation_medium": {
                "prompt": "Create a Python class for a simple calculator with basic arithmetic operations",
                "expected_response_time": 10.0,
                "category": "code_generation"
            },
            "code_generation_large": {
                "prompt": "Generate a complete Python web scraper that handles multiple URLs, error handling, and data export to CSV",
                "expected_response_time": 20.0,
                "category": "code_generation"
            },
            "debugging_analysis": {
                "prompt": "Analyze this Python error and provide a detailed fix: 'AttributeError: 'NoneType' object has no attribute 'split''. The error occurs in this code: result = data.split(',') where data comes from an API call.",
                "expected_response_time": 8.0,
                "category": "debugging"
            },
            "json_tool_request": {
                "prompt": "I need to create a new directory called 'output' and then write a file 'results.txt' with some data. Provide the appropriate tool requests in JSON format.",
                "expected_response_time": 6.0,
                "category": "tool_usage"
            },
            "context_analysis": {
                "prompt": "Given this project structure: src/main.py, src/models/user.py, src/utils/database.py, config/settings.json, tests/test_user.py - analyze the architecture and suggest improvements for maintainability and scalability.",
                "expected_response_time": 15.0,
                "category": "analysis"
            }
        }
    
    def init_database(self):
        """Initialize SQLite database for performance tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create performance_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                scenario_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                response_time REAL NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                memory_usage_mb REAL NOT NULL,
                request_size INTEGER NOT NULL,
                response_size INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT
            )
        ''')
        
        # Create resource_snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resource_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                cpu_percent REAL NOT NULL,
                memory_percent REAL NOT NULL,
                memory_available_mb REAL NOT NULL,
                memory_used_mb REAL NOT NULL,
                disk_io_read_mb REAL NOT NULL,
                disk_io_write_mb REAL NOT NULL,
                network_sent_mb REAL NOT NULL,
                network_recv_mb REAL NOT NULL
            )
        ''')
        
        # Create benchmark_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS benchmark_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                base_model TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_requests INTEGER DEFAULT 0,
                successful_requests INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0.0,
                avg_cpu_usage REAL DEFAULT 0.0,
                avg_memory_usage REAL DEFAULT 0.0,
                performance_grade TEXT DEFAULT 'F'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_resource_monitoring(self, session_id: str, interval: float = 1.0):
        """Start continuous resource monitoring"""
        self.monitoring_active = True
        self.resource_snapshots = []
        
        def monitor_resources():
            # Get initial disk and network stats
            disk_io_start = psutil.disk_io_counters()
            net_io_start = psutil.net_io_counters()
            
            while self.monitoring_active:
                try:
                    # Get current resource usage
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    
                    # Get disk and network IO
                    disk_io_current = psutil.disk_io_counters()
                    net_io_current = psutil.net_io_counters()
                    
                    # Calculate IO rates (MB)
                    disk_read_mb = (disk_io_current.read_bytes - disk_io_start.read_bytes) / (1024 * 1024)
                    disk_write_mb = (disk_io_current.write_bytes - disk_io_start.write_bytes) / (1024 * 1024)
                    net_sent_mb = (net_io_current.bytes_sent - net_io_start.bytes_sent) / (1024 * 1024)
                    net_recv_mb = (net_io_current.bytes_recv - net_io_start.bytes_recv) / (1024 * 1024)
                    
                    snapshot = ResourceSnapshot(
                        timestamp=datetime.now(),
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_available_mb=memory.available / (1024 * 1024),
                        memory_used_mb=memory.used / (1024 * 1024),
                        disk_io_read_mb=disk_read_mb,
                        disk_io_write_mb=disk_write_mb,
                        network_sent_mb=net_sent_mb,
                        network_recv_mb=net_recv_mb
                    )
                    
                    self.resource_snapshots.append(snapshot)
                    
                    # Store in database
                    self.store_resource_snapshot(session_id, snapshot)
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"Resource monitoring error: {e}")
                    break
        
        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        self.monitor_thread.start()
    
    def stop_resource_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2.0)
    
    def store_resource_snapshot(self, session_id: str, snapshot: ResourceSnapshot):
        """Store resource snapshot in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resource_snapshots (
                session_id, timestamp, cpu_percent, memory_percent,
                memory_available_mb, memory_used_mb, disk_io_read_mb,
                disk_io_write_mb, network_sent_mb, network_recv_mb
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            snapshot.timestamp.isoformat(),
            snapshot.cpu_percent,
            snapshot.memory_percent,
            snapshot.memory_available_mb,
            snapshot.memory_used_mb,
            snapshot.disk_io_read_mb,
            snapshot.disk_io_write_mb,
            snapshot.network_sent_mb,
            snapshot.network_recv_mb
        ))
        
        conn.commit()
        conn.close()
    
    def send_request_with_monitoring(self, model: str, prompt: str, 
                                   timeout: int = 45) -> PerformanceMetrics:
        """Send request with detailed performance monitoring"""
        # Get initial resource state
        process = psutil.Process()
        cpu_before = process.cpu_percent()
        memory_before = process.memory_info()
        
        # Measure request
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            request_size = len(json.dumps(payload).encode('utf-8'))
            
            response = requests.post(self.api_url, json=payload, timeout=timeout)
            response_time = time.time() - start_time
            
            # Get resource usage after request
            cpu_after = process.cpu_percent()
            memory_after = process.memory_info()
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                response_size = len(response_text.encode('utf-8'))
                
                # Calculate resource usage
                cpu_usage = max(cpu_after - cpu_before, 0)  # CPU percentage increase
                memory_usage = (memory_after.rss - memory_before.rss) / (1024 * 1024)  # MB
                memory_usage_percent = (memory_after.rss / psutil.virtual_memory().total) * 100
                
                return PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time=response_time,
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage_percent,
                    memory_usage_mb=memory_usage,
                    request_size=request_size,
                    response_size=response_size,
                    success=True
                )
            else:
                return PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time=response_time,
                    cpu_usage=0,
                    memory_usage=0,
                    memory_usage_mb=0,
                    request_size=request_size,
                    response_size=0,
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return PerformanceMetrics(
                timestamp=datetime.now(),
                response_time=response_time,
                cpu_usage=0,
                memory_usage=0,
                memory_usage_mb=0,
                request_size=len(prompt.encode('utf-8')),
                response_size=0,
                success=False,
                error_message=f"Request error: {str(e)}"
            )
    
    def run_performance_benchmark(self, scenario_name: str, iterations: int = 5) -> Dict[str, Any]:
        """Run performance benchmark for a specific scenario"""
        scenario = self.performance_scenarios[scenario_name]
        prompt = scenario["prompt"]
        expected_time = scenario["expected_response_time"]
        category = scenario["category"]
        
        print(f"  ⚡ Benchmarking: {scenario_name} ({iterations} iterations)")
        
        results = {
            "scenario_name": scenario_name,
            "category": category,
            "expected_response_time": expected_time,
            "iterations": iterations,
            "metrics": []
        }
        
        # Test custom model
        print(f"    Testing {self.model_name}...")
        custom_metrics = []
        
        for i in range(iterations):
            metrics = self.send_request_with_monitoring(self.model_name, prompt)
            custom_metrics.append(metrics)
            
            # Store in database
            self.store_performance_metrics(self.model_name, scenario_name, metrics)
            
            time.sleep(0.5)  # Brief pause between requests
        
        results["custom_model_metrics"] = custom_metrics
        
        # Test base model for comparison
        print(f"    Testing {self.base_model} (baseline)...")
        base_metrics = []
        
        for i in range(iterations):
            metrics = self.send_request_with_monitoring(self.base_model, prompt)
            base_metrics.append(metrics)
            
            # Store in database
            self.store_performance_metrics(self.base_model, scenario_name, metrics)
            
            time.sleep(0.5)
        
        results["base_model_metrics"] = base_metrics
        
        # Calculate comparative statistics
        results["performance_comparison"] = self.calculate_performance_comparison(
            custom_metrics, base_metrics
        )
        
        return results
    
    def store_performance_metrics(self, model_name: str, scenario_name: str, 
                                metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics (
                model_name, scenario_name, timestamp, response_time, cpu_usage,
                memory_usage, memory_usage_mb, request_size, response_size,
                success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_name,
            scenario_name,
            metrics.timestamp.isoformat(),
            metrics.response_time,
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.memory_usage_mb,
            metrics.request_size,
            metrics.response_size,
            metrics.success,
            metrics.error_message
        ))
        
        conn.commit()
        conn.close()
    
    def calculate_performance_comparison(self, custom_metrics: List[PerformanceMetrics], 
                                       base_metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Calculate performance comparison between custom and base model"""
        # Filter successful requests only
        custom_successful = [m for m in custom_metrics if m.success]
        base_successful = [m for m in base_metrics if m.success]
        
        if not custom_successful or not base_successful:
            return {"error": "Insufficient successful requests for comparison"}
        
        # Calculate statistics for custom model
        custom_response_times = [m.response_time for m in custom_successful]
        custom_memory_usage = [m.memory_usage_mb for m in custom_successful]
        custom_cpu_usage = [m.cpu_usage for m in custom_successful]
        
        # Calculate statistics for base model
        base_response_times = [m.response_time for m in base_successful]
        base_memory_usage = [m.memory_usage_mb for m in base_successful]
        base_cpu_usage = [m.cpu_usage for m in base_successful]
        
        # Performance comparison
        comparison = {
            "custom_model": {
                "avg_response_time": statistics.mean(custom_response_times),
                "min_response_time": min(custom_response_times),
                "max_response_time": max(custom_response_times),
                "avg_memory_usage_mb": statistics.mean(custom_memory_usage),
                "avg_cpu_usage": statistics.mean(custom_cpu_usage),
                "success_rate": len(custom_successful) / len(custom_metrics)
            },
            "base_model": {
                "avg_response_time": statistics.mean(base_response_times),
                "min_response_time": min(base_response_times),
                "max_response_time": max(base_response_times),
                "avg_memory_usage_mb": statistics.mean(base_memory_usage),
                "avg_cpu_usage": statistics.mean(base_cpu_usage),
                "success_rate": len(base_successful) / len(base_metrics)
            }
        }
        
        # Calculate improvement ratios
        custom_avg_time = comparison["custom_model"]["avg_response_time"]
        base_avg_time = comparison["base_model"]["avg_response_time"]
        
        comparison["performance_ratios"] = {
            "response_time_ratio": custom_avg_time / base_avg_time if base_avg_time > 0 else 1.0,
            "memory_efficiency_ratio": (comparison["base_model"]["avg_memory_usage_mb"] / 
                                      comparison["custom_model"]["avg_memory_usage_mb"] 
                                      if comparison["custom_model"]["avg_memory_usage_mb"] > 0 else 1.0),
            "cpu_efficiency_ratio": (comparison["base_model"]["avg_cpu_usage"] / 
                                   comparison["custom_model"]["avg_cpu_usage"] 
                                   if comparison["custom_model"]["avg_cpu_usage"] > 0 else 1.0)
        }
        
        # Performance verdict
        response_time_improvement = comparison["performance_ratios"]["response_time_ratio"] < 1.0
        memory_improvement = comparison["performance_ratios"]["memory_efficiency_ratio"] > 1.0
        cpu_improvement = comparison["performance_ratios"]["cpu_efficiency_ratio"] > 1.0
        
        improvements = sum([response_time_improvement, memory_improvement, cpu_improvement])
        
        if improvements >= 2:
            comparison["verdict"] = "Custom model shows significant performance improvement"
        elif improvements == 1:
            comparison["verdict"] = "Custom model shows moderate performance improvement"
        else:
            comparison["verdict"] = "Custom model performance is similar to base model"
        
        return comparison
    
    def run_comprehensive_performance_analysis(self, session_id: str, 
                                             iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        print(f"🚀 Starting comprehensive performance analysis: {session_id}")
        print(f"📊 Testing {len(self.performance_scenarios)} scenarios with {iterations} iterations each")
        print("=" * 70)
        
        # Start resource monitoring
        self.start_resource_monitoring(session_id)
        
        # Create session record
        session_start = datetime.now()
        self.create_session_record(session_id, session_start)
        
        analysis_results = {
            "session_info": {
                "session_id": session_id,
                "model_name": self.model_name,
                "base_model": self.base_model,
                "start_time": session_start.isoformat(),
                "iterations_per_scenario": iterations
            },
            "scenario_results": {},
            "overall_performance": {},
            "resource_analysis": {}
        }
        
        total_requests = 0
        successful_requests = 0
        all_response_times = []
        all_cpu_usage = []
        all_memory_usage = []
        
        # Run benchmarks for each scenario
        for scenario_name in self.performance_scenarios:
            try:
                print(f"\n📈 Scenario: {scenario_name}")
                scenario_results = self.run_performance_benchmark(scenario_name, iterations)
                analysis_results["scenario_results"][scenario_name] = scenario_results
                
                # Aggregate metrics
                custom_metrics = scenario_results["custom_model_metrics"]
                successful_custom = [m for m in custom_metrics if m.success]
                
                total_requests += len(custom_metrics)
                successful_requests += len(successful_custom)
                
                if successful_custom:
                    all_response_times.extend([m.response_time for m in successful_custom])
                    all_cpu_usage.extend([m.cpu_usage for m in successful_custom])
                    all_memory_usage.extend([m.memory_usage_mb for m in successful_custom])
                
                # Display immediate results
                if "performance_comparison" in scenario_results:
                    comp = scenario_results["performance_comparison"]
                    if "error" not in comp:
                        custom_time = comp["custom_model"]["avg_response_time"]
                        base_time = comp["base_model"]["avg_response_time"]
                        ratio = comp["performance_ratios"]["response_time_ratio"]
                        
                        if ratio < 0.9:
                            status = f"✅ FASTER ({ratio:.2f}x)"
                        elif ratio > 1.1:
                            status = f"⚠️  SLOWER ({ratio:.2f}x)"
                        else:
                            status = f"➡️  SIMILAR ({ratio:.2f}x)"
                        
                        print(f"    Custom: {custom_time:.2f}s | Base: {base_time:.2f}s | {status}")
                        print(f"    Verdict: {comp['verdict']}")
                
            except Exception as e:
                print(f"    ❌ Scenario failed: {str(e)}")
                analysis_results["scenario_results"][scenario_name] = {"error": str(e)}
        
        # Stop resource monitoring
        self.stop_resource_monitoring()
        
        # Calculate overall performance metrics
        session_end = datetime.now()
        
        if all_response_times:
            analysis_results["overall_performance"] = {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": successful_requests / total_requests,
                "avg_response_time": statistics.mean(all_response_times),
                "min_response_time": min(all_response_times),
                "max_response_time": max(all_response_times),
                "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times),
                "avg_cpu_usage": statistics.mean(all_cpu_usage) if all_cpu_usage else 0.0,
                "avg_memory_usage_mb": statistics.mean(all_memory_usage) if all_memory_usage else 0.0,
                "performance_grade": self.calculate_performance_grade(all_response_times, successful_requests / total_requests)
            }
        
        # Analyze resource usage
        if self.resource_snapshots:
            analysis_results["resource_analysis"] = self.analyze_resource_usage()
        
        # Update session record
        analysis_results["session_info"]["end_time"] = session_end.isoformat()
        analysis_results["session_info"]["total_duration"] = (session_end - session_start).total_seconds()
        
        overall_perf = analysis_results.get("overall_performance", {})
        self.update_session_record(
            session_id, session_end, 
            overall_perf.get("total_requests", 0),
            overall_perf.get("successful_requests", 0),
            overall_perf.get("avg_response_time", 0.0),
            overall_perf.get("avg_cpu_usage", 0.0),
            overall_perf.get("avg_memory_usage_mb", 0.0),
            overall_perf.get("performance_grade", "F")
        )
        
        return analysis_results
    
    def analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze resource usage from monitoring snapshots"""
        if not self.resource_snapshots:
            return {"error": "No resource snapshots available"}
        
        cpu_usage = [s.cpu_percent for s in self.resource_snapshots]
        memory_usage = [s.memory_percent for s in self.resource_snapshots]
        memory_used_mb = [s.memory_used_mb for s in self.resource_snapshots]
        
        return {
            "monitoring_duration": len(self.resource_snapshots),
            "cpu_usage": {
                "avg": statistics.mean(cpu_usage),
                "min": min(cpu_usage),
                "max": max(cpu_usage),
                "std_dev": statistics.stdev(cpu_usage) if len(cpu_usage) > 1 else 0.0
            },
            "memory_usage": {
                "avg_percent": statistics.mean(memory_usage),
                "max_percent": max(memory_usage),
                "avg_used_mb": statistics.mean(memory_used_mb),
                "max_used_mb": max(memory_used_mb)
            },
            "resource_efficiency": {
                "cpu_stable": statistics.stdev(cpu_usage) < 10.0 if len(cpu_usage) > 1 else True,
                "memory_stable": statistics.stdev(memory_usage) < 5.0 if len(memory_usage) > 1 else True,
                "resource_grade": self.calculate_resource_grade(cpu_usage, memory_usage)
            }
        }
    
    def calculate_performance_grade(self, response_times: List[float], success_rate: float) -> str:
        """Calculate performance grade based on response times and success rate"""
        if not response_times:
            return "F"
        
        avg_time = statistics.mean(response_times)
        
        # Grading criteria
        if success_rate >= 0.95 and avg_time <= 5.0:
            return "A"
        elif success_rate >= 0.90 and avg_time <= 8.0:
            return "B"
        elif success_rate >= 0.85 and avg_time <= 12.0:
            return "C"
        elif success_rate >= 0.75 and avg_time <= 20.0:
            return "D"
        else:
            return "F"
    
    def calculate_resource_grade(self, cpu_usage: List[float], memory_usage: List[float]) -> str:
        """Calculate resource efficiency grade"""
        avg_cpu = statistics.mean(cpu_usage)
        avg_memory = statistics.mean(memory_usage)
        
        # Resource efficiency grading
        if avg_cpu <= 20 and avg_memory <= 50:
            return "A"  # Excellent efficiency
        elif avg_cpu <= 40 and avg_memory <= 70:
            return "B"  # Good efficiency
        elif avg_cpu <= 60 and avg_memory <= 85:
            return "C"  # Acceptable efficiency
        elif avg_cpu <= 80 and avg_memory <= 95:
            return "D"  # Poor efficiency
        else:
            return "F"  # Very poor efficiency
    
    def create_session_record(self, session_id: str, start_time: datetime):
        """Create benchmark session record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO benchmark_sessions (
                session_id, model_name, base_model, start_time
            ) VALUES (?, ?, ?, ?)
        ''', (session_id, self.model_name, self.base_model, start_time.isoformat()))
        
        conn.commit()
        conn.close()
    
    def update_session_record(self, session_id: str, end_time: datetime,
                            total_requests: int, successful_requests: int,
                            avg_response_time: float, avg_cpu_usage: float,
                            avg_memory_usage: float, performance_grade: str):
        """Update benchmark session record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE benchmark_sessions SET
                end_time = ?, total_requests = ?, successful_requests = ?,
                avg_response_time = ?, avg_cpu_usage = ?, avg_memory_usage = ?,
                performance_grade = ?
            WHERE session_id = ?
        ''', (
            end_time.isoformat(), total_requests, successful_requests,
            avg_response_time, avg_cpu_usage, avg_memory_usage,
            performance_grade, session_id
        ))
        
        conn.commit()
        conn.close()
    
    def generate_performance_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate comprehensive performance analysis report"""
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 55)
        
        info = analysis_results["session_info"]
        report.append(f"Session ID: {info['session_id']}")
        report.append(f"Custom Model: {info['model_name']}")
        report.append(f"Base Model: {info['base_model']}")
        report.append(f"Start Time: {info['start_time']}")
        report.append(f"End Time: {info.get('end_time', 'N/A')}")
        report.append(f"Duration: {info.get('total_duration', 0):.1f}s")
        report.append("")
        
        # Overall Performance Summary
        if "overall_performance" in analysis_results:
            overall = analysis_results["overall_performance"]
            report.append("OVERALL PERFORMANCE SUMMARY")
            report.append("-" * 30)
            report.append(f"Total Requests: {overall['total_requests']}")
            report.append(f"Successful Requests: {overall['successful_requests']}")
            report.append(f"Success Rate: {overall['success_rate']:.2%}")
            report.append(f"Average Response Time: {overall['avg_response_time']:.3f}s")
            report.append(f"95th Percentile Response Time: {overall['p95_response_time']:.3f}s")
            report.append(f"Average CPU Usage: {overall['avg_cpu_usage']:.1f}%")
            report.append(f"Average Memory Usage: {overall['avg_memory_usage_mb']:.1f} MB")
            report.append(f"Performance Grade: {overall['performance_grade']}")
            report.append("")
        
        # Resource Analysis
        if "resource_analysis" in analysis_results and "error" not in analysis_results["resource_analysis"]:
            resource = analysis_results["resource_analysis"]
            report.append("RESOURCE USAGE ANALYSIS")
            report.append("-" * 25)
            report.append(f"Monitoring Duration: {resource['monitoring_duration']} snapshots")
            
            cpu = resource["cpu_usage"]
            report.append(f"CPU Usage - Avg: {cpu['avg']:.1f}%, Max: {cpu['max']:.1f}%, StdDev: {cpu['std_dev']:.1f}%")
            
            memory = resource["memory_usage"]
            report.append(f"Memory Usage - Avg: {memory['avg_percent']:.1f}%, Max: {memory['max_percent']:.1f}%")
            report.append(f"Memory Used - Avg: {memory['avg_used_mb']:.1f} MB, Max: {memory['max_used_mb']:.1f} MB")
            
            efficiency = resource["resource_efficiency"]
            report.append(f"Resource Stability - CPU: {'✅' if efficiency['cpu_stable'] else '⚠️'}, Memory: {'✅' if efficiency['memory_stable'] else '⚠️'}")
            report.append(f"Resource Efficiency Grade: {efficiency['resource_grade']}")
            report.append("")
        
        # Scenario Performance Comparison
        report.append("SCENARIO PERFORMANCE COMPARISON")
        report.append("-" * 35)
        
        for scenario_name, scenario_results in analysis_results["scenario_results"].items():
            if "error" in scenario_results:
                report.append(f"{scenario_name}: ERROR - {scenario_results['error']}")
                continue
            
            report.append(f"{scenario_name.replace('_', ' ').title()}:")
            
            if "performance_comparison" in scenario_results:
                comp = scenario_results["performance_comparison"]
                if "error" not in comp:
                    custom = comp["custom_model"]
                    base = comp["base_model"]
                    ratios = comp["performance_ratios"]
                    
                    report.append(f"  Custom Model - Time: {custom['avg_response_time']:.3f}s, Memory: {custom['avg_memory_usage_mb']:.1f}MB")
                    report.append(f"  Base Model   - Time: {base['avg_response_time']:.3f}s, Memory: {base['avg_memory_usage_mb']:.1f}MB")
                    report.append(f"  Performance Ratio: {ratios['response_time_ratio']:.2f}x")
                    report.append(f"  Verdict: {comp['verdict']}")
                else:
                    report.append(f"  Comparison Error: {comp['error']}")
            
            report.append("")
        
        # Performance Recommendations
        report.append("PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 30)
        
        if "overall_performance" in analysis_results:
            overall = analysis_results["overall_performance"]
            grade = overall["performance_grade"]
            avg_time = overall["avg_response_time"]
            success_rate = overall["success_rate"]
            
            if grade in ["A", "B"]:
                report.append("✅ Excellent performance! Model meets or exceeds performance targets.")
            elif grade == "C":
                report.append("⚠️  Acceptable performance with room for improvement.")
            else:
                report.append("❌ Performance below expectations. Optimization needed.")
            
            if avg_time > 10.0:
                report.append("⚠️  Response times are high. Consider:")
                report.append("   - Model parameter optimization")
                report.append("   - Hardware upgrade (more RAM/faster CPU)")
                report.append("   - Prompt engineering to reduce complexity")
            
            if success_rate < 0.90:
                report.append("⚠️  Success rate below 90%. Consider:")
                report.append("   - Model configuration review")
                report.append("   - Timeout adjustments")
                report.append("   - Error handling improvements")
        
        if "resource_analysis" in analysis_results and "error" not in analysis_results["resource_analysis"]:
            resource = analysis_results["resource_analysis"]
            efficiency = resource["resource_efficiency"]
            
            if efficiency["resource_grade"] in ["D", "F"]:
                report.append("⚠️  High resource usage detected. Consider:")
                report.append("   - Memory optimization")
                report.append("   - Concurrent request limiting")
                report.append("   - System resource monitoring")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Enhanced Performance Monitor")
    parser.add_argument("--model", default="olympus-coder-v1", help="Custom model name")
    parser.add_argument("--base-model", default="llama3:8b", help="Base model for comparison")
    parser.add_argument("--host", default="localhost", help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port")
    parser.add_argument("--session-id", help="Session ID for tracking")
    parser.add_argument("--iterations", type=int, default=3, help="Iterations per scenario")
    parser.add_argument("--db-path", default="olympus_performance_monitoring.db", help="Database path")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(
        model_name=args.model,
        base_model=args.base_model,
        host=args.host,
        port=args.port,
        db_path=args.db_path
    )
    
    # Generate session ID
    session_id = args.session_id or f"perf_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Run comprehensive performance analysis
    results = monitor.run_comprehensive_performance_analysis(session_id, args.iterations)
    
    # Generate and display report
    report = monitor.generate_performance_report(results)
    print("\n" + "=" * 70)
    print("PERFORMANCE ANALYSIS COMPLETE")
    print("=" * 70)
    print(report)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to: {args.output}")
    
    # Exit with appropriate code based on performance grade
    if "overall_performance" in results:
        grade = results["overall_performance"]["performance_grade"]
        success = grade in ["A", "B", "C"]
    else:
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()