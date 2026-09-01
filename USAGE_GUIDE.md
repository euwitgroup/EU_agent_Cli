# MyAgent Enhanced CLI - Complete Usage Guide

## Installation & Setup

```bash
# Navigate to project directory
cd EU_agent

# Install with new dependencies
pip install -e .

# Verify installation
myagent --version
```

## Basic Usage

### 1. Start Interactive Mode

```bash
myagent
```

or

```bash
python -m myagent
```

You'll see the main menu with interactive options.

### 2. Execute Single Task

```bash
myagent "your task description here"
```

Example:
```bash
myagent "add unit tests for the authentication module"
```

### 3. Verbose Mode (Show Logs)

```bash
myagent --verbose "your task"
```

Use this when debugging or if you want to see detailed logs.

## Interactive Menu Navigation

### Main Menu Options

1. **💬 Chat with Agent**
   - Have a conversation with the AI
   - Ask questions, get explanations
   - Iterative problem-solving
   - Type "back" to return to menu

2. **📋 Execute Task**
   - Opens text editor for detailed task description
   - Best for complex, multi-step tasks
   - Agent executes and shows results

3. **📊 View Status**
   - See session statistics
   - Check iterations used
   - View files changed
   - See commands executed

4. **🔧 Configure Settings**
   - Change AI provider
   - Select different model
   - View current configuration

5. **📁 File Operations**
   - View files with syntax highlighting
   - Edit files via AI agent
   - Search across files
   - Show git changes

6. **🔄 Git Operations**
   - Check status
   - View diff
   - See commit log
   - Stage files
   - Create commits

7. **❓ Help**
   - Show help information
   - Feature descriptions
   - Tips and tricks

8. **🚪 Exit**
   - Quit the application

### Keyboard Shortcuts

- **Arrow Up/Down (↑/↓)**: Navigate menu items
- **Enter**: Select current item
- **Ctrl+C**: Cancel current operation, return to menu
- **Ctrl+D**: Exit application (in some contexts)
- **Mouse Click**: Select menu item (terminal dependent)

## Detailed Workflows

### Workflow 1: Quick Bug Fix

```bash
# Start MyAgent
myagent

# Select: Execute Task
# In editor, type:
"Fix the authentication bug in auth.py where tokens expire too quickly"

# Agent will:
# 1. Read auth.py
# 2. Analyze the issue
# 3. Fix the bug
# 4. Show you the changes
# 5. Summarize what was done
```

### Workflow 2: Add New Feature

```bash
# Single command approach
myagent "Add a new password reset feature with email verification"

# You'll see:
# Task: Add a new password reset feature...
#   → Reading existing files
#   → Creating password_reset.py
#   → Updating routes.py
#   → Creating email template
#   → Adding tests
#
# Response: I've implemented the password reset feature...
#
# ✓ Created 3 file(s)
# ✓ Modified 2 file(s)
# Completed in 8.5s
```

### Workflow 3: Interactive Development

```bash
myagent
# Select: Chat with Agent

You: "I need to add user authentication"
Agent: "I can help with that. Would you like JWT-based or session-based auth?"

You: "JWT please"
Agent: "Great! I'll implement JWT authentication. Should I include refresh tokens?"

You: "Yes, and add rate limiting"
Agent: "I'll implement JWT auth with refresh tokens and rate limiting..."
```

### Workflow 4: Code Review and Refactoring

```bash
myagent
# Select: File Operations → View File
# Enter: auth.py
# (Review the code)

# Back to main menu
# Select: Chat with Agent
You: "Refactor auth.py to improve readability and add error handling"
# Agent refactors and explains changes
```

### Workflow 5: Git Workflow

```bash
myagent
# After making changes with the agent:

# Select: Git Operations → Show Changes
# (Review the diff)

# Select: Git Operations → Stage Changes
# Enter: . (to stage all)

# Select: Git Operations → Commit
# Enter: "Add authentication system with JWT and rate limiting"
```

## Settings Management

### Change Provider

