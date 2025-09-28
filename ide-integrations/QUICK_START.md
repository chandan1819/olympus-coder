# 🚀 Quick Start Guide - IDE Integrations

Get Olympus-Coder working in your favorite IDE in under 5 minutes!

## ⚡ Universal Method (Works with ANY IDE)

### 1. Test the Helper Script

```bash
# Navigate to the integrations directory
cd olympus-coder-v1/ide-integrations

# Test connection
python3 olympus_ide_helper.py health

# Generate some code
python3 olympus_ide_helper.py generate "Create a Python function to validate emails"
```

### 2. IDE-Specific Quick Setup

#### VS Code (Recommended - 2 minutes)

1. **Install REST Client extension**
   ```
   ext install humao.rest-client
   ```

2. **Open the requests file**
   ```bash
   code vscode/olympus-requests.http
   ```

3. **Click "Send Request" above any example**
   - Modify the prompt as needed
   - Results appear instantly

#### JetBrains IDEs (PyCharm, IntelliJ, WebStorm)

1. **Add External Tool**
   - `File` → `Settings` → `Tools` → `External Tools` → `+`
   - **Name**: `Olympus Generate`
   - **Program**: `python3`
   - **Arguments**: `$ProjectFileDir$/ide-integrations/olympus_ide_helper.py generate "$Prompt$" --file "$FilePath$"`
   - **Working Directory**: `$ProjectFileDir$`

2. **Use it**
   - Right-click in editor → `External Tools` → `Olympus Generate`
   - Enter your prompt when asked

#### Vim/Neovim

1. **Add to your config**
   ```vim
   " Add to .vimrc or init.vim
   command! -nargs=1 OlympusGenerate :r !python3 /path/to/olympus_ide_helper.py generate <args>
   command! OlympusDebug :r !python3 /path/to/olympus_ide_helper.py debug --file %
   ```

2. **Use commands**
   ```vim
   :OlympusGenerate "Create a sorting function"
   :OlympusDebug
   ```

#### Sublime Text

1. **Add Build System**
   - `Tools` → `Build System` → `New Build System`
   - Paste this content:
   ```json
   {
     "shell_cmd": "python3 /path/to/olympus_ide_helper.py generate \"$prompt\" --file \"$file\"",
     "variants": [
       {
         "name": "Debug",
         "shell_cmd": "python3 /path/to/olympus_ide_helper.py debug --file \"$file\""
       }
     ]
   }
   ```

2. **Use it**
   - `Ctrl+B` to build/generate
   - `Ctrl+Shift+B` to choose variant

## 🎯 Common Usage Patterns

### Generate Code
```bash
# Basic generation
python3 olympus_ide_helper.py generate "Create a REST API endpoint for users"

# With file context
python3 olympus_ide_helper.py generate "Add error handling" --file mycode.py

# Save to file
python3 olympus_ide_helper.py generate "Create tests" --output tests.py
```

### Debug Code
```bash
# Debug entire file
python3 olympus_ide_helper.py debug --file buggy_code.py

# Debug specific code
python3 olympus_ide_helper.py debug --text "def broken_function():\n    return 1/0"
```

### Explain Code
```bash
# Explain selected code
python3 olympus_ide_helper.py explain --text "lambda x: x**2 + 2*x + 1"

# With file context
python3 olympus_ide_helper.py explain --text "complex_algorithm()" --file algorithm.py
```

### Refactor Code
```bash
# Refactor for better quality
python3 olympus_ide_helper.py refactor --text "old_style_code()" --file legacy.py
```

### Generate Tests
```bash
# Generate tests for file
python3 olympus_ide_helper.py test --file mymodule.py

# Generate tests for specific code
python3 olympus_ide_helper.py test --text "def add(a, b): return a + b"
```

### Chat with AI
```bash
# Ask questions about your code
python3 olympus_ide_helper.py chat "How can I optimize this function?" --file slow_code.py

# General programming questions
python3 olympus_ide_helper.py chat "What's the best way to handle errors in Python?"
```

## ⚙️ Configuration

### Environment Variables
```bash
# Set default configuration
export OLLAMA_URL="http://localhost:11434"
export OLYMPUS_MODEL="olympus-coder-v1:latest"
export OLYMPUS_TEMPERATURE="0.1"
```

### Command Line Options
```bash
# Custom model
python3 olympus_ide_helper.py generate "code" --model olympus-coder-v1-precise:latest

# Custom temperature
python3 olympus_ide_helper.py generate "creative solution" --temperature 0.3

# Custom Ollama URL
python3 olympus_ide_helper.py generate "code" --url http://remote-server:11434
```

## 🔧 Troubleshooting

### Quick Fixes

1. **"Connection refused"**
   ```bash
   # Start Ollama
   ollama serve
   
   # Check if running
   curl http://localhost:11434/api/tags
   ```

2. **"Model not found"**
   ```bash
   # List models
   ollama list
   
   # Pull if missing
   ollama pull olympus-coder-v1:latest
   ```

3. **"Permission denied"**
   ```bash
   # Make script executable
   chmod +x olympus_ide_helper.py
   ```

4. **Slow responses**
   ```bash
   # Use lightweight config
   python3 olympus_ide_helper.py generate "code" --temperature 0.05 --max-tokens 1024
   ```

### Test Your Setup

```bash
# Complete test
python3 olympus_ide_helper.py health
python3 olympus_ide_helper.py generate "print('Hello, World!')"
```

## 📚 Examples by Language

### Python
```bash
python3 olympus_ide_helper.py generate "Create a Flask API with authentication"
python3 olympus_ide_helper.py generate "Add type hints to this function" --file mycode.py
```

### JavaScript
```bash
python3 olympus_ide_helper.py generate "Create a React component for user profile"
python3 olympus_ide_helper.py generate "Convert to async/await" --text "callback_code()"
```

### Java
```bash
python3 olympus_ide_helper.py generate "Create a Spring Boot controller"
python3 olympus_ide_helper.py debug --file MyClass.java
```

## 🎨 IDE-Specific Tips

### VS Code
- Use the REST Client for interactive development
- Set up tasks.json for one-click generation
- Use the integrated terminal for quick commands

### JetBrains
- Create multiple external tools for different actions
- Use live templates with Olympus-generated code
- Integrate with the HTTP Client plugin

### Vim/Neovim
- Map commands to key combinations
- Use with existing LSP setup
- Create custom functions for complex workflows

### Sublime Text
- Set up multiple build variants
- Use snippets for common prompts
- Integrate with existing packages

---

**Need more help?** Check the detailed README for your specific IDE in the respective directories!