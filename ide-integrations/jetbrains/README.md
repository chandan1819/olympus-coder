# JetBrains IDEs Integration (PyCharm, IntelliJ IDEA, WebStorm)

Integration guide for JetBrains IDEs including PyCharm, IntelliJ IDEA, WebStorm, and other JetBrains products.

## 🚀 Setup Methods

### Method 1: HTTP Client Plugin (Built-in)

1. **Open HTTP Client**
   - Go to `Tools` → `HTTP Client` → `Create Request in HTTP Client`
   - Or create a new `.http` file

2. **Use provided requests**
   - Copy content from `olympus-requests.http`
   - Modify prompts as needed
   - Click the green arrow to execute

### Method 2: External Tools Integration

1. **Add External Tool**
   - Go to `File` → `Settings` → `Tools` → `External Tools`
   - Click `+` to add new tool

2. **Configure Olympus Coder Tool**
   ```
   Name: Olympus Coder - Generate Code
   Program: python3
   Arguments: $ProjectFileDir$/ide-integrations/jetbrains/olympus_tool.py generate "$SelectedText$" "$FilePath$"
   Working Directory: $ProjectFileDir$
   ```

3. **Add to Menu/Toolbar**
   - Go to `File` → `Settings` → `Appearance & Behavior` → `Menus and Toolbars`
   - Add the external tool to desired location

### Method 3: Live Templates

1. **Import Live Templates**
   - Go to `File` → `Settings` → `Editor` → `Live Templates`
   - Import `olympus-templates.xml`

2. **Use Templates**
   - Type abbreviation (e.g., `ocgen`) and press Tab
   - Fill in the prompt when requested

## 📁 Files Included

- `olympus-requests.http` - HTTP Client requests
- `olympus_tool.py` - External tool script
- `olympus-templates.xml` - Live templates
- `keymap.xml` - Custom keymap
- `settings.zip` - Complete IDE settings

## ⌨️ Keyboard Shortcuts

After importing keymap:
- `Ctrl+Alt+G` - Generate code
- `Ctrl+Alt+D` - Debug code
- `Ctrl+Alt+E` - Explain selection
- `Ctrl+Alt+R` - Refactor code
- `Ctrl+Alt+T` - Generate tests

## 🔧 Configuration

### HTTP Client Environment

Create `.http-client-env.json`:
```json
{
  "dev": {
    "ollamaUrl": "http://localhost:11434",
    "modelName": "olympus-coder-v1:latest"
  }
}
```

### External Tool Variables

Available variables:
- `$SelectedText$` - Currently selected text
- `$FilePath$` - Current file path
- `$ProjectFileDir$` - Project root directory
- `$FileDir$` - Current file directory

## 🎯 Features

### Code Generation
- Context-aware completions
- Function and class generation
- Documentation generation

### Debugging
- Error analysis
- Performance suggestions
- Code review

### Refactoring
- Code optimization
- Modern syntax conversion
- Best practices application

## 🔧 Troubleshooting

### Common Issues

1. **External tool not working**
   - Check Python path in tool configuration
   - Verify script permissions: `chmod +x olympus_tool.py`
   - Check Ollama service status

2. **HTTP Client errors**
   - Verify Ollama URL in environment file
   - Check model availability: `ollama list`
   - Ensure proper JSON formatting

3. **Live templates not expanding**
   - Check template scope (Python, JavaScript, etc.)
   - Verify abbreviation spelling
   - Ensure templates are enabled