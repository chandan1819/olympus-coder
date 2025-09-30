#!/usr/bin/env python3
"""
Olympus-Coder Interactive Demo Script

This script provides an interactive demonstration of Olympus-Coder's capabilities.
Perfect for presentations, meetups, or showcasing to potential users.

Usage: python3 demo_script.py
"""

import subprocess
import time
import sys
import os
from typing import List, Tuple

class OlympusDemo:
    def __init__(self):
        self.helper_script = "ide-integrations/olympus_ide_helper.py"
        self.demo_steps = []
        self.setup_demo_steps()
    
    def setup_demo_steps(self):
        """Define all demo steps"""
        self.demo_steps = [
            {
                "title": "🏥 Health Check",
                "description": "First, let's verify that Olympus-Coder is running and accessible",
                "command": f"python3 {self.helper_script} health",
                "explanation": "This checks if the Ollama service is running and the model is available"
            },
            {
                "title": "🚀 Code Generation",
                "description": "Generate a complete Python function from natural language",
                "command": f"python3 {self.helper_script} generate 'Create a Python function to validate email addresses using regex with proper error handling'",
                "explanation": "Watch how Olympus-Coder converts natural language into working code with documentation"
            },
            {
                "title": "🐛 Code Debugging",
                "description": "Analyze and fix problematic code",
                "command": f"python3 {self.helper_script} debug --text 'def get_last_item(items): return items[len(items)]'",
                "explanation": "The AI identifies the off-by-one error and provides a fix with explanation"
            },
            {
                "title": "📚 Code Explanation",
                "description": "Explain complex algorithms in plain English",
                "command": f"python3 {self.helper_script} explain --text 'def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)'",
                "explanation": "Perfect for understanding unfamiliar code or learning new algorithms"
            },
            {
                "title": "🧪 Test Generation",
                "description": "Automatically generate comprehensive unit tests",
                "command": f"python3 {self.helper_script} test --text 'def calculate_circle_area(radius): return 3.14159 * radius ** 2'",
                "explanation": "Creates test cases including edge cases and error conditions"
            },
            {
                "title": "💬 AI Chat",
                "description": "Interactive conversation about programming concepts",
                "command": f"python3 {self.helper_script} chat 'What are the best practices for error handling in Python web applications?'",
                "explanation": "Get expert advice and explanations on programming topics"
            }
        ]
    
    def print_header(self):
        """Print demo header"""
        print("=" * 70)
        print("🏛️  OLYMPUS-CODER INTERACTIVE DEMO")
        print("   AI-Powered Coding Assistant")
        print("=" * 70)
        print()
        print("This demo showcases the key features of Olympus-Coder:")
        print("• Natural language to code generation")
        print("• Intelligent debugging assistance")
        print("• Code explanation and learning")
        print("• Automated test generation")
        print("• Interactive AI chat")
        print()
        print("🎯 Goal: Show how AI can make you 4-6x more productive")
        print()
    
    def run_step(self, step_num: int, step: dict):
        """Run a single demo step"""
        print(f"\n{step['title']}")
        print("─" * 50)
        print(f"📝 {step['description']}")
        print()
        
        # Wait for user input
        input("👆 Press Enter to run this demo...")
        
        print(f"🔧 Command: {step['command']}")
        print()
        print("⏳ Running...")
        
        # Execute command
        try:
            result = subprocess.run(
                step['command'], 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Success!")
                print()
                print("📤 Output:")
                print("─" * 30)
                print(result.stdout)
                print("─" * 30)
                print()
                print(f"💡 Explanation: {step['explanation']}")
            else:
                print("❌ Error occurred:")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ Command timed out (this can happen with complex requests)")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        input("👆 Press Enter to continue to next step...")
    
    def run_demo(self):
        """Run the complete demo"""
        self.print_header()
        
        # Check if helper script exists
        if not os.path.exists(self.helper_script):
            print("❌ Error: Olympus-Coder helper script not found!")
            print(f"Expected location: {self.helper_script}")
            print()
            print("Please make sure you're running this from the olympus-coder-v1 directory")
            return False
        
        try:
            for i, step in enumerate(self.demo_steps, 1):
                print(f"\n🎬 DEMO STEP {i}/{len(self.demo_steps)}")
                self.run_step(i, step)
            
            # Demo completion
            self.print_completion()
            return True
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            return False
    
    def print_completion(self):
        """Print demo completion message"""
        print("\n" + "=" * 70)
        print("🎉 DEMO COMPLETE!")
        print("=" * 70)
        print()
        print("What you just saw:")
        print("✅ AI-powered code generation from natural language")
        print("✅ Intelligent debugging and error analysis")
        print("✅ Complex code explanation in plain English")
        print("✅ Automated test generation with edge cases")
        print("✅ Interactive AI chat for programming help")
        print()
        print("🚀 Productivity Benefits:")
        print("• 4-6x faster development")
        print("• Higher code quality")
        print("• Better error handling")
        print("• Comprehensive testing")
        print("• Continuous learning")
        print()
        print("🔒 Privacy Benefits:")
        print("• Runs entirely on your machine")
        print("• No code sent to external servers")
        print("• Complete control over your data")
        print()
        print("🛠️  IDE Integration:")
        print("• VS Code extension")
        print("• JetBrains plugins")
        print("• Vim/Neovim support")
        print("• Sublime Text integration")
        print("• Universal command-line tool")
        print()
        print("📚 Get Started:")
        print("• GitHub: https://github.com/chandan1819/olympus-coder")
        print("• Documentation: See README.md")
        print("• Quick Start: ide-integrations/QUICK_START.md")
        print()
        print("🤝 Join the Community:")
        print("• Star the repository")
        print("• Report issues and suggestions")
        print("• Contribute improvements")
        print("• Share your experience")
        print()
        print("Thank you for watching the Olympus-Coder demo! 🙏")

def main():
    """Main demo function"""
    demo = OlympusDemo()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Olympus-Coder Interactive Demo")
            print("Usage: python3 demo_script.py")
            print()
            print("This script demonstrates the key features of Olympus-Coder")
            print("Make sure to run it from the olympus-coder-v1 directory")
            return
        elif sys.argv[1] in ['-q', '--quick']:
            print("Running quick demo (non-interactive)...")
            # Run a quick automated demo
            for i, step in enumerate(demo.demo_steps[:3], 1):
                print(f"\n--- Step {i}: {step['title']} ---")
                subprocess.run(step['command'], shell=True)
            return
    
    # Run interactive demo
    success = demo.run_demo()
    
    if success:
        print("\n🎯 Ready to boost your productivity with Olympus-Coder?")
        print("Visit: https://github.com/chandan1819/olympus-coder")
    else:
        print("\n🔧 Need help setting up Olympus-Coder?")
        print("Check the troubleshooting guide in the documentation")

if __name__ == "__main__":
    main()