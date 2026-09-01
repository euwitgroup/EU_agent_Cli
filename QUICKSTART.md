# MyAgent Quick Start Guide

## 🚀 3-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/myagent.git
cd myagent

# 2. Install globally (makes 'myagent' command available everywhere)
pip install -e .

# 3. Configure provider
myagent provider add --provider anthropic
# OR: myagent provider add --provider openai
```

✨ **After step 2, you can run `myagent` from ANY directory!**

## ⚡ Quick Commands

```bash
# Run interactive mode (from any directory!)
myagent main                    # Starts interactive REPL

# Execute a single task
myagent main "create a hello world script"

# Provider management
myagent provider list        # Show all providers
myagent provider test        # Test connection
myagent provider switch X    # Switch provider
myagent provider models      # List available models

# Get help
myagent --help              # Show all commands
myagent main --help         # Show main command options
```

## 🎯 Common Tasks

### Interactive Mode Commands

Once in interactive mode (`myagent main`):

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/status` | Show session info |
| `/config` | Edit provider settings and API keys |
| `/history` | Show conversation history |
| `/sessions` | List saved sessions |
| `/clear` | Clear chat history |
| `/exit` | Quit REPL |
| `/reset` | Reset session |
| `/model` | Change model |
| `/provider` | Switch provider |
| `/tools` | List available tools |

### Example Tasks

```bash
# File operations
myagent main "create a Python calculator"
myagent main "add type hints to utils.py"
myagent main "write unit tests for my functions"

# Code analysis
myagent main "explain what this project does"
myagent main "find all TODO comments"
myagent main "check for code smells"

# Git operations  
myagent main "show git status"
myagent main "create a commit message for my changes"

# Testing
myagent main "run the test suite"
myagent main "fix failing tests"
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Provider (choose one)
MYAGENT_PROVIDER=anthropic

# API Keys
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
CUSTOM_API_KEY=your-key-here

# Models
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4
CUSTOM_MODEL=your-model

# Custom Provider
CUSTOM_BASE_URL=https://api.your-provider.com/v1

# Agent Settings
MYAGENT_MAX_ITERATIONS=50
MYAGENT_COMMAND_TIMEOUT=120

# Rate Limiting
MYAGENT_MAX_RETRIES=3
MYAGENT_INITIAL_RETRY_DELAY=1.0
MYAGENT_MAX_RETRY_DELAY=60.0
```

## 💡 Pro Tips

### Run from Anywhere
```bash
# After installation, myagent works from any directory!
cd ~/Documents/my-project
myagent main

cd ~/Downloads/another-project
myagent main
```

### Continue Previous Work
```bash
myagent main
# On startup: "Continue previous session? (y/n)"
# Type 'y' to restore your conversation history!
```

### Quick Provider Switch
```bash
# Inside interactive mode
> /config
# Choose option 1 to change provider
```

## 🆘 Troubleshooting

### Problem: "myagent: command not found"
**Solution:** 
1. Reinstall: `pip install -e .` in the myagent directory
2. Check PATH: Make sure Python scripts directory is in PATH
3. Alternative: Use `python -m myagent` instead

### Problem: "No API key found"
**Solution:** Run `myagent provider add --provider anthropic`

### Problem: "Rate limit exceeded"
**Solution:** MyAgent retries automatically. Wait a bit or increase retry settings in `.env`

### Problem: Import errors
**Solution:** 
```bash
pip install -e . --force-reinstall
```

## 📚 More Information

- **Full Documentation:** [README.md](README.md)
- **Installation Guide:** [INSTALLATION.md](INSTALLATION.md)
- **Testing:** [TESTING.md](TESTING.md)
- **GitHub:** https://github.com/YOUR_USERNAME/myagent

## 💡 Tips

1. **Use Tab completion** - Type `/` and press Tab to see commands
2. **Arrow keys** - Use ↑ ↓ to navigate command history
3. **Ctrl+C** - Interrupt current task (doesn't exit)
4. **Ctrl+D** - Exit interactive mode
5. **Test first** - Run `python -m myagent provider test` before starting

## 🎉 You're Ready!

Start coding with AI:
```bash
python -m myagent main
```

Happy coding! 🚀