```bash
myagent
# Select: Configure Settings → Change Provider

? Select AI Provider (current: anthropic)
  OpenAI (GPT-4, GPT-3.5)
❯ Anthropic (Claude)
  Custom (OpenAI-compatible)
  Cancel

# Select your choice
# Settings saved automatically
```

### Change Model

```bash
myagent
# Select: Configure Settings → Change Model

? Select Model (current: claude-3-5-sonnet-20241022)
  claude-3-5-sonnet-20241022
  claude-3-opus-20240229
❯ claude-3-sonnet-20240229
  Enter custom model name
  Cancel

# Select your choice
✓ Model changed to: claude-3-sonnet-20240229
```

### View Configuration

```bash
myagent
# Select: Configure Settings → View Configuration

Current Configuration

Provider:       anthropic
Model:          claude-3-5-sonnet-20241022
Max Iterations: 50
Workspace:      /path/to/EU_agent

Press Enter to continue...
```

## File Operations

### View a File

```bash
myagent
# Select: File Operations → View File
? Enter file path: src/myagent/agent/loop.py

# File contents displayed with syntax highlighting
# Press Enter to continue
```

### Edit a File

```bash
myagent
# Select: File Operations → Edit File
? Enter file path: README.md
? How should I edit README.md? Add installation instructions

# Agent edits the file and shows you what changed
```

### Search Files

```bash
myagent
# Select: File Operations → Search Files
? Enter search query (regex): def\s+authenticate

Found 3 matches

auth.py:45  def authenticate(username, password):
utils.py:12  def authenticate_api_key(key):
tests/test_auth.py:23  def test_authenticate():

Press Enter to continue...
```

### Show Changes

```bash
myagent
# Select: File Operations → Show Changes

# Shows git diff of all changes
# Color-coded:
#   + Green for additions
#   - Red for deletions

Press Enter to continue...
```

## Git Operations

### Check Status

```bash
myagent
# Select: Git Operations → Status

On branch main
Changes not staged for commit:
  modified: src/myagent/cli.py
  modified: src/myagent/agent/loop.py

Untracked files:
  src/myagent/ui/enhanced_display.py
  src/myagent/ui/menu.py

Press Enter to continue...
```

### View Diff

```bash
myagent
# Select: Git Operations → Diff

# Shows detailed diff of all changes
# Syntax highlighted

Press Enter to continue...
```

### View Log

```bash
myagent
# Select: Git Operations → Log

* abc1234 (HEAD -> main) Add authentication system
* def5678 Update database schema
* ghi9012 Fix login bug
...

Press Enter to continue...
```

### Stage Changes

```bash
myagent
# Select: Git Operations → Stage Changes
? Enter files to stage: src/myagent/ui/enhanced_display.py src/myagent/ui/menu.py

✓ Files staged successfully
```

### Commit Changes

```bash
myagent
# Select: Git Operations → Commit
? Enter commit message: Add enhanced CLI with interactive menus

✓ Changes committed successfully
```

## Advanced Features

### Multi-line Task Input

When you select "Execute Task", an editor opens where you can write detailed, multi-line instructions:

```
Add a comprehensive logging system with the following features:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- File rotation to prevent log files from growing too large
- Structured logging with JSON format
- Integration with existing error handling
- Configuration via environment variables

Also update the documentation to explain how to use the new logging system.
```

The agent will handle all of this in one go!

### Chat Mode Conversation

Chat mode maintains context throughout the conversation:

```
You: "I need to optimize the database queries"
Agent: "I can help! Which queries are slow?"

You: "The user lookup is taking 2 seconds"
Agent: "I'll add an index on the username field and cache the results"

You: "Also cache the user's permissions"
Agent: "I'll implement that as well..."
```

## Tips & Best Practices

### Tip 1: Use Chat for Exploration
When you're not sure what you want, use Chat mode to explore options before executing.

### Tip 2: Check Status Regularly
Use "View Status" to monitor the agent's progress and resource usage.

### Tip 3: Review Changes Before Committing
Always use "File Operations → Show Changes" or "Git Operations → Diff" before committing.

