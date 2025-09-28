# Olympus-Coder-v1 Monitoring Tools

This document describes the comprehensive monitoring and metrics system for Olympus-Coder-v1, implementing requirements 5.1, 5.2, and 3.4.

## Overview

The monitoring system consists of three main components:

1. **Accuracy Tracker** - Tracks task completion rates, structured response accuracy, and human intervention requirements
2. **Performance Monitor** - Monitors response times, resource usage, and comparative performance vs base models
3. **Monitoring Dashboard** - Provides unified view of all metrics and health scoring

## Components

### 1. Accuracy Tracker (`accuracy_tracker.py`)

Implements comprehensive accuracy tracking as specified in requirements:
- **Requirement 5.1**: Measures 75% autonomous completion rate target
- **Requirement 3.4**: Monitors >95% structured response accuracy target  
- **Requirement 5.2**: Tracks human intervention rate (target ≤50%)

#### Features:
- SQLite database for persistent tracking
- Task categorization (code_generation, debugging, tool_usage, etc.)
- Real-time accuracy scoring and grading
- Historical trend analysis
- Requirements compliance reporting

#### Usage:
```bash
# Run accuracy tracking session
python scripts/accuracy_tracker.py --session-id "test_session_001"

# Generate report only
python scripts/accuracy_tracker.py --report-only

# Custom database path
python scripts/accuracy_tracker.py --db-path "custom_accuracy.db"
```

#### Database Schema:
- `task_results`: Individual task execution results
- `accuracy_sessions`: Aggregated session metrics
- Tracks completion rates, response accuracy, intervention needs

### 2. Performance Monitor (`performance_monitor.py`)

Implements advanced performance benchmarking as specified in requirement 5.2:
- Response time measurement and analysis
- Resource usage monitoring (CPU, memory)
- Comparative analysis vs base model performance
- Load testing and concurrent request handling

#### Features:
- Real-time resource monitoring with psutil
- Comparative benchmarking against base models
- Performance grading and trend analysis
- Detailed scenario-based testing
- Resource efficiency scoring

#### Usage:
```bash
# Run comprehensive performance analysis
python scripts/performance_monitor.py --session-id "perf_test_001"

# Compare against different base model
python scripts/performance_monitor.py --base-model "codellama:13b"

# Custom iterations and output
python scripts/performance_monitor.py --iterations 5 --output results.json
```

#### Test Scenarios:
- Simple queries (baseline performance)
- Code generation (small, medium, large)
- Debugging analysis
- JSON tool requests
- Context analysis

### 3. Monitoring Dashboard (`monitoring_dashboard.py`)

Provides unified monitoring dashboard combining accuracy and performance metrics:
- Overall model health scoring
- Requirements compliance tracking
- Historical trend analysis
- Issue identification and recommendations

#### Features:
- Health score calculation (0-100 scale)
- Requirements compliance dashboard
- Trend analysis and alerting
- JSON export for external systems
- Automated health checks

#### Usage:
```bash
# Generate dashboard report
python scripts/monitoring_dashboard.py

# Export metrics as JSON
python scripts/monitoring_dashboard.py --export-json metrics.json

# Health check with exit codes
python scripts/monitoring_dashboard.py --health-check
```

#### Health Scoring:
- **Accuracy (50 points)**: Task completion (20), Response accuracy (20), Intervention rate (10)
- **Performance (50 points)**: Response time (25), Resource usage (25)
- **Grades**: A (90%+), B (80%+), C (70%+), D (60%+), F (<60%)

## Requirements Compliance

### Requirement 5.1 - Autonomous Completion Rate
- **Target**: 75% autonomous completion rate
- **Measurement**: Successful task completion without human intervention
- **Tracking**: Per-task and session-level completion rates
- **Alerting**: Warnings when below 75% threshold

### Requirement 5.2 - Human Intervention Reduction  
- **Target**: 50% reduction in human-in-the-loop interventions
- **Measurement**: Percentage of tasks requiring human assistance
- **Tracking**: Intervention rate trends and comparative analysis
- **Alerting**: Warnings when intervention rate >50%

### Requirement 3.4 - Structured Response Accuracy
- **Target**: >95% accuracy in structured response formatting
- **Measurement**: JSON format validation, code block formatting, response structure
- **Tracking**: Per-response accuracy scoring and aggregation
- **Alerting**: Warnings when accuracy <95%

