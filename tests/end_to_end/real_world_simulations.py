#!/usr/bin/env python3
"""
Real-World Coding Task Simulations for Olympus-Coder-v1

This module implements realistic coding scenarios that simulate actual
software development tasks, including complex problem-solving, integration
challenges, and production-ready code development.

Requirements addressed: 5.1, 5.2, 5.4, 5.5
"""

import json
import time
import asyncio
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

from ..integration.ollama_client import OllamaClient
from ..integration.logging_tools import TestLogger
from ..validation.code_validator import CodeValidator


@dataclass
class TaskRequirement:
    """Represents a specific requirement for a coding task"""
    id: str
    description: str
    priority: str  # "high", "medium", "low"
    acceptance_criteria: List[str]
    completed: bool = False


@dataclass
class RealWorldTask:
    """Represents a complete real-world coding task"""
    name: str
    description: str
    domain: str
    complexity: str  # "simple", "medium", "complex"
    requirements: List[TaskRequirement]
    time_limit: int  # seconds
    success_criteria: Dict[str, Any]
    artifacts: Dict[str, str]  # filename -> content
    success: bool = False
    completion_time: float = 0.0
    error_message: str = ""
    metrics: Dict[str, Any] = None


class RealWorldTaskSimulator:
    """Simulates real-world coding tasks and evaluates completion"""
    
    def __init__(self, model_name: str = "olympus-coder-v1", 
                 host: str = "localhost", port: int = 11434):
        self.model_name = model_name
        self.client = OllamaClient(model_name, host, port)
        self.code_validator = CodeValidator()
        self.logger = TestLogger("real_world_simulations")
        
        self.tasks = self._create_real_world_tasks()
        self.results = {}
    
    def _create_real_world_tasks(self) -> List[RealWorldTask]:
        """Create comprehensive real-world coding tasks"""
        
        tasks = []
        
        # Task 1: E-commerce API Development
        ecommerce_requirements = [
            TaskRequirement(
                id="EC-001",
                description="Implement product catalog API",
                priority="high",
                acceptance_criteria=[
                    "GET /products endpoint returns paginated product list",
                    "GET /products/{id} endpoint returns single product",
                    "Products include name, price, description, category",
                    "Proper error handling for invalid product IDs"
                ]
            ),
            TaskRequirement(
                id="EC-002", 
                description="Implement shopping cart functionality",
                priority="high",
                acceptance_criteria=[
                    "POST /cart/items endpoint adds items to cart",
                    "GET /cart endpoint returns current cart contents",
                    "PUT /cart/items/{id} endpoint updates item quantities",
                    "DELETE /cart/items/{id} endpoint removes items"
                ]
            ),
            TaskRequirement(
                id="EC-003",
                description="Add input validation and error handling",
                priority="medium",
                acceptance_criteria=[
                    "All endpoints validate input data",
                    "Proper HTTP status codes returned",
                    "Meaningful error messages provided",
                    "Handle edge cases (empty cart, invalid quantities)"
                ]
            )
        ]
        
        tasks.append(RealWorldTask(
            name="ecommerce_api_development",
            description="Build a complete e-commerce REST API with product catalog and shopping cart",
            domain="E-commerce",
            complexity="complex",
            requirements=ecommerce_requirements,
            time_limit=1800,  # 30 minutes
            success_criteria={
                "requirements_completed": 0.8,
                "code_quality_score": 0.7,
                "api_completeness": 0.8,
                "error_handling_coverage": 0.7
            },
            artifacts={}
        ))
        
        # Task 2: Data Processing Pipeline
        data_pipeline_requirements = [
            TaskRequirement(
                id="DP-001",
                description="Implement CSV data ingestion",
                priority="high",
                acceptance_criteria=[
                    "Read CSV files with proper error handling",
                    "Validate data types and formats",
                    "Handle missing or malformed data",
                    "Support different CSV formats and delimiters"
                ]
            ),
            TaskRequirement(
                id="DP-002",
                description="Create data transformation functions",
                priority="high",
                acceptance_criteria=[
                    "Clean and normalize data",
                    "Apply business rules and calculations",
                    "Handle data type conversions",
                    "Aggregate data by different dimensions"
                ]
            ),
            TaskRequirement(
                id="DP-003",
                description="Implement data export functionality",
                priority="medium",
                acceptance_criteria=[
                    "Export processed data to JSON format",
                    "Generate summary statistics",
                    "Create data quality reports",
                    "Handle large datasets efficiently"
                ]
            )
        ]
        
        tasks.append(RealWorldTask(
            name="data_processing_pipeline",
            description="Build a data processing pipeline for CSV analysis and transformation",
            domain="Data Engineering",
            complexity="medium",
            requirements=data_pipeline_requirements,
            time_limit=1200,  # 20 minutes
            success_criteria={
                "requirements_completed": 0.8,
                "code_quality_score": 0.7,
                "data_handling_accuracy": 0.8,
                "performance_efficiency": 0.6
            },
            artifacts={}
        ))
        
        # Task 3: Microservice Integration
        microservice_requirements = [
            TaskRequirement(
                id="MS-001",
                description="Create user authentication service",
                priority="high",
                acceptance_criteria=[
                    "JWT-based authentication implementation",
                    "User registration and login endpoints",
                    "Password hashing and validation",
                    "Token refresh mechanism"
                ]
            ),
            TaskRequirement(
                id="MS-002",
                description="Implement service-to-service communication",
                priority="high",
                acceptance_criteria=[
                    "HTTP client for inter-service calls",
                    "Proper error handling and retries",
                    "Request/response logging",
                    "Circuit breaker pattern implementation"
                ]
            ),
            TaskRequirement(
                id="MS-003",
                description="Add monitoring and health checks",
                priority="medium",
                acceptance_criteria=[
                    "Health check endpoints",
                    "Metrics collection",
                    "Structured logging",
                    "Error tracking and alerting"
                ]
            )
        ]
        
        tasks.append(RealWorldTask(
            name="microservice_integration",
            description="Build microservice with authentication, inter-service communication, and monitoring",
            domain="Microservices",
            complexity="complex",
            requirements=microservice_requirements,
            time_limit=2100,  # 35 minutes
            success_criteria={
                "requirements_completed": 0.7,
                "code_quality_score": 0.8,
                "architecture_soundness": 0.7,
                "production_readiness": 0.6
            },
            artifacts={}
        ))
        
        # Task 4: Frontend Component Library
        frontend_requirements = [
            TaskRequirement(
                id="FE-001",
                description="Create reusable UI components",
                priority="high",
                acceptance_criteria=[
                    "Button component with multiple variants",
                    "Input component with validation",
                    "Modal component with proper accessibility",
                    "Card component for content display"
                ]
            ),
            TaskRequirement(
                id="FE-002",
                description="Implement component testing",
                priority="high",
                acceptance_criteria=[
                    "Unit tests for all components",
                    "Integration tests for component interactions",
                    "Accessibility testing",
                    "Visual regression testing setup"
                ]
            ),
            TaskRequirement(
                id="FE-003",
                description="Create documentation and examples",
                priority="medium",
                acceptance_criteria=[
                    "Component API documentation",
                    "Usage examples for each component",
                    "Storybook integration",
                    "Design system guidelines"
                ]
            )
        ]
        
        tasks.append(RealWorldTask(
            name="frontend_component_library",
            description="Build a reusable frontend component library with testing and documentation",
            domain="Frontend Development",
            complexity="medium",
            requirements=frontend_requirements,
            time_limit=1500,  # 25 minutes
            success_criteria={
                "requirements_completed": 0.8,
                "code_quality_score": 0.8,
                "component_reusability": 0.7,
                "testing_coverage": 0.7
            },
            artifacts={}
        ))
        
        return tasks
    
    async def simulate_task(self, task: RealWorldTask) -> bool:
        """Simulate completion of a real-world coding task"""
        self.logger.log(f"Starting task simulation: {task.name}", "INFO")
        
        start_time = time.time()
        
        try:
            # Create temporary workspace
            workspace = Path(tempfile.mkdtemp(prefix=f"olympus_task_{task.name}_"))
            
            # Generate initial project prompt
            initial_prompt = self._generate_initial_prompt(task)
            
            # Start task execution
            conversation_history = []
            completed_requirements = []
            
            # Phase 1: Project setup and planning
            planning_response = await self._execute_task_phase(
                "planning", initial_prompt, conversation_history
            )
            
            if not self._validate_planning_response(planning_response, task):
                task.error_message = "Planning phase validation failed"
                return False
            
            # Phase 2: Core implementation
            for req in task.requirements:
                if req.priority == "high":
                    impl_prompt = self._generate_implementation_prompt(req, task, conversation_history)
                    impl_response = await self._execute_task_phase(
                        f"implement_{req.id}", impl_prompt, conversation_history
                    )
                    
                    if self._validate_requirement_implementation(impl_response, req):
                        req.completed = True
                        completed_requirements.append(req)
                        
                        # Extract and save code artifacts
                        artifacts = self._extract_code_artifacts(impl_response)
                        task.artifacts.update(artifacts)
                    
                    # Check time limit
                    if time.time() - start_time > task.time_limit:
                        task.error_message = "Task exceeded time limit"
                        break
            
            # Phase 3: Integration and testing (if time permits)
            if time.time() - start_time < task.time_limit * 0.8:
                testing_prompt = self._generate_testing_prompt(task, completed_requirements)
                testing_response = await self._execute_task_phase(
                    "testing", testing_prompt, conversation_history
                )
                
                # Process medium priority requirements if time allows
                for req in task.requirements:
                    if req.priority == "medium" and not req.completed:
                        if time.time() - start_time < task.time_limit * 0.9:
                            impl_prompt = self._generate_implementation_prompt(req, task, conversation_history)
                            impl_response = await self._execute_task_phase(
                                f"implement_{req.id}", impl_prompt, conversation_history
                            )
                            
                            if self._validate_requirement_implementation(impl_response, req):
                                req.completed = True
                                completed_requirements.append(req)
            
            # Calculate completion metrics
            task.completion_time = time.time() - start_time
            task.metrics = self._calculate_task_metrics(task, completed_requirements, conversation_history)
            
            # Evaluate task success
            task.success = self._evaluate_task_success(task)
            
            # Cleanup workspace
            shutil.rmtree(workspace)
            
            status = "SUCCESS" if task.success else "FAILED"
            self.logger.log(f"Task {task.name} completed: {status} ({task.completion_time:.1f}s)", "INFO")
            
            return task.success
            
        except Exception as e:
            task.error_message = f"Task simulation failed: {str(e)}"
            task.completion_time = time.time() - start_time
            self.logger.log(f"Task {task.name} failed: {str(e)}", "ERROR")
            return False
    
    async def _execute_task_phase(self, phase_name: str, prompt: str, 
                                 conversation_history: List[Dict[str, Any]]) -> str:
        """Execute a single phase of task completion"""
        self.logger.log(f"Executing phase: {phase_name}", "DEBUG")
        
        # Add conversation context if available
        if conversation_history:
            context_summary = self._summarize_conversation_context(conversation_history[-3:])
            prompt = f"Context from previous work:\n{context_summary}\n\nCurrent task:\n{prompt}"
        
        response = await self.client.generate_response(prompt)
        
        # Record conversation
        conversation_history.append({
            "phase": phase_name,
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_initial_prompt(self, task: RealWorldTask) -> str:
        """Generate initial prompt for task execution"""
        requirements_text = "\n".join([
            f"- {req.id}: {req.description} (Priority: {req.priority})"
            for req in task.requirements
        ])
        
        return f"""
I need to build a {task.domain.lower()} solution: {task.description}

Requirements:
{requirements_text}

This is a {task.complexity} project that needs to be production-ready. Please:
1. Analyze the requirements and suggest a project structure
2. Identify the key components and their relationships
3. Recommend the technology stack and architecture
4. Provide a development plan with priorities

Focus on creating maintainable, well-documented code with proper error handling.
"""
    
    def _generate_implementation_prompt(self, requirement: TaskRequirement, 
                                      task: RealWorldTask, 
                                      conversation_history: List[Dict[str, Any]]) -> str:
        """Generate implementation prompt for a specific requirement"""
        criteria_text = "\n".join([f"- {criteria}" for criteria in requirement.acceptance_criteria])
        
        return f"""
Now implement requirement {requirement.id}: {requirement.description}

Acceptance Criteria:
{criteria_text}

Please provide complete, production-ready code that:
1. Meets all acceptance criteria
2. Includes proper error handling
3. Has comprehensive comments and documentation
4. Follows best practices for {task.domain.lower()}
5. Is testable and maintainable

Include any necessary configuration, dependencies, or setup instructions.
"""
    
    def _generate_testing_prompt(self, task: RealWorldTask, 
                                completed_requirements: List[TaskRequirement]) -> str:
        """Generate testing prompt for completed requirements"""
        completed_ids = [req.id for req in completed_requirements]
        
        return f"""
Create comprehensive tests for the implemented requirements: {', '.join(completed_ids)}

The tests should include:
1. Unit tests for individual functions/methods
2. Integration tests for component interactions
3. Error handling and edge case tests
4. Performance tests where applicable

Use appropriate testing frameworks and follow testing best practices.
Ensure good test coverage and clear test documentation.
"""
    
    def _validate_planning_response(self, response: str, task: RealWorldTask) -> bool:
        """Validate the quality of planning response"""
        planning_indicators = [
            "structure", "architecture", "component", "technology", 
            "plan", "priority", "framework", "design"
        ]
        
        response_lower = response.lower()
        indicator_count = sum(1 for indicator in planning_indicators if indicator in response_lower)
        
        return indicator_count >= 4 and len(response) > 200
    
    def _validate_requirement_implementation(self, response: str, requirement: TaskRequirement) -> bool:
        """Validate that a requirement has been properly implemented"""
        # Check for code blocks
        if "```" not in response:
            return False
        
        # Check for key terms from acceptance criteria
        response_lower = response.lower()
        criteria_keywords = []
        
        for criteria in requirement.acceptance_criteria:
            # Extract key technical terms
            words = criteria.lower().split()
            technical_words = [w for w in words if len(w) > 3 and w.isalpha()]
            criteria_keywords.extend(technical_words[:3])  # Top 3 words per criteria
        
        # Check if at least half of the criteria keywords are mentioned
        mentioned_keywords = sum(1 for keyword in criteria_keywords if keyword in response_lower)
        
        return mentioned_keywords >= len(criteria_keywords) * 0.5
    
    def _extract_code_artifacts(self, response: str) -> Dict[str, str]:
        """Extract code artifacts from response"""
        import re
        
        artifacts = {}
        
        # Find all code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', response, re.DOTALL)
        
        for i, (language, code) in enumerate(code_blocks):
            if language:
                extension = self._get_file_extension(language)
                filename = f"artifact_{i+1}.{extension}"
            else:
                filename = f"artifact_{i+1}.txt"
            
            artifacts[filename] = code.strip()
        
        return artifacts
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for programming language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "csharp": "cs",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rs",
            "php": "php",
            "ruby": "rb",
            "swift": "swift",
            "kotlin": "kt",
            "scala": "scala",
            "html": "html",
            "css": "css",
            "sql": "sql",
            "json": "json",
            "yaml": "yml",
            "xml": "xml"
        }
        
        return extensions.get(language.lower(), "txt")
    
    def _summarize_conversation_context(self, recent_history: List[Dict[str, Any]]) -> str:
        """Summarize recent conversation context"""
        if not recent_history:
            return ""
        
        summary_parts = []
        for entry in recent_history:
            phase = entry["phase"]
            # Extract key points from response (first 200 chars)
            response_summary = entry["response"][:200] + "..." if len(entry["response"]) > 200 else entry["response"]
            summary_parts.append(f"Phase {phase}: {response_summary}")
        
        return "\n".join(summary_parts)
    
    def _calculate_task_metrics(self, task: RealWorldTask, 
                               completed_requirements: List[TaskRequirement],
                               conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive task completion metrics"""
        total_requirements = len(task.requirements)
        completed_count = len(completed_requirements)
        
        # Priority-weighted completion
        high_priority_reqs = [req for req in task.requirements if req.priority == "high"]
        high_priority_completed = [req for req in completed_requirements if req.priority == "high"]
        
        medium_priority_reqs = [req for req in task.requirements if req.priority == "medium"]
        medium_priority_completed = [req for req in completed_requirements if req.priority == "medium"]
        
        # Calculate weighted completion score
        high_weight = 0.7
        medium_weight = 0.3
        
        high_completion = len(high_priority_completed) / len(high_priority_reqs) if high_priority_reqs else 1.0
        medium_completion = len(medium_priority_completed) / len(medium_priority_reqs) if medium_priority_reqs else 1.0
        
        weighted_completion = (high_completion * high_weight) + (medium_completion * medium_weight)
        
        # Code quality assessment
        total_code_length = sum(len(artifact) for artifact in task.artifacts.values())
        code_quality_score = min(total_code_length / 1000, 1.0)  # Normalize by expected code length
        
        # Time efficiency
        time_efficiency = min(task.time_limit / task.completion_time, 1.0) if task.completion_time > 0 else 0.0
        
        return {
            "requirements_completed": completed_count / total_requirements if total_requirements > 0 else 0.0,
            "weighted_completion": weighted_completion,
            "high_priority_completion": high_completion,
            "medium_priority_completion": medium_completion,
            "code_artifacts_generated": len(task.artifacts),
            "total_code_length": total_code_length,
            "code_quality_score": code_quality_score,
            "time_efficiency": time_efficiency,
            "conversation_phases": len(conversation_history),
            "completion_time": task.completion_time,
            "time_limit_adherence": task.completion_time <= task.time_limit
        }
    
    def _evaluate_task_success(self, task: RealWorldTask) -> bool:
        """Evaluate if task meets success criteria"""
        if not task.metrics:
            return False
        
        # Check each success criterion
        for criterion, threshold in task.success_criteria.items():
            actual_value = task.metrics.get(criterion, 0.0)
            if actual_value < threshold:
                task.error_message = f"Failed criterion: {criterion} ({actual_value:.2f} < {threshold})"
                return False
        
        return True
    
    async def run_all_simulations(self) -> Dict[str, Any]:
        """Run all real-world task simulations"""
        self.logger.log("Starting Real-World Task Simulations", "INFO")
        
        suite_start_time = datetime.now()
        task_results = {}
        
        for task in self.tasks:
            success = await self.simulate_task(task)
            task_results[task.name] = self._compile_task_results(task)
        
        suite_end_time = datetime.now()
        
        # Compile overall results
        self.results = {
            "suite_info": {
                "model_name": self.model_name,
                "start_time": suite_start_time.isoformat(),
                "end_time": suite_end_time.isoformat(),
                "total_execution_time": (suite_end_time - suite_start_time).total_seconds(),
                "tasks_simulated": len(self.tasks)
            },
            "task_results": task_results,
            "overall_metrics": self._calculate_overall_metrics(task_results),
            "domain_analysis": self._analyze_domain_performance(task_results)
        }
        
        return self.results
    
    def _compile_task_results(self, task: RealWorldTask) -> Dict[str, Any]:
        """Compile results for a single task"""
        return {
            "name": task.name,
            "description": task.description,
            "domain": task.domain,
            "complexity": task.complexity,
            "success": task.success,
            "error_message": task.error_message,
            "completion_time": task.completion_time,
            "time_limit": task.time_limit,
            "requirements": [
                {
                    "id": req.id,
                    "description": req.description,
                    "priority": req.priority,
                    "completed": req.completed
                }
                for req in task.requirements
            ],
            "artifacts_generated": list(task.artifacts.keys()),
            "metrics": task.metrics or {},
            "success_criteria": task.success_criteria
        }
    
    def _calculate_overall_metrics(self, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall simulation metrics"""
        successful_tasks = sum(1 for result in task_results.values() if result["success"])
        total_tasks = len(task_results)
        
        # Aggregate metrics
        completion_times = [result["completion_time"] for result in task_results.values()]
        time_efficiencies = [result["metrics"].get("time_efficiency", 0.0) for result in task_results.values()]
        code_quality_scores = [result["metrics"].get("code_quality_score", 0.0) for result in task_results.values()]
        requirements_completion = [result["metrics"].get("requirements_completed", 0.0) for result in task_results.values()]
        
        # Calculate complexity-weighted success
        complexity_weights = {"simple": 1.0, "medium": 1.5, "complex": 2.0}
        weighted_success = 0.0
        total_weight = 0.0
        
        for result in task_results.values():
            weight = complexity_weights.get(result["complexity"], 1.0)
            total_weight += weight
            if result["success"]:
                weighted_success += weight
        
        complexity_weighted_success = weighted_success / total_weight if total_weight > 0 else 0.0
        
        return {
            "task_success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0.0,
            "successful_tasks": successful_tasks,
            "total_tasks": total_tasks,
            "complexity_weighted_success": complexity_weighted_success,
            "average_completion_time": sum(completion_times) / len(completion_times) if completion_times else 0.0,
            "average_time_efficiency": sum(time_efficiencies) / len(time_efficiencies) if time_efficiencies else 0.0,
            "average_code_quality": sum(code_quality_scores) / len(code_quality_scores) if code_quality_scores else 0.0,
            "average_requirements_completion": sum(requirements_completion) / len(requirements_completion) if requirements_completion else 0.0,
            "production_readiness_score": complexity_weighted_success * 0.4 + 
                                        (sum(code_quality_scores) / len(code_quality_scores) if code_quality_scores else 0.0) * 0.3 +
                                        (sum(time_efficiencies) / len(time_efficiencies) if time_efficiencies else 0.0) * 0.3
        }
    
    def _analyze_domain_performance(self, task_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance by domain"""
        domain_performance = {}
        
        # Group results by domain
        domains = {}
        for result in task_results.values():
            domain = result["domain"]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(result)
        
        # Calculate domain-specific metrics
        for domain, results in domains.items():
            successful = sum(1 for r in results if r["success"])
            total = len(results)
            
            avg_completion_time = sum(r["completion_time"] for r in results) / total
            avg_requirements_completion = sum(r["metrics"].get("requirements_completed", 0.0) for r in results) / total
            
            domain_performance[domain] = {
                "success_rate": successful / total,
                "tasks_completed": successful,
                "total_tasks": total,
                "average_completion_time": avg_completion_time,
                "average_requirements_completion": avg_requirements_completion,
                "complexity_distribution": {
                    complexity: sum(1 for r in results if r["complexity"] == complexity)
                    for complexity in ["simple", "medium", "complex"]
                }
            }
        
        return domain_performance
    
    def generate_report(self) -> str:
        """Generate comprehensive real-world simulation report"""
        if not self.results:
            return "No simulation results available. Run simulations first."
        
        report = []
        
        # Header
        report.append("OLYMPUS-CODER-V1 REAL-WORLD TASK SIMULATION REPORT")
        report.append("=" * 56)
        
        suite_info = self.results["suite_info"]
        report.append(f"Model: {suite_info['model_name']}")
        report.append(f"Execution Time: {suite_info['total_execution_time']:.1f}s")
        report.append(f"Tasks Simulated: {suite_info['tasks_simulated']}")
        report.append("")
        
        # Overall Metrics
        metrics = self.results["overall_metrics"]
        report.append("OVERALL SIMULATION METRICS")
        report.append("-" * 27)
        report.append(f"Task Success Rate: {metrics['task_success_rate']:.2%}")
        report.append(f"Complexity-Weighted Success: {metrics['complexity_weighted_success']:.2%}")
        report.append(f"Production Readiness Score: {metrics['production_readiness_score']:.2%}")
        report.append(f"Average Completion Time: {metrics['average_completion_time']:.1f}s")
        report.append(f"Average Time Efficiency: {metrics['average_time_efficiency']:.2%}")
        report.append(f"Average Code Quality: {metrics['average_code_quality']:.2%}")
        report.append(f"Average Requirements Completion: {metrics['average_requirements_completion']:.2%}")
        report.append("")
        
        # Domain Performance
        domain_analysis = self.results["domain_analysis"]
        report.append("DOMAIN PERFORMANCE ANALYSIS")
        report.append("-" * 28)
        
        for domain, performance in domain_analysis.items():
            report.append(f"{domain}:")
            report.append(f"  Success Rate: {performance['success_rate']:.2%}")
            report.append(f"  Tasks: {performance['tasks_completed']}/{performance['total_tasks']}")
            report.append(f"  Avg Completion Time: {performance['average_completion_time']:.1f}s")
            report.append(f"  Avg Requirements Completion: {performance['average_requirements_completion']:.2%}")
            
            complexity_dist = performance['complexity_distribution']
            report.append(f"  Complexity Distribution: Simple({complexity_dist['simple']}) "
                         f"Medium({complexity_dist['medium']}) Complex({complexity_dist['complex']})")
            report.append("")
        
        # Task Results
        report.append("INDIVIDUAL TASK RESULTS")
        report.append("-" * 24)
        
        for task_name, task_result in self.results["task_results"].items():
            status = "✅ SUCCESS" if task_result["success"] else "❌ FAILED"
            
            report.append(f"{task_name.replace('_', ' ').title()}: {status}")
            report.append(f"  Domain: {task_result['domain']}")
            report.append(f"  Complexity: {task_result['complexity'].title()}")
            report.append(f"  Completion Time: {task_result['completion_time']:.1f}s / {task_result['time_limit']}s")
            
            # Requirements completion
            completed_reqs = sum(1 for req in task_result["requirements"] if req["completed"])
            total_reqs = len(task_result["requirements"])
            report.append(f"  Requirements: {completed_reqs}/{total_reqs} completed")
            
            # Artifacts
            report.append(f"  Code Artifacts: {len(task_result['artifacts_generated'])}")
            
            if not task_result["success"]:
                report.append(f"  Error: {task_result['error_message']}")
            
            # Key metrics
            metrics = task_result["metrics"]
            if metrics:
                report.append(f"  Code Quality: {metrics.get('code_quality_score', 0.0):.2%}")
                report.append(f"  Time Efficiency: {metrics.get('time_efficiency', 0.0):.2%}")
            
            report.append("")
        
        return "\n".join(report)


async def main():
    """Main function to run real-world simulations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Olympus-Coder-v1 Real-World Task Simulations")
    parser.add_argument("--model", default="olympus-coder-v1", help="Model name to test")
    parser.add_argument("--host", default="localhost", help="Ollama host")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create and run simulator
    simulator = RealWorldTaskSimulator(args.model, args.host, args.port)
    
    print("Starting Real-World Task Simulations...")
    print("This will simulate complex, production-ready coding tasks.")
    print()
    
    results = await simulator.run_all_simulations()
    
    # Generate and display report
    report = simulator.generate_report()
    print(report)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Exit with appropriate code
    success_rate = results["overall_metrics"]["task_success_rate"]
    return 0 if success_rate >= 0.75 else 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))