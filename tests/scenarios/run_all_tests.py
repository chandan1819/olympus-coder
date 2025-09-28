"""
Comprehensive test suite runner for all Olympus-Coder-v1 test scenarios.

This module runs all test categories and provides a comprehensive report
of model performance across different capabilities.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any

from test_code_generation import CodeGenerationTestRunner
from test_debugging import DebuggingTestRunner
from test_tool_usage import ToolUsageTestRunner
from test_context_awareness import ContextAwarenessTestRunner


class ComprehensiveTestSuite:
    """Runs all test categories and generates comprehensive reports."""
    
    def __init__(self):
        self.code_gen_runner = CodeGenerationTestRunner()
        self.debugging_runner = DebuggingTestRunner()
        self.tool_usage_runner = ToolUsageTestRunner()
        self.context_runner = ContextAwarenessTestRunner()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and compile comprehensive results."""
        print("Starting Comprehensive Test Suite for Olympus-Coder-v1...")
        print("=" * 60)
        
        start_time = time.time()
        results = {
            'test_run_info': {
                'timestamp': datetime.now().isoformat(),
                'model_name': 'olympus-coder-v1',
                'test_categories': ['code_generation', 'debugging', 'tool_usage', 'context_awareness']
            },
            'category_results': {},
            'overall_summary': {},
            'performance_metrics': {}
        }
        
        # Run Code Generation Tests
        print("\n1. Running Code Generation Tests...")
        print("-" * 40)
        code_gen_start = time.time()
        code_gen_results = self.code_gen_runner.run_full_test_suite()
        code_gen_time = time.time() - code_gen_start
        results['category_results']['code_generation'] = code_gen_results
        
        print(f"Code Generation: {code_gen_results['successful_tests']}/{code_gen_results['total_tests']} "
              f"({code_gen_results['success_rate']:.2%}) - {code_gen_time:.2f}s")
        
        # Run Debugging Tests
        print("\n2. Running Debugging and Analysis Tests...")
        print("-" * 40)
        debugging_start = time.time()
        debugging_results = self.debugging_runner.run_full_debugging_suite()
        debugging_time = time.time() - debugging_start
        results['category_results']['debugging'] = debugging_results
        
        print(f"Debugging: {debugging_results['successful_tests']}/{debugging_results['total_tests']} "
              f"({debugging_results['success_rate']:.2%}) - {debugging_time:.2f}s")
        
        # Run Tool Usage Tests
        print("\n3. Running Tool Usage Decision Tests...")
        print("-" * 40)
        tool_usage_start = time.time()
        tool_usage_results = self.tool_usage_runner.run_full_tool_usage_suite()
        tool_usage_time = time.time() - tool_usage_start
        results['category_results']['tool_usage'] = tool_usage_results
        
        print(f"Tool Usage: {tool_usage_results['successful_tests']}/{tool_usage_results['total_tests']} "
              f"({tool_usage_results['success_rate']:.2%}) - {tool_usage_time:.2f}s")
        print(f"JSON Format Accuracy: {tool_usage_results['json_format_accuracy']:.2%}")
        
        # Run Context Awareness Tests
        print("\n4. Running Context Awareness Tests...")
        print("-" * 40)
        context_start = time.time()
        context_results = self.context_runner.run_full_context_awareness_suite()
        context_time = time.time() - context_start
        results['category_results']['context_awareness'] = context_results
        
        print(f"Context Awareness: {context_results['successful_tests']}/{context_results['total_tests']} "
              f"({context_results['success_rate']:.2%}) - {context_time:.2f}s")
        
        # Calculate overall metrics
        total_time = time.time() - start_time
        
        # Compile overall summary
        total_tests = sum(cat['total_tests'] for cat in results['category_results'].values())
        total_successful = sum(cat['successful_tests'] for cat in results['category_results'].values())
        overall_success_rate = total_successful / total_tests if total_tests > 0 else 0.0
        
        results['overall_summary'] = {
            'total_tests': total_tests,
            'total_successful': total_successful,
            'overall_success_rate': overall_success_rate,
            'category_breakdown': {
                category: {
                    'success_rate': data['success_rate'],
                    'test_count': data['total_tests']
                }
                for category, data in results['category_results'].items()
            }
        }
        
        # Performance metrics
        results['performance_metrics'] = {
            'total_execution_time': total_time,
            'category_execution_times': {
                'code_generation': code_gen_time,
                'debugging': debugging_time,
                'tool_usage': tool_usage_time,
                'context_awareness': context_time
            },
            'average_test_time': total_time / total_tests if total_tests > 0 else 0.0
        }
        
        # Special metrics for requirements validation
        results['requirements_validation'] = self._validate_requirements_compliance(results)
        
        return results
    
    def _validate_requirements_compliance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compliance with specific requirements from the spec."""
        compliance = {
            'requirement_1_code_generation': {
                'target': 'Generate high-quality code with proper formatting',
                'metrics': {
                    'success_rate': results['category_results']['code_generation']['success_rate'],
                    'target_threshold': 0.75,
                    'compliant': results['category_results']['code_generation']['success_rate'] >= 0.75
                }
            },
            'requirement_2_debugging': {
                'target': 'Analyze and debug existing code effectively',
                'metrics': {
                    'success_rate': results['category_results']['debugging']['success_rate'],
                    'target_threshold': 0.70,
                    'compliant': results['category_results']['debugging']['success_rate'] >= 0.70
                }
            },
            'requirement_3_tool_usage': {
                'target': 'Achieve >95% accuracy in structured response formatting',
                'metrics': {
                    'json_accuracy': results['category_results']['tool_usage']['json_format_accuracy'],
                    'target_threshold': 0.95,
                    'compliant': results['category_results']['tool_usage']['json_format_accuracy'] >= 0.95
                }
            },
            'requirement_4_context_awareness': {
                'target': 'Understand project context accurately',
                'metrics': {
                    'success_rate': results['category_results']['context_awareness']['success_rate'],
                    'target_threshold': 0.70,
                    'compliant': results['category_results']['context_awareness']['success_rate'] >= 0.70
                }
            },
            'requirement_5_autonomous_completion': {
                'target': 'Achieve 75% autonomous completion rate',
                'metrics': {
                    'overall_success_rate': results['overall_summary']['overall_success_rate'],
                    'target_threshold': 0.75,
                    'compliant': results['overall_summary']['overall_success_rate'] >= 0.75
                }
            }
        }
        
        # Calculate overall compliance
        compliant_requirements = sum(1 for req in compliance.values() if req['metrics']['compliant'])
        total_requirements = len(compliance)
        compliance['overall_compliance'] = {
            'compliant_count': compliant_requirements,
            'total_count': total_requirements,
            'compliance_rate': compliant_requirements / total_requirements
        }
        
        return compliance
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive text report."""
        report = []
        report.append("OLYMPUS-CODER-V1 COMPREHENSIVE TEST REPORT")
        report.append("=" * 50)
        report.append(f"Test Run: {results['test_run_info']['timestamp']}")
        report.append(f"Model: {results['test_run_info']['model_name']}")
        report.append("")
        
        # Overall Summary
        summary = results['overall_summary']
        report.append("OVERALL SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Successful: {summary['total_successful']}")
        report.append(f"Success Rate: {summary['overall_success_rate']:.2%}")
        report.append("")
        
        # Category Breakdown
        report.append("CATEGORY BREAKDOWN")
        report.append("-" * 20)
        for category, data in summary['category_breakdown'].items():
            report.append(f"{category.replace('_', ' ').title()}: "
                         f"{data['success_rate']:.2%} ({data['test_count']} tests)")
        report.append("")
        
        # Requirements Compliance
        compliance = results['requirements_validation']
        report.append("REQUIREMENTS COMPLIANCE")
        report.append("-" * 25)
        for req_id, req_data in compliance.items():
            if req_id == 'overall_compliance':
                continue
            
            status = "✓ PASS" if req_data['metrics']['compliant'] else "✗ FAIL"
            report.append(f"{req_id}: {status}")
            report.append(f"  Target: {req_data['target']}")
            
            if 'success_rate' in req_data['metrics']:
                rate = req_data['metrics']['success_rate']
                threshold = req_data['metrics']['target_threshold']
                report.append(f"  Actual: {rate:.2%} (threshold: {threshold:.2%})")
            elif 'json_accuracy' in req_data['metrics']:
                accuracy = req_data['metrics']['json_accuracy']
                threshold = req_data['metrics']['target_threshold']
                report.append(f"  Actual: {accuracy:.2%} (threshold: {threshold:.2%})")
            
            report.append("")
        
        overall_compliance = compliance['overall_compliance']
        report.append(f"Overall Compliance: {overall_compliance['compliant_count']}/{overall_compliance['total_count']} "
                     f"({overall_compliance['compliance_rate']:.2%})")
        report.append("")
        
        # Performance Metrics
        perf = results['performance_metrics']
        report.append("PERFORMANCE METRICS")
        report.append("-" * 20)
        report.append(f"Total Execution Time: {perf['total_execution_time']:.2f}s")
        report.append(f"Average Test Time: {perf['average_test_time']:.3f}s")
        report.append("")
        report.append("Category Execution Times:")
        for category, time_taken in perf['category_execution_times'].items():
            report.append(f"  {category.replace('_', ' ').title()}: {time_taken:.2f}s")
        report.append("")
        
        # Detailed Category Results
        report.append("DETAILED CATEGORY RESULTS")
        report.append("-" * 30)
        
        # Code Generation Details
        code_gen = results['category_results']['code_generation']
        report.append("Code Generation:")
        report.append(f"  Python: {code_gen['by_language']['python']['successful']}/{code_gen['by_language']['python']['total']}")
        report.append(f"  JavaScript: {code_gen['by_language']['javascript']['successful']}/{code_gen['by_language']['javascript']['total']}")
        report.append("")
        
        # Tool Usage Details
        tool_usage = results['category_results']['tool_usage']
        report.append("Tool Usage:")
        report.append(f"  JSON Format Accuracy: {tool_usage['json_format_accuracy']:.2%}")
        for response_type, stats in tool_usage['by_response_type'].items():
            rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            report.append(f"  {response_type}: {stats['successful']}/{stats['total']} ({rate:.2%})")
        report.append("")
        
        # Context Awareness Details
        context = results['category_results']['context_awareness']
        report.append("Context Awareness:")
        avg_scores = context['average_scores']
        for metric, score in avg_scores.items():
            report.append(f"  {metric.replace('_', ' ').title()}: {score:.2%}")
        report.append("")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], base_filename: str = "olympus_coder_test_results"):
        """Save results in multiple formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_filename = f"{base_filename}_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save text report
        report = self.generate_report(results)
        txt_filename = f"{base_filename}_{timestamp}.txt"
        with open(txt_filename, 'w') as f:
            f.write(report)
        
        return json_filename, txt_filename


def main():
    """Main function to run comprehensive test suite."""
    suite = ComprehensiveTestSuite()
    
    print("Olympus-Coder-v1 Comprehensive Test Suite")
    print("This will run all test categories and generate a comprehensive report.")
    print()
    
    # Run all tests
    results = suite.run_all_tests()
    
    # Generate and display report
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    report = suite.generate_report(results)
    print(report)
    
    # Save results
    json_file, txt_file = suite.save_results(results)
    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Report: {txt_file}")
    
    # Summary for quick reference
    overall_rate = results['overall_summary']['overall_success_rate']
    compliance_rate = results['requirements_validation']['overall_compliance']['compliance_rate']
    
    print(f"\nQUICK SUMMARY:")
    print(f"Overall Success Rate: {overall_rate:.2%}")
    print(f"Requirements Compliance: {compliance_rate:.2%}")
    
    if overall_rate >= 0.75 and compliance_rate >= 0.8:
        print("✓ Model meets performance targets!")
    else:
        print("⚠ Model needs improvement in some areas.")


if __name__ == "__main__":
    main()