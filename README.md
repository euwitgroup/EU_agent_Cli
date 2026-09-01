# MyAgent

**AI-powered coding agent for terminal**

MyAgent is a production-ready CLI tool that brings AI assistance directly to your terminal. It can understand your project, read and modify files, run commands, execute tests, and help you build and debug software autonomously.

[![Tests](https://img.shields.io/badge/tests-128%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## ✨ Features

### 💾 Conversation History (NEW!) 🌟
- 📝 **Auto-save Sessions** - Every interaction saved automatically
- 🔄 **Continue from Where You Left Off** - Restore previous conversations on restart
- 📜 **History Browser** - View past messages with `/history` command
- 🗂️ **Session Management** - List and manage saved sessions with `/sessions`
- 💬 **Full Context Preservation** - Never lose your work progress
- 🔐 **Privacy First** - History stored locally, git-ignored by default

### 🎨 Enhanced CLI Interface
- ✨ **Beautiful ASCII Logo** - "MY AGENT" with modern UI
- 🎮 **Auto-complete** - Tab completion for all slash commands
- � **Command History** - Arrow key navigation through past commands
- 📊 **Session Info Panel** - Combined logo + status in single box
- ⚡ **Real-time Feedback** - Live progress and status updates
- 🎯 **Quick Commands Menu** - Easy access to all features

### 🤖 Core Features
- 🤖 **Autonomous Coding Agent** - Not just a chatbot, executes real coding tasks end-to-end
- 🔧 **File Operations** - Read, write, and edit files with precision
- 🔍 **Code Search** - Find relevant code across your project using regex or ripgrep
- ⚡ **Command Execution** - Run tests, build commands, and git operations
- 🧪 **Test Runner** - Automatic test framework detection (pytest, jest, mocha, etc.)
- 🔀 **Git Integration** - Status, diff, log, commit, and branch operations
- 🔒 **Permission System** - Safe operations with configurable policies
- 🔌 **Multi-Provider** - Support for OpenAI, Anthropic, and custom endpoints
- ⚙️ **Provider Management** - CLI commands to add, test, and configure providers
- 🧭 **Model Discovery** - List available models from any provider
- 💬 **Interactive REPL** - Chat with the agent or execute single tasks
- 🛡️ **Security First** - Workspace isolation, dangerous command detection, path traversal protection

## 📖 Documentation

- 🚀 **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 3 steps
- 📦 **[Installation Guide](INSTALLATION.md)** - Detailed installation instructions
- 💾 **[Conversation History Guide](CONVERSATION_HISTORY_GUIDE.md)** - Session management and history
- ⚙️ **[Config Command Guide](NEW_FEATURE_CONFIG_COMMAND.md)** - In-session provider configuration
- 🧪 **[Testing Guide](TESTING.md)** - How to run and write tests
- 🐙 **[GitHub Upload Guide](GITHUB_UPLOAD_GUIDE.md)** - For project maintainers

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- An API key for your chosen provider (OpenAI, Anthropic, or custom)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/myagent.git
cd myagent

# Install MyAgent globally (makes 'myagent' command available everywhere)
pip install -e .

# Verify installation
myagent --version
```

**✨ After installation, run `myagent` from ANY directory in your terminal!**

### Configuration

**Option 1: Interactive Setup (Recommended)**

Use the interactive provider setup:

```bash
# Add your provider with interactive prompts
myagent provider add --provider anthropic

# Or for a custom provider
myagent provider add --provider custom --base-url https://api.example.com/v1
```

**Option 2: Manual Setup**

1. **Create a `.env` file**:

```bash
cp .env.example .env
```

2. **Add your API key** (choose one provider):

```env
# For Anthropic (Claude) - Recommended
MYAGENT_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Or for OpenAI
MYAGENT_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Or for a custom OpenAI-compatible provider
MYAGENT_PROVIDER=custom
CUSTOM_API_KEY=your-api-key-here
CUSTOM_BASE_URL=https://your-provider.com/v1
CUSTOM_MODEL=your-model-name
```

3. **Test your configuration**:

```bash
myagent provider test
```

### First Run

**Interactive Mode (Recommended):**

```bash
# Start from any directory!
cd /path/to/your/project
myagent main

# Note: 'myagent' command is globally available after installation
```

You'll see the beautiful MyAgent interface with ASCII logo:

```
   ███╗   ███╗██╗   ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗
   ████╗ ████║╚██╗ ██╔╝    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
   ██╔████╔██║ ╚████╔╝     ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
   ██║╚██╔╝██║  ╚██╔╝      ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
   ██║ ╚═╝ ██║   ██║       ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
   ╚═╝     ╚═╝   ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
   
              🤖 AI-Powered Autonomous Coding Agent

────────────────────────────────────────────────────────────────────

Session Info
  📁 Project:   your-project
  🔌 Provider:  anthropic
  🤖 Model:     claude-3-5-sonnet-20241022
  ⚡ Status:    Ready

Quick Commands (Use arrow keys or type command)
💬 /help      Show all commands    📊 /status    Session info
🧹 /clear     Clear history        � /exit      Quit REPL

✨ Ready to assist! What would you like to build?

❯ 
```

**Single Task Mode:**

```bash
# Clean, direct execution
myagent "create a hello world Python script"
```

Output:
```
Task: create a hello world Python script

  → Creating hello.py

Response
────────────────────────────────────────
I've created hello.py with a simple...
────────────────────────────────────────

  ✓ Created 1 file(s)
  Completed in 1.2s
```

**Verbose Mode (for debugging):**

```bash
myagent --verbose "your task"
```

## 📖 Usage

### Interactive Mode (Menu-Driven)

Start the enhanced interactive session:

```bash
myagent
```

**Main Menu Options:**

1. **💬 Chat with Agent** - Have a conversation
2. **📋 Execute Task** - Opens editor for detailed tasks
3. **📊 View Status** - See session statistics
4. **🔧 Configure Settings** - Change provider/model
5. **📁 File Operations** - View, edit, search files
6. **🔄 Git Operations** - Git status, diff, commit
7. **❓ Help** - Get help
8. **🚪 Exit** - Quit

**Navigation:**
- Use **↑/↓** arrow keys to navigate
- Press **Enter** to select
- Press **Ctrl+C** to cancel
- **Mouse clicks** work in some terminals

### Chat Mode Example

Select "💬 Chat with Agent" from menu:

```
You: "Add authentication to the API"
Agent: "I'll add JWT-based authentication. Here's my plan..."

You: "Also add rate limiting"
Agent: "I'll implement that as well..."
```

Type "back" to return to main menu.

### Execute Task Example

Select "📋 Execute Task" - an editor opens where you can write:

```
Add comprehensive unit tests for the authentication module including:
- Login validation
- Token generation
- Password hashing
- Session management
```

The agent executes everything and shows clean output:

```
Task: Add comprehensive unit tests...

  → Reading auth.py
  → Creating tests/test_auth.py
  → Running pytest

Response: I've created comprehensive tests...

  ✓ Created 1 file(s)
  ✓ Ran 1 command(s)
  Completed in 4.3s
```

### Single Task Mode (Command Line)

Execute tasks directly without opening the menu:

```bash
# Quick, one-off tasks
myagent "fix the login bug"
myagent "add unit tests for database.py"
myagent "refactor the API endpoints"
```

**Clean output without logs:**

```
Task: fix the login bug

  → Reading login.py
  → Editing login.py
  → Running tests

Response: Fixed the bug by correcting token validation...

  ✓ Modified 1 file(s)
  ✓ Ran 1 command(s)
  Completed in 2.1s
```

### Old Interactive Mode (Still Available)

For those who prefer the command-based interface:

```bash
myagent
```

Example session:

```
╭────────────────────────────────────────────╮
│                  MyAgent                   │
│              AI Coding Agent               │
╰────────────────────────────────────────────╯

Project: my-project
Provider: Anthropic
Model: Claude

> Fix the authentication bug in auth.py
→ run_command("pytest tests/test_auth.py")
✓ 18 passed

╭─ Completed ─────────────────────────────────╮
│ Fixed authentication validation issue.      │
│                                             │
│ Changed:                                    │
│ • app/auth.py                               │
│                                             │
│ Tests: 18 passed                            │
╰─────────────────────────────────────────────╯

>
```

### Single Task Mode

Execute a specific task and exit:

```bash
myagent "add unit tests for the payment module"
myagent "refactor the database connection code"
myagent "fix all linting errors"
```

### CLI Options

```bash
myagent --help                          # Show help
myagent --version                       # Show version
myagent --provider openai               # Use specific provider
myagent --model gpt-4-turbo-preview     # Use specific model
myagent --cwd /path/to/project          # Set working directory
myagent --verbose                       # Enable verbose logging
myagent --no-color                      # Disable colored output
```

## 🎮 Interactive Commands

When in interactive mode, use these slash commands:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/status` | Show current session status |
| `/config` | Edit provider settings and API keys (in session) |
| `/history` | Show conversation history summary |
| `/sessions` | List and manage saved sessions |
| `/clear` | Clear conversation history |
| `/reset` | Reset agent session |
| `/model [name]` | Show or change model |
| `/provider [name]` | Show or change provider |
| `/context` | Show current context size |
| `/tools` | List available tools |
| `/diff` | Show git diff of changes |
| `/exit`, `/quit` | Exit the REPL |

**Keyboard shortcuts:**
- `Ctrl+C` - Interrupt current task
- `Ctrl+D` - Exit REPL
- `↑` / `↓` - Navigate command history

## 🔧 Configuration

### Provider Management Commands

MyAgent includes dedicated commands for managing AI provider configurations:

#### Add a New Provider

Interactive setup for a provider with connection testing:

```bash
# Add custom provider (will prompt for API key and model)
myagent provider add --provider custom --base-url https://api.your-provider.com/v1

# Add OpenAI provider
myagent provider add --provider openai

# Add Anthropic provider  
myagent provider add --provider anthropic
```

The `add` command will:
1. Prompt for your API key (hidden input)
2. Prompt for the model name
3. Test the connection
4. Save configuration to `.env` file (if `--save` is used, default: true)

#### Test Provider Connection

Verify your provider configuration works:

```bash
# Test current provider
myagent provider test

# Test specific provider
myagent provider test --provider openai
```

#### List Available Models

Fetch available models from your provider:

```bash
# List models from current provider
myagent provider models

# List models from specific provider
myagent provider models --provider openai
```

Note: Anthropic doesn't provide a models API, so it shows known models.

#### List All Providers

See which providers are configured:

```bash
myagent provider list
```

This shows:
- All available providers (openai, anthropic, custom)
- Configuration status for each
- Current active provider

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MYAGENT_PROVIDER` | `anthropic` | Provider: `openai`, `anthropic`, or `custom` |
| `MYAGENT_MAX_ITERATIONS` | `50` | Maximum agent loop iterations |
| `MYAGENT_COMMAND_TIMEOUT` | `120` | Command timeout in seconds |
| `MYAGENT_AUTO_APPROVE_READS` | `true` | Auto-approve read operations |
| `MYAGENT_LOG_LEVEL` | `INFO` | Logging level |

### Provider-Specific Configuration

**OpenAI:**
```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

**Anthropic:**
```env
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Custom (OpenAI-compatible):**
```env
CUSTOM_API_KEY=your-key
CUSTOM_BASE_URL=https://your-api.com/v1
CUSTOM_MODEL=your-model
```

### Configuration Precedence

1. CLI arguments (highest priority)
2. Environment variables
3. `.env` file
4. Default values (lowest priority)

## 🎨 New Enhanced UI

MyAgent now features a completely redesigned CLI interface with:

### Key Improvements

- **90% Less Visual Noise** - No raw logs, only relevant information
- **Interactive Menus** - Navigate with arrow keys and mouse
- **Flash Messages** - Clean success/error/warning indicators  
- **Organized Navigation** - Menu-driven interface with 8 main options
- **Real-time Feedback** - Thinking indicators and progress updates

### Usage Modes

**1. Interactive Menu Mode (Default)**
```bash
myagent
```
Displays a beautiful menu with icons and organized options.

**2. Single Task Mode**
```bash
myagent "your task description"
```
Clean output showing only what matters.

**3. Verbose Mode (Debugging)**
```bash
myagent --verbose "your task"
```
Shows detailed logs when you need them.

### Documentation

- 📖 **[Quick Start Guide](QUICK_START.md)** - Get started in minutes
- 📚 **[Complete Usage Guide](USAGE_GUIDE.md)** - All features explained
- 🎨 **[Visual Comparison](VISUAL_COMPARISON.md)** - Before/after examples
- 📋 **[Enhancement Summary](ENHANCEMENT_SUMMARY.md)** - Technical details
- ✨ **[UI Enhancements](UI_ENHANCEMENTS.md)** - Feature documentation

## 🛠️ Available Tools

MyAgent has access to these tools:

### File Operations
- **read_file** - Read file contents (supports line ranges)
- **write_file** - Create or overwrite files
- **edit_file** - Make targeted edits by replacing text
- **list_files** - Browse directory structure (respects .gitignore)

### Search
- **search_files** - Search content with regex (uses ripgrep if available)
- **find_files** - Find files by name pattern (glob syntax)

### Execution
- **run_command** - Execute shell commands with timeout

### Git Integration
- **git_status** - Show current status
- **git_diff** - Show changes
- **git_log** - Show commit history
- **git_branch** - Show branches

## 🔒 Security

MyAgent implements multiple security layers:

### Workspace Isolation
All file operations are restricted to the project directory:
```python
# ✓ Allowed
read_file("src/main.py")

# ✗ Blocked (path traversal)
read_file("../../etc/passwd")
```

### Permission Policies

Configure permission policies per category:

| Category | Default | Options |
|----------|---------|---------|
| READ | `always` | `always`, `ask`, `never` |
| WRITE | `ask` | `always`, `ask`, `never` |
| DELETE | `ask` | `always`, `ask`, `never` |
| COMMAND | `ask` | `always`, `ask`, `never` |

### Dangerous Command Detection

Potentially destructive commands require explicit approval:
- `rm -rf`, `del /f`
- `git reset --hard`, `git clean`
- `DROP DATABASE`, `TRUNCATE`
- `shutdown`, `reboot`
- And more...

### Secret Protection

Sensitive files are excluded by default:
- `.env`, `.env.*`
- `*.pem`, `*.key`
- `credentials.json`
- Private keys

## 📊 Project Structure

```
myagent/
├── src/myagent/
│   ├── agent/          # Agent loop and state management
│   │   ├── context.py  # Context building and formatting
│   │   ├── loop.py     # Main agent execution loop
│   │   └── state.py    # Session state tracking
│   ├── providers/      # AI provider implementations
│   │   ├── base.py     # Abstract provider interface
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   └── custom.py
│   ├── tools/          # Tool implementations
│   │   ├── registry.py # Tool registration system
│   │   ├── filesystem.py
│   │   ├── search.py
│   │   ├── terminal.py
│   │   ├── git.py
│   │   └── tests.py
│   ├── permissions/    # Permission and safety system
│   │   └── manager.py
│   ├── ui/             # Terminal UI components
│   │   ├── console.py
│   │   ├── display.py
│   │   └── prompt.py   # Interactive REPL
│   ├── config/         # Configuration management
│   │   └── settings.py
│   └── cli.py          # CLI entry point
├── tests/              # Comprehensive test suite (116 tests)
│   ├── test_agent.py
│   ├── test_providers.py
│   ├── test_tools.py
│   ├── test_permissions.py
│   └── test_config.py
├── pyproject.toml      # Project configuration
├── README.md           # This file
└── TESTING.md          # Testing documentation
```

## 🧪 Testing

MyAgent has comprehensive test coverage with 116 passing tests.

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=myagent tests/

# Run specific test file
pytest tests/test_agent.py -v

# Run tests in watch mode
ptw tests/
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## 🐛 Troubleshooting

### "No API key found"

**Problem:** Missing or invalid API key.

**Solution:** 
1. Create a `.env` file in the project root
2. Add your API key: `ANTHROPIC_API_KEY=your-key-here`
3. Or set environment variable: `export ANTHROPIC_API_KEY=your-key-here`

### "Module not found"

**Problem:** Package not installed.

**Solution:**
```bash
pip install -e .
```

### "Permission denied"

**Problem:** File or command requires permission.

**Solution:** In interactive mode, the agent will ask for permission. You can configure policies in `.env`:
```env
MYAGENT_AUTO_APPROVE_READS=true
```

### "Command timed out"

**Problem:** Command took longer than timeout limit.

**Solution:** Increase timeout in `.env`:
```env
MYAGENT_COMMAND_TIMEOUT=300  # 5 minutes
```

### "Git not available"

**Problem:** Git is not installed or not in PATH.

**Solution:**
1. Install git: https://git-scm.com/downloads
2. Ensure it's in your PATH
3. Restart terminal

### Verbose Logging

Enable verbose logging for debugging:
```bash
myagent --verbose
```

Or set in `.env`:
```env
MYAGENT_LOG_LEVEL=DEBUG
```

## 💡 Examples

### Example 1: Fix a Bug

```bash
myagent "Find and fix the bug causing the login test to fail"
```

The agent will:
1. Search for login-related code
2. Read relevant files
3. Identify the issue
4. Make targeted edits
5. Run tests
6. Iterate until tests pass

### Example 2: Add a Feature

```bash
myagent "Add input validation to the user registration form"
```

The agent will:
1. Locate the registration form code
2. Understand the current implementation
3. Add appropriate validation
4. Update or create tests
5. Verify the implementation

### Example 3: Refactor Code

```bash
myagent "Refactor the database connection code to use connection pooling"
```

The agent will:
1. Find all database connection code
2. Plan the refactoring
3. Make necessary changes
4. Update related code
5. Ensure tests still pass

### Example 4: Write Tests

```bash
myagent "Write unit tests for the payment processing module"
```

The agent will:
1. Analyze the payment module
2. Identify test cases
3. Create comprehensive tests
4. Run the tests
5. Ensure good coverage

## 🤝 Development

### Setup Development Environment

```bash
# Clone and install with dev dependencies
git clone <repository-url>
cd myagent
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/

# Lint code
ruff check src/
```

### Architecture

MyAgent follows a modular architecture:

1. **CLI Layer** - User interface and command handling
2. **Agent Layer** - Core logic, iteration management, state tracking
3. **Provider Layer** - Abstract AI provider interface with multiple implementations
4. **Tool Layer** - Concrete tools for file operations, search, commands
5. **Permission Layer** - Safety system for dangerous operations
6. **UI Layer** - Rich terminal output and interactive prompts

### Adding New Tools

1. Implement tool in appropriate module (`tools/`)
2. Register tool in `tools/__init__.py`
3. Add permission category
4. Write tests
5. Update documentation

### Adding New Providers

1. Inherit from `AIProvider` base class
2. Implement required methods
3. Add to `ProviderRouter`
4. Write tests
5. Document configuration

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) - Interactive prompts
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [OpenAI Python](https://github.com/openai/openai-python) - OpenAI API
- [Anthropic Python](https://github.com/anthropics/anthropic-sdk-python) - Anthropic API

## 🗺️ Roadmap

Future enhancements:
- [ ] Streaming responses in interactive mode
- [ ] Browser automation tools
- [ ] Web search integration
- [ ] MCP (Model Context Protocol) support
- [ ] Plugin system for custom tools
- [ ] Multi-agent orchestration
- [ ] Persistent memory across sessions
- [ ] IDE integrations (VS Code extension)
- [ ] GitHub integration (PR creation, issue management)
- [ ] Remote execution capabilities

## 📞 Support

- **Issues:** Open an issue on GitHub
- **Documentation:** See docs in the repository
- **Testing:** See [TESTING.md](TESTING.md)

---

**Status:** Production Ready ✅ | 128 Tests Passing ✅ | Fully Documented ✅
#   E U _ a g e n t _ C l i  
 