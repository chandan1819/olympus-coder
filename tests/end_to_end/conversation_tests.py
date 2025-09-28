#!/usr/bin/env python3
"""
Multi-turn Conversation Tests for Olympus-Coder-v1

This module implements comprehensive multi-turn conversation testing to validate
context retention, conversation coherence, and progressive task completion.

Requirements addressed: 5.1, 5.2, 5.4, 5.5
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from ..integration.ollama_client import OllamaClient
from ..integration.logging_tools import TestLogger


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation"""
    turn_number: int
    prompt: str
    response: str
    timestamp: datetime
    response_time: float
    context_elements: List[str]
    validation_results: Dict[str, Any]


@dataclass
class ConversationScenario:
    """Represents a complete conversation scenario"""
    name: str
    description: str
    initial_context: Dict[str, Any]
    expected_turns: int
    success_criteria: Dict[str, Any]
    turns: List[ConversationTurn]
    success: bool = False
    error_message: str = ""


class ConversationValidator:
    """Validates conversation quality and context retention"""
    
    def __init__(self):
        self.context_keywords = set()
        self.technical_terms = set()
    
    def validate_turn(self, turn: ConversationTurn, previous_turns: List[ConversationTurn]) -> Dict[str, Any]:
        """Validate a single conversation turn"""
        validation = {
            "response_quality": self._assess_response_quality(turn.response),
            "context_retention": self._assess_context_retention(turn, previous_turns),
            "technical_accuracy": self._assess_technical_accuracy(turn.response),
            "conversation_coherence": self._assess_coherence(turn, previous_turns),
            "progressive_understanding": self._assess_progressive_understanding(turn, previous_turns)
        }
        
        # Overall turn score
        scores = [v for v in validation.values() if isinstance(v, (int, float))]
        validation["overall_score"] = sum(scores) / len(scores) if scores else 0.0
        
        return validation
    
    def _assess_response_quality(self, response: str) -> float:
        """Assess the quality of a response"""
        quality_indicators = {
            "length": min(len(response) / 500, 1.0),  # Reasonable length
            "structure": 1.0 if any(marker in response for marker in ["```", "1.", "2.", "-"]) else 0.5,
            "completeness": 1.0 if len(response.split()) > 20 else 0.5,
            "clarity": 1.0 if not any(unclear in response.lower() for unclear in ["unclear", "not sure", "maybe"]) else 0.7
        }
        
        return sum(quality_indicators.values()) / len(quality_indicators)
    
    def _assess_context_retention(self, turn: ConversationTurn, previous_turns: List[ConversationTurn]) -> float:
        """Assess how well the model retains context from previous turns"""
        if not previous_turns:
            return 1.0
        
        # Extract key terms from previous turns
        previous_context = set()
        for prev_turn in previous_turns[-3:]:  # Last 3 turns
            words = prev_turn.prompt.lower().split() + prev_turn.response.lower().split()
            technical_words = [w for w in words if len(w) > 4 and w.isalpha()]
            previous_context.update(technical_words[:10])  # Top 10 technical words
        
        # Check retention in current response
        current_words = set(turn.response.lower().split())
        retained_context = len(previous_context.intersection(current_words))
        
        if len(previous_context) == 0:
            return 1.0
        
        return min(retained_context / len(previous_context), 1.0)
    
    def _assess_technical_accuracy(self, response: str) -> float:
        """Assess technical accuracy of the response"""
        # Look for code blocks, technical terms, proper formatting
        technical_indicators = {
            "code_blocks": 1.0 if "```" in response else 0.5,
            "technical_terms": min(len([w for w in response.split() if w.lower() in 
                                      ["function", "class", "import", "return", "async", "await", 
                                       "const", "let", "var", "def", "if", "else", "for", "while"]]) / 5, 1.0),
            "proper_syntax": 1.0 if not any(error in response.lower() for error in 
                                          ["syntax error", "undefined", "null reference"]) else 0.3
        }
        
        return sum(technical_indicators.values()) / len(technical_indicators)
    
    def _assess_coherence(self, turn: ConversationTurn, previous_turns: List[ConversationTurn]) -> float:
        """Assess conversation coherence"""
        if not previous_turns:
            return 1.0
        
        # Check if response addresses the prompt appropriately
        prompt_keywords = set(turn.prompt.lower().split())
        response_keywords = set(turn.response.lower().split())
        
        # Remove common words
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        prompt_keywords -= common_words
        response_keywords -= common_words
        
        if len(prompt_keywords) == 0:
            return 1.0
        
        relevance = len(prompt_keywords.intersection(response_keywords)) / len(prompt_keywords)
        return min(relevance * 2, 1.0)  # Scale up relevance
    
    def _assess_progressive_understanding(self, turn: ConversationTurn, previous_turns: List[ConversationTurn]) -> float:
        """Assess if the model shows progressive understanding"""
        if len(previous_turns) < 2:
            return 1.0
        
        # Look for references to previous work, building upon concepts
        progressive_indicators = [
            "based on", "building on", "as mentioned", "from the previous", 
            "continuing", "extending", "improving", "refining"
        ]
        
        response_lower = turn.response.lower()
        progressive_score = sum(1 for indicator in progressive_indicators if indicator in response_lower)
        
        return min(progressive_score / 2, 1.0)


