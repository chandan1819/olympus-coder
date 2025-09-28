#!/usr/bin/env python3
"""
Olympus-Coder-v1 Monitoring Dashboard

Comprehensive monitoring dashboard that combines accuracy tracking and performance monitoring
to provide a unified view of model performance and compliance with requirements.
"""

import json
import sys
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

class MonitoringDashboard:
    """Unified monitoring dashboard for Olympus-Coder-v1"""
    
    def __init__(self, accuracy_db: str = "olympus_accuracy_tracking.db",
                 performance_db: str = "olympus_performance_monitoring.db"):
        self.accuracy_db = accuracy_db
        self.performance_db = performance_db
    
    def get_accuracy_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get accuracy tracking summary"""
        try:
            conn = sqlite3.connect(self.accuracy_db)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get recent sessions
            cursor.execute('''
                SELECT * FROM accuracy_sessions 
                WHERE start_time >= ? AND end_time IS NOT NULL
                ORDER BY start_time DESC
            ''', (cutoff_date,))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                conn.close()
                return {"status": "no_data", "message": "No accuracy data available"}
            
            # Calculate summary metrics
            completion_rates = [s[5] for s in sessions]  # task_completion_rate
            accuracy_rates = [s[6] for s in sessions]   # avg_structured_response_accuracy
            intervention_rates = [s[7] for s in sessions]  # human_intervention_rate
            
            # Get latest session details
            latest = sessions[0]
            
            summary = {
                "status": "success",
                "period_days": days,
                "total_sessions": len(sessions),
                "latest_session": {
                    "session_id": latest[1],
                    "completion_rate": latest[5],
                    "accuracy": latest[6],
                    "intervention_rate": latest[7],
                    "grade": latest[9],
                    "timestamp": latest[3]
                },
                "averages": {
                    "completion_rate": statistics.mean(completion_rates),
                    "accuracy": statistics.mean(accuracy_rates),
                    "intervention_rate": statistics.mean(intervention_rates)
                },
                "trends": {
                    "completion_trend": self.calculate_trend(completion_rates),
                    "accuracy_trend": self.calculate_trend(accuracy_rates),
                    "intervention_trend": self.calculate_trend(intervention_rates)
                },
                "compliance": {
                    "req_5_1_completion": latest[5] >= 0.75,  # 75% completion rate
                    "req_3_4_accuracy": latest[6] >= 0.95,   # >95% accuracy
                    "req_5_2_intervention": latest[7] <= 0.50  # ≤50% intervention
                }
            }
            
            conn.close()
            return summary
            
        except Exception as e:
            return {"status": "error", "message": f"Accuracy data error: {str(e)}"}
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance monitoring summary"""
        try:
            conn = sqlite3.connect(self.performance_db)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get recent sessions
            cursor.execute('''
                SELECT * FROM benchmark_sessions 
                WHERE start_time >= ? AND end_time IS NOT NULL
                ORDER BY start_time DESC
            ''', (cutoff_date,))
            
            sessions = cursor.fetchall()
            
            if not sessions:
                conn.close()
                return {"status": "no_data", "message": "No performance data available"}
            
            # Calculate summary metrics
            response_times = [s[7] for s in sessions if s[7] > 0]  # avg_response_time
            cpu_usage = [s[8] for s in sessions if s[8] > 0]      # avg_cpu_usage
            memory_usage = [s[9] for s in sessions if s[9] > 0]   # avg_memory_usage
            
            # Get latest session details
            latest = sessions[0]
            
            summary = {
                "status": "success",
                "period_days": days,
                "total_sessions": len(sessions),
                "latest_session": {
                    "session_id": latest[1],
                    "response_time": latest[7],
                    "cpu_usage": latest[8],
                    "memory_usage": latest[9],
                    "grade": latest[10],
                    "timestamp": latest[4]
                },
                "averages": {
                    "response_time": statistics.mean(response_times) if response_times else 0.0,
                    "cpu_usage": statistics.mean(cpu_usage) if cpu_usage else 0.0,
                    "memory_usage": statistics.mean(memory_usage) if memory_usage else 0.0
                },
                "trends": {
                    "response_time_trend": self.calculate_trend(response_times),
                    "cpu_trend": self.calculate_trend(cpu_usage),
                    "memory_trend": self.calculate_trend(memory_usage)
                }
            }
            
            conn.close()
            return summary
            
        except Exception as e:
            return {"status": "error", "message": f"Performance data error: {str(e)}"}
    
    def get_detailed_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get detailed metrics for recent period"""
        detailed = {
            "accuracy_details": {},
            "performance_details": {},
            "task_breakdown": {},
            "scenario_breakdown": {}
        }
        
        # Get detailed accuracy metrics
        try:
            conn = sqlite3.connect(self.accuracy_db)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Task type breakdown
            cursor.execute('''
                SELECT task_type, 
                       COUNT(*) as total_tasks,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_tasks,
                       AVG(completion_rate) as avg_completion_rate,
                       AVG(structured_response_accuracy) as avg_accuracy,
                       SUM(CASE WHEN human_intervention_required THEN 1 ELSE 0 END) as interventions
                FROM task_results 
                WHERE timestamp >= ?
                GROUP BY task_type
            ''', (cutoff_date,))
            
            task_breakdown = cursor.fetchall()
            
            for task in task_breakdown:
                task_type, total, successful, completion, accuracy, interventions = task
                detailed["task_breakdown"][task_type] = {
                    "total_tasks": total,
                    "successful_tasks": successful,
                    "success_rate": successful / total if total > 0 else 0.0,
                    "avg_completion_rate": completion or 0.0,
                    "avg_accuracy": accuracy or 0.0,
                    "intervention_rate": interventions / total if total > 0 else 0.0
                }
            
            conn.close()
            
        except Exception as e:
            detailed["accuracy_details"]["error"] = str(e)
        
        # Get detailed performance metrics
        try:
            conn = sqlite3.connect(self.performance_db)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Scenario breakdown
            cursor.execute('''
                SELECT scenario_name,
                       COUNT(*) as total_requests,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
                       AVG(response_time) as avg_response_time,
                       AVG(memory_usage_mb) as avg_memory_usage
                FROM performance_metrics 
                WHERE timestamp >= ? AND model_name LIKE '%olympus-coder%'
                GROUP BY scenario_name
            ''', (cutoff_date,))
            
            scenario_breakdown = cursor.fetchall()
            
            for scenario in scenario_breakdown:
                scenario_name, total, successful, response_time, memory = scenario
                detailed["scenario_breakdown"][scenario_name] = {
                    "total_requests": total,
                    "successful_requests": successful,
                    "success_rate": successful / total if total > 0 else 0.0,
                    "avg_response_time": response_time or 0.0,
                    "avg_memory_usage": memory or 0.0
                }
            
            conn.close()
            
        except Exception as e:
            detailed["performance_details"]["error"] = str(e)
        
        return detailed
    
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
    
    def calculate_overall_health_score(self, accuracy_summary: Dict[str, Any], 
                                     performance_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall model health score"""
        health_score = 0
        max_score = 100
        issues = []
        
        # Accuracy health (50 points)
        if accuracy_summary["status"] == "success":
            latest_acc = accuracy_summary["latest_session"]
            
            # Task completion rate (20 points)
            completion_score = min(20, (latest_acc["completion_rate"] / 0.75) * 20)
            health_score += completion_score
            
            if latest_acc["completion_rate"] < 0.75:
                issues.append(f"Task completion rate below target: {latest_acc['completion_rate']:.2%}")
            
            # Structured response accuracy (20 points)
            accuracy_score = min(20, (latest_acc["accuracy"] / 0.95) * 20)
            health_score += accuracy_score
            
            if latest_acc["accuracy"] < 0.95:
                issues.append(f"Response accuracy below target: {latest_acc['accuracy']:.2%}")
            
            # Human intervention rate (10 points - inverted)
            intervention_score = max(0, 10 - (latest_acc["intervention_rate"] * 20))
            health_score += intervention_score
            
            if latest_acc["intervention_rate"] > 0.50:
                issues.append(f"High human intervention rate: {latest_acc['intervention_rate']:.2%}")
        
        # Performance health (50 points)
        if performance_summary["status"] == "success":
            latest_perf = performance_summary["latest_session"]
            
            # Response time (25 points)
            target_response_time = 10.0  # seconds
            if latest_perf["response_time"] <= target_response_time:
                response_time_score = 25
            else:
                response_time_score = max(0, 25 - ((latest_perf["response_time"] - target_response_time) * 2))
            health_score += response_time_score
            
            if latest_perf["response_time"] > target_response_time:
                issues.append(f"Response time above target: {latest_perf['response_time']:.2f}s")
            
            # Resource usage (25 points)
            cpu_score = max(0, 12.5 - (latest_perf["cpu_usage"] / 100 * 12.5))
            memory_score = max(0, 12.5 - (latest_perf["memory_usage"] / 1000 * 12.5))  # Assuming MB
            health_score += cpu_score + memory_score
            
            if latest_perf["cpu_usage"] > 50:
                issues.append(f"High CPU usage: {latest_perf['cpu_usage']:.1f}%")
            
            if latest_perf["memory_usage"] > 500:  # 500MB threshold
                issues.append(f"High memory usage: {latest_perf['memory_usage']:.1f}MB")
        
        # Calculate health grade
        health_percentage = health_score / max_score
        
        if health_percentage >= 0.90:
            health_grade = "A"
            health_status = "Excellent"
        elif health_percentage >= 0.80:
            health_grade = "B"
            health_status = "Good"
        elif health_percentage >= 0.70:
            health_grade = "C"
            health_status = "Acceptable"
        elif health_percentage >= 0.60:
            health_grade = "D"
            health_status = "Poor"
        else:
            health_grade = "F"
            health_status = "Critical"
        
        return {
            "health_score": health_score,
            "max_score": max_score,
            "health_percentage": health_percentage,
            "health_grade": health_grade,
            "health_status": health_status,
            "issues": issues
        }
    
    def generate_dashboard_report(self, days: int = 30) -> str:
        """Generate comprehensive monitoring dashboard report"""
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 MONITORING DASHBOARD")
        report.append("=" * 45)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Monitoring Period: Last {days} days")
        report.append("")
        
        # Get summaries
        accuracy_summary = self.get_accuracy_summary(days)
        performance_summary = self.get_performance_summary(days)
        detailed_metrics = self.get_detailed_metrics(7)  # Last 7 days for details
        
        # Overall Health Score
        health = self.calculate_overall_health_score(accuracy_summary, performance_summary)
        
        report.append("OVERALL MODEL HEALTH")
        report.append("-" * 22)
        report.append(f"Health Score: {health['health_score']:.0f}/{health['max_score']} ({health['health_percentage']:.1%})")
        report.append(f"Health Grade: {health['health_grade']}")
        report.append(f"Status: {health['health_status']}")
        
        if health["issues"]:
            report.append("\nCurrent Issues:")
            for issue in health["issues"]:
                report.append(f"  ⚠️  {issue}")
        else:
            report.append("✅ No critical issues detected")
        
        report.append("")
        
        # Accuracy Monitoring
        report.append("ACCURACY MONITORING")
        report.append("-" * 19)
        
        if accuracy_summary["status"] == "success":
            latest = accuracy_summary["latest_session"]
            averages = accuracy_summary["averages"]
            compliance = accuracy_summary["compliance"]
            
            report.append(f"Latest Session: {latest['session_id']}")
            report.append(f"Timestamp: {latest['timestamp']}")
            report.append(f"Accuracy Grade: {latest['grade']}")
            report.append("")
            
            report.append("Current Metrics:")
            report.append(f"  Task Completion Rate: {latest['completion_rate']:.2%}")
            report.append(f"  Structured Response Accuracy: {latest['accuracy']:.2%}")
            report.append(f"  Human Intervention Rate: {latest['intervention_rate']:.2%}")
            report.append("")
            
            report.append(f"Period Averages ({days} days):")
            report.append(f"  Avg Completion Rate: {averages['completion_rate']:.2%}")
            report.append(f"  Avg Response Accuracy: {averages['accuracy']:.2%}")
            report.append(f"  Avg Intervention Rate: {averages['intervention_rate']:.2%}")
            report.append("")
            
            report.append("Requirements Compliance:")
            req_5_1 = "✅" if compliance["req_5_1_completion"] else "❌"
            req_3_4 = "✅" if compliance["req_3_4_accuracy"] else "❌"
            req_5_2 = "✅" if compliance["req_5_2_intervention"] else "❌"
            
            report.append(f"  Req 5.1 - Task Completion (≥75%): {req_5_1}")
            report.append(f"  Req 3.4 - Response Accuracy (>95%): {req_3_4}")
            report.append(f"  Req 5.2 - Human Intervention (≤50%): {req_5_2}")
            
        else:
            report.append(f"Status: {accuracy_summary['message']}")
        
        report.append("")
        
        # Performance Monitoring
        report.append("PERFORMANCE MONITORING")
        report.append("-" * 21)
        
        if performance_summary["status"] == "success":
            latest = performance_summary["latest_session"]
            averages = performance_summary["averages"]
            
            report.append(f"Latest Session: {latest['session_id']}")
            report.append(f"Timestamp: {latest['timestamp']}")
            report.append(f"Performance Grade: {latest['grade']}")
            report.append("")
            
            report.append("Current Metrics:")
            report.append(f"  Average Response Time: {latest['response_time']:.3f}s")
            report.append(f"  CPU Usage: {latest['cpu_usage']:.1f}%")
            report.append(f"  Memory Usage: {latest['memory_usage']:.1f}MB")
            report.append("")
            
            report.append(f"Period Averages ({days} days):")
            report.append(f"  Avg Response Time: {averages['response_time']:.3f}s")
            report.append(f"  Avg CPU Usage: {averages['cpu_usage']:.1f}%")
            report.append(f"  Avg Memory Usage: {averages['memory_usage']:.1f}MB")
            
        else:
            report.append(f"Status: {performance_summary['message']}")
        
        report.append("")
        
        # Task Type Breakdown
        if "task_breakdown" in detailed_metrics and detailed_metrics["task_breakdown"]:
            report.append("TASK TYPE PERFORMANCE (Last 7 Days)")
            report.append("-" * 35)
            
            for task_type, metrics in detailed_metrics["task_breakdown"].items():
                report.append(f"{task_type.replace('_', ' ').title()}:")
                report.append(f"  Tasks: {metrics['successful_tasks']}/{metrics['total_tasks']} "
                             f"({metrics['success_rate']:.2%} success)")
                report.append(f"  Completion Rate: {metrics['avg_completion_rate']:.2%}")
                report.append(f"  Accuracy: {metrics['avg_accuracy']:.2%}")
                report.append(f"  Intervention Rate: {metrics['intervention_rate']:.2%}")
                report.append("")
        
        # Scenario Performance Breakdown
        if "scenario_breakdown" in detailed_metrics and detailed_metrics["scenario_breakdown"]:
            report.append("SCENARIO PERFORMANCE (Last 7 Days)")
            report.append("-" * 33)
            
            for scenario_name, metrics in detailed_metrics["scenario_breakdown"].items():
                report.append(f"{scenario_name.replace('_', ' ').title()}:")
                report.append(f"  Requests: {metrics['successful_requests']}/{metrics['total_requests']} "
                             f"({metrics['success_rate']:.2%} success)")
                report.append(f"  Avg Response Time: {metrics['avg_response_time']:.3f}s")
                report.append(f"  Avg Memory Usage: {metrics['avg_memory_usage']:.1f}MB")
                report.append("")
        
        # Trends Analysis
        report.append("TRENDS ANALYSIS")
        report.append("-" * 15)
        
        if accuracy_summary["status"] == "success":
            trends = accuracy_summary["trends"]
            report.append("Accuracy Trends:")
            report.append(f"  Task Completion: {trends['completion_trend'].title()}")
            report.append(f"  Response Accuracy: {trends['accuracy_trend'].title()}")
            report.append(f"  Human Intervention: {trends['intervention_trend'].title()}")
            report.append("")
        
        if performance_summary["status"] == "success":
            trends = performance_summary["trends"]
            report.append("Performance Trends:")
            report.append(f"  Response Time: {trends['response_time_trend'].title()}")
            report.append(f"  CPU Usage: {trends['cpu_trend'].title()}")
            report.append(f"  Memory Usage: {trends['memory_trend'].title()}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)
        
        if health["health_grade"] in ["A", "B"]:
            report.append("🎉 Model performance is excellent! Continue current monitoring.")
        elif health["health_grade"] == "C":
            report.append("⚠️  Model performance is acceptable but could be improved.")
        else:
            report.append("❌ Model performance needs attention. Review issues above.")
        
        # Specific recommendations based on issues
        for issue in health["issues"]:
            if "completion rate" in issue.lower():
                report.append("💡 Consider prompt engineering improvements for better task completion")
            elif "accuracy" in issue.lower():
                report.append("💡 Review output formatting instructions and validation logic")
            elif "intervention" in issue.lower():
                report.append("💡 Enhance autonomous decision-making capabilities")
            elif "response time" in issue.lower():
                report.append("💡 Consider model optimization or hardware upgrades")
            elif "cpu" in issue.lower():
                report.append("💡 Monitor concurrent requests and consider load balancing")
            elif "memory" in issue.lower():
                report.append("💡 Review memory usage patterns and optimize if needed")
        
        if not health["issues"]:
            report.append("✅ All metrics within acceptable ranges")
            report.append("💡 Continue regular monitoring and maintain current configuration")
        
        return "\n".join(report)
    
    def export_metrics_json(self, days: int = 30) -> Dict[str, Any]:
        """Export all metrics as JSON for external analysis"""
        return {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "accuracy_summary": self.get_accuracy_summary(days),
            "performance_summary": self.get_performance_summary(days),
            "detailed_metrics": self.get_detailed_metrics(7),
            "health_score": self.calculate_overall_health_score(
                self.get_accuracy_summary(days),
                self.get_performance_summary(days)
            )
        }

def main():
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Monitoring Dashboard")
    parser.add_argument("--accuracy-db", default="olympus_accuracy_tracking.db",
                       help="Accuracy tracking database path")
    parser.add_argument("--performance-db", default="olympus_performance_monitoring.db",
                       help="Performance monitoring database path")
    parser.add_argument("--days", type=int, default=30,
                       help="Number of days for analysis")
    parser.add_argument("--export-json", help="Export metrics to JSON file")
    parser.add_argument("--health-check", action="store_true",
                       help="Exit with error code if health is poor")
    
    args = parser.parse_args()
    
    dashboard = MonitoringDashboard(args.accuracy_db, args.performance_db)
    
    if args.export_json:
        # Export metrics as JSON
        metrics = dashboard.export_metrics_json(args.days)
        with open(args.export_json, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"📄 Metrics exported to: {args.export_json}")
        
        # Also display health summary
        health = metrics["health_score"]
        print(f"\n🏥 Health Summary: {health['health_grade']} ({health['health_percentage']:.1%})")
        
        if args.health_check:
            sys.exit(0 if health["health_grade"] in ["A", "B", "C"] else 1)
    else:
        # Generate and display dashboard report
        report = dashboard.generate_dashboard_report(args.days)
        print(report)
        
        if args.health_check:
            # Get health score for exit code
            accuracy_summary = dashboard.get_accuracy_summary(args.days)
            performance_summary = dashboard.get_performance_summary(args.days)
            health = dashboard.calculate_overall_health_score(accuracy_summary, performance_summary)
            
            sys.exit(0 if health["health_grade"] in ["A", "B", "C"] else 1)

if __name__ == "__main__":
    main()