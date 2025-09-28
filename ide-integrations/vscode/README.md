# VS Code Integration for Olympus-Coder

This directory contains VS Code integration tools for Olympus-Coder, including extensions, snippets, and configuration files.

## 🚀 Quick Setup

### Method 1: VS Code Extension (Recommended)

1. **Install the extension**
   ```bash
   cd ide-integrations/vscode/extension
   npm install
   npm run compile
   code --install-extension olympus-coder-*.vsix
   ```

2. **Configure Ollama endpoint**
   - Open VS Code Settings (Cmd/Ctrl + ,)
   - Search for "Olympus Coder"
   - Set your Ollama URL (default: http://localhost:11434)

3. **Start coding with AI assistance**
   - Use `Ctrl+Shift+P` → "Olympus: Generate Code"
   - Use `Ctrl+Shift+P` → "Olympus: Debug Code"
   - Use `Ctrl+Shift+P` → "Olympus: Explain Code"

### Method 2: REST Client Integration

1. **Install REST Client extension**
   ```
   ext install humao.rest-client
   ```

2. **Use the provided .http files**
   - Open `olympus-requests.http`
   - Click "Send Request" above any request
   - Modify prompts as needed

### Method 3: Terminal Integration

1. **Add to VS Code tasks**
   - Copy `tasks.json` to `.vscode/tasks.json`
   - Use `Ctrl+Shift+P` → "Tasks: Run Task" → "Olympus Coder"

## 📁 Files Included

- `extension/` - Complete VS Code extension
- `snippets/` - Code snippets for common Olympus-Coder patterns
- `tasks.json` - VS Code tasks configuration
- `settings.json` - Recommended VS Code settings
- `olympus-requests.http` - REST Client requests
- `keybindings.json` - Custom keyboard shortcuts

## ⚙️ Configuration

### Extension Settings

```json
{
  "olympusCoder.ollamaUrl": "http://localhost:11434",
  "olympusCoder.modelName": "olympus-coder-v1:latest",
  "olympusCoder.temperature": 0.1,
  "olympusCoder.maxTokens": 2048,
  "olympusCoder.autoSave": true,
  "olympusCoder.showInlineCompletion": true
}
```

### Keyboard Shortcuts

- `Ctrl+Alt+G` - Generate code
- `Ctrl+Alt+D` - Debug current file
- `Ctrl+Alt+E` - Explain selected code
- `Ctrl+Alt+R` - Refactor selection
- `Ctrl+Alt+T` - Generate tests

## 🎯 Features

### Code Generation
- Context-aware code completion
- Function and class generation
- Documentation generation
- Test case creation

### Debugging
- Error analysis and fixes
- Performance optimization suggestions
- Code review and improvements

### Project Understanding
- Automatic project context detection
- Import statement validation
- Architecture analysis

## 🔧 Troubleshooting

### Common Issues

1. **Extension not working**
   - Check Ollama is running: `ollama list`
   - Verify model exists: `ollama run olympus-coder-v1:latest`
   - Check VS Code Developer Console for errors

2. **Slow responses**
   - Reduce `maxTokens` in settings
   - Use lightweight model configuration
   - Check system resources

3. **Connection errors**
   - Verify `ollamaUrl` in settings
   - Check firewall settings
   - Ensure Ollama service is accessible