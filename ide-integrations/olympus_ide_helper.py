#!/usr/bin/env python3
"""
Olympus Coder IDE Helper Script

A universal helper script that can be called from any IDE or editor
to interact with Olympus-Coder LLM.

Usage:
    python3 olympus_ide_helper.py generate "Create a function to sort array"
    python3 olympus_ide_helper.py debug --file mycode.py
    python3 olympus_ide_helper.py explain --text "selected code here"
"""

import argparse
import json
import requests
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

class OlympusIDEHelper:
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 model_name: str = "olympus-coder-v1:latest",
                 temperature: float = 0.1,
                 max_tokens: int = 2048):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def call_api(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Call Olympus Coder API with the given prompt"""
        try:
            temp = temperature if temperature is not None else self.temperature
            
            response = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temp,
                    "num_predict": self.max_tokens
                }
            }, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure it's running on " + self.ollama_url
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be processing a complex request."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_file_context(self, file_path: str, max_lines: int = 100) -> str:
        """Read file content for context"""
        try:
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if len(lines) <= max_lines:
                content = ''.join(lines)
            else:
                # Take first half and last half
                half = max_lines // 2
                content = ''.join(lines[:half]) + "\n... (truncated) ...\n" + ''.join(lines[-half:])
            
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C Header',
            '.hpp': 'C++ Header',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.md': 'Markdown',
            '.sh': 'Shell Script',
            '.bash': 'Bash Script',
            '.zsh': 'Zsh Script'
        }
        return language_map.get(ext, 'Unknown')
    
    def generate_code(self, prompt: str, file_path: Optional[str] = None) -> str:
        """Generate code based on prompt and optional file context"""
        context = ""
        if file_path:
            file_content = self.get_file_context(file_path)
            language = self.detect_language(file_path)
            context = f"""
File: {file_path}
Language: {language}

Current file content:
{file_content}

"""
        
        full_prompt = f"""{context}Request: {prompt}

Generate the requested code with proper formatting, documentation, and error handling:"""
        
        return self.call_api(full_prompt)
    
    def debug_code(self, code: Optional[str] = None, file_path: Optional[str] = None) -> str:
        """Debug code or file"""
        if file_path:
            code = self.get_file_context(file_path)
            language = self.detect_language(file_path)
            context = f"File: {file_path}\nLanguage: {language}\n\n"
        else:
            context = ""
        
        if not code:
            return "Error: No code provided to debug"
        
        prompt = f"""{context}Code to debug:
{code}

Analyze this code for:
1. Syntax errors
2. Logical errors
3. Performance issues
4. Security vulnerabilities
5. Best practice violations

Provide specific fixes and explanations:"""
        
        return self.call_api(prompt, temperature=0.05)
    
    def explain_code(self, code: str, file_path: Optional[str] = None) -> str:
        """Explain what the code does"""
        context = ""
        if file_path:
            language = self.detect_language(file_path)
            context = f"File: {file_path}\nLanguage: {language}\n\n"
        
        prompt = f"""{context}Code to explain:
{code}

Provide a clear, detailed explanation of:
1. What this code does
2. How it works step by step
3. Input and output
4. Any important details or edge cases
5. Potential improvements"""
        
        return self.call_api(prompt, temperature=0.2)
    
    def refactor_code(self, code: str, file_path: Optional[str] = None) -> str:
        """Refactor code for better quality"""
        context = ""
        if file_path:
            language = self.detect_language(file_path)
            context = f"File: {file_path}\nLanguage: {language}\n\n"
        
        prompt = f"""{context}Code to refactor:
{code}

Refactor this code to improve:
1. Readability and maintainability
2. Performance
3. Code structure and organization
4. Adherence to best practices
5. Error handling

Provide the refactored code with explanations:"""
        
        return self.call_api(prompt)
    
    def generate_tests(self, code: Optional[str] = None, file_path: Optional[str] = None) -> str:
        """Generate tests for the code"""
        if file_path:
            code = self.get_file_context(file_path)
            language = self.detect_language(file_path)
            
            # Determine test framework based on language
            test_frameworks = {
                'Python': 'pytest',
                'JavaScript': 'Jest',
                'TypeScript': 'Jest',
                'Java': 'JUnit',
                'C#': 'NUnit',
                'Go': 'Go testing package',
                'Rust': 'Rust built-in testing'
            }
            framework = test_frameworks.get(language, 'appropriate testing framework')
            context = f"File: {file_path}\nLanguage: {language}\nTest Framework: {framework}\n\n"
        else:
            context = ""
            framework = "appropriate testing framework"
        
        if not code:
            return "Error: No code provided to generate tests for"
        
        prompt = f"""{context}Code to test:
{code}

Generate comprehensive unit tests using {framework}:
1. Test normal functionality
2. Test edge cases and boundary conditions
3. Test error handling
4. Include setup and teardown if needed
5. Use descriptive test names and assertions"""
        
        return self.call_api(prompt)
    
    def chat(self, message: str, file_path: Optional[str] = None) -> str:
        """Chat with AI about code"""
        context = ""
        if file_path:
            file_content = self.get_file_context(file_path)
            language = self.detect_language(file_path)
            context = f"""
File: {file_path}
Language: {language}

File content:
{file_content}

"""
        
        prompt = f"""{context}Question: {message}

Please provide a helpful response based on the context and question:"""
        
        return self.call_api(prompt, temperature=0.2)
    
    def health_check(self) -> str:
        """Check if Olympus Coder is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                if self.model_name in model_names:
                    return f"✅ Olympus Coder is available at {self.ollama_url}"
                else:
                    available = ', '.join(model_names) if model_names else 'None'
                    return f"❌ Model '{self.model_name}' not found. Available models: {available}"
            else:
                return f"❌ Ollama server error: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Cannot connect to Ollama: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Olympus Coder IDE Helper')
    parser.add_argument('action', choices=['generate', 'debug', 'explain', 'refactor', 'test', 'chat', 'health'],
                       help='Action to perform')
    parser.add_argument('prompt', nargs='?', help='Prompt or message for the action')
    parser.add_argument('--file', '-f', help='File path for context')
    parser.add_argument('--text', '-t', help='Code text to process')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama URL')
    parser.add_argument('--model', default='olympus-coder-v1:latest', help='Model name')
    parser.add_argument('--temperature', type=float, default=0.1, help='Temperature setting')
    parser.add_argument('--max-tokens', type=int, default=2048, help='Maximum tokens')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    # Initialize helper
    helper = OlympusIDEHelper(
        ollama_url=args.url,
        model_name=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    # Execute action
    result = ""
    
    if args.action == 'generate':
        if not args.prompt:
            print("Error: Prompt required for generate action")
            sys.exit(1)
        result = helper.generate_code(args.prompt, args.file)
    
    elif args.action == 'debug':
        result = helper.debug_code(args.text, args.file)
    
    elif args.action == 'explain':
        if not args.text:
            print("Error: --text required for explain action")
            sys.exit(1)
        result = helper.explain_code(args.text, args.file)
    
    elif args.action == 'refactor':
        if not args.text:
            print("Error: --text required for refactor action")
            sys.exit(1)
        result = helper.refactor_code(args.text, args.file)
    
    elif args.action == 'test':
        result = helper.generate_tests(args.text, args.file)
    
    elif args.action == 'chat':
        if not args.prompt:
            print("Error: Prompt required for chat action")
            sys.exit(1)
        result = helper.chat(args.prompt, args.file)
    
    elif args.action == 'health':
        result = helper.health_check()
    
    # Output result
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Result saved to {args.output}")
        except Exception as e:
            print(f"Error saving to file: {e}")
            print(result)
    else:
        print(result)

if __name__ == "__main__":
    main()