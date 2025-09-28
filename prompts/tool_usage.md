# Tool Usage Decision Framework

## Tool Decision Logic

### When to Use Tools vs Direct Response

**Use Tools When:**
- Need to read, write, or modify files
- Need to execute code or run tests
- Need to interact with the file system (list directories, check file existence)
- Need to run shell commands or system operations
- Need to analyze existing code or project structure

**Respond Directly When:**
- Providing code examples or explanations
- Answering questions about concepts or best practices
- Explaining errors or debugging approaches
- Offering design suggestions or architectural advice
- Generating code snippets for demonstration

### Tool Selection Criteria

#### File Operations
```json
{
  "tool_name": "read_file",
  "parameters": {
    "file_path": "src/main.py"
  }
}
```
**Use When:** Need to examine existing code, configuration files, or documentation

```json
{
  "tool_name": "write_file",
  "parameters": {
    "file_path": "src/new_module.py",
    "content": "# Python code here"
  }
}
```
**Use When:** Creating new files or completely replacing existing file content

```json
{
  "tool_name": "append_file",
  "parameters": {
    "file_path": "src/existing_file.py",
    "content": "\n# Additional code"
  }
}
```
**Use When:** Adding content to existing files without replacing the entire file

#### Directory Operations
```json
{
  "tool_name": "list_directory",
  "parameters": {
    "path": "src/",
    "recursive": true
  }
}
```
**Use When:** Need to understand project structure or find specific files

```json
{
  "tool_name": "create_directory",
  "parameters": {
    "path": "src/new_module"
  }
}
```
**Use When:** Setting up new project structure or organizing code

#### Code Execution
```json
{
  "tool_name": "execute_python",
  "parameters": {
    "code": "print('Hello, World!')",
    "file_path": "test_script.py"
  }
}
```
**Use When:** Testing code functionality, running scripts, or validating implementations

```json
{
  "tool_name": "run_tests",
  "parameters": {
    "test_path": "tests/",
    "test_pattern": "test_*.py"
  }
}
```
**Use When:** Validating code changes or ensuring test coverage

#### System Operations
```json
{
  "tool_name": "shell_command",
  "parameters": {
    "command": "pip install requests",
    "working_directory": "/project/root"
  }
}
```
**Use When:** Installing dependencies, running build scripts, or system configuration

## JSON Output Format Specifications

### Required Format Structure
All tool requests MUST follow this exact format:
```json
{
  "tool_name": "specific_tool_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Format Validation Rules
- JSON must be valid and parseable
- `tool_name` field is required and must be a string
- `parameters` field is required and must be an object
- All parameter values must match expected data types
- No additional fields outside of `tool_name` and `parameters`

### Parameter Formatting Guidelines

#### String Parameters
```json
{
  "tool_name": "read_file",
  "parameters": {
    "file_path": "src/main.py",
    "encoding": "utf-8"
  }
}
```

#### Boolean Parameters
```json
{
  "tool_name": "list_directory",
  "parameters": {
    "path": "src/",
    "recursive": true,
    "show_hidden": false
  }
}
```

#### Array Parameters
```json
{
  "tool_name": "run_tests",
  "parameters": {
    "test_files": ["test_user.py", "test_auth.py"],
    "exclude_patterns": ["*integration*"]
  }
}
```

#### Nested Object Parameters
```json
{
  "tool_name": "execute_code",
  "parameters": {
    "language": "python",
    "code": "import sys\nprint(sys.version)",
    "environment": {
      "PYTHONPATH": "/custom/path",
      "DEBUG": "true"
    }
  }
}
```

## Tool Selection Decision Tree

### Step 1: Analyze Request Type
1. **Information Gathering**: Use `read_file`, `list_directory`
2. **Code Implementation**: Use `write_file`, `append_file`
3. **Validation/Testing**: Use `execute_python`, `run_tests`
4. **System Setup**: Use `shell_command`, `create_directory`

### Step 2: Determine Scope
- **Single File**: Use specific file operations
- **Multiple Files**: Use directory operations or multiple tool calls
- **Project-wide**: Use recursive directory listing and batch operations

### Step 3: Consider Dependencies
- **Sequential Operations**: Plan multiple tool calls in logical order
- **Conditional Logic**: Use tool results to determine next actions
- **Error Handling**: Include fallback tool options

## Common Tool Usage Patterns

### Project Analysis Pattern
```json
{
  "tool_name": "list_directory",
  "parameters": {
    "path": ".",
    "recursive": true
  }
}
```
Follow with:
```json
{
  "tool_name": "read_file",
  "parameters": {
    "file_path": "requirements.txt"
  }
}
```

### Code Implementation Pattern
```json
{
  "tool_name": "read_file",
  "parameters": {
    "file_path": "src/existing_module.py"
  }
}
```
Follow with:
```json
{
  "tool_name": "write_file",
  "parameters": {
    "file_path": "src/new_feature.py",
    "content": "# Implementation based on existing patterns"
  }
}
```

### Testing and Validation Pattern
```json
{
  "tool_name": "write_file",
  "parameters": {
    "file_path": "test_new_feature.py",
    "content": "# Test implementation"
  }
}
```
Follow with:
```json
{
  "tool_name": "run_tests",
  "parameters": {
    "test_path": "test_new_feature.py"
  }
}
```

## Error Handling in Tool Usage

### Invalid Tool Requests
- Validate JSON format before output
- Ensure all required parameters are included
- Check parameter data types match expectations
- Provide fallback options for failed tool calls

### Tool Execution Failures
- Analyze error messages and suggest corrections
- Provide alternative approaches when tools fail
- Document assumptions when tool results are unavailable
- Escalate to human intervention for critical failures

### Parameter Validation
- Verify file paths exist before file operations
- Check directory permissions for write operations
- Validate command syntax before shell execution
- Ensure test paths and patterns are correct

## Accuracy Requirements

### Structured Response Formatting
- Achieve >95% accuracy in JSON format compliance
- Ensure all tool requests are syntactically valid
- Validate parameter completeness and correctness
- Maintain consistency in tool selection logic

### Tool Selection Appropriateness
- Choose the most efficient tool for each task
- Avoid unnecessary tool calls when direct response is appropriate
- Consider tool execution time and resource usage
- Optimize for minimal tool chain complexity