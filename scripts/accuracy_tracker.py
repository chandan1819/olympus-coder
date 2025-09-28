#!/usr/bin/env python3
"""
Olympus-Coder-v1 Enhanced Accuracy Tracking System

Comprehensive accuracy tracking with task completion rates, structured response monitoring,
and human intervention tracking as specified in requirements 5.1, 5.2, and 3.4.
"""

import json
import sys
import time
import sqlite3
import requests
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

@dataclass
class TaskResult:
    """Data class for tracking individual task results"""
    task_id: str
    task_type: str
    prompt: str
    timestamp: datetime
    success: bool
    completion_rate: float
    response_time: float
    structured_response_accuracy: float
    human_intervention_required: bool
    error_message: Optional[str] = None
    response_text: Optional[str] = None

@dataclass
class AccuracyMetrics:
    """Data class for accuracy metrics"""
    total_tasks: int
    successful_tasks: int
    task_completion_rate: float
    avg_structured_response_accuracy: float
    human_intervention_rate: float
    avg_response_time: float
    accuracy_grade: str

class AccuracyTracker:
    """Enhanced accuracy tracking system for Olympus-Coder-v1"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434,
                 db_path: str = "olympus_accuracy_tracking.db"):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        self.db_path = db_path
        
        # Initialize database
        self.init_database()
        
        # Task categories for tracking
        self.task_categories = {
            "code_generation": {
                "description": "Generate new code from requirements",
                "target_completion_rate": 0.75,  # 75% from requirement 5.1
                "structured_response_target": 0.95  # >95% from requirement 3.4
            },
            "debugging": {
                "description": "Debug and fix existing code",
                "target_completion_rate": 0.75,
                "structured_response_target": 0.95
            },
            "tool_usage": {
                "description": "Make structured tool requests",
                "target_completion_rate": 0.75,
                "structured_response_target": 0.95
            },
            "context_analysis": {
                "description": "Analyze project context and structure",
                "target_completion_rate": 0.75,
                "structured_response_target": 0.95
            },
            "autonomous_task": {
                "description": "Complete complex multi-step tasks",
                "target_completion_rate": 0.75,
                "structured_response_target": 0.95
            }
        }
    
    def init_database(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                prompt TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                completion_rate REAL NOT NULL,
                response_time REAL NOT NULL,
                structured_response_accuracy REAL NOT NULL,
                human_intervention_required BOOLEAN NOT NULL,
                error_message TEXT,
                response_text TEXT
            )
        ''')
        
        # Create accuracy_sessions table for tracking assessment sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accuracy_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_tasks INTEGER DEFAULT 0,
                successful_tasks INTEGER DEFAULT 0,
                task_completion_rate REAL DEFAULT 0.0,
                avg_structured_response_accuracy REAL DEFAULT 0.0,
                human_intervention_rate REAL DEFAULT 0.0,
                avg_response_time REAL DEFAULT 0.0,
                accuracy_grade TEXT DEFAULT 'F'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def send_request(self, prompt: str, timeout: int = 45) -> Tuple[bool, str, float]:
        """Send request to model and measure response time"""
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
                return True, result.get("response", ""), response_time
            else:
                return False, f"HTTP {response.status_code}: {response.text}", response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            return False, f"Request error: {str(e)}", response_time
    
    def evaluate_structured_response_accuracy(self, response_text: str, task_type: str) -> float:
        """Evaluate structured response accuracy based on task type"""
        response_lower = response_text.lower()
        
        if task_type == "tool_usage":
            # Check for proper JSON structure
            has_json_structure = "{" in response_text and "}" in response_text
            has_tool_name = "tool_name" in response_lower
            has_parameters = "parameters" in response_lower
            
            # Calculate accuracy score
            criteria_met = sum([has_json_structure, has_tool_name, has_parameters])
            return criteria_met / 3.0
        
        elif task_type == "code_generation":
            # Check for proper code formatting
            has_code_blocks = "```" in response_text
            has_function_def = bool(re.search(r'\b(def|function)\s+\w+', response_text))
            has_proper_structure = ":" in response_text or "{" in response_text
            
            criteria_met = sum([has_code_blocks, has_function_def, has_proper_structure])
            return criteria_met / 3.0
        
        elif task_type == "debugging":
            # Check for debugging response structure
            has_error_identification = any(error_type in response_lower 
                                         for error_type in ["error", "exception", "bug", "issue"])
            has_explanation = any(keyword in response_lower 
                                for keyword in ["because", "due to", "caused by", "reason"])
            has_solution = any(keyword in response_lower 
                             for keyword in ["fix", "solution", "correct", "change"])
            
            criteria_met = sum([has_error_identification, has_explanation, has_solution])
            return criteria_met / 3.0
        
        else:
            # Generic structured response check
            has_clear_structure = len(response_text.split('\n')) > 1
            has_proper_formatting = any(marker in response_text 
                                      for marker in ["```", "1.", "-", "*"])
            
            criteria_met = sum([has_clear_structure, has_proper_formatting])
            return criteria_met / 2.0
    
    def evaluate_task_completion(self, response_text: str, task_type: str, 
                               expected_elements: List[str]) -> Tuple[float, bool]:
        """Evaluate task completion rate and determine if human intervention is needed"""
        response_lower = response_text.lower()
        
        # Check for expected elements
        found_elements = [elem for elem in expected_elements 
                         if elem.lower() in response_lower]
        element_coverage = len(found_elements) / len(expected_elements) if expected_elements else 1.0
        
        # Check for completion indicators
        completion_indicators = {
            "code_generation": ["def", "function", "class", "return"],
            "debugging": ["error", "fix", "solution", "correct"],
            "tool_usage": ["tool_name", "parameters", "{", "}"],
            "context_analysis": ["import", "from", "file", "directory"],
            "autonomous_task": ["complete", "finished", "done", "implemented"]
        }
        
        indicators = completion_indicators.get(task_type, ["complete", "done"])
        found_indicators = sum(1 for indicator in indicators if indicator in response_lower)
        indicator_coverage = found_indicators / len(indicators)
        
        # Calculate overall completion rate
        completion_rate = (element_coverage + indicator_coverage) / 2.0
        
        # Determine if human intervention is needed
        # Human intervention required if completion rate < 70% or response seems incomplete
        human_intervention_needed = (
            completion_rate < 0.7 or
            len(response_text.strip()) < 50 or
            "i don't know" in response_lower or
            "cannot" in response_lower or
            "unable" in response_lower
        )
        
        return completion_rate, human_intervention_needed
    
    def track_task_result(self, task_id: str, task_type: str, prompt: str, 
                         expected_elements: List[str]) -> TaskResult:
        """Track a single task result"""
        # Send request and measure performance
        success, response_text, response_time = self.send_request(prompt)
        
        if success:
            # Evaluate completion and intervention needs
            completion_rate, human_intervention = self.evaluate_task_completion(
                response_text, task_type, expected_elements
            )
            
            # Evaluate structured response accuracy
            structured_accuracy = self.evaluate_structured_response_accuracy(
                response_text, task_type
            )
            
            task_result = TaskResult(
                task_id=task_id,
                task_type=task_type,
                prompt=prompt,
                timestamp=datetime.now(),
                success=True,
                completion_rate=completion_rate,
                response_time=response_time,
                structured_response_accuracy=structured_accuracy,
                human_intervention_required=human_intervention,
                response_text=response_text
            )
        else:
            # Task failed
            task_result = TaskResult(
                task_id=task_id,
                task_type=task_type,
                prompt=prompt,
                timestamp=datetime.now(),
                success=False,
                completion_rate=0.0,
                response_time=response_time,
                structured_response_accuracy=0.0,
                human_intervention_required=True,
                error_message=response_text
            )
        
        # Store in database
        self.store_task_result(task_result)
        
        return task_result
    
    def store_task_result(self, task_result: TaskResult):
        """Store task result in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO task_results (
                task_id, task_type, prompt, timestamp, success, completion_rate,
                response_time, structured_response_accuracy, human_intervention_required,
                error_message, response_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_result.task_id,
            task_result.task_type,
            task_result.prompt,
            task_result.timestamp.isoformat(),
            task_result.success,
            task_result.completion_rate,
            task_result.response_time,
            task_result.structured_response_accuracy,
            task_result.human_intervention_required,
            task_result.error_message,
            task_result.response_text
        ))
        
        conn.commit()
        conn.close()
    
    def run_accuracy_tracking_session(self, session_id: str, 
                                    task_scenarios: List[Dict[str, Any]]) -> AccuracyMetrics:
        """Run a complete accuracy tracking session"""
        print(f"🎯 Starting accuracy tracking session: {session_id}")
        print(f"📊 Tracking {len(task_scenarios)} tasks")
        print("=" * 60)
        
        # Create session record
        session_start = datetime.now()
        self.create_session_record(session_id, session_start)
        
        task_results = []
        
        # Process each task scenario
        for i, scenario in enumerate(task_scenarios):
            task_id = f"{session_id}_task_{i+1}"
            task_type = scenario["task_type"]
            prompt = scenario["prompt"]
            expected_elements = scenario.get("expected_elements", [])
            
            print(f"  📝 Task {i+1}/{len(task_scenarios)}: {task_type}")
            print(f"     Prompt: {prompt[:60]}...")
            
            # Track task result
            result = self.track_task_result(task_id, task_type, prompt, expected_elements)
            task_results.append(result)
            
            # Display immediate feedback
            if result.success:
                status = "✅ SUCCESS" if result.completion_rate >= 0.7 else "⚠️  PARTIAL"
                intervention = "🤖 AUTONOMOUS" if not result.human_intervention_required else "👤 NEEDS HELP"
                print(f"     Result: {status} | Completion: {result.completion_rate:.2%} | {intervention}")
                print(f"     Response Time: {result.response_time:.2f}s | Accuracy: {result.structured_response_accuracy:.2%}")
            else:
                print(f"     Result: ❌ FAILED | Error: {result.error_message}")
            
            print()
            time.sleep(1)  # Brief pause between tasks
        
        # Calculate session metrics
        metrics = self.calculate_session_metrics(task_results)
        
        # Update session record
        session_end = datetime.now()
        self.update_session_record(session_id, session_end, metrics)
        
        print("🎯 Accuracy tracking session complete!")
        print(f"📊 Final Metrics:")
        print(f"   Task Completion Rate: {metrics.task_completion_rate:.2%}")
        print(f"   Structured Response Accuracy: {metrics.avg_structured_response_accuracy:.2%}")
        print(f"   Human Intervention Rate: {metrics.human_intervention_rate:.2%}")
        print(f"   Average Response Time: {metrics.avg_response_time:.2f}s")
        print(f"   Accuracy Grade: {metrics.accuracy_grade}")
        
        return metrics
    
    def calculate_session_metrics(self, task_results: List[TaskResult]) -> AccuracyMetrics:
        """Calculate accuracy metrics from task results"""
        if not task_results:
            return AccuracyMetrics(0, 0, 0.0, 0.0, 0.0, 0.0, "F")
        
        total_tasks = len(task_results)
        successful_tasks = sum(1 for result in task_results if result.success)
        
        # Calculate completion rates for successful tasks only
        successful_results = [r for r in task_results if r.success]
        
        if successful_results:
            avg_completion_rate = statistics.mean([r.completion_rate for r in successful_results])
            avg_structured_accuracy = statistics.mean([r.structured_response_accuracy for r in successful_results])
            avg_response_time = statistics.mean([r.response_time for r in successful_results])
        else:
            avg_completion_rate = 0.0
            avg_structured_accuracy = 0.0
            avg_response_time = 0.0
        
        # Calculate human intervention rate (across all tasks)
        human_interventions = sum(1 for result in task_results if result.human_intervention_required)
        human_intervention_rate = human_interventions / total_tasks
        
        # Calculate overall task completion rate
        task_completion_rate = successful_tasks / total_tasks
        
        # Calculate accuracy grade
        accuracy_grade = self.calculate_accuracy_grade(
            task_completion_rate, avg_structured_accuracy, human_intervention_rate
        )
        
        return AccuracyMetrics(
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            task_completion_rate=task_completion_rate,
            avg_structured_response_accuracy=avg_structured_accuracy,
            human_intervention_rate=human_intervention_rate,
            avg_response_time=avg_response_time,
            accuracy_grade=accuracy_grade
        )
    
    def calculate_accuracy_grade(self, task_completion_rate: float, 
                               structured_accuracy: float, 
                               human_intervention_rate: float) -> str:
        """Calculate accuracy grade based on multiple factors"""
        # Requirements targets:
        # - Task completion rate: 75% (requirement 5.1)
        # - Structured response accuracy: >95% (requirement 3.4)
        # - Human intervention reduction: 50% (requirement 5.2)
        
        # Grade based on meeting requirements
        meets_completion_target = task_completion_rate >= 0.75
        meets_accuracy_target = structured_accuracy >= 0.95
        meets_intervention_target = human_intervention_rate <= 0.50
        
        targets_met = sum([meets_completion_target, meets_accuracy_target, meets_intervention_target])
        
        if targets_met == 3:
            return "A"  # Meets all targets
        elif targets_met == 2:
            return "B"  # Meets most targets
        elif targets_met == 1:
            return "C"  # Meets some targets
        elif task_completion_rate >= 0.60:
            return "D"  # Partial performance
        else:
            return "F"  # Poor performance
    
    def create_session_record(self, session_id: str, start_time: datetime):
        """Create accuracy session record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO accuracy_sessions (
                session_id, model_name, start_time
            ) VALUES (?, ?, ?)
        ''', (session_id, self.model_name, start_time.isoformat()))
        
        conn.commit()
        conn.close()
    
    def update_session_record(self, session_id: str, end_time: datetime, 
                            metrics: AccuracyMetrics):
        """Update accuracy session record with final metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE accuracy_sessions SET
                end_time = ?,
                total_tasks = ?,
                successful_tasks = ?,
                task_completion_rate = ?,
                avg_structured_response_accuracy = ?,
                human_intervention_rate = ?,
                avg_response_time = ?,
                accuracy_grade = ?
            WHERE session_id = ?
        ''', (
            end_time.isoformat(),
            metrics.total_tasks,
            metrics.successful_tasks,
            metrics.task_completion_rate,
            metrics.avg_structured_response_accuracy,
            metrics.human_intervention_rate,
            metrics.avg_response_time,
            metrics.accuracy_grade,
            session_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_historical_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get historical accuracy metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get sessions from last N days
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT * FROM accuracy_sessions 
            WHERE start_time >= ? AND end_time IS NOT NULL
            ORDER BY start_time DESC
        ''', (cutoff_date,))
        
        sessions = cursor.fetchall()
        
        if not sessions:
            conn.close()
            return {"error": "No historical data available"}
        
        # Calculate historical trends
        completion_rates = [session[5] for session in sessions]  # task_completion_rate
        accuracy_rates = [session[6] for session in sessions]   # avg_structured_response_accuracy
        intervention_rates = [session[7] for session in sessions]  # human_intervention_rate
        response_times = [session[8] for session in sessions]   # avg_response_time
        
        historical_metrics = {
            "period_days": days,
            "total_sessions": len(sessions),
            "avg_task_completion_rate": statistics.mean(completion_rates),
            "avg_structured_response_accuracy": statistics.mean(accuracy_rates),
            "avg_human_intervention_rate": statistics.mean(intervention_rates),
            "avg_response_time": statistics.mean(response_times),
            "completion_rate_trend": self.calculate_trend(completion_rates),
            "accuracy_trend": self.calculate_trend(accuracy_rates),
            "intervention_trend": self.calculate_trend(intervention_rates),
            "latest_session": {
                "session_id": sessions[0][1],
                "completion_rate": sessions[0][5],
                "accuracy": sessions[0][6],
                "intervention_rate": sessions[0][7],
                "grade": sessions[0][9]
            }
        }
        
        conn.close()
        return historical_metrics
    
    def calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from list of values"""
        if len(values) < 2:
            return "stable"
        
        # Compare first half to second half
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid])
        second_half_avg = statistics.mean(values[mid:])
        
        if second_half_avg > first_half_avg * 1.05:
            return "improving"
        elif second_half_avg < first_half_avg * 0.95:
            return "declining"
        else:
            return "stable"
    
    def generate_accuracy_report(self, session_id: str = None, 
                               historical_days: int = 30) -> str:
        """Generate comprehensive accuracy tracking report"""
        report = []
        
        report.append("OLYMPUS-CODER-V1 ACCURACY TRACKING REPORT")
        report.append("=" * 50)
        report.append(f"Model: {self.model_name}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Historical metrics
        historical = self.get_historical_metrics(historical_days)
        
        if "error" not in historical:
            report.append("HISTORICAL PERFORMANCE (Last 30 Days)")
            report.append("-" * 40)
            report.append(f"Total Sessions: {historical['total_sessions']}")
            report.append(f"Avg Task Completion Rate: {historical['avg_task_completion_rate']:.2%}")
            report.append(f"Avg Structured Response Accuracy: {historical['avg_structured_response_accuracy']:.2%}")
            report.append(f"Avg Human Intervention Rate: {historical['avg_human_intervention_rate']:.2%}")
            report.append(f"Avg Response Time: {historical['avg_response_time']:.2f}s")
            report.append("")
            
            report.append("PERFORMANCE TRENDS")
            report.append("-" * 18)
            report.append(f"Task Completion: {historical['completion_rate_trend'].title()}")
            report.append(f"Response Accuracy: {historical['accuracy_trend'].title()}")
            report.append(f"Human Intervention: {historical['intervention_trend'].title()}")
            report.append("")
            
            # Requirements compliance
            report.append("REQUIREMENTS COMPLIANCE")
            report.append("-" * 23)
            
            latest = historical['latest_session']
            
            # Requirement 5.1: 75% autonomous completion rate
            completion_compliant = latest['completion_rate'] >= 0.75
            report.append(f"Req 5.1 - Task Completion (≥75%): {'✅' if completion_compliant else '❌'} {latest['completion_rate']:.2%}")
            
            # Requirement 3.4: >95% structured response accuracy
            accuracy_compliant = latest['accuracy'] >= 0.95
            report.append(f"Req 3.4 - Response Accuracy (>95%): {'✅' if accuracy_compliant else '❌'} {latest['accuracy']:.2%}")
            
            # Requirement 5.2: 50% reduction in human intervention
            intervention_compliant = latest['intervention_rate'] <= 0.50
            report.append(f"Req 5.2 - Human Intervention (≤50%): {'✅' if intervention_compliant else '❌'} {latest['intervention_rate']:.2%}")
            
            report.append("")
            
            # Overall grade
            report.append(f"Current Accuracy Grade: {latest['grade']}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        if "error" not in historical:
            latest = historical['latest_session']
            
            if latest['completion_rate'] < 0.75:
                report.append("⚠️  Task completion rate below target. Review prompt engineering and model parameters.")
            
            if latest['accuracy'] < 0.95:
                report.append("⚠️  Structured response accuracy below target. Improve output formatting instructions.")
            
            if latest['intervention_rate'] > 0.50:
                report.append("⚠️  High human intervention rate. Enhance autonomous decision-making capabilities.")
            
            if historical['completion_rate_trend'] == "declining":
                report.append("📉 Task completion trend is declining. Monitor model performance closely.")
            
            if historical['accuracy_trend'] == "declining":
                report.append("📉 Response accuracy trend is declining. Consider model retraining or prompt updates.")
            
            if all([latest['completion_rate'] >= 0.75, latest['accuracy'] >= 0.95, latest['intervention_rate'] <= 0.50]):
                report.append("🎉 All accuracy targets met! Model performance is excellent.")
        else:
            report.append("📊 No historical data available. Run accuracy tracking sessions to generate metrics.")
        
        return "\n".join(report)

# Import regex for pattern matching
import re

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Enhanced Accuracy Tracker")
    parser.add_argument("--model", default="olympus-coder-v1", help="Model name to track")
    parser.add_argument("--host", default="localhost", help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port")
    parser.add_argument("--session-id", help="Session ID for tracking")
    parser.add_argument("--db-path", default="olympus_accuracy_tracking.db", help="Database path")
    parser.add_argument("--report-only", action="store_true", help="Generate report only")
    parser.add_argument("--historical-days", type=int, default=30, help="Days for historical analysis")
    
    args = parser.parse_args()
    
    tracker = AccuracyTracker(args.model, args.host, args.port, args.db_path)
    
    if args.report_only:
        # Generate report only
        report = tracker.generate_accuracy_report(historical_days=args.historical_days)
        print(report)
        return
    
    # Default test scenarios for accuracy tracking
    test_scenarios = [
        {
            "task_type": "code_generation",
            "prompt": "Generate a Python function that calculates the area of a circle given its radius",
            "expected_elements": ["def", "pi", "radius", "return", "area"]
        },
        {
            "task_type": "tool_usage",
            "prompt": "I need to read the contents of a file called 'config.json'. Provide the appropriate tool request.",
            "expected_elements": ["tool_name", "parameters", "read_file", "config.json"]
        },
        {
            "task_type": "debugging",
            "prompt": "Debug this Python error: 'TypeError: unsupported operand type(s) for +: 'int' and 'str''. Explain and fix.",
            "expected_elements": ["TypeError", "int", "str", "fix", "solution"]
        },
        {
            "task_type": "context_analysis",
            "prompt": "Given project structure: src/main.py, src/utils/helpers.py - write import statement for helpers in main.py",
            "expected_elements": ["import", "from", "src.utils.helpers", "helpers"]
        },
        {
            "task_type": "autonomous_task",
            "prompt": "Create a complete Python script that reads a CSV file and calculates average values for numeric columns",
            "expected_elements": ["import", "csv", "def", "average", "numeric", "open"]
        }
    ]
    
    # Run accuracy tracking session
    session_id = args.session_id or f"accuracy_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    metrics = tracker.run_accuracy_tracking_session(session_id, test_scenarios)
    
    # Generate and display report
    report = tracker.generate_accuracy_report(session_id, args.historical_days)
    print("\n" + "=" * 60)
    print("ACCURACY TRACKING COMPLETE")
    print("=" * 60)
    print(report)
    
    # Exit with appropriate code based on accuracy grade
    success = metrics.accuracy_grade in ["A", "B", "C"]
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()