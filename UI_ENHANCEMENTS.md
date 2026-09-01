# Enhanced CLI Interface

## Overview

The MyAgent CLI has been redesigned with a modern, user-friendly interface inspired by Claude Code. The new interface provides:

- **Interactive menus** with arrow key and mouse support
- **Clean output** without raw logs (only flash messages)
- **Better visual hierarchy** with icons and colors
- **Menu-driven navigation** for all operations

## Features

### Main Menu

When you start MyAgent in interactive mode, you'll see a clean menu with these options:

- 💬 **Chat with Agent** - Have a conversation with the AI
- 📋 **Execute Task** - Give a specific task (opens editor)
- 📊 **View Status** - See session statistics
- 🔧 **Configure Settings** - Change provider and model
- 📁 **File Operations** - View, edit, search files
- 🔄 **Git Operations** - Version control operations
- ❓ **Help** - Show help information
- 🚪 **Exit** - Quit the application

### Enhanced Display

#### Flash Messages
Instead of verbose logs, you'll see clean flash messages:
- ✓ Success messages in green
- ✗ Error messages in red
- ⚠ Warning messages in yellow
- ℹ Info messages in cyan

#### Tool Execution
Tool calls are shown in a compact format:
```
Task: Fix the authentication bug

  → Reading auth.py
  → Editing auth.py
  → Running pytest tests/test_auth.py

Response
────────────────────────────────────────
I've fixed the authentication bug by...
────────────────────────────────────────

  ✓ Modified 1 file(s)
  ✓ Ran 1 command(s)
  Completed in 3.2s
```

### Settings Menu

Configure your AI provider and model interactively:

1. Select **Configure Settings** from main menu
2. Choose:
   - Change Provider (OpenAI, Anthropic, Custom)
   - Change Model (with suggestions)
   - View Configuration

### File Operations

Manage files without leaving the CLI:

- View files with syntax highlighting
- Edit files via AI agent
- Search files with regex
- Show git changes

### Git Operations

Version control at your fingertips:

- View status
- Check diff
- View log
- Stage changes
- Commit changes

## Usage

### Interactive Mode

Start the enhanced interactive mode:

```bash
myagent
# or
python -m myagent
```

Navigate using arrow keys, select with Enter.

### Single Task Mode

Execute a single task with clean output:

```bash
myagent "Add unit tests for the payment module"
```

### Verbose Mode

If you need to see logs for debugging:

```bash
myagent --verbose "Fix the bug"
```

## Navigation

- **Arrow Keys** - Navigate menu options
- **Enter** - Select option
- **Ctrl+C** - Cancel current operation
- **Mouse** - Click on options (terminal dependent)

## Tips

1. Use **Execute Task** for complex, multi-step tasks
2. Use **Chat Mode** for back-and-forth conversations
3. Check **View Status** to see what the agent has done
4. All changes are tracked and summarized
5. Press Ctrl+C to interrupt long-running tasks

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑/↓ | Navigate menu |
| Enter | Select option |
| Ctrl+C | Cancel/Interrupt |
| Ctrl+D | Exit (in some contexts) |

## Configuration

The enhanced UI respects your terminal settings:

- Colors are automatically adapted
- Mouse support depends on terminal
- Works in all modern terminals

## Troubleshooting

### Menu not showing?

Make sure `inquirer` is installed:
```bash
pip install inquirer
```

### Colors not working?

Check your terminal supports colors, or use:
```bash
myagent --no-color
```

### Verbose logs needed?

Enable verbose mode:
```bash
myagent --verbose
```

## Comparison: Old vs New

### Old Interface
```
2024-01-20 10:30:45 - myagent.agent - INFO - Starting task
2024-01-20 10:30:46 - myagent.tools - DEBUG - Reading file: auth.py
→ read_file(path=auth.py, start_line=None, end_line=None)
✓ Success
2024-01-20 10:30:47 - myagent.tools - DEBUG - Writing file: auth.py
→ edit_file(path=auth.py, old_text=..., new_text=...)
✓ Success
...
```

### New Interface
```
Task: Fix the authentication bug

  → Reading auth.py
  → Editing auth.py
  → Running tests

Response: I've fixed the authentication bug...

  ✓ Modified 1 file(s)
  Completed in 2.1s
```

## Migration

The old prompt system is still available via:

```python
from myagent.ui.prompt import start_interactive_session
start_interactive_session(workspace_dir)
```

But we recommend using the new enhanced interface:

```python
from myagent.ui.enhanced_prompt import start_enhanced_session
start_enhanced_session(workspace_dir)
```

## Future Enhancements

Planned improvements:

- Streaming responses with live updates
- Syntax highlighting in file viewer
- Inline diff viewer
- Command history with fuzzy search
- Customizable themes
