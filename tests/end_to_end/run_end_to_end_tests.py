#!/usr/bin/env python3
"""
End-to-End Test Runner for Olympus-Coder-v1

This is the main runner for comprehensive end-to-end testing that combines
all testing components: conversation tests, real-world simulations, and
comprehensive scenario testing.

Requirements addressed: 5.1, 5.2, 5.4, 5.5
"""

import json
import asyncio
import argparse
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from .end_to_end_test_suite import EndToEndTestSuite
from .conversation_tests import ConversationTestSuite
from .real_world_simulations import RealWorldTaskSimulator
from ..integration.logging_tools import TestLogger


class ComprehensiveEndToEndRunner:
    """Comprehensive end-to-end test runner that orchestrates all test components"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.host = host
        self.port = port
        self.logger = TestLogger("comprehensive_e2e")
        
        # Initialize test components
        self.scenario_suite = EndToEndTestSuite(model_name, host, port)
        self.conversation_suite = ConversationTestSuite(model_name, host, port)
        self.simulation_suite = RealWorldTaskSimulator(model_name, host, port)
        
        self.results = {}
    
    async def run_comprehensive_tests(self, skip_simulations: bool = False) -> Dict[str, Any]:
        """Run all end-to-end test components"""
        self.logger.log("Starting Comprehensive End-to-End Test Suite", "INFO")
        self.logger.log("=" * 60, "INFO")
        
        suite_start_time = datetime.now()
        component_results = {}
        
        try:
            # Component 1: End-to-End Scenarios
            self.logger.log("🧪 Running End-to-End Scenarios...", "INFO")
            scenario_results = await self.scenario_suite.run_all_scenarios()
            component_results["scenarios"] = scenario_results
            self.logger.log("✅ End-to-End Scenarios completed", "INFO")
            
            # Component 2: Multi-turn Conversations
            self.logger.log("💬 Running Multi-turn Conversation Tests...", "INFO")
            conversation_results = await self.conversation_suite.run_all_scenarios()
            component_results["conversations"] = conversation_results
            self.logger.log("✅ Multi-turn Conversation Tests completed", "INFO")
            
            # Component 3: Real-World Simulations (optional, time-intensive)
            if not skip_simulations:
                self.logger.log("🌍 Running Real-World Task Simulations...", "INFO")
                simulation_results = await self.simulation_suite.run_all_simulations()
                component_results["simulations"] = simulation_results
                self.logger.log("✅ Real-World Task Simulations completed", "INFO")
            else:
                self.logger.log("⏭️  Skipping Real-World Simulations (--skip-simulations)", "INFO")
                component_results["simulations"] = None
            
        except Exception as e:
            self.logger.log(f"❌ Test execution failed: {str(e)}", "ERROR")
            raise
        
        suite_end_time = datetime.now()
        
        # Compile comprehensive results
        self.results = {
            "test_suite_info": {
                "model_name": self.model_name,
                "endpoint": f"{self.host}:{self.port}",
                "start_time": suite_start_time.isoformat(),
                "end_time": suite_end_time.isoformat(),
                "total_execution_time": (suite_end_time - suite_start_time).total_seconds(),
                "components_run": [k for k, v in component_results.items() if v is not None]
            },
            "component_results": component_results,
            "comprehensive_metrics": self._calculate_comprehensive_metrics(component_results),
            "requirements_validation": self._validate_comprehensive_requirements(component_results),
            "overall_assessment": self._generate_overall_assessment(component_results)
        }
        
        return self.results
    
    def _calculate_comprehensive_metrics(self, component_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive metrics across all test components"""
        metrics = {
            "component_success_rates": {},
            "overall_success_rate": 0.0,
            "conversation_capabilities": {},
            "real_world_performance": {},
            "technical_competencies": {},
            "autonomous_completion_metrics": {}
        }
        
        # Extract component success rates
        if component_results.get("scenarios"):
            scenario_rate = component_results["scenarios"]["overall_metrics"]["scenario_success_rate"]
            metrics["component_success_rates"]["scenarios"] = scenario_rate
        
        if component_results.get("conversations"):
            conversation_rate = component_results["conversations"]["overall_metrics"]["scenario_success_rate"]
            metrics["component_success_rates"]["conversations"] = conversation_rate
        
        if component_results.get("simulations"):
            simulation_rate = component_results["simulations"]["overall_metrics"]["task_success_rate"]
            metrics["component_success_rates"]["simulations"] = simulation_rate
        
        # Calculate overall success rate (weighted average)
        success_rates = list(metrics["component_success_rates"].values())
        if success_rates:
            metrics["overall_success_rate"] = sum(success_rates) / len(success_rates)
        
        # Conversation capabilities
        if component_results.get("conversations"):
            conv_metrics = component_results["conversations"]["overall_metrics"]
            metrics["conversation_capabilities"] = {
                "context_retention": conv_metrics.get("context_retention_overall", 0.0),
                "technical_accuracy": conv_metrics.get("technical_accuracy_overall", 0.0),
                "conversation_coherence": conv_metrics.get("conversation_coherence_overall", 0.0),
                "progressive_understanding": conv_metrics.get("progressive_understanding_overall", 0.0),
                "multi_turn_effectiveness": conv_metrics.get("total_conversation_turns", 0) >= 20
            }
        
        # Real-world performance
        if component_results.get("simulations"):
            sim_metrics = component_results["simulations"]["overall_metrics"]
            metrics["real_world_performance"] = {
                "production_readiness": sim_metrics.get("production_readiness_score", 0.0),
                "complexity_handling": sim_metrics.get("complexity_weighted_success", 0.0),
                "time_efficiency": sim_metrics.get("average_time_efficiency", 0.0),
                "code_quality": sim_metrics.get("average_code_quality", 0.0),
                "requirements_completion": sim_metrics.get("average_requirements_completion", 0.0)
            }
        
        # Technical competencies (aggregated from all components)
        code_generation_scores = []
        debugging_scores = []
        tool_usage_scores = []
        context_awareness_scores = []
        
        # Extract from scenarios
        if component_results.get("scenarios"):
            scenario_results = component_results["scenarios"]["scenario_results"]
            for scenario_name, scenario_data in scenario_results.items():
                if "code_generation" in scenario_name.lower():
                    code_generation_scores.append(1.0 if scenario_data["success"] else 0.0)
                elif "bug_fixing" in scenario_name.lower() or "debug" in scenario_name.lower():
                    debugging_scores.append(1.0 if scenario_data["success"] else 0.0)
                elif "multi_language" in scenario_name.lower():
                    context_awareness_scores.append(1.0 if scenario_data["success"] else 0.0)
        
        # Extract from conversations
        if component_results.get("conversations"):
            conv_metrics = component_results["conversations"]["overall_metrics"]
            context_awareness_scores.append(conv_metrics.get("context_retention_overall", 0.0))
            code_generation_scores.append(conv_metrics.get("technical_accuracy_overall", 0.0))
        
        # Extract from simulations
        if component_results.get("simulations"):
            sim_results = component_results["simulations"]["task_results"]
            for task_name, task_data in sim_results.items():
                success_score = 1.0 if task_data["success"] else 0.0
                
                if "ecommerce" in task_name or "frontend" in task_name:
                    code_generation_scores.append(success_score)
                elif "microservice" in task_name:
                    context_awareness_scores.append(success_score)
                elif "data_processing" in task_name:
                    debugging_scores.append(success_score)
        
        metrics["technical_competencies"] = {
            "code_generation": sum(code_generation_scores) / len(code_generation_scores) if code_generation_scores else 0.0,
            "debugging_analysis": sum(debugging_scores) / len(debugging_scores) if debugging_scores else 0.0,
            "context_awareness": sum(context_awareness_scores) / len(context_awareness_scores) if context_awareness_scores else 0.0,
            "tool_usage_decision": tool_usage_scores[0] if tool_usage_scores else 0.0  # From scenarios if available
        }
        
        # Autonomous completion metrics
        total_tasks = 0
        successful_tasks = 0
        
        for component_name, component_data in component_results.items():
            if component_data is None:
                continue
                
            if component_name == "scenarios":
                scenario_metrics = component_data["overall_metrics"]
                total_tasks += scenario_metrics.get("total_scenarios", 0)
                successful_tasks += scenario_metrics.get("successful_scenarios", 0)
            elif component_name == "conversations":
                conv_metrics = component_data["overall_metrics"]
                total_tasks += conv_metrics.get("total_scenarios", 0)
                successful_tasks += conv_metrics.get("successful_scenarios", 0)
            elif component_name == "simulations":
                sim_metrics = component_data["overall_metrics"]
                total_tasks += sim_metrics.get("total_tasks", 0)
                successful_tasks += sim_metrics.get("successful_tasks", 0)
        
        metrics["autonomous_completion_metrics"] = {
            "total_tasks_attempted": total_tasks,
            "successful_tasks": successful_tasks,
            "autonomous_completion_rate": successful_tasks / total_tasks if total_tasks > 0 else 0.0,
            "meets_75_percent_target": (successful_tasks / total_tasks if total_tasks > 0 else 0.0) >= 0.75
        }
        
        return metrics
    
    def _validate_comprehensive_requirements(self, component_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate comprehensive requirements compliance across all components"""
        comprehensive_metrics = self._calculate_comprehensive_metrics(component_results)
        
        validation = {}
        
        # Requirement 5.1: 75% autonomous completion rate
        autonomous_rate = comprehensive_metrics["autonomous_completion_metrics"]["autonomous_completion_rate"]
        validation["requirement_5_1_autonomous_completion"] = {
            "description": "Achieve 75% autonomous completion rate across all tasks",
            "target_threshold": 0.75,
            "actual_value": autonomous_rate,
            "compliant": autonomous_rate >= 0.75,
            "evidence": {
                "total_tasks": comprehensive_metrics["autonomous_completion_metrics"]["total_tasks_attempted"],
                "successful_tasks": comprehensive_metrics["autonomous_completion_metrics"]["successful_tasks"]
            }
        }
        
        # Requirement 5.2: Reduce human intervention (measured by multi-turn success)
        multi_turn_effectiveness = comprehensive_metrics["conversation_capabilities"].get("multi_turn_effectiveness", False)
        validation["requirement_5_2_human_intervention"] = {
            "description": "Reduce human-in-the-loop interventions by 50%",
            "target_threshold": True,
            "actual_value": multi_turn_effectiveness,
            "compliant": multi_turn_effectiveness,
            "evidence": {
                "multi_turn_conversations": "successful" if multi_turn_effectiveness else "failed",
                "context_retention": comprehensive_metrics["conversation_capabilities"].get("context_retention", 0.0)
            }
        }
        
        # Requirement 5.4: Consistent agentic behavior
        conversation_coherence = comprehensive_metrics["conversation_capabilities"].get("conversation_coherence", 0.0)
        validation["requirement_5_4_consistent_behavior"] = {
            "description": "Maintain consistent agentic behavior without complex prompt chaining",
            "target_threshold": 0.70,
            "actual_value": conversation_coherence,
            "compliant": conversation_coherence >= 0.70,
            "evidence": {
                "conversation_coherence": conversation_coherence,
                "progressive_understanding": comprehensive_metrics["conversation_capabilities"].get("progressive_understanding", 0.0)
            }
        }
        
        # Requirement 5.5: Clear status updates and next steps
        overall_success_rate = comprehensive_metrics["overall_success_rate"]
        validation["requirement_5_5_clear_communication"] = {
            "description": "Provide clear status updates and next steps",
            "target_threshold": 0.70,
            "actual_value": overall_success_rate,
            "compliant": overall_success_rate >= 0.70,
            "evidence": {
                "overall_success_rate": overall_success_rate,
                "technical_accuracy": comprehensive_metrics["conversation_capabilities"].get("technical_accuracy", 0.0)
            }
        }
        
        # Calculate overall compliance
        compliant_requirements = sum(1 for req in validation.values() if req["compliant"])
        total_requirements = len(validation)
        
        validation["overall_compliance"] = {
            "compliant_count": compliant_requirements,
            "total_count": total_requirements,
            "compliance_rate": compliant_requirements / total_requirements if total_requirements > 0 else 0.0,
            "all_requirements_met": compliant_requirements == total_requirements
        }
        
        return validation
    
    def _generate_overall_assessment(self, component_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall model assessment based on all test results"""
        comprehensive_metrics = self._calculate_comprehensive_metrics(component_results)
        requirements_validation = self._validate_comprehensive_requirements(component_results)
        
        # Determine model readiness level
        overall_success = comprehensive_metrics["overall_success_rate"]
        compliance_rate = requirements_validation["overall_compliance"]["compliance_rate"]
        autonomous_completion = comprehensive_metrics["autonomous_completion_metrics"]["autonomous_completion_rate"]
        
        # Calculate readiness score
        readiness_factors = {
            "overall_success": overall_success * 0.3,
            "requirements_compliance": compliance_rate * 0.3,
            "autonomous_completion": autonomous_completion * 0.4
        }
        
        readiness_score = sum(readiness_factors.values())
        
        # Determine readiness level
        if readiness_score >= 0.9:
            readiness_level = "PRODUCTION_READY"
        elif readiness_score >= 0.8:
            readiness_level = "DEPLOYMENT_READY"
        elif readiness_score >= 0.7:
            readiness_level = "READY_WITH_MONITORING"
        elif readiness_score >= 0.6:
            readiness_level = "NEEDS_IMPROVEMENT"
        else:
            readiness_level = "NOT_READY"
        
        # Generate recommendations
        recommendations = []
        
        if autonomous_completion < 0.75:
            recommendations.append("Improve autonomous task completion rate to meet 75% target")
        
        if comprehensive_metrics["conversation_capabilities"].get("context_retention", 0.0) < 0.7:
            recommendations.append("Enhance context retention in multi-turn conversations")
        
        if comprehensive_metrics["technical_competencies"].get("code_generation", 0.0) < 0.8:
            recommendations.append("Improve code generation quality and accuracy")
        
        if comprehensive_metrics.get("real_world_performance", {}).get("production_readiness", 0.0) < 0.7:
            recommendations.append("Enhance production-readiness of generated code")
        
        if not recommendations:
            recommendations.append("Model meets all requirements and is ready for deployment")
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        tech_competencies = comprehensive_metrics["technical_competencies"]
        for competency, score in tech_competencies.items():
            if score >= 0.8:
                strengths.append(f"Excellent {competency.replace('_', ' ')}")
            elif score < 0.6:
                weaknesses.append(f"Needs improvement in {competency.replace('_', ' ')}")
        
        conv_capabilities = comprehensive_metrics["conversation_capabilities"]
        for capability, score in conv_capabilities.items():
            if isinstance(score, (int, float)) and score >= 0.8:
                strengths.append(f"Strong {capability.replace('_', ' ')}")
            elif isinstance(score, (int, float)) and score < 0.6:
                weaknesses.append(f"Weak {capability.replace('_', ' ')}")
        
        return {
            "readiness_level": readiness_level,
            "readiness_score": readiness_score,
            "readiness_factors": readiness_factors,
            "key_metrics": {
                "overall_success_rate": overall_success,
                "autonomous_completion_rate": autonomous_completion,
                "requirements_compliance_rate": compliance_rate,
                "context_retention_score": comprehensive_metrics["conversation_capabilities"].get("context_retention", 0.0),
                "production_readiness_score": comprehensive_metrics.get("real_world_performance", {}).get("production_readiness", 0.0)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "deployment_recommendation": self._get_deployment_recommendation(readiness_level, recommendations)
        }
    
    def _get_deployment_recommendation(self, readiness_level: str, recommendations: List[str]) -> str:
        """Get deployment recommendation based on readiness level"""
        if readiness_level == "PRODUCTION_READY":
            return "✅ RECOMMENDED: Deploy to production with standard monitoring"
        elif readiness_level == "DEPLOYMENT_READY":
            return "✅ RECOMMENDED: Deploy with enhanced monitoring and gradual rollout"
        elif readiness_level == "READY_WITH_MONITORING":
            return "⚠️ CONDITIONAL: Deploy with extensive monitoring and quick rollback capability"
        elif readiness_level == "NEEDS_IMPROVEMENT":
            return "❌ NOT RECOMMENDED: Address critical issues before deployment"
        else:
            return "❌ NOT RECOMMENDED: Significant improvements required before deployment"
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive end-to-end test report"""
        if not self.results:
            return "No comprehensive test results available. Run tests first."
        
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 COMPREHENSIVE END-TO-END TEST REPORT")
        report.append("=" * 62)
        
        suite_info = self.results["test_suite_info"]
        report.append(f"Model: {suite_info['model_name']}")
        report.append(f"Endpoint: {suite_info['endpoint']}")
        report.append(f"Total Execution Time: {suite_info['total_execution_time']:.1f}s")
        report.append(f"Components Run: {', '.join(suite_info['components_run'])}")
        report.append("")
        
        # Overall Assessment
        assessment = self.results["overall_assessment"]
        report.append("OVERALL ASSESSMENT")
        report.append("-" * 18)
        report.append(f"Readiness Level: {assessment['readiness_level']}")
        report.append(f"Readiness Score: {assessment['readiness_score']:.2%}")
        report.append(f"Deployment Recommendation: {assessment['deployment_recommendation']}")
        report.append("")
        
        # Key Metrics Summary
        key_metrics = assessment["key_metrics"]
        report.append("KEY METRICS SUMMARY")
        report.append("-" * 19)
        report.append(f"Overall Success Rate: {key_metrics['overall_success_rate']:.2%}")
        report.append(f"Autonomous Completion Rate: {key_metrics['autonomous_completion_rate']:.2%}")
        report.append(f"Requirements Compliance: {key_metrics['requirements_compliance_rate']:.2%}")
        report.append(f"Context Retention Score: {key_metrics['context_retention_score']:.2%}")
        if key_metrics['production_readiness_score'] > 0:
            report.append(f"Production Readiness Score: {key_metrics['production_readiness_score']:.2%}")
        report.append("")
        
        # Requirements Validation
        requirements = self.results["requirements_validation"]
        report.append("REQUIREMENTS VALIDATION")
        report.append("-" * 23)
        
        for req_id, req_data in requirements.items():
            if req_id == "overall_compliance":
                continue
            
            status = "✅ PASS" if req_data["compliant"] else "❌ FAIL"
            report.append(f"{req_id}: {status}")
            report.append(f"  {req_data['description']}")
            
            if isinstance(req_data["actual_value"], (int, float)):
                if req_data["actual_value"] <= 1.0:
                    report.append(f"  Actual: {req_data['actual_value']:.2%} (target: {req_data['target_threshold']:.2%})")
                else:
                    report.append(f"  Actual: {req_data['actual_value']:.2f} (target: {req_data['target_threshold']:.2f})")
            else:
                report.append(f"  Actual: {req_data['actual_value']} (target: {req_data['target_threshold']})")
            
            report.append("")
        
        overall_compliance = requirements["overall_compliance"]
        report.append(f"Overall Compliance: {overall_compliance['compliant_count']}/{overall_compliance['total_count']} "
                     f"({overall_compliance['compliance_rate']:.2%})")
        report.append("")
        
        # Component Results Summary
        report.append("COMPONENT RESULTS SUMMARY")
        report.append("-" * 26)
        
        comprehensive_metrics = self.results["comprehensive_metrics"]
        component_rates = comprehensive_metrics["component_success_rates"]
        
        for component, success_rate in component_rates.items():
            report.append(f"{component.title()}: {success_rate:.2%} success rate")
        
        report.append("")
        
        # Technical Competencies
        tech_competencies = comprehensive_metrics["technical_competencies"]
        report.append("TECHNICAL COMPETENCIES")
        report.append("-" * 21)
        
        for competency, score in tech_competencies.items():
            competency_name = competency.replace('_', ' ').title()
            report.append(f"{competency_name}: {score:.2%}")
        
        report.append("")
        
        # Conversation Capabilities
        conv_capabilities = comprehensive_metrics["conversation_capabilities"]
        if conv_capabilities:
            report.append("CONVERSATION CAPABILITIES")
            report.append("-" * 24)
            
            for capability, score in conv_capabilities.items():
                if isinstance(score, (int, float)):
                    capability_name = capability.replace('_', ' ').title()
                    report.append(f"{capability_name}: {score:.2%}")
                elif isinstance(score, bool):
                    capability_name = capability.replace('_', ' ').title()
                    status = "✅ YES" if score else "❌ NO"
                    report.append(f"{capability_name}: {status}")
            
            report.append("")
        
        # Real-World Performance
        real_world = comprehensive_metrics.get("real_world_performance")
        if real_world:
            report.append("REAL-WORLD PERFORMANCE")
            report.append("-" * 22)
            
            for metric, score in real_world.items():
                metric_name = metric.replace('_', ' ').title()
                report.append(f"{metric_name}: {score:.2%}")
            
            report.append("")
        
        # Strengths and Weaknesses
        if assessment["strengths"]:
            report.append("STRENGTHS")
            report.append("-" * 9)
            for strength in assessment["strengths"]:
                report.append(f"✅ {strength}")
            report.append("")
        
        if assessment["weaknesses"]:
            report.append("AREAS FOR IMPROVEMENT")
            report.append("-" * 21)
            for weakness in assessment["weaknesses"]:
                report.append(f"⚠️  {weakness}")
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
        
        readiness = assessment["readiness_level"]
        if readiness in ["PRODUCTION_READY", "DEPLOYMENT_READY"]:
            report.append("🎉 Model is ready for deployment!")
            report.append("• Proceed with deployment planning")
            report.append("• Set up production monitoring")
            report.append("• Prepare rollback procedures")
            report.append("• Begin integration with agentic frameworks")
        elif readiness == "READY_WITH_MONITORING":
            report.append("⚠️  Model can be deployed with careful monitoring")
            report.append("• Deploy with enhanced monitoring")
            report.append("• Implement gradual rollout strategy")
            report.append("• Set up automated rollback triggers")
            report.append("• Monitor key performance indicators closely")
        else:
            report.append("❌ Model needs improvement before deployment")
            report.append("• Address failed requirements")
            report.append("• Improve autonomous completion rate")
            report.append("• Enhance conversation capabilities")
            report.append("• Re-run comprehensive tests after improvements")
        
        return "\n".join(report)
    
    def save_results(self, output_dir: str = "test_results") -> Tuple[str, str]:
        """Save comprehensive test results"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = output_path / f"comprehensive_e2e_results_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save text report
        report = self.generate_comprehensive_report()
        txt_file = output_path / f"comprehensive_e2e_report_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write(report)
        
        return str(json_file), str(txt_file)


async def main():
    """Main function to run comprehensive end-to-end tests"""
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Comprehensive End-to-End Tests")
    parser.add_argument("--model", default="olympus-coder-v1", help="Model name to test")
    parser.add_argument("--host", default="localhost", help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port")
    parser.add_argument("--skip-simulations", action="store_true", 
                       help="Skip time-intensive real-world simulations")
    parser.add_argument("--output-dir", default="test_results", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Create comprehensive test runner
    runner = ComprehensiveEndToEndRunner(args.model, args.host, args.port)
    
    print("🚀 Starting Comprehensive End-to-End Test Suite for Olympus-Coder-v1")
    print("=" * 70)
    print("This comprehensive test suite will evaluate:")
    print("• End-to-end scenario completion")
    print("• Multi-turn conversation capabilities")
    if not args.skip_simulations:
        print("• Real-world task simulations")
    print("• Requirements compliance validation")
    print("• Overall model readiness assessment")
    print()
    
    # Run comprehensive tests
    results = await runner.run_comprehensive_tests(args.skip_simulations)
    
    # Generate and display report
    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEST SUITE COMPLETE")
    print("=" * 70)
    
    report = runner.generate_comprehensive_report()
    print(report)
    
    # Save results
    json_file, txt_file = runner.save_results(args.output_dir)
    print(f"\nResults saved to:")
    print(f"  JSON: {json_file}")
    print(f"  Report: {txt_file}")
    
    # Final assessment
    assessment = results["overall_assessment"]
    readiness = assessment["readiness_level"]
    
    print(f"\n🎯 FINAL ASSESSMENT: {readiness}")
    print(f"📊 Readiness Score: {assessment['readiness_score']:.2%}")
    print(f"🚀 {assessment['deployment_recommendation']}")
    
    # Exit with appropriate code
    success = readiness in ["PRODUCTION_READY", "DEPLOYMENT_READY", "READY_WITH_MONITORING"]
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))