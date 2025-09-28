import * as vscode from 'vscode';
import axios from 'axios';

interface OlympusCoderConfig {
    ollamaUrl: string;
    modelName: string;
    temperature: number;
    maxTokens: number;
    autoSave: boolean;
    showInlineCompletion: boolean;
    contextLines: number;
}

class OlympusCoderProvider {
    private config: OlympusCoderConfig;
    private outputChannel: vscode.OutputChannel;

    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('Olympus Coder');
        this.updateConfig();
    }

    private updateConfig() {
        const config = vscode.workspace.getConfiguration('olympusCoder');
        this.config = {
            ollamaUrl: config.get('ollamaUrl', 'http://localhost:11434'),
            modelName: config.get('modelName', 'olympus-coder-v1:latest'),
            temperature: config.get('temperature', 0.1),
            maxTokens: config.get('maxTokens', 2048),
            autoSave: config.get('autoSave', true),
            showInlineCompletion: config.get('showInlineCompletion', true),
            contextLines: config.get('contextLines', 50)
        };
    }

    private async callOlympusCoder(prompt: string): Promise<string> {
        try {
            this.outputChannel.appendLine(`Sending request to ${this.config.ollamaUrl}`);
            
            const response = await axios.post(`${this.config.ollamaUrl}/api/generate`, {
                model: this.config.modelName,
                prompt: prompt,
                stream: false,
                options: {
                    temperature: this.config.temperature,
                    num_predict: this.config.maxTokens
                }
            }, {
                timeout: 30000
            });

            if (response.data && response.data.response) {
                return response.data.response;
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            this.outputChannel.appendLine(`Error: ${error}`);
            throw error;
        }
    }

    private getContext(editor: vscode.TextEditor): string {
        const document = editor.document;
        const position = editor.selection.active;
        const startLine = Math.max(0, position.line - this.config.contextLines);
        const endLine = Math.min(document.lineCount - 1, position.line + this.config.contextLines);
        
        const contextRange = new vscode.Range(startLine, 0, endLine, document.lineAt(endLine).text.length);
        const context = document.getText(contextRange);
        
        return `File: ${document.fileName}\nLanguage: ${document.languageId}\n\nContext:\n${context}`;
    }

    async generateCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const prompt = await vscode.window.showInputBox({
            prompt: 'What code would you like to generate?',
            placeHolder: 'e.g., Create a function to validate email addresses'
        });

        if (!prompt) return;

        const context = this.getContext(editor);
        const fullPrompt = `${context}\n\nRequest: ${prompt}\n\nGenerate the requested code:`;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Generating code with Olympus Coder...',
                cancellable: false
            }, async () => {
                const response = await this.callOlympusCoder(fullPrompt);
                
                // Insert the generated code at cursor position
                await editor.edit(editBuilder => {
                    editBuilder.insert(editor.selection.active, response);
                });

                if (this.config.autoSave) {
                    await editor.document.save();
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate code: ${error}`);
        }
    }

    async debugCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const context = this.getContext(editor);
        const diagnostics = vscode.languages.getDiagnostics(editor.document.uri);
        
        let errorInfo = '';
        if (diagnostics.length > 0) {
            errorInfo = '\n\nErrors found:\n' + diagnostics.map(d => 
                `Line ${d.range.start.line + 1}: ${d.message}`
            ).join('\n');
        }

        const fullPrompt = `${context}${errorInfo}\n\nAnalyze this code for errors and provide fixes:`;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Debugging code with Olympus Coder...',
                cancellable: false
            }, async () => {
                const response = await this.callOlympusCoder(fullPrompt);
                
                // Show debug results in a new document
                const doc = await vscode.workspace.openTextDocument({
                    content: response,
                    language: 'markdown'
                });
                await vscode.window.showTextDocument(doc);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to debug code: ${error}`);
        }
    }

    async explainCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showErrorMessage('Please select code to explain');
            return;
        }

        const selectedCode = editor.document.getText(selection);
        const context = this.getContext(editor);
        const fullPrompt = `${context}\n\nSelected code:\n${selectedCode}\n\nExplain what this code does:`;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Explaining code with Olympus Coder...',
                cancellable: false
            }, async () => {
                const response = await this.callOlympusCoder(fullPrompt);
                
                // Show explanation in a new document
                const doc = await vscode.workspace.openTextDocument({
                    content: `# Code Explanation\n\n## Selected Code:\n\`\`\`${editor.document.languageId}\n${selectedCode}\n\`\`\`\n\n## Explanation:\n${response}`,
                    language: 'markdown'
                });
                await vscode.window.showTextDocument(doc);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to explain code: ${error}`);
        }
    }

    async refactorCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const selection = editor.selection;
        if (selection.isEmpty) {
            vscode.window.showErrorMessage('Please select code to refactor');
            return;
        }

        const selectedCode = editor.document.getText(selection);
        const context = this.getContext(editor);
        const fullPrompt = `${context}\n\nSelected code to refactor:\n${selectedCode}\n\nRefactor this code to improve readability, performance, and maintainability:`;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Refactoring code with Olympus Coder...',
                cancellable: false
            }, async () => {
                const response = await this.callOlympusCoder(fullPrompt);
                
                // Replace selected code with refactored version
                await editor.edit(editBuilder => {
                    editBuilder.replace(selection, response);
                });

                if (this.config.autoSave) {
                    await editor.document.save();
                }
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to refactor code: ${error}`);
        }
    }

    async generateTests() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        const context = this.getContext(editor);
        const fullPrompt = `${context}\n\nGenerate comprehensive unit tests for this code:`;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Generating tests with Olympus Coder...',
                cancellable: false
            }, async () => {
                const response = await this.callOlympusCoder(fullPrompt);
                
                // Create a new test file
                const fileName = editor.document.fileName;
                const testFileName = fileName.replace(/\.(py|js|ts)$/, '.test.$1');
                
                const doc = await vscode.workspace.openTextDocument({
                    content: response,
                    language: editor.document.languageId
                });
                await vscode.window.showTextDocument(doc);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate tests: ${error}`);
        }
    }

    async chatWithAI() {
        const prompt = await vscode.window.showInputBox({
            prompt: 'Ask Olympus Coder anything about your code',
            placeHolder: 'e.g., How can I optimize this function?'
        });

        if (!prompt) return;

        const editor = vscode.window.activeTextEditor;
        let context = '';
        if (editor) {
            context = this.getContext(editor);
        }

        const fullPrompt = context ? `${context}\n\nQuestion: ${prompt}` : prompt;

        try {
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Chatting with Olympus Coder...',
                cancellable: false
            }, async () => {
                const response = await this.callOlympusCoder(fullPrompt);
                
                // Show response in a new document
                const doc = await vscode.workspace.openTextDocument({
                    content: `# Chat with Olympus Coder\n\n**You:** ${prompt}\n\n**Olympus Coder:** ${response}`,
                    language: 'markdown'
                });
                await vscode.window.showTextDocument(doc);
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to chat with AI: ${error}`);
        }
    }
}

export function activate(context: vscode.ExtensionContext) {
    const provider = new OlympusCoderProvider();

    // Register commands
    const commands = [
        vscode.commands.registerCommand('olympusCoder.generateCode', () => provider.generateCode()),
        vscode.commands.registerCommand('olympusCoder.debugCode', () => provider.debugCode()),
        vscode.commands.registerCommand('olympusCoder.explainCode', () => provider.explainCode()),
        vscode.commands.registerCommand('olympusCoder.refactorCode', () => provider.refactorCode()),
        vscode.commands.registerCommand('olympusCoder.generateTests', () => provider.generateTests()),
        vscode.commands.registerCommand('olympusCoder.chatWithAI', () => provider.chatWithAI())
    ];

    commands.forEach(command => context.subscriptions.push(command));

    // Update config when settings change
    vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('olympusCoder')) {
            provider['updateConfig']();
        }
    });

    vscode.window.showInformationMessage('Olympus Coder extension activated!');
}

export function deactivate() {}