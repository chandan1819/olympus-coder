# Troubleshooting Guide

Common issues and solutions for Olympus-Coder-v1 deployment and operation.

## Installation Issues

### Ollama Not Found
**Problem**: `ollama: command not found`

**Solution**:
1. Install Ollama from https://ollama.ai
2. Ensure Ollama is in your PATH
3. Restart your terminal/shell

### Base Model Not Available
**Problem**: Base model (llama3:8b) not found

**Solution**:
```bash
ollama pull llama3:8b
# or for alternative base model
ollama pull codellama:13b
```

## Build Issues

### Modelfile Syntax Errors
**Problem**: Model build fails with syntax errors

**Solution**:
1. Check Modelfile syntax
2. Ensure all PARAMETER lines are valid
3. Verify SYSTEM prompt is properly formatted
4. Check for special characters or encoding issues

### Insufficient Resources
**Problem**: Model build fails due to memory/disk space

**Solution**:
1. Free up disk space (models can be several GB)
2. Ensure sufficient RAM (8GB+ recommended)
3. Close other applications during build

## Runtime Issues

### Model Not Responding
**Problem**: API calls timeout or return errors

**Solution**:
1. Check if Ollama service is running: `ollama list`
2. Restart Ollama service
3. Verify model is loaded: `ollama list | grep olympus-coder-v1`
4. Check system resources (CPU, memory)

### Poor Response Quality
**Problem**: Model generates low-quality or incorrect responses

**Solution**:
1. Verify system prompt is complete and correct
2. Check model parameters (temperature, top_p)
3. Ensure base model is appropriate for task
4. Run validation tests: `python scripts/validate.py`

### JSON Format Issues
**Problem**: Tool requests not properly formatted as JSON

**Solution**:
1. Check system prompt includes JSON formatting instructions
2. Verify stop sequences are configured correctly
3. Adjust temperature (lower = more consistent formatting)
4. Review prompt examples and formatting guidelines

## Performance Issues

### Slow Response Times
**Problem**: Model takes too long to respond

**Solution**:
1. Reduce context window size in configuration
2. Lower num_predict parameter
3. Use smaller base model (llama3:8b vs codellama:13b)
4. Optimize system resources

### High Resource Usage
**Problem**: Model consumes too much CPU/memory

**Solution**:
1. Adjust model parameters to reduce resource usage
2. Limit concurrent requests
3. Monitor and optimize system prompt length
4. Consider using quantized model versions

## Integration Issues

### API Connection Failures
**Problem**: Cannot connect to Ollama API

**Solution**:
1. Verify Ollama is running on correct host/port
2. Check firewall settings
3. Ensure API endpoints are accessible
4. Test with curl: `curl http://localhost:11434/api/tags`

### Framework Integration Problems
**Problem**: Issues integrating with agentic frameworks

**Solution**:
1. Verify API compatibility
2. Check request/response format expectations
3. Review framework-specific integration requirements
4. Test with minimal integration example

## Validation Failures

### Test Failures
**Problem**: Validation tests fail

**Solution**:
1. Check specific test failure messages
2. Verify model is properly loaded
3. Test individual components separately
4. Review system prompt completeness

### Accuracy Issues
**Problem**: Model accuracy below target thresholds

**Solution**:
1. Review and improve system prompt
2. Adjust model parameters
3. Increase training examples in prompt
4. Consider using different base model

## Getting Help

### Diagnostic Information

When reporting issues, include:
- Ollama version: `ollama --version`
- Model list: `ollama list`
- System specifications (OS, RAM, CPU)
- Error messages and logs
- Configuration files

### Log Files

Check Ollama logs for detailed error information:
- Linux/macOS: `~/.ollama/logs/`
- Windows: `%USERPROFILE%\.ollama\logs\`

### Support Resources

- Ollama Documentation: https://ollama.ai/docs
- GitHub Issues: [Project repository]
- Community Forums: [Community links]

## Prevention

### Best Practices

1. **Regular Validation**: Run validation tests after changes
2. **Resource Monitoring**: Monitor system resources during operation
3. **Configuration Backup**: Keep backup copies of working configurations
4. **Gradual Updates**: Test changes in development before production
5. **Documentation**: Keep deployment and configuration documented