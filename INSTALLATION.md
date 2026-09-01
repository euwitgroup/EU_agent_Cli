# MyAgent Installation Guide

## 📦 Quick Install

### For Users (Download and Run)

#### Prerequisites
- Python 3.12 or higher
- pip (comes with Python)
- Git (optional, for cloning)

#### Option 1: Clone from GitHub (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/euwitgroup/EU_agent_Cli.git
cd myagent

# 2. Install MyAgent globally
pip install -e .

# 3. Configure your AI provider
myagent provider add --provider anthropic
# OR
myagent provider add --provider openai
# OR for custom provider
myagent provider add --provider custom --base-url YOUR_URL

# 4. Start MyAgent (from any directory!)
myagent main
```

✨ **After installation, you can run `myagent` from ANY directory in your terminal!**

#### Option 2: Download ZIP

1. Download the ZIP file from GitHub
2. Extract to a folder
3. Open terminal/PowerShell in that folder
4. Run:

```bash
# Install globally
pip install -e .

# Configure provider
myagent provider add --provider anthropic

# Run from anywhere
myagent main
```

#### Option 3: Install from PyPI (when published)

```bash
# Install globally
pip install myagent

# Configure
myagent provider add --provider anthropic

# Run
myagent main
```

---

## 🎯 Step-by-Step Installation (Windows)

### 1. Install Python

Download from [python.org](https://www.python.org/downloads/) (version 3.12+)

Check installation:
```powershell
python --version
# Should show: Python 3.12.x or higher
```

### 2. Download MyAgent

**Option A: Using Git**
```powershell
git clone https://github.com/YOUR_USERNAME/myagent.git
cd myagent
```

**Option B: Download ZIP**
1. Go to: `https://github.com/YOUR_USERNAME/myagent`
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open PowerShell in the extracted folder (Shift + Right-click → "Open PowerShell window here")

### 3. Install MyAgent Globally

```powershell
# This makes 'myagent' command available everywhere
pip install -e .

```powershell
# This makes 'myagent' command available everywhere
pip install -e .
```

**What this does:**
- ✅ Installs all dependencies automatically (typer, rich, openai, anthropic, etc.)
- ✅ Creates `myagent` command that works from ANY directory
- ✅ Editable mode - changes to code are immediately available

**Verify installation:**
```powershell
myagent --version
# Should show: MyAgent 0.1.0
```

### 4. Configure API Provider

Choose one of the following:

**For Anthropic (Claude):**
```powershell
myagent provider add --provider anthropic
# Enter your API key when prompted
# Enter model: claude-3-5-sonnet-20241022
```

**For OpenAI:**
```powershell
myagent provider add --provider openai
# Enter your API key when prompted
# Enter model: gpt-4
```

**For Custom Provider:**
```powershell
myagent provider add --provider custom --base-url https://api.your-provider.com/v1
# Enter your API key when prompted
# Enter your model name
```

### 5. Test Installation

```powershell
# Test provider connection
myagent provider test

# List available models
myagent provider models

# Run interactive mode (from ANY directory!)
cd C:\your\project
myagent main
```

✨ **That's it! Now you can use `myagent` from anywhere in your terminal!**

---

## 🐧 Step-by-Step Installation (Linux/Mac)

### 1. Install Python 3.12+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3-pip git
```

**Mac (using Homebrew):**
```bash
brew install python@3.12 git
```

### 2. Download MyAgent

```bash
git clone https://github.com/YOUR_USERNAME/myagent.git
cd myagent
```

### 3. Install MyAgent Globally

```bash
# Option 1: Install globally (recommended)
pip install -e .

# Option 2: Use virtual environment (isolated)
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Verify:**
```bash
myagent --version
```

### 4. Configure Provider

```bash
myagent provider add --provider anthropic
# Enter your API key and model
```

### 5. Run MyAgent

```bash
# From any directory!
cd ~/your/project
myagent main
```

**For Windows PowerShell:** If you don't see any output, set UTF-8 encoding first:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
myagent main
```

---

## 🔧 Manual Configuration (Alternative)

If you prefer to configure manually without the interactive setup:

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` file with your API key:
```env
MYAGENT_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-actual-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

3. Run MyAgent:
```bash
myagent main
```

---

## 🚀 Usage

### Interactive Mode (Recommended)
```bash
# Start from any directory - your project or anywhere!
cd /path/to/your/project
myagent main
```

### Single Task Execution
```bash
myagent main "create a hello world script in Python"
```

### Provider Management Commands
```bash
# List all configured providers
myagent provider list

# Switch to different provider
myagent provider switch anthropic

# Test provider connection
myagent provider test

# List available models from provider
myagent provider models

# Add a new provider
myagent provider add --provider openai
```

### Get Help
```bash
# Show all commands
myagent --help

# Show specific command help
myagent provider --help
myagent main --help
```

---

## 💡 Tips

### Run from Anywhere

After installation with `pip install -e .`, the `myagent` command is globally available:

```bash
# Works from your home directory
cd ~
myagent main

# Works from any project
cd /path/to/my-project
myagent main

# Works from Downloads folder
cd ~/Downloads
myagent main
```

Each project gets its own conversation history in `.myagent/history/`!

### Quick Commands Inside REPL

Once inside `myagent main`, use these slash commands:
- `/help` - Show all commands
- `/config` - Edit provider settings
- `/history` - View conversation
- `/sessions` - List saved sessions
- `/exit` - Quit

### Upgrade MyAgent

```bash
cd /path/to/myagent
git pull origin main
pip install -e .
```

---

## 🔍 Troubleshooting

### "myagent: command not found"

Use `python -m myagent` instead:
```bash
python -m myagent main
```

### "No module named 'myagent'"

Make sure you installed it:
```bash
pip install -e .
```

### "API key not found"

Configure your provider:
```bash
python -m myagent provider add --provider anthropic
```

### Rate Limit Errors

MyAgent automatically retries with exponential backoff. You can adjust retry settings in `.env`:
```env
MYAGENT_MAX_RETRIES=5
MYAGENT_INITIAL_RETRY_DELAY=2.0
MYAGENT_MAX_RETRY_DELAY=120.0
```

### Import Errors

Reinstall dependencies:
```bash
pip install -e . --force-reinstall
```

---

## 📝 Next Steps

1. ✅ Install MyAgent
2. ✅ Configure your AI provider
3. ✅ Test the connection
4. ✅ Run your first task
5. 📖 Read the [README.md](README.md) for more features
6. 🧪 Check [TESTING.md](TESTING.md) for running tests

---

## 🆘 Getting Help

- 📖 Documentation: [README.md](README.md)
- 🐛 Issues: https://github.com/YOUR_USERNAME/myagent/issues
- 💬 Discussions: https://github.com/YOUR_USERNAME/myagent/discussions

---

## 🎉 You're Ready!

Run this to get started:
```bash
python -m myagent main
```

Enjoy coding with your AI agent! 🚀
