#!/bin/bash

# Olympus-Coder-v1 Model Build Script
# Builds the custom Ollama model from the Modelfile with comprehensive validation

set -e

echo "🚀 Building Olympus-Coder-v1 model..."

# Configuration
MODEL_NAME="olympus-coder-v1"
MODELFILE_PATH="./modelfile/Modelfile"
CONFIG_PATH="./config/model_config.json"
VALIDATION_SCRIPT="./scripts/validate.py"
LOG_FILE="./build_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Error handling function
handle_error() {
    log "❌ Build failed at step: $1"
    log "📋 Check log file: $LOG_FILE"
    exit 1
}

log "🚀 Starting Olympus-Coder-v1 build process..."
log "📅 Build started at: $(date)"

# Check prerequisites
log "📋 Checking prerequisites..."

if ! command -v ollama &> /dev/null; then
    handle_error "Ollama is not installed or not in PATH. Please install from https://ollama.ai"
fi

if ! command -v python3 &> /dev/null; then
    log "⚠️  Warning: Python3 not found, validation tests will be skipped"
    SKIP_VALIDATION=true
else
    SKIP_VALIDATION=false
fi

# Check Ollama service status
log "🔍 Checking Ollama service status..."
if ! ollama list &> /dev/null; then
    handle_error "Ollama service is not running. Please start Ollama service first."
fi

# Determine base model from Modelfile
BASE_MODEL=$(grep "^FROM" "$MODELFILE_PATH" | awk '{print $2}' | head -1)
if [ -z "$BASE_MODEL" ]; then
    handle_error "Could not determine base model from Modelfile"
fi

log "📦 Base model: $BASE_MODEL"

# Check if base model is available
if ! ollama list | grep -q "$BASE_MODEL"; then
    log "⬇️  Base model $BASE_MODEL not found, pulling..."
    if ! ollama pull "$BASE_MODEL"; then
        handle_error "Failed to pull base model $BASE_MODEL"
    fi
    log "✅ Base model $BASE_MODEL pulled successfully"
fi

# Validate Modelfile syntax
log "🔍 Validating Modelfile syntax..."
if [ ! -f "$MODELFILE_PATH" ]; then
    handle_error "Modelfile not found at $MODELFILE_PATH"
fi

# Check for required Modelfile components
if ! grep -q "^FROM" "$MODELFILE_PATH"; then
    handle_error "Modelfile missing FROM directive"
fi

if ! grep -q "^SYSTEM" "$MODELFILE_PATH"; then
    handle_error "Modelfile missing SYSTEM directive"
fi

log "✅ Modelfile validation passed"

# Remove existing model if it exists
if ollama list | grep -q "$MODEL_NAME"; then
    log "🗑️  Removing existing model $MODEL_NAME..."
    ollama rm "$MODEL_NAME" || log "⚠️  Warning: Could not remove existing model"
fi

# Build the model
log "🔨 Building model from Modelfile..."
cd "$(dirname "$0")/.."

if ! ollama create "$MODEL_NAME" -f "$MODELFILE_PATH" 2>&1 | tee -a "$LOG_FILE"; then
    handle_error "Model creation failed"
fi

# Verify model creation
log "🔍 Verifying model creation..."
if ! ollama list | grep -q "$MODEL_NAME"; then
    handle_error "Model verification failed - model not found in Ollama list"
fi

# Get model info
MODEL_SIZE=$(ollama list | grep "$MODEL_NAME" | awk '{print $2}')
log "✅ Model created successfully!"
log "📊 Model size: $MODEL_SIZE"

# Health check - basic functionality test
log "🏥 Performing health check..."
HEALTH_CHECK_RESPONSE=$(ollama run "$MODEL_NAME" "Hello" --verbose 2>&1 || echo "HEALTH_CHECK_FAILED")

if [[ "$HEALTH_CHECK_RESPONSE" == *"HEALTH_CHECK_FAILED"* ]]; then
    handle_error "Health check failed - model does not respond"
fi

log "✅ Health check passed"

# Run validation tests if available
if [ "$SKIP_VALIDATION" = false ] && [ -f "$VALIDATION_SCRIPT" ]; then
    log "🧪 Running validation tests..."
    if python3 "$VALIDATION_SCRIPT" --model "$MODEL_NAME" --quick 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ Validation tests passed"
    else
        log "⚠️  Warning: Some validation tests failed, but model is functional"
    fi
else
    log "⚠️  Skipping validation tests (Python3 or validation script not available)"
fi

# Run comprehensive health check
HEALTH_CHECK_SCRIPT="./scripts/health_check.py"
if [ "$SKIP_VALIDATION" = false ] && [ -f "$HEALTH_CHECK_SCRIPT" ]; then
    log "🏥 Running comprehensive health check..."
    if python3 "$HEALTH_CHECK_SCRIPT" --model "$MODEL_NAME" --no-performance 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ Health check passed"
    else
        log "⚠️  Warning: Health check issues detected"
    fi
fi

# Run deployment verification
DEPLOYMENT_VERIFICATION_SCRIPT="./scripts/deployment_verification.py"
if [ "$SKIP_VALIDATION" = false ] && [ -f "$DEPLOYMENT_VERIFICATION_SCRIPT" ]; then
    log "🔍 Running deployment verification..."
    if python3 "$DEPLOYMENT_VERIFICATION_SCRIPT" --model "$MODEL_NAME" 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ Deployment verification passed"
    else
        log "⚠️  Warning: Deployment verification issues detected"
    fi
fi

# Performance benchmark (basic)
log "⚡ Running performance benchmark..."
START_TIME=$(date +%s.%N)
ollama run "$MODEL_NAME" "Generate a simple Python function that returns 'Hello World'" > /dev/null 2>&1
END_TIME=$(date +%s.%N)
RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc -l 2>/dev/null || echo "N/A")

if [ "$RESPONSE_TIME" != "N/A" ]; then
    log "📊 Response time: ${RESPONSE_TIME}s"
else
    log "📊 Response time: Could not measure"
fi

# Generate build report
log ""
log "📋 Build Report:"
log "=================="
log "Model Name: $MODEL_NAME"
log "Base Model: $BASE_MODEL"
log "Model Size: $MODEL_SIZE"
log "Build Time: $(date)"
log "Log File: $LOG_FILE"
log ""
log "🎉 Olympus-Coder-v1 build completed successfully!"
log ""
log "💡 Usage Examples:"
log "  Interactive: ollama run $MODEL_NAME"
log "  API: curl -X POST http://localhost:11434/api/generate -d '{\"model\":\"$MODEL_NAME\",\"prompt\":\"Hello\"}'"
log "  Validation: python3 $VALIDATION_SCRIPT --model $MODEL_NAME"