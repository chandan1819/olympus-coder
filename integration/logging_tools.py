"""
Logging and Debugging Tools for Agent Interactions

Provides comprehensive logging, debugging, and monitoring utilities
for agent execution and framework integration.
"""

import json
import logging
import time
import traceback
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import threading
from queue import Queue

from .agentic_adapter import AgentContext, AgentResponse, AgentState


@dataclass
class LogEntry:
    """Structured log entry for agent interactions"""
    timestamp: float
    level: str
    component: str
    event_type: str
    task_id: Optional[str]
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None


class AgentLogger:
    """
    Specialized logger for agent interactions with structured logging,
    performance tracking, and debugging capabilities.
    """
    
    def __init__(
        self,
        name: str = "olympus_agent",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        structured_file: Optional[str] = None,
        max_entries: int = 10000
    ):
        """
        Initialize agent logger.
        
        Args:
            name: Logger name
            log_level: Logging level
            log_file: Optional log file path
            structured_file: Optional structured log file path
            max_entries: Maximum log entries to keep in memory
        """
        self.name = name
        self.max_entries = max_entries
        
        # Set up standard logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Configure handlers
        self._setup_handlers(log_file)
        
        # Structured logging
        self.structured_file = structured_file
        self.log_entries: List[LogEntry] = []
        self.entry_lock = threading.Lock()
        
        # Performance tracking
        self.performance_metrics: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        
        # Async logging queue
        self.log_queue = Queue()
        self.async_logging = False
    
    def _setup_handlers(self, log_file: Optional[str]):
        """Set up logging handlers"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_task_start(self, context: AgentContext, prompt: str):
        """Log task execution start"""
        self._add_log_entry(
            level="INFO",
            component="task_execution",
            event_type="task_start",
            task_id=context.task_id,
            message=f"Starting task: {context.task_description}",
            data={
                "prompt_length": len(prompt),
                "files_count": len(context.files),
                "has_error_context": context.error_context is not None
            }
        )
        
        self.logger.info(f"Task started: {context.task_id} - {context.task_description}")
    
    def log_task_complete(
        self,
        context: AgentContext,
        response: AgentResponse,
        execution_time: float
    ):
        """Log task execution completion"""
        self._add_log_entry(
            level="INFO" if response.is_successful() else "ERROR",
            component="task_execution",
            event_type="task_complete",
            task_id=context.task_id,
            message=f"Task completed: {context.task_description}",
            data={
                "success": response.is_successful(),
                "has_tool_request": response.has_tool_request(),
                "response_length": len(response.content),
                "confidence": response.confidence,
                "state": response.state.value
            },
            execution_time=execution_time,
            error=response.error
        )
        
        # Track performance
        self._track_performance("task_execution", execution_time)
        
        if response.is_successful():
            self.logger.info(f"Task completed successfully: {context.task_id}")
        else:
            self.logger.error(f"Task failed: {context.task_id} - {response.error}")
    
    def log_tool_execution(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        execution_time: float,
        task_id: Optional[str] = None
    ):
        """Log tool execution"""
        success = result.get("success", False)
        
        self._add_log_entry(
            level="INFO" if success else "ERROR",
            component="tool_execution",
            event_type="tool_execute",
            task_id=task_id,
            message=f"Tool executed: {tool_name}",
            data={
                "tool_name": tool_name,
                "parameters": parameters,
                "success": success,
                "result_type": type(result.get("result")).__name__
            },
            execution_time=execution_time,
            error=result.get("error")
        )
        
        # Track performance
        self._track_performance(f"tool_{tool_name}", execution_time)
        
        if success:
            self.logger.info(f"Tool executed successfully: {tool_name}")
        else:
            self.logger.error(f"Tool execution failed: {tool_name} - {result.get('error')}")
    
    def log_model_interaction(
        self,
        prompt_length: int,
        response_length: int,
        token_count: Optional[int],
        execution_time: float,
        task_id: Optional[str] = None
    ):
        """Log model interaction details"""
        self._add_log_entry(
            level="DEBUG",
            component="model_interaction",
            event_type="model_generate",
            task_id=task_id,
            message="Model generation completed",
            data={
                "prompt_length": prompt_length,
                "response_length": response_length,
                "token_count": token_count,
                "tokens_per_second": token_count / execution_time if token_count and execution_time > 0 else None
            },
            execution_time=execution_time
        )
        
        self._track_performance("model_generation", execution_time)
    
    def log_error(
        self,
        error: Exception,
        context: Optional[AgentContext] = None,
        component: str = "unknown"
    ):
        """Log error with full traceback"""
        error_msg = str(error)
        error_traceback = traceback.format_exc()
        
        self._add_log_entry(
            level="ERROR",
            component=component,
            event_type="error",
            task_id=context.task_id if context else None,
            message=f"Error occurred: {error_msg}",
            data={
                "error_type": type(error).__name__,
                "traceback": error_traceback
            },
            error=error_msg
        )
        
        # Track error counts
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        self.logger.error(f"Error in {component}: {error_msg}\n{error_traceback}")
    
    def log_context_update(self, context: AgentContext, update_type: str):
        """Log context updates"""
        self._add_log_entry(
            level="DEBUG",
            component="context_management",
            event_type="context_update",
            task_id=context.task_id,
            message=f"Context updated: {update_type}",
            data={
                "update_type": update_type,
                "files_count": len(context.files),
                "conversation_length": len(context.conversation_history),
                "has_error": context.error_context is not None
            }
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        for operation, times in self.performance_metrics.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "total_time": sum(times),
                    "average_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times)
                }
        
        stats["error_counts"] = self.error_counts.copy()
        stats["total_log_entries"] = len(self.log_entries)
        
        return stats
    
    def get_recent_logs(
        self,
        count: int = 100,
        level: Optional[str] = None,
        component: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> List[LogEntry]:
        """Get recent log entries with optional filtering"""
        with self.entry_lock:
            entries = self.log_entries.copy()
        
        # Apply filters
        if level:
            entries = [e for e in entries if e.level == level]
        if component:
            entries = [e for e in entries if e.component == component]
        if task_id:
            entries = [e for e in entries if e.task_id == task_id]
        
        # Return most recent entries
        return entries[-count:] if count > 0 else entries
    
    def export_logs(
        self,
        file_path: str,
        format_type: str = "json",
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ):
        """Export logs to file"""
        with self.entry_lock:
            entries = self.log_entries.copy()
        
        # Filter by time range
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]
        
        try:
            if format_type.lower() == "json":
                with open(file_path, 'w') as f:
                    json.dump([asdict(entry) for entry in entries], f, indent=2)
            elif format_type.lower() == "csv":
                import csv
                with open(file_path, 'w', newline='') as f:
                    if entries:
                        writer = csv.DictWriter(f, fieldnames=asdict(entries[0]).keys())
                        writer.writeheader()
                        for entry in entries:
                            writer.writerow(asdict(entry))
            
            self.logger.info(f"Logs exported to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
    
    def clear_logs(self):
        """Clear log entries from memory"""
        with self.entry_lock:
            self.log_entries.clear()
        self.performance_metrics.clear()
        self.error_counts.clear()
        
        self.logger.info("Log entries cleared")
    
    def _add_log_entry(
        self,
        level: str,
        component: str,
        event_type: str,
        message: str,
        task_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        execution_time: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Add structured log entry"""
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            component=component,
            event_type=event_type,
            task_id=task_id,
            message=message,
            data=data,
            execution_time=execution_time,
            error=error
        )
        
        with self.entry_lock:
            self.log_entries.append(entry)
            
            # Maintain max entries limit
            if len(self.log_entries) > self.max_entries:
                self.log_entries = self.log_entries[-self.max_entries:]
        
        # Write to structured file if configured
        if self.structured_file:
            self._write_structured_entry(entry)
    
    def _write_structured_entry(self, entry: LogEntry):
        """Write structured entry to file"""
        try:
            with open(self.structured_file, 'a') as f:
                json.dump(asdict(entry), f)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to write structured log: {e}")
    
    def _track_performance(self, operation: str, execution_time: float):
        """Track performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        
        self.performance_metrics[operation].append(execution_time)
        
        # Keep only last 1000 measurements per operation
        if len(self.performance_metrics[operation]) > 1000:
            self.performance_metrics[operation] = self.performance_metrics[operation][-1000:]


class DebugSession:
    """
    Debug session for interactive agent debugging and analysis.
    """
    
    def __init__(self, logger: AgentLogger):
        """Initialize debug session"""
        self.logger = logger
        self.breakpoints: Dict[str, bool] = {}
        self.watch_variables: Dict[str, Any] = {}
        self.step_mode = False
        self.session_start = time.time()
    
    def set_breakpoint(self, component: str, event_type: str):
        """Set breakpoint for specific component and event"""
        key = f"{component}:{event_type}"
        self.breakpoints[key] = True
        print(f"Breakpoint set: {key}")
    
    def remove_breakpoint(self, component: str, event_type: str):
        """Remove breakpoint"""
        key = f"{component}:{event_type}"
        if key in self.breakpoints:
            del self.breakpoints[key]
            print(f"Breakpoint removed: {key}")
    
    def watch_variable(self, name: str, value: Any):
        """Watch variable value"""
        self.watch_variables[name] = value
        print(f"Watching variable: {name} = {value}")
    
    def check_breakpoint(self, component: str, event_type: str) -> bool:
        """Check if breakpoint should trigger"""
        key = f"{component}:{event_type}"
        return self.breakpoints.get(key, False) or self.step_mode
    
    def print_context(self, context: AgentContext):
        """Print current context state"""
        print(f"\n=== Context Debug Info ===")
        print(f"Task ID: {context.task_id}")
        print(f"Task: {context.task_description}")
        print(f"Files: {len(context.files)}")
        print(f"Conversation: {len(context.conversation_history)} messages")
        print(f"Error: {context.error_context is not None}")
        print(f"Updated: {datetime.fromtimestamp(context.updated_at)}")
    
    def print_response(self, response: AgentResponse):
        """Print response debug info"""
        print(f"\n=== Response Debug Info ===")
        print(f"Content length: {len(response.content)}")
        print(f"Has tool request: {response.has_tool_request()}")
        print(f"Confidence: {response.confidence}")
        print(f"State: {response.state.value}")
        print(f"Execution time: {response.execution_time}")
        print(f"Error: {response.error}")
    
    def interactive_debug(self):
        """Start interactive debugging session"""
        print("=== Interactive Debug Session Started ===")
        print("Commands: step, continue, breakpoint <component:event>, watch <name> <value>, quit")
        
        while True:
            try:
                command = input("debug> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit" or cmd == "q":
                    break
                elif cmd == "step" or cmd == "s":
                    self.step_mode = True
                    print("Step mode enabled")
                elif cmd == "continue" or cmd == "c":
                    self.step_mode = False
                    print("Continuing execution")
                elif cmd == "breakpoint" or cmd == "bp":
                    if len(command) > 1:
                        parts = command[1].split(':')
                        if len(parts) == 2:
                            self.set_breakpoint(parts[0], parts[1])
                elif cmd == "watch" or cmd == "w":
                    if len(command) > 2:
                        name = command[1]
                        value = ' '.join(command[2:])
                        self.watch_variable(name, value)
                elif cmd == "stats":
                    stats = self.logger.get_performance_stats()
                    print(json.dumps(stats, indent=2))
                elif cmd == "logs":
                    count = int(command[1]) if len(command) > 1 else 10
                    logs = self.logger.get_recent_logs(count)
                    for log in logs:
                        print(f"{datetime.fromtimestamp(log.timestamp)} - {log.level} - {log.message}")
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Debug session ended")


def create_agent_logger(
    name: str = "olympus_agent",
    log_dir: Optional[str] = None
) -> AgentLogger:
    """
    Create configured agent logger.
    
    Args:
        name: Logger name
        log_dir: Optional log directory
        
    Returns:
        Configured AgentLogger instance
    """
    log_file = None
    structured_file = None
    
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        log_file = str(log_path / f"{name}.log")
        structured_file = str(log_path / f"{name}_structured.jsonl")
    
    return AgentLogger(
        name=name,
        log_file=log_file,
        structured_file=structured_file
    )