class ConversationTestSuite:
    """Comprehensive multi-turn conversation test suite"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.client = OllamaClient(model_name, host, port)
        self.validator = ConversationValidator()
        self.logger = TestLogger("conversation_tests")
        
        self.scenarios = self._create_conversation_scenarios()
        self.results = {}
    
    def _create_conversation_scenarios(self) -> List[ConversationScenario]:
        """Create comprehensive conversation test scenarios"""
        
        scenarios = []
        
        # Scenario 1: Progressive Code Development
        scenarios.append(ConversationScenario(
            name="progressive_code_development",
            description="Building a complete application through progressive conversation",
            initial_context={
                "task": "Build a REST API for a todo application",
                "language": "Python",
                "framework": "FastAPI"
            },
            expected_turns=8,
            success_criteria={
                "context_retention": 0.7,
                "progressive_understanding": 0.6,
                "technical_accuracy": 0.8,
                "conversation_coherence": 0.7
            },
            turns=[]
        ))
        
        # Scenario 2: Debugging and Problem Solving
        scenarios.append(ConversationScenario(
            name="debugging_conversation",
            description="Multi-turn debugging and problem-solving conversation",
            initial_context={
                "task": "Debug and fix a complex application error",
                "language": "JavaScript",
                "error_type": "Async/await issues"
            },
            expected_turns=6,
            success_criteria={
                "context_retention": 0.8,
                "progressive_understanding": 0.7,
                "technical_accuracy": 0.8,
                "conversation_coherence": 0.8
            },
            turns=[]
        ))
        
        # Scenario 3: Architecture Discussion
        scenarios.append(ConversationScenario(
            name="architecture_discussion",
            description="High-level architecture design conversation",
            initial_context={
                "task": "Design microservices architecture",
                "domain": "E-commerce platform",
                "constraints": "High availability, scalability"
            },
            expected_turns=7,
            success_criteria={
                "context_retention": 0.6,
                "progressive_understanding": 0.8,
                "technical_accuracy": 0.7,
                "conversation_coherence": 0.8
            },
            turns=[]
        ))
        
        # Scenario 4: Code Review and Improvement
        scenarios.append(ConversationScenario(
            name="code_review_conversation",
            description="Iterative code review and improvement process",
            initial_context={
                "task": "Review and improve existing code",
                "focus": "Performance and maintainability",
                "language": "Python"
            },
            expected_turns=5,
            success_criteria={
                "context_retention": 0.8,
                "progressive_understanding": 0.7,
                "technical_accuracy": 0.8,
                "conversation_coherence": 0.7
            },
            turns=[]
        ))
        
        return scenarios
    
    async def run_conversation_scenario(self, scenario: ConversationScenario) -> bool:
        """Run a single conversation scenario"""
        self.logger.log(f"Starting conversation scenario: {scenario.name}", "INFO")
        
        try:
            # Get conversation prompts for this scenario
            prompts = self._get_scenario_prompts(scenario)
            
            for turn_num, prompt in enumerate(prompts, 1):
                start_time = time.time()
                
                # Generate response
                response = await self.client.generate_response(prompt)
                response_time = time.time() - start_time
                
                # Create turn object
                turn = ConversationTurn(
                    turn_number=turn_num,
                    prompt=prompt,
                    response=response,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    context_elements=self._extract_context_elements(prompt, response),
                    validation_results={}
                )
                
                # Validate turn
                turn.validation_results = self.validator.validate_turn(turn, scenario.turns)
                
                # Add to scenario
                scenario.turns.append(turn)
                
                self.logger.log(f"Turn {turn_num} completed (score: {turn.validation_results['overall_score']:.2f})", "INFO")
                
                # Brief pause between turns
                await asyncio.sleep(1)
            
            # Evaluate scenario success
            scenario.success = self._evaluate_scenario_success(scenario)
            
            if scenario.success:
                self.logger.log(f"Scenario {scenario.name} completed successfully", "INFO")
            else:
                self.logger.log(f"Scenario {scenario.name} failed to meet success criteria", "WARNING")
            
            return scenario.success
            
        except Exception as e:
            scenario.error_message = f"Scenario execution failed: {str(e)}"
            self.logger.log(f"Scenario {scenario.name} failed: {str(e)}", "ERROR")
            return False
    
    def _get_scenario_prompts(self, scenario: ConversationScenario) -> List[str]:
        """Get conversation prompts for a specific scenario"""
        
        if scenario.name == "progressive_code_development":
            return [
                "I want to build a REST API for a todo application using Python and FastAPI. What's the best way to structure this project?",
                "Great! Now let's start with the data models. What Pydantic models do I need for a todo item?",
                "Perfect. Now create the main FastAPI application file with the basic setup and database connection.",
                "Now implement the CRUD endpoints for todo items. Start with GET /todos and POST /todos.",
                "Add the PUT /todos/{id} and DELETE /todos/{id} endpoints to complete the CRUD operations.",
                "I'm getting a validation error when creating todos. Can you help me debug this issue?",
                "Now let's add user authentication. How should I implement JWT-based auth for this API?",
                "Finally, create a simple test suite to verify all the endpoints work correctly."
            ]
        
        elif scenario.name == "debugging_conversation":
            return [
                "I'm having issues with async/await in my JavaScript application. Here's the error: 'Cannot read property of undefined'. Can you help?",
                "Here's my code: async function fetchData() { const result = await api.getData(); return result.data.items; }. The error happens on the return line.",
                "The api.getData() sometimes returns null. How should I handle this case properly?",
                "I implemented your suggestion but now I'm getting 'Promise pending' when I call fetchData(). What's wrong?",
                "Great! Now I want to add error handling for network failures. What's the best pattern for this?",
                "Perfect. Can you show me how to implement retry logic for failed requests?"
            ]
        
        elif scenario.name == "architecture_discussion":
            return [
                "I need to design a microservices architecture for an e-commerce platform. What are the key services I should consider?",
                "How should these services communicate with each other? What patterns should I use?",
                "What about data consistency across services? How do I handle transactions that span multiple services?",
                "How should I handle user authentication and authorization across all these services?",
                "What's the best approach for handling service discovery and load balancing?",
                "How do I ensure high availability and fault tolerance in this architecture?",
                "What monitoring and observability tools should I implement for this system?"
            ]
        
        elif scenario.name == "code_review_conversation":
            return [
                "Can you review this Python function for performance issues? def process_data(items): result = []; for item in items: if item > 0: result.append(item * 2); return result",
                "Thanks for the suggestions. Here's my updated version using list comprehension. Any other improvements?",
                "What about memory usage? This function will process lists with millions of items. How can I optimize for memory?",
                "Great! Now can you help me add proper error handling and input validation?",
                "Perfect. Finally, can you suggest how to add logging and make this function more testable?"
            ]
        
        else:
            return ["Hello, let's start a conversation about coding."]
    
    def _extract_context_elements(self, prompt: str, response: str) -> List[str]:
        """Extract key context elements from prompt and response"""
        # Extract technical terms, function names, concepts
        combined_text = f"{prompt} {response}".lower()
        
        # Technical keywords
        technical_terms = []
        for word in combined_text.split():
            if len(word) > 3 and any(tech in word for tech in 
                                   ["api", "function", "class", "async", "await", "error", "debug", 
                                    "test", "auth", "data", "service", "micro", "rest", "http"]):
                technical_terms.append(word)
        
        return list(set(technical_terms))[:10]  # Top 10 unique terms
    
    def _evaluate_scenario_success(self, scenario: ConversationScenario) -> bool:
        """Evaluate if a scenario meets its success criteria"""
        if not scenario.turns:
            return False
        
        # Calculate average scores for each criterion
        avg_scores = {}
        for criterion in scenario.success_criteria:
            scores = [turn.validation_results.get(criterion, 0.0) for turn in scenario.turns]
            avg_scores[criterion] = sum(scores) / len(scores) if scores else 0.0
        
        # Check if all criteria are met
        for criterion, threshold in scenario.success_criteria.items():
            if avg_scores.get(criterion, 0.0) < threshold:
                scenario.error_message = f"Failed criterion: {criterion} ({avg_scores.get(criterion, 0.0):.2f} < {threshold})"
                return False
        
        return True
    
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all conversation test scenarios"""
        self.logger.log("Starting Multi-turn Conversation Test Suite", "INFO")
        
        suite_start_time = datetime.now()
        scenario_results = {}
        
        for scenario in self.scenarios:
            success = await self.run_conversation_scenario(scenario)
            scenario_results[scenario.name] = self._compile_scenario_results(scenario)
        
        suite_end_time = datetime.now()
        
        # Compile overall results
        self.results = {
            "suite_info": {
                "model_name": self.model_name,
                "start_time": suite_start_time.isoformat(),
                "end_time": suite_end_time.isoformat(),
                "total_execution_time": (suite_end_time - suite_start_time).total_seconds(),
                "scenarios_run": len(self.scenarios)
            },
            "scenario_results": scenario_results,
            "overall_metrics": self._calculate_overall_metrics(scenario_results),
            "conversation_analysis": self._analyze_conversation_patterns(scenario_results)
        }
        
        return self.results
    
    def _compile_scenario_results(self, scenario: ConversationScenario) -> Dict[str, Any]:
        """Compile results for a single scenario"""
        if not scenario.turns:
            return {
                "name": scenario.name,
                "success": False,
                "error_message": scenario.error_message or "No turns completed",
                "turns_completed": 0,
                "metrics": {}
            }
        
        # Calculate metrics
        turn_scores = [turn.validation_results.get("overall_score", 0.0) for turn in scenario.turns]
        response_times = [turn.response_time for turn in scenario.turns]
        
        metrics = {
            "turns_completed": len(scenario.turns),
            "expected_turns": scenario.expected_turns,
            "completion_rate": len(scenario.turns) / scenario.expected_turns,
            "average_turn_score": sum(turn_scores) / len(turn_scores) if turn_scores else 0.0,
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0.0,
            "context_retention_avg": sum(turn.validation_results.get("context_retention", 0.0) 
                                       for turn in scenario.turns) / len(scenario.turns),
            "technical_accuracy_avg": sum(turn.validation_results.get("technical_accuracy", 0.0) 
                                        for turn in scenario.turns) / len(scenario.turns),
            "conversation_coherence_avg": sum(turn.validation_results.get("conversation_coherence", 0.0) 
                                            for turn in scenario.turns) / len(scenario.turns),
            "progressive_understanding_avg": sum(turn.validation_results.get("progressive_understanding", 0.0) 
                                               for turn in scenario.turns) / len(scenario.turns)
        }
        
        return {
            "name": scenario.name,
            "description": scenario.description,
            "success": scenario.success,
            "error_message": scenario.error_message,
            "success_criteria": scenario.success_criteria,
            "metrics": metrics,
            "turn_details": [
                {
                    "turn_number": turn.turn_number,
                    "response_time": turn.response_time,
                    "validation_score": turn.validation_results.get("overall_score", 0.0),
                    "context_retention": turn.validation_results.get("context_retention", 0.0)
                }
                for turn in scenario.turns
            ]
        }
    
    def _calculate_overall_metrics(self, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall conversation test metrics"""
        successful_scenarios = sum(1 for result in scenario_results.values() if result["success"])
        total_scenarios = len(scenario_results)
        
        # Aggregate metrics
        total_turns = sum(result["metrics"]["turns_completed"] for result in scenario_results.values())
        avg_turn_scores = [result["metrics"]["average_turn_score"] for result in scenario_results.values()]
        avg_response_times = [result["metrics"]["average_response_time"] for result in scenario_results.values()]
        
        context_retention_scores = [result["metrics"]["context_retention_avg"] for result in scenario_results.values()]
        technical_accuracy_scores = [result["metrics"]["technical_accuracy_avg"] for result in scenario_results.values()]
        coherence_scores = [result["metrics"]["conversation_coherence_avg"] for result in scenario_results.values()]
        progressive_scores = [result["metrics"]["progressive_understanding_avg"] for result in scenario_results.values()]
        
        return {
            "scenario_success_rate": successful_scenarios / total_scenarios if total_scenarios > 0 else 0.0,
            "successful_scenarios": successful_scenarios,
            "total_scenarios": total_scenarios,
            "total_conversation_turns": total_turns,
            "average_turns_per_scenario": total_turns / total_scenarios if total_scenarios > 0 else 0.0,
            "overall_turn_score": sum(avg_turn_scores) / len(avg_turn_scores) if avg_turn_scores else 0.0,
            "average_response_time": sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0.0,
            "context_retention_overall": sum(context_retention_scores) / len(context_retention_scores) if context_retention_scores else 0.0,
            "technical_accuracy_overall": sum(technical_accuracy_scores) / len(technical_accuracy_scores) if technical_accuracy_scores else 0.0,
            "conversation_coherence_overall": sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0,
            "progressive_understanding_overall": sum(progressive_scores) / len(progressive_scores) if progressive_scores else 0.0
        }
    
    def _analyze_conversation_patterns(self, scenario_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze conversation patterns and trends"""
        analysis = {
            "conversation_quality_trends": {},
            "context_retention_patterns": {},
            "response_time_analysis": {},
            "technical_discussion_effectiveness": {}
        }
        
        # Analyze quality trends across turns
        for scenario_name, result in scenario_results.items():
            if result["success"] and result["turn_details"]:
                turn_scores = [turn["validation_score"] for turn in result["turn_details"]]
                
                # Check if quality improves, degrades, or stays stable
                if len(turn_scores) > 2:
                    early_avg = sum(turn_scores[:2]) / 2
                    late_avg = sum(turn_scores[-2:]) / 2
                    
                    if late_avg > early_avg + 0.1:
                        trend = "improving"
                    elif late_avg < early_avg - 0.1:
                        trend = "degrading"
                    else:
                        trend = "stable"
                    
                    analysis["conversation_quality_trends"][scenario_name] = {
                        "trend": trend,
                        "early_average": early_avg,
                        "late_average": late_avg,
                        "improvement": late_avg - early_avg
                    }
        
        return analysis
    
    def generate_report(self) -> str:
        """Generate comprehensive conversation test report"""
        if not self.results:
            return "No conversation test results available. Run tests first."
        
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 MULTI-TURN CONVERSATION TEST REPORT")
        report.append("=" * 58)
        
        suite_info = self.results["suite_info"]
        report.append(f"Model: {suite_info['model_name']}")
        report.append(f"Execution Time: {suite_info['total_execution_time']:.1f}s")
        report.append(f"Scenarios: {suite_info['scenarios_run']}")
        report.append("")
        
        # Overall Metrics
        metrics = self.results["overall_metrics"]
        report.append("OVERALL CONVERSATION METRICS")
        report.append("-" * 30)
        report.append(f"Scenario Success Rate: {metrics['scenario_success_rate']:.2%}")
        report.append(f"Total Conversation Turns: {metrics['total_conversation_turns']}")
        report.append(f"Average Turns per Scenario: {metrics['average_turns_per_scenario']:.1f}")
        report.append(f"Overall Turn Quality Score: {metrics['overall_turn_score']:.2%}")
        report.append(f"Average Response Time: {metrics['average_response_time']:.2f}s")
        report.append("")
        
        # Key Conversation Capabilities
        report.append("CONVERSATION CAPABILITIES")
        report.append("-" * 25)
        report.append(f"Context Retention: {metrics['context_retention_overall']:.2%}")
        report.append(f"Technical Accuracy: {metrics['technical_accuracy_overall']:.2%}")
        report.append(f"Conversation Coherence: {metrics['conversation_coherence_overall']:.2%}")
        report.append(f"Progressive Understanding: {metrics['progressive_understanding_overall']:.2%}")
        report.append("")
        
        # Scenario Results
        report.append("SCENARIO RESULTS")
        report.append("-" * 16)
        
        for scenario_name, scenario_result in self.results["scenario_results"].items():
            status = "✅ SUCCESS" if scenario_result["success"] else "❌ FAILED"
            metrics = scenario_result["metrics"]
            
            report.append(f"{scenario_name.replace('_', ' ').title()}: {status}")
            report.append(f"  Turns Completed: {metrics['turns_completed']}/{metrics['expected_turns']}")
            report.append(f"  Average Turn Score: {metrics['average_turn_score']:.2%}")
            report.append(f"  Context Retention: {metrics['context_retention_avg']:.2%}")
            report.append(f"  Technical Accuracy: {metrics['technical_accuracy_avg']:.2%}")
            report.append(f"  Response Time: {metrics['average_response_time']:.2f}s")
            
            if not scenario_result["success"]:
                report.append(f"  Error: {scenario_result['error_message']}")
            
            report.append("")
        
        # Conversation Analysis
        analysis = self.results["conversation_analysis"]
        if analysis["conversation_quality_trends"]:
            report.append("CONVERSATION QUALITY TRENDS")
            report.append("-" * 28)
            
            for scenario, trend_data in analysis["conversation_quality_trends"].items():
                trend = trend_data["trend"]
                improvement = trend_data["improvement"]
                
                trend_symbol = "📈" if trend == "improving" else "📉" if trend == "degrading" else "➡️"
                report.append(f"{scenario.replace('_', ' ').title()}: {trend_symbol} {trend.title()}")
                report.append(f"  Quality Change: {improvement:+.2f}")
                report.append("")
        
        return "\n".join(report)


async def main():
    """Main function to run conversation tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Multi-turn Conversation Tests")
    parser.add_argument("--model", default="olympus-coder-v1", help="Model name to test")
    parser.add_argument("--host", default="localhost", help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create and run test suite
    suite = ConversationTestSuite(args.model, args.host, args.port)
    
    print("Starting Multi-turn Conversation Test Suite...")
    print("This will test context retention and conversation coherence.")
    print()
    
    results = await suite.run_all_scenarios()
    
    # Generate and display report
    report = suite.generate_report()
    print(report)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    success_rate = results["overall_metrics"]["scenario_success_rate"]
    return 0 if success_rate >= 0.75 else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))