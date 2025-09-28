#!/usr/bin/env python3
"""
Olympus Coder External Tool for JetBrains IDEs
Usage: python3 olympus_tool.py <action> <text> <file_path>
"""

import sys
import json
import requests
import os
from pathlib import Path

class OlympusCoderTool:
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.model_name = os.getenv('OLYMPUS_MODEL', 'olympus-coder-v1:latest')
        self.temperature = float(os.getenv('OLYMPUS_TEMPERATURE', '0.1'))
        
    def call_olympus_coder(self, prompt: str, temperature: float = None) -> str:
        """Call Olympus Coder API"""
        try:
            temp = temperature or self.temperature
            response = requests.post(f"{self.ollama_url}/api/generate", json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temp,
                    "num_predict": 2048
                }
            }, timeout=30)
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"Error: HTTP {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_file_context(self, file_path: str, lines_before: int = 20, lines_after: int = 20) -> str:
        """Get context around current cursor position"""
        try:
            if not os.path.exists(file_path):
                return ""
                
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # For simplicity, return the entire file if it's small
            if len(lines) <= 100:
                return ''.join(lines)
            
            # Otherwise return first 50 lines as context
            return ''.join(lines[:50])
            
        except Exception:
            return ""
    
    def generate_code(self, prompt: str, file_path: str) -> str:
        """Generate code based on prompt and context"""
        context = self.get_file_context(file_path)
        file_ext = Path(file_path).suffix
        
        language = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust'
        }.get(file_ext, 'Unknown')
        
        full_prompt = f"""File: {file_path}
Language: {language}

Current file context:
{context}

Request: {prompt}

Generate the requested code with proper formatting and documentation:"""
        
        return self.call_olympus_coder(full_prompt)
    
    def debug_code(self, selected_text: str, file_path: str) -> str:
        """Debug selected code or entire file"""
        if selected_text.strip():
            code_to_debug = selected_text
        else:
            code_to_debug = self.get_file_context(file_path)
        
        prompt = f"""File: {file_path}

Code to debug:
{code_to_debug}

Analyze this code for potential issues, bugs, and improvements. Provide:
1. Any syntax or logical errors
2. Performance issues
3. Security concerns
4. Best practice violations
5. Suggested fixes with explanations"""
        
        return self.call_olympus_coder(prompt, temperature=0.05)
    
    def explain_code(self, selected_text: str, file_path: str) -> str:
        """Explain selected code"""
        if not selected_text.strip():
            return "Error: No code selected to explain"
        
        context = self.get_file_context(file_path)
        
        prompt = f"""File: {file_path}

File context:
{context}

Selected code to explain:
{selected_text}

Provide a clear, detailed explanation of what this code does, including:
1. Purpose and functionality
2. How it works step by step
3. Input and output
4. Any important details or edge cases"""
        
        return self.call_olympus_coder(prompt, temperature=0.2)
    
    def refactor_code(self, selected_text: str, file_path: str) -> str:
        """Refactor selected code"""
        if not selected_text.strip():
            return "Error: No code selected to refactor"
        
        context = self.get_file_context(file_path)
        
        prompt = f"""File: {file_path}

File context:
{context}

Code to refactor:
{selected_text}

Refactor this code to improve:
1. Readability and maintainability
2. Performance
3. Code structure and organization
4. Adherence to best practices
5. Error handling

Provide the refactored code with explanations of changes made:"""
        
        return self.call_olympus_coder(prompt, temperature=0.1)
    
    def generate_tests(self, selected_text: str, file_path: str) -> str:
        """Generate tests for selected code or entire file"""
        if selected_text.strip():
            code_to_test = selected_text
        else:
            code_to_test = self.get_file_context(file_path)
        
        file_ext = Path(file_path).suffix
        test_framework = {
            '.py': 'pytest',
            '.js': 'Jest',
            '.ts': 'Jest',
            '.java': 'JUnit',
            '.go': 'Go testing package'
        }.get(file_ext, 'appropriate testing framework')
        
        prompt = f"""File: {file_path}

Code to test:
{code_to_test}

Generate comprehensive unit tests using {test_framework}. Include:
1. Test cases for normal functionality
2. Edge cases and boundary conditions
3. Error handling tests
4. Mock objects where appropriate
5. Clear test descriptions and assertions"""
        
        return self.call_olympus_coder(prompt, temperature=0.1)

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 olympus_tool.py <action> <selected_text> <file_path>")
        print("Actions: generate, debug, explain, refactor, test")
        sys.exit(1)
    
    action = sys.argv[1]
    selected_text = sys.argv[2] if len(sys.argv) > 2 else ""
    file_path = sys.argv[3] if len(sys.argv) > 3 else ""
    
    tool = OlympusCoderTool()
    
    try:
        if action == "generate":
            if not selected_text:
                selected_text = input("What code would you like to generate? ")
            result = tool.generate_code(selected_text, file_path)
        elif action == "debug":
            result = tool.debug_code(selected_text, file_path)
        elif action == "explain":
            result = tool.explain_code(selected_text, file_path)
        elif action == "refactor":
            result = tool.refactor_code(selected_text, file_path)
        elif action == "test":
            result = tool.generate_tests(selected_text, file_path)
        else:
            result = f"Unknown action: {action}"
        
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()