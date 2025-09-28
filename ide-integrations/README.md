# 🔧 IDE Integrations for Olympus-Coder

Complete integration guide for using Olympus-Coder with popular IDEs and editors.

## 🎯 Supported IDEs

| IDE/Editor | Status | Integration Method | Features |
|------------|--------|-------------------|----------|
| **VS Code** | ✅ Full | Extension + REST Client | Complete feature set |
| **JetBrains IDEs** | ✅ Full | External Tools + HTTP Client | PyCharm, IntelliJ, WebStorm |
| **Vim/Neovim** | ✅ Full | Plugin + Lua API | Async operations, LSP integration |
| **Sublime Text** | ✅ Full | Package + Python API | Context menus, build systems |
| **Emacs** | 🔄 Planned | Elisp package | Org-mode integration |
| **Atom** | 🔄 Planned | Package + JavaScript | Tree-sitter integration |
| **Eclipse** | 🔄 Planned | Plugin + Java API | Workspace integration |

## 🚀 Quick Setup Guide

### 1. Prerequisites

Ensure Olympus-Coder is running:
```bash
# Check if model is available
ollama list | grep olympus-coder-v1

# Test the model
echo "Hello" | ollama run olympus-coder-v1:latest

# Verify API endpoint
curl http://localhost:11434/api/tags
```

### 2. Choose Your IDE

Click on your preferred IDE for detailed setup instructions:

- **[VS Code](vscode/README.md)** - Most comprehensive integration
- **[JetBrains IDEs](jetbrains/README.md)** - PyCharm, IntelliJ, WebStorm
- **[Vim/Neovim](vim-neovim/README.md)** - Terminal-based editors
- **[Sublime Text](sublime-text/README.md)** - Lightweight and fast

## 🎯 Common Features Across All IDEs

### Code Generation
- **Context-aware completions** - Understands your project structure
- **Multi-language support** - Python, JavaScript, TypeScript, Java, Go, Rust
- **Automatic formatting** - Follows language-specific style guides
- **Documentation generation** - Creates docstrings and comments

### Debugging & Analysis
- **Error detection** - Identifies syntax and logical errors
- **Performance analysis** - Suggests optimizations
- **Security review** - Finds potential vulnerabilities
- **Code quality assessment** - Checks best practices

### Refactoring
- **Code modernization** - Updates to latest language features
- **Structure improvement** - Better organization and readability
- **Performance optimization** - Faster and more efficient code
- **Best practices application** - Industry standards compliance

### Testing
- **Unit test generation** - Comprehensive test suites
- **Edge case coverage** - Boundary conditions and error scenarios
- **Mock object creation** - Isolated testing components
- **Test documentation** - Clear test descriptions

## ⌨️ Universal Keyboard Shortcuts

Most integrations use these consistent shortcuts:

| Action | Windows/Linux | macOS | Description |
|--------|---------------|-------|-------------|
| Generate Code | `Ctrl+Alt+G` | `Cmd+Alt+G` | Generate new code |
| Debug Code | `Ctrl+Alt+D` | `Cmd+Alt+D` | Analyze and debug |
| Explain Code | `Ctrl+Alt+E` | `Cmd+Alt+E` | Explain selection |
| Refactor Code | `Ctrl+Alt+R` | `Cmd+Alt+R` | Improve code quality |
| Generate Tests | `Ctrl+Alt+T` | `Cmd+Alt+T` | Create test cases |
| Chat with AI | `Ctrl+Alt+C` | `Cmd+Alt+C` | Interactive chat |

## 🔧 Configuration Options

### Common Settings

All integrations support these configuration options:

```json
{
  "ollama_url": "http://localhost:11434",
  "model_name": "olympus-coder-v1:latest",
  "temperature": 0.1,
  "max_tokens": 2048,
  "context_lines": 50,
  "auto_save": true,
  "show_progress": true,
  "timeout": 30
}
```

### Model Configurations

Choose the right configuration for your use case:

```json
{
  "configurations": {
    "default": {
      "temperature": 0.1,
      "use_case": "General coding tasks"
    },
    "creative": {
      "temperature": 0.3,
      "use_case": "Complex problem-solving"
    },
    "precise": {
      "temperature": 0.05,
      "use_case": "Critical debugging"
    },
    "lightweight": {
      "model": "olympus-coder-v1-light:latest",
      "use_case": "Fast responses"
    }
  }
}
```

