# 🌍 Sharing Olympus-Coder: Distribution Guide

Complete guide on how to share your Olympus-Coder with teams, organizations, and the community.

## 🎯 **Sharing Options Overview**

| Method | Audience | Complexity | Benefits |
|--------|----------|------------|----------|
| **GitHub Repository** | Public/Teams | Easy | Version control, collaboration |
| **Docker Container** | Teams/Enterprise | Medium | Easy deployment, consistency |
| **Ollama Model Hub** | Community | Medium | Wide distribution, easy install |
| **Package Distribution** | Developers | Medium | pip/npm installable |
| **Cloud Deployment** | Enterprise | Advanced | Scalable, centralized |
| **Local Network** | Teams | Easy | Private, secure |

## 🚀 **Method 1: GitHub Repository (Current)**

### **Your Repository is Already Live!**
**URL**: https://github.com/chandan1819/olympus-coder

### **How Others Can Use It:**

```bash
# Clone the repository
git clone https://github.com/chandan1819/olympus-coder.git
cd olympus-coder

# Install Ollama (if not installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Build the model
./scripts/build_model.sh

# Test it works
python3 scripts/validate.py --quick

# Start using
python3 ide-integrations/olympus_ide_helper.py generate "Hello World function"
```

### **Improve Repository for Sharing:**

Let me add some files to make it easier for others:

<function_calls>
<invoke name="fsWrite">
<parameter name="path">olympus-coder-v1/INSTALL.md Olympus-Coder Installation Guide

Quick installation guide for new users.

## ⚡ Quick Install (5 minutes)

### **Step 1: Prerequisites**

**Install Ollama:**
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows (PowerShell)
winget install Ollama.Ollama

# Or download from: https://ollama.ai/download
```

**Install Python 3.8+:**
```bash
# Check if you have Python
python3 --version

# If not installed:
# macOS: brew install python3
# Ubuntu: sudo apt install python3 python3-pip
# Windows: Download from python.org
```

### **Step 2: Get Olympus-Coder**

```bash
# Clone the repository
git clone https://github.com/chandan1819/olympus-coder.git
cd olympus-coder

# Make scripts executable
chmod +x scripts/*.sh
```

### **Step 3: Build the Model**

```bash
# This will download CodeLlama 13B and build Olympus-Coder
./scripts/build_model.sh

# Wait for completion (5-10 minutes depending on internet speed)
```

### **Step 4: Test Installation**

```bash
# Quick health check
python3 scripts/validate.py --quick

# Test code generation
python3 ide-integrations/olympus_ide_helper.py generate "Create a hello world function"
```

### **Step 5: Start Coding!**

```bash
# Generate code
python3 ide-integrations/olympus_ide_helper.py generate "Create a Flask API endpoint"

# Debug code
python3 ide-integrations/olympus_ide_helper.py debug --file mycode.py

# Explain code
python3 ide-integrations/olympus_ide_helper.py explain --text "complex_code_here"
```

## 🔧 **IDE Setup (Optional)**

### **VS Code (Recommended)**
1. Install REST Client extension: `ext install humao.rest-client`
2. Open `ide-integrations/vscode/olympus-requests.http`
3. Click "Send Request" above any example

### **JetBrains IDEs**
1. Go to `File` → `Settings` → `Tools` → `External Tools`
2. Add new tool with provided configuration in `ide-integrations/jetbrains/README.md`

### **Other IDEs**
See `ide-integrations/README.md` for Vim, Sublime Text, and other editors.

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Model not found"**
   ```bash
   ollama list  # Check if model exists
   ./scripts/build_model.sh  # Rebuild if missing
   ```

2. **"Connection refused"**
   ```bash
   ollama serve  # Start Ollama service
   ```

3. **"Permission denied"**
   ```bash
   chmod +x scripts/*.sh  # Make scripts executable
   ```

4. **Slow responses**
   - Use shorter prompts
   - Check system resources (8GB+ RAM recommended)
   - Use lightweight configuration

### **Get Help:**
- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](https://github.com/chandan1819/olympus-coder/issues)
- 💬 [Discussions](https://github.com/chandan1819/olympus-coder/discussions)

## 🎯 **What's Next?**

1. **Read the [Productivity Guide](docs/PRODUCTIVITY_GUIDE.md)**
2. **Try the [IDE Integrations](ide-integrations/README.md)**
3. **Join the community and share your experience!**

---

**Total setup time: 5-10 minutes**
**Start boosting your productivity immediately!** 🚀