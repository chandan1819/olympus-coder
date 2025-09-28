#!/bin/bash

# Olympus-Coder-v1 Deployment Script
# Handles deployment and configuration of the model

set -e

echo "🚀 Deploying Olympus-Coder-v1..."

# Configuration
MODEL_NAME="olympus-coder-v1"
CONFIG_PATH="./config/deployment.json"
VALIDATION_SCRIPT="./scripts/validate.py"

# Check if model exists
echo "📋 Checking model availability..."

if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "❌ Error: Model $MODEL_NAME not found"
    echo "Please build the model first using: ./scripts/build_model.sh"
    exit 1
fi

# Load deployment configuration
if [ -f "$CONFIG_PATH" ]; then
    echo "📝 Loading deployment configuration from $CONFIG_PATH"
    # Extract configuration values (simplified - in production, use proper JSON parsing)
    OLLAMA_HOST=$(grep -o '"ollama_host": "[^"]*"' "$CONFIG_PATH" | cut -d'"' -f4)
    OLLAMA_PORT=$(grep -o '"ollama_port": [0-9]*' "$CONFIG_PATH" | cut -d':' -f2 | tr -d ' ')
    
    echo "🌐 Target host: $OLLAMA_HOST:$OLLAMA_PORT"
else
    echo "⚠️  Warning: Deployment config not found, using defaults"
    OLLAMA_HOST="localhost"
    OLLAMA_PORT="11434"
fi

# Health check
echo "🏥 Performing health check..."

if curl -s "http://$OLLAMA_HOST:$OLLAMA_PORT/api/tags" > /dev/null; then
    echo "✅ Ollama service is running"
else
    echo "❌ Error: Cannot connect to Ollama service at $OLLAMA_HOST:$OLLAMA_PORT"
    echo "Please ensure Ollama is running and accessible"
    exit 1
fi

# Validate model functionality
if [ -f "$VALIDATION_SCRIPT" ]; then
    echo "🧪 Running validation tests..."
    python3 "$VALIDATION_SCRIPT" --model "$MODEL_NAME" --quick
    
    if [ $? -eq 0 ]; then
        echo "✅ Validation tests passed"
    else
        echo "⚠️  Warning: Some validation tests failed"
        echo "Model is deployed but may not function optimally"
    fi
else
    echo "⚠️  Warning: Validation script not found, skipping tests"
fi

echo ""
echo "🎉 Deployment complete!"
echo "📊 Model: $MODEL_NAME"
echo "🌐 Endpoint: http://$OLLAMA_HOST:$OLLAMA_PORT"
echo "💡 Test with: curl -X POST http://$OLLAMA_HOST:$OLLAMA_PORT/api/generate -d '{\"model\":\"$MODEL_NAME\",\"prompt\":\"Hello\"}'"