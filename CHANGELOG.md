# Changelog

All notable changes to MyAgent will be documented in this file.

## [1.0.0] - 2026-09-01

### Added
- **Complete MyAgent CLI implementation**
  - Multi-provider support (OpenAI, Anthropic, Custom)
  - Interactive REPL with enhanced UI
  - Autonomous agent loop with tool execution
  - Comprehensive permission system
  - **NEW: Conversation history persistence system** 🌟

- **Conversation History & Session Management** 🌟
  - Automatic session saving after each interaction
  - Smart session restore on startup (optional)
  - `/history` command to view conversation
  - `/sessions` command to list and manage saved sessions
  - History stored in `.myagent/history/` (git-ignored)
  - Session archiving and cleanup
  - Full context preservation across restarts

- **Provider Management**
  - CLI commands for provider configuration (`provider add/test/switch/models/list`)
  - Rate limit handling with exponential backoff
  - Automatic retry on rate limit errors
  - Custom provider support with configurable base URLs
  - **NEW: `/config` command for in-session provider editing**

- **Enhanced User Interface**
  - Beautiful ASCII art logo ("MY AGENT")
  - Combined logo + session info panel
  - Full-width layout with navigation menu
  - Auto-complete for slash commands using Tab
  - Command history with arrow key navigation

- **Interactive Commands**
  - `/help` - Show all commands
  - `/status` - Session status and statistics
  - `/config` - **NEW: Edit provider settings and API keys**
  - `/history` - **NEW: Show conversation history**
  - `/sessions` - **NEW: List and manage saved sessions**
  - `/clear` - Clear conversation history
  - `/reset` - Reset agent session
  - `/model` - Change AI model
  - `/provider` - Switch provider
  - `/context` - Show context size
  - `/tools` - List available tools
  - `/diff` - Show git changes
  - `/exit` - Quit REPL

- **Tools & Capabilities**
  - File operations (read, write, edit, delete, list)
  - Search functionality (grep, find files)
  - Git integration (status, diff, commit, push)
  - Command execution with timeout controls
  - Test runner integration

- **Testing**
  - Comprehensive test suite with 128 tests
  - Unit tests for all major components
  - Provider integration tests
  - Tool functionality tests
  - Mock providers for testing

- **Documentation**
  - Complete README with examples
  - INSTALLATION.md - User installation guide
  - QUICKSTART.md - Fast reference guide
  - GITHUB_UPLOAD_GUIDE.md - Maintainer guide
  - UPLOAD_CHECKLIST.md - Pre-upload checklist
  - TESTING.md - Testing documentation

### Features in Detail

#### `/config` Command (New in 1.0.0)
Interactive provider configuration from within the REPL session:

**Options:**
1. **Change provider and API key** - Switch to a different provider completely
2. **Change model only** - Update model while keeping current provider
3. **Update API key** - Replace API key for current provider
4. **Cancel** - Exit without changes

**Features:**
- Lists available providers (anthropic, openai, custom)
- Fetches available models from provider API
- Secure password input for API keys
- Updates .env file automatically
- Shows confirmation messages
- Warns to restart REPL for changes to take effect

**Usage:**
```
> /config

Provider Configuration

Current provider: custom
Current model: claude-opus-4-8

What would you like to configure?
  1. Change provider and API key
  2. Change model only
  3. Update API key for current provider
  4. Cancel

Enter choice (1-4):
```

#### Rate Limit Handling
Automatic retry with exponential backoff for 429 errors:
- Configurable max retries (default: 3)
- Initial delay: 1.0 seconds
- Max delay: 60.0 seconds
- Exponential backoff with jitter

Configuration in `.env`:
```env
MYAGENT_MAX_RETRIES=3
MYAGENT_INITIAL_RETRY_DELAY=1.0
MYAGENT_MAX_RETRY_DELAY=60.0
```

#### Auto-Complete
Press Tab after typing `/` to see all available commands:
- Intelligent command completion
- Case-insensitive matching
- Works with partial commands

### Configuration

Environment variables supported:
```env
# Provider Selection
MYAGENT_PROVIDER=anthropic|openai|custom

# API Keys
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
CUSTOM_API_KEY=your-key-here

# Models
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4
CUSTOM_MODEL=your-model-name

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

### Project Structure

```
EU_agent/
├── src/myagent/
│   ├── agent/           # Agent loop and state management
│   ├── config/          # Configuration and settings
│   ├── permissions/     # Permission management system
│   ├── providers/       # AI provider implementations
│   ├── tools/           # Tool implementations
│   └── ui/              # User interface components
├── tests/               # Test suite (128 tests)
├── .env.example         # Example configuration
├── pyproject.toml       # Project dependencies
├── README.md            # Main documentation
├── INSTALLATION.md      # Installation guide
├── QUICKSTART.md        # Quick reference
├── TESTING.md           # Testing guide
├── GITHUB_UPLOAD_GUIDE.md  # Upload instructions
└── UPLOAD_CHECKLIST.md  # Pre-upload checklist
```

### Dependencies

Core dependencies:
- typer - CLI framework
- rich - Terminal formatting
- prompt-toolkit - Interactive prompts
- pydantic - Data validation
- python-dotenv - Environment variables
- openai - OpenAI API client
- anthropic - Anthropic API client

Development dependencies:
- pytest - Testing framework
- pytest-asyncio - Async test support
- pytest-mock - Mocking support

### Known Issues

None at this time.

### Future Enhancements

Planned features:
- [ ] MCP (Model Context Protocol) support
- [ ] Plugin system for custom tools
- [ ] Multi-session support
- [ ] Enhanced diff viewer
- [ ] Code review mode
- [ ] Task templates
- [ ] Conversation export
- [ ] Usage analytics

### Breaking Changes

None - Initial release.

### Migration Guide

Not applicable - Initial release.

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with Claude (Anthropic)
- Inspired by various AI coding assistants
- Thanks to the open-source community

---

**Full Changelog**: https://github.com/YOUR_USERNAME/myagent/commits/main
