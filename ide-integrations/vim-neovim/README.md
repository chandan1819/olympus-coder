# Vim/Neovim Integration for Olympus-Coder

Integration plugins and configurations for Vim and Neovim editors.

## 🚀 Setup Methods

### Method 1: Vim Plugin (Recommended)

1. **Install using vim-plug**
   ```vim
   " Add to your .vimrc or init.vim
   Plug 'local-path-to/olympus-coder-v1/ide-integrations/vim-neovim/plugin'
   ```

2. **Install using Packer (Neovim)**
   ```lua
   -- Add to your plugins.lua
   use {
     'local-path-to/olympus-coder-v1/ide-integrations/vim-neovim/plugin',
     config = function()
       require('olympus-coder').setup({
         ollama_url = 'http://localhost:11434',
         model_name = 'olympus-coder-v1:latest',
         temperature = 0.1
       })
     end
   }
   ```

### Method 2: Direct Configuration

1. **Copy configuration files**
   ```bash
   cp olympus-coder.vim ~/.vim/plugin/
   cp olympus-coder.lua ~/.config/nvim/lua/
   ```

2. **Add to your config**
   ```vim
   " Vim (.vimrc)
   source ~/.vim/plugin/olympus-coder.vim
   ```
   
   ```lua
   -- Neovim (init.lua)
   require('olympus-coder')
   ```

## ⌨️ Default Key Mappings

- `<leader>og` - Generate code
- `<leader>od` - Debug code
- `<leader>oe` - Explain selection
- `<leader>or` - Refactor selection
- `<leader>ot` - Generate tests
- `<leader>oc` - Chat with AI

## 🔧 Configuration

### Vim Configuration (.vimrc)
```vim
" Olympus Coder settings
let g:olympus_coder_url = 'http://localhost:11434'
let g:olympus_coder_model = 'olympus-coder-v1:latest'
let g:olympus_coder_temperature = 0.1
let g:olympus_coder_max_tokens = 2048

" Custom key mappings
nnoremap <leader>og :OlympusGenerate<CR>
nnoremap <leader>od :OlympusDebug<CR>
vnoremap <leader>oe :OlympusExplain<CR>
vnoremap <leader>or :OlympusRefactor<CR>
nnoremap <leader>ot :OlympusTest<CR>
```

### Neovim Configuration (init.lua)
```lua
require('olympus-coder').setup({
  ollama_url = 'http://localhost:11434',
  model_name = 'olympus-coder-v1:latest',
  temperature = 0.1,
  max_tokens = 2048,
  auto_save = true,
  show_progress = true,
  
  -- Custom key mappings
  mappings = {
    generate = '<leader>og',
    debug = '<leader>od',
    explain = '<leader>oe',
    refactor = '<leader>or',
    test = '<leader>ot',
    chat = '<leader>oc'
  }
})
```

## 📁 Files Included

- `plugin/olympus-coder.vim` - Vim plugin
- `lua/olympus-coder.lua` - Neovim Lua plugin
- `autoload/olympus.vim` - Vim autoload functions
- `doc/olympus-coder.txt` - Documentation
- `ftplugin/` - Filetype-specific configurations

## 🎯 Commands

### Vim Commands
```vim
:OlympusGenerate [prompt]    " Generate code
:OlympusDebug               " Debug current buffer
:OlympusExplain             " Explain visual selection
:OlympusRefactor            " Refactor visual selection
:OlympusTest                " Generate tests
:OlympusChat [message]      " Chat with AI
:OlympusHealth              " Check connection
```

### Neovim Lua API
```lua
require('olympus-coder').generate_code("Create a function to sort array")
require('olympus-coder').debug_buffer()
require('olympus-coder').explain_selection()
require('olympus-coder').refactor_selection()
require('olympus-coder').generate_tests()
require('olympus-coder').chat("How to optimize this code?")
```

## 🔧 Advanced Features

### Context-Aware Generation
- Automatically includes file context
- Respects current filetype
- Maintains cursor position

### Async Operations (Neovim)
- Non-blocking API calls
- Progress indicators
- Background processing

### Integration with LSP
- Works alongside language servers
- Complements existing diagnostics
- Enhances code completion

## 🛠️ Customization

### Custom Prompts
```vim
" Add custom prompt templates
let g:olympus_coder_prompts = {
  \ 'docstring': 'Add comprehensive docstring to this function',
  \ 'optimize': 'Optimize this code for better performance',
  \ 'secure': 'Review this code for security vulnerabilities'
  \ }

" Use custom prompts
:OlympusGenerate docstring
```

### Filetype-Specific Settings
```lua
-- Neovim filetype configuration
require('olympus-coder').setup({
  filetype_settings = {
    python = {
      temperature = 0.05,
      include_imports = true,
      style_guide = 'PEP 8'
    },
    javascript = {
      temperature = 0.1,
      use_modern_syntax = true,
      include_jsdoc = true
    }
  }
})
```

## 🔧 Troubleshooting

### Common Issues

1. **Plugin not loading**
   ```vim
   " Check if plugin is loaded
   :echo exists('g:loaded_olympus_coder')
   
   " Reload plugin
   :source ~/.vim/plugin/olympus-coder.vim
   ```

2. **Connection errors**
   ```vim
   " Test connection
   :OlympusHealth
   
   " Check settings
   :echo g:olympus_coder_url
   ```

3. **Slow responses**
   - Reduce `max_tokens` setting
   - Use lightweight model configuration
   - Check system resources

### Debug Mode
```vim
" Enable debug logging
let g:olympus_coder_debug = 1

" View debug messages
:messages
```

## 📚 Examples

### Generate Function
1. Position cursor where you want the function
2. Press `<leader>og`
3. Enter prompt: "Create a function to validate email"
4. Code is inserted at cursor position

### Debug Code
1. Open file with errors
2. Press `<leader>od`
3. Review analysis in new buffer
4. Apply suggested fixes

### Explain Selection
1. Visually select complex code
2. Press `<leader>oe`
3. Read explanation in new buffer

## 🎨 Themes and UI

### Status Line Integration
```vim
" Add Olympus Coder status to statusline
set statusline+=%{OlympusStatus()}
```

### Popup Windows (Neovim)
```lua
-- Configure popup appearance
require('olympus-coder').setup({
  ui = {
    popup = {
      border = 'rounded',
      winblend = 10,
      title = 'Olympus Coder'
    }
  }
})
```