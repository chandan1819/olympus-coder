#!/usr/bin/env python3
"""
Olympus-Coder Ollama Submission Preparation Script

This script prepares all necessary files for submitting Olympus-Coder
to the official Ollama library at https://ollama.com/new

Usage: python3 scripts/prepare_ollama_submission.py
"""

import os
import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime

class OllamaSubmissionPrep:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.submission_dir = self.project_root / "ollama_submission"
        self.model_info = {
            "name": "olympus-coder",
            "version": "1.0.0",
            "description": "AI-powered coding assistant for autonomous software development",
            "author": "Olympus-Coder Contributors",
            "license": "MIT",
            "base_model": "codellama:13b",
            "repository": "https://github.com/chandan1819/olympus-coder",
            "tags": ["coding", "ai-assistant", "development", "python", "javascript", "autonomous"],
            "use_cases": [
                "Code generation from natural language",
                "Real-time debugging assistance", 
                "Project context understanding",
                "Automated testing and documentation"
            ],
            "performance": {
                "accuracy": ">95%",
                "syntax_correctness": ">98%",
                "response_time": "<5s",
                "task_completion": ">75%"
            }
        }
    
    def create_submission_directory(self):
        """Create clean submission directory"""
        if self.submission_dir.exists():
            shutil.rmtree(self.submission_dir)
        self.submission_dir.mkdir(parents=True)
        print(f"✅ Created submission directory: {self.submission_dir}")
    
    def copy_modelfile(self):
        """Copy the production Modelfile"""
        source = self.project_root / "modelfile" / "Modelfile.public"
        dest = self.submission_dir / "Modelfile"
        
        if source.exists():
            shutil.copy2(source, dest)
            print("✅ Copied production Modelfile")
        else:
            # Fallback to regular Modelfile
            source = self.project_root / "modelfile" / "Modelfile"
            shutil.copy2(source, dest)
            print("✅ Copied regular Modelfile (consider creating Modelfile.public)")
    
    def copy_readme(self):
        """Copy the Ollama-specific README"""
        source = self.project_root / "OLLAMA_README.md"
        dest = self.submission_dir / "README.md"
        
        if source.exists():
            shutil.copy2(source, dest)
            print("✅ Copied Ollama README")
        else:
            print("❌ OLLAMA_README.md not found - please create it first")
    
    def copy_license(self):
        """Copy the license file"""
        source = self.project_root / "LICENSE"
        dest = self.submission_dir / "LICENSE"
        
        if source.exists():
            shutil.copy2(source, dest)
            print("✅ Copied LICENSE file")
        else:
            print("❌ LICENSE file not found")
    
    def create_model_info(self):
        """Create model-info.yaml file"""
        model_info_path = self.submission_dir / "model-info.yaml"
        
        with open(model_info_path, 'w') as f:
            yaml.dump(self.model_info, f, default_flow_style=False, sort_keys=False)
        
        print("✅ Created model-info.yaml")
    
    def create_submission_checklist(self):
        """Create a submission checklist"""
        checklist = """# Ollama Submission Checklist for Olympus-Coder

## Pre-Submission Validation ✅

### Model Testing
- [ ] Model builds successfully locally
- [ ] All validation tests pass
- [ ] Performance benchmarks meet targets
- [ ] No critical bugs or issues

### Documentation
- [ ] README.md is comprehensive and clear
- [ ] Usage examples are accurate and tested
- [ ] Performance metrics are documented
- [ ] Integration guides are complete

### Legal & Licensing
- [ ] MIT License is properly applied
- [ ] All dependencies are compatible
- [ ] Attribution to base model (CodeLlama) is included
- [ ] No proprietary code or data included

### Quality Assurance
- [ ] Code follows best practices
- [ ] Responses are appropriate and safe
- [ ] No bias or harmful content
- [ ] Consistent output formatting

## Submission Information 📝

### Basic Details
- **Model Name**: olympus-coder
- **Version**: 1.0.0
- **Base Model**: codellama:13b
- **License**: MIT
- **Repository**: https://github.com/chandan1819/olympus-coder

### Description
AI-powered coding assistant for autonomous software development. Built on CodeLlama 13B with specialized prompts and optimized parameters for high-quality code generation, debugging, and project assistance.

### Tags
- coding
- ai-assistant  
- development
- python
- javascript
- autonomous

### Use Cases
1. **Code Generation**: Natural language to working code
2. **Debugging**: Intelligent error analysis and fixes
3. **Learning**: Algorithm explanation and code understanding
4. **Testing**: Automated test case generation
5. **Documentation**: Code comments and API docs

### Performance Metrics
- Response Accuracy: >95%
- Code Syntax Correctness: >98%
- Task Completion Rate: >75%
- Average Response Time: <5 seconds

### Unique Features
- **Privacy-First**: Runs entirely locally
- **Autonomous Operation**: Minimal human intervention needed
- **Multi-IDE Integration**: VS Code, JetBrains, Vim, Sublime
- **Structured Output**: JSON formatting for tool integration
- **Context Awareness**: Understands project patterns

## Files Included 📁

- [ ] `Modelfile` - Production-ready model definition
- [ ] `README.md` - Comprehensive documentation
- [ ] `LICENSE` - MIT license file
- [ ] `model-info.yaml` - Structured metadata
- [ ] This checklist for reference

## Submission Steps 🚀

1. **Visit**: https://ollama.com/new
2. **Login**: Use GitHub account
3. **Fill Form**: Use information from this checklist
4. **Upload Files**: All files from this directory
5. **Submit**: Wait for review process
6. **Monitor**: Check for feedback and respond promptly

## Post-Submission 📊

### If Approved
- [ ] Announce on social media
- [ ] Update documentation with new install instructions
- [ ] Monitor usage and feedback
- [ ] Plan future updates and improvements

### If Rejected
- [ ] Review feedback carefully
- [ ] Address all concerns raised
- [ ] Test improvements thoroughly
- [ ] Resubmit with changes

## Support & Maintenance 🛠️

### Ongoing Responsibilities
- [ ] Monitor community feedback
- [ ] Fix bugs and issues promptly
- [ ] Provide user support
- [ ] Regular model updates
- [ ] Documentation maintenance

### Community Engagement
- [ ] Respond to questions and issues
- [ ] Share usage examples
- [ ] Collaborate with other developers
- [ ] Contribute to Ollama ecosystem

---

**Ready to submit? Double-check all items above and visit https://ollama.com/new** 🚀
"""
        
        checklist_path = self.submission_dir / "SUBMISSION_CHECKLIST.md"
        with open(checklist_path, 'w') as f:
            f.write(checklist)
        
        print("✅ Created submission checklist")
    
    def validate_submission(self):
        """Validate that all required files are present"""
        required_files = ["Modelfile", "README.md", "LICENSE", "model-info.yaml"]
        missing_files = []
        
        for file_name in required_files:
            file_path = self.submission_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            print(f"❌ Missing required files: {', '.join(missing_files)}")
            return False
        else:
            print("✅ All required files present")
            return True
    
    def generate_submission_summary(self):
        """Generate a summary of the submission"""
        summary = f"""
# Olympus-Coder Ollama Submission Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Model Information
- **Name**: {self.model_info['name']}
- **Version**: {self.model_info['version']}
- **Base Model**: {self.model_info['base_model']}
- **License**: {self.model_info['license']}
- **Repository**: {self.model_info['repository']}

## Performance Targets
- **Accuracy**: {self.model_info['performance']['accuracy']}
- **Syntax Correctness**: {self.model_info['performance']['syntax_correctness']}
- **Response Time**: {self.model_info['performance']['response_time']}
- **Task Completion**: {self.model_info['performance']['task_completion']}

## Files Prepared
"""
        
        for file_path in self.submission_dir.iterdir():
            if file_path.is_file():
                size = file_path.stat().st_size
                summary += f"- **{file_path.name}**: {size:,} bytes\n"
        
        summary += f"""
## Next Steps
1. Review all files in: {self.submission_dir}
2. Test the Modelfile locally: `ollama create olympus-coder-test -f {self.submission_dir}/Modelfile`
3. Visit https://ollama.com/new to submit
4. Use SUBMISSION_CHECKLIST.md as your guide

## Quick Test Commands
```bash
# Test the prepared Modelfile
ollama create olympus-coder-test -f {self.submission_dir}/Modelfile

# Quick validation
ollama run olympus-coder-test "Create a hello world function"

# Clean up test
ollama rm olympus-coder-test
```

**Good luck with your submission!** 🚀
"""
        
        summary_path = self.submission_dir / "SUBMISSION_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(summary)
        
        print("✅ Generated submission summary")
    
    def prepare_submission(self):
        """Main method to prepare the submission"""
        print("🚀 Preparing Olympus-Coder for Ollama Library Submission")
        print("=" * 60)
        
        try:
            self.create_submission_directory()
            self.copy_modelfile()
            self.copy_readme()
            self.copy_license()
            self.create_model_info()
            self.create_submission_checklist()
            self.generate_submission_summary()
            
            if self.validate_submission():
                print("\n" + "=" * 60)
                print("🎉 Submission preparation complete!")
                print(f"📁 Files ready in: {self.submission_dir}")
                print("\n📋 Next steps:")
                print("1. Review all files in the submission directory")
                print("2. Test the Modelfile locally")
                print("3. Visit https://ollama.com/new to submit")
                print("4. Use SUBMISSION_CHECKLIST.md as your guide")
                print("\n🔗 Submission URL: https://ollama.com/new")
                return True
            else:
                print("\n❌ Submission preparation failed - missing required files")
                return False
                
        except Exception as e:
            print(f"\n❌ Error during preparation: {e}")
            return False

def main():
    """Main function"""
    prep = OllamaSubmissionPrep()
    success = prep.prepare_submission()
    
    if success:
        print("\n✨ Ready to submit Olympus-Coder to the Ollama library!")
    else:
        print("\n🔧 Please fix the issues above and try again.")

if __name__ == "__main__":
    main()