## Database Schema

### Accuracy Tracking Database
```sql
-- Individual task results
CREATE TABLE task_results (
    id INTEGER PRIMARY KEY,
    task_id TEXT NOT NULL,
    task_type TEXT NOT NULL,
    prompt TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    completion_rate REAL NOT NULL,
    structured_response_accuracy REAL NOT NULL,
    human_intervention_required BOOLEAN NOT NULL,
    response_text TEXT
);

-- Session aggregates
CREATE TABLE accuracy_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    task_completion_rate REAL DEFAULT 0.0,
    avg_structured_response_accuracy REAL DEFAULT 0.0,
    human_intervention_rate REAL DEFAULT 0.0,
    accuracy_grade TEXT DEFAULT 'F'
);
```

### Performance Monitoring Database
```sql
-- Performance metrics per request
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY,
    model_name TEXT NOT NULL,
    scenario_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    response_time REAL NOT NULL,
    cpu_usage REAL NOT NULL,
    memory_usage_mb REAL NOT NULL,
    success BOOLEAN NOT NULL
);

-- Resource usage snapshots
CREATE TABLE resource_snapshots (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    cpu_percent REAL NOT NULL,
    memory_percent REAL NOT NULL,
    memory_used_mb REAL NOT NULL
);

-- Benchmark sessions
CREATE TABLE benchmark_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    base_model TEXT NOT NULL,
    avg_response_time REAL DEFAULT 0.0,
    performance_grade TEXT DEFAULT 'F'
);
```

## Integration Examples

### Automated Monitoring Pipeline
```bash
#!/bin/bash
# Daily monitoring pipeline

# Run accuracy tracking
python scripts/accuracy_tracker.py --session-id "daily_$(date +%Y%m%d)"

# Run performance benchmarking  
python scripts/performance_monitor.py --session-id "perf_$(date +%Y%m%d)"

# Generate dashboard and check health
python scripts/monitoring_dashboard.py --health-check --export-json daily_metrics.json

# Exit with error if health is poor
if [ $? -ne 0 ]; then
    echo "❌ Model health check failed!"
    exit 1
fi
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Model Health Check
  run: |
    python scripts/monitoring_dashboard.py --health-check
  continue-on-error: false
```

### Alerting Integration
```python
# Example alerting integration
import json
from monitoring_dashboard import MonitoringDashboard

dashboard = MonitoringDashboard()
metrics = dashboard.export_metrics_json(7)

health = metrics["health_score"]
if health["health_grade"] in ["D", "F"]:
    # Send alert to monitoring system
    send_alert(f"Model health degraded: {health['health_grade']}")
```

## Troubleshooting

### Common Issues

1. **Database Lock Errors**
   - Ensure only one monitoring process runs at a time
   - Check file permissions on database files

2. **High Resource Usage**
   - Monitor concurrent request limits
   - Check for memory leaks in long-running sessions

3. **Accuracy Degradation**
   - Review recent prompt changes
   - Check model configuration parameters
   - Analyze failed task patterns

4. **Performance Regression**
   - Compare against baseline measurements
   - Check system resource availability
   - Review model parameter changes

### Debugging Commands
```bash
# Check database contents
sqlite3 olympus_accuracy_tracking.db "SELECT * FROM accuracy_sessions ORDER BY start_time DESC LIMIT 5;"

# Validate script syntax
python -m py_compile scripts/accuracy_tracker.py

# Test monitoring tools
python scripts/test_monitoring_tools.py
```

## Best Practices

1. **Regular Monitoring**: Run accuracy tracking and performance monitoring daily
2. **Baseline Establishment**: Establish performance baselines before making changes
3. **Trend Analysis**: Monitor trends over time, not just point-in-time metrics
4. **Automated Alerting**: Set up automated alerts for requirement violations
5. **Data Retention**: Implement data retention policies for monitoring databases
6. **Backup Strategy**: Regular backup of monitoring databases for historical analysis

## Future Enhancements

1. **Real-time Monitoring**: WebSocket-based real-time monitoring dashboard
2. **Advanced Analytics**: Machine learning-based anomaly detection
3. **Integration APIs**: REST APIs for external monitoring system integration
4. **Visualization**: Grafana/Prometheus integration for advanced visualization
5. **Predictive Analytics**: Trend-based performance prediction and capacity planning