## 🛠️ Custom Integration

### REST API Usage

For IDEs not yet supported, use the REST API directly:

```bash
# Generate code
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "olympus-coder-v1:latest",
    "prompt": "Create a Python function to validate emails",
    "stream": false,
    "options": {
      "temperature": 0.1,
      "num_predict": 1024
    }
  }'
```

### Python Integration

```python
import requests

class OlympusCoderClient:
    def __init__(self, url="http://localhost:11434", model="olympus-coder-v1:latest"):
        self.url = url
        self.model = model
    
    def generate_code(self, prompt, temperature=0.1):
        response = requests.post(f"{self.url}/api/generate", json={
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature}
        })
        return response.json()["response"]

# Usage
client = OlympusCoderClient()
code = client.generate_code("Create a sorting function")
print(code)
```

### JavaScript Integration

```javascript
class OlympusCoderClient {
    constructor(url = 'http://localhost:11434', model = 'olympus-coder-v1:latest') {
        this.url = url;
        this.model = model;
    }
    
    async generateCode(prompt, temperature = 0.1) {
        const response = await fetch(`${this.url}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: this.model,
                prompt: prompt,
                stream: false,
                options: { temperature }
            })
        });
        
        const data = await response.json();
        return data.response;
    }
}

// Usage
const client = new OlympusCoderClient();
const code = await client.generateCode('Create a React component');
console.log(code);
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if Ollama is running
   ps aux | grep ollama
   
   # Start Ollama if not running
   ollama serve
   ```

2. **Model Not Found**
   ```bash
   # List available models
   ollama list
   
   # Pull the model if missing
   ollama pull olympus-coder-v1:latest
   ```

3. **Slow Responses**
   - Reduce `max_tokens` setting
   - Use lightweight configuration
   - Check system resources (RAM, CPU)

4. **IDE-Specific Issues**
   - Check IDE console/logs for errors
   - Verify plugin/extension installation
   - Restart IDE after configuration changes

### Debug Mode

Enable debug logging in your IDE integration:

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "log_requests": true
}
```

### Health Check

Test your setup:

```bash
# Test API endpoint
curl http://localhost:11434/api/tags

# Test model response
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"olympus-coder-v1:latest","prompt":"Hello","stream":false}'

# Run validation script
python3 scripts/validate.py --quick
```

## 📚 Examples by Language

### Python Development
```python
# Generate with context
prompt = """
Create a Python class for user authentication with the following methods:
- login(username, password)
- logout()
- is_authenticated()
- get_user_info()

Include proper error handling and type hints.
"""
```

### JavaScript Development
```javascript
// Generate React component
const prompt = `
Create a React functional component called UserProfile that:
- Accepts user data as props
- Displays user avatar, name, and email
- Has a loading state
- Uses modern React hooks
`;
```

### Java Development
```java
// Generate Spring Boot controller
String prompt = """
Create a Spring Boot REST controller for user management with:
- GET /users - list all users
- GET /users/{id} - get user by ID
- POST /users - create new user
- PUT /users/{id} - update user
- DELETE /users/{id} - delete user

Include proper validation and error handling.
""";
```

## 🎨 Customization

### Custom Prompts

Create reusable prompt templates:

```json
{
  "prompt_templates": {
    "api_endpoint": "Create a REST API endpoint for {resource} with CRUD operations",
    "unit_test": "Generate comprehensive unit tests for the following code: {code}",
    "documentation": "Add detailed documentation to this code: {code}",
    "optimization": "Optimize this code for better performance: {code}"
  }
}
```

### Language-Specific Settings

```json
{
  "language_settings": {
    "python": {
      "style_guide": "PEP 8",
      "max_line_length": 79,
      "include_type_hints": true
    },
    "javascript": {
      "style_guide": "Airbnb",
      "use_semicolons": true,
      "prefer_const": true
    }
  }
}
```

## 🔗 Integration Roadmap

### Upcoming Integrations

- **Emacs** - Elisp package with org-mode support
- **Atom** - Package with tree-sitter integration
- **Eclipse** - Plugin with workspace integration
- **Android Studio** - Kotlin and Java support
- **Xcode** - Swift development support

### Community Contributions

We welcome community contributions for additional IDE integrations! See our [Contributing Guide](../CONTRIBUTING.md) for details.

---

**Need help?** Check the specific IDE documentation or open an issue on our [GitHub repository](https://github.com/chandan1819/olympus-coder).