# Deployment Guide

This guide covers the deployment and integration of Olympus-Coder-v1 with agentic frameworks.

## Prerequisites

- Ollama framework installed and running
- Python 3.8+ for validation scripts
- Base model (llama3:8b or codellama:13b) available

## Quick Deployment

1. **Build the model**:
   ```bash
   ./scripts/build_model.sh
   ```

2. **Deploy and validate**:
   ```bash
   ./scripts/deploy.sh
   ```

3. **Test the deployment**:
   ```bash
   python scripts/validate.py --quick
   ```

## Configuration

### Model Configuration

Edit `config/model_config.json` to customize:
- Base model selection
- Temperature and sampling parameters
- Context window limits
- Performance targets

### Deployment Configuration

Edit `config/deployment.json` to configure:
- Ollama connection settings
- Monitoring and logging
- Integration parameters
- Validation settings

## Integration with Agentic Frameworks

### API Endpoints

The model is accessible through standard Ollama API endpoints:

- **Generate**: `POST /api/generate`
- **Chat**: `POST /api/chat`
- **Health Check**: `GET /api/tags`

### Example Integration

```python
import requests

def query_olympus_coder(prompt: str) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "olympus-coder-v1",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]
```

## Monitoring and Maintenance

### Health Checks

Regular health checks should verify:
- Model availability
- Response quality
- Performance metrics
- Error rates

### Performance Monitoring

Key metrics to track:
- Task completion rate (target: 75%)
- Structured response accuracy (target: >95%)
- Response time and resource usage
- Human intervention rate

## Troubleshooting

See `troubleshooting.md` for common issues and solutions.

## Advanced Configuration

### Custom System Prompts

To modify the system prompt:
1. Edit components in `prompts/` directory
2. Rebuild the model with updated Modelfile
3. Redeploy and validate

### Performance Tuning

Adjust model parameters in `config/model_config.json`:
- Lower temperature for more deterministic responses
- Adjust context window for longer conversations
- Modify sampling parameters for different response styles