### Tip 4: Start Simple
Begin with small tasks to understand how the agent works, then move to complex tasks.

### Tip 5: Be Specific in Tasks
The more specific your task description, the better the results:
- ❌ "fix the bug"
- ✓ "fix the bug in auth.py where tokens expire after 5 minutes instead of 1 hour"

### Tip 6: Use Verbose Mode for Learning
When starting out, use `--verbose` to see what the agent is doing:
```bash
myagent --verbose "your task"
```

### Tip 7: Interrupt if Needed
Don't hesitate to press Ctrl+C if the agent is going in the wrong direction. You can restart with a better description.

### Tip 8: Iterate Incrementally
Break large features into smaller tasks:
1. "Add user model"
2. "Add user authentication"
3. "Add user permissions"
4. "Add user profile page"

### Tip 9: Use the Right Mode
- **Single command**: Quick, well-defined tasks
- **Execute Task**: Complex, multi-step tasks
- **Chat mode**: Exploration and iterative development

### Tip 10: Save Your Work
The agent doesn't auto-commit. Use Git Operations to commit your changes!

## Troubleshooting

### Issue: Menu Not Showing

**Symptom:** Text-based prompt appears instead of menu
**Solution:**
```bash
pip install inquirer
pip install -e .
```

### Issue: Colors Not Working

**Symptom:** No colors or garbled characters
**Solution:**
```bash
# Disable colors
myagent --no-color
```

### Issue: Can't See What Agent Is Doing

**Symptom:** Want more detailed information
**Solution:**
```bash
# Enable verbose mode
myagent --verbose
```

### Issue: Mouse Not Working

**Symptom:** Clicking doesn't work in menus
**Solution:** Use arrow keys instead. Mouse support depends on your terminal.

### Issue: Editor Not Opening for "Execute Task"

**Symptom:** No editor appears
**Solution:** Set your EDITOR environment variable:
```bash
# Linux/Mac
export EDITOR=nano  # or vim, code, etc.

# Windows
set EDITOR=notepad
```

### Issue: Import Errors

**Symptom:** ModuleNotFoundError
**Solution:**
```bash
# Reinstall in editable mode
pip install -e .
```

### Issue: Provider/Model Not Working

**Symptom:** API errors or configuration issues
**Solution:**
```bash
# Test your provider
python -m myagent provider test

# Or configure a new provider
python -m myagent provider add --provider anthropic
```

## Command Line Options

```bash
# Show version
myagent --version

# Verbose mode (show logs)
myagent --verbose

# Custom working directory
myagent --cwd /path/to/project

# Specific provider
myagent --provider openai

# Specific model
myagent --model gpt-4o

# Disable colors
myagent --no-color

# Combined options
myagent --verbose --provider anthropic --model claude-3-opus-20240229 "your task"
```

## Examples

### Example 1: Add Tests
```bash
myagent "Add comprehensive unit tests for the authentication module including tests for login, logout, token validation, and password reset"
```

### Example 2: Refactor Code
```bash
myagent "Refactor the database connection code to use a connection pool and add error handling for connection failures"
```

### Example 3: Add Documentation
```bash
myagent "Add docstrings to all functions in auth.py and create a README for the authentication module"
```

### Example 4: Fix Bug
```bash
myagent "Fix the bug where users can't login with special characters in their password"
```

### Example 5: Add Feature
```bash
myagent "Add a new API endpoint for user profile management with GET, PUT, and DELETE methods"
```

## Getting Help

If you need help:

1. **In-app help**: Select "Help" from main menu
2. **Documentation**: Check `UI_ENHANCEMENTS.md` for detailed docs
3. **Quick start**: Check `QUICK_START.md` for quick reference
4. **Visual guide**: Check `VISUAL_COMPARISON.md` for before/after examples

## Conclusion

The enhanced CLI makes MyAgent more intuitive and enjoyable to use. With interactive menus, clean output, and organized workflows, you can focus on building great software while the AI handles the implementation details.

Happy coding! 🚀
