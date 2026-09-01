# Enhanced CLI - Quick Start Guide

## Installation

The enhanced CLI is now installed with the standard MyAgent installation:

```bash
pip install -e .
```

This will automatically install all required dependencies including `inquirer` for interactive menus.

## Starting MyAgent

### Interactive Mode (Menu-Driven)

Simply run:

```bash
myagent
```

or

```bash
python -m myagent
```

You'll see a beautiful menu interface with these options:

```
✨ MyAgent - AI Coding Assistant

Session Info
┌─────────────────────────────────┐
│ Project    EU_agent             │
│ Provider   anthropic            │
│ Model      claude-3-5-sonnet... │
└─────────────────────────────────┘

? What would you like to do?
❯ 💬 Chat with Agent
  📋 Execute Task
  📊 View Status
  🔧 Configure Settings
  📁 File Operations
  🔄 Git Operations
  ❓ Help
  🚪 Exit
```

### Single Task Mode

Execute a task directly:

```bash
myagent "Add unit tests for the payment module"
```

You'll see clean output without logs:

```
Task: Add unit tests for the payment module

  → Reading payment.py
  → Creating tests/test_payment.py
  → Running pytest

Response
────────────────────────────────────────
I've created comprehensive unit tests...
────────────────────────────────────────

  ✓ Created 1 file(s)
  ✓ Modified 1 file(s)
  ✓ Ran 1 command(s)
  Completed in 5.3s
```

## Key Features

### 1. Clean Output (No Raw Logs)

By default, you won't see verbose logs. Only clean flash messages:
- ✓ Success (green)
- ✗ Error (red)
- ⚠ Warning (yellow)
- ℹ Info (cyan)

### 2. Interactive Menus

Navigate with arrow keys:
- ↑/↓ to move
- Enter to select
- Ctrl+C to cancel

### 3. Mouse Support

Click on menu items if your terminal supports it.

### 4. Compact Tool Display

Tool calls are shown cleanly:
```
  → Reading auth.py
  → Editing auth.py
  → Running tests
```

Instead of verbose logs with timestamps and arguments.

## Common Workflows

### Workflow 1: Quick Task

```bash
myagent "fix the bug in auth.py"
```

Fast, clean output, done!

### Workflow 2: Interactive Chat

1. Run `myagent`
2. Select "💬 Chat with Agent"
3. Type your questions/requests
4. Type "back" to return to menu

### Workflow 3: Configure Settings

1. Run `myagent`
2. Select "🔧 Configure Settings"
3. Choose provider/model
4. Changes are saved automatically

### Workflow 4: File Operations

1. Run `myagent`
2. Select "📁 File Operations"
3. Choose:
   - View files
   - Search code
   - Show changes

### Workflow 5: Git Operations

1. Run `myagent`
2. Select "🔄 Git Operations"
3. Manage commits, view diffs, etc.

## Advanced Usage

### Enable Verbose Logs (Debugging)

If you need to see detailed logs:

```bash
myagent --verbose "your task"
```

### Change Provider on the Fly

```bash
myagent --provider openai --model gpt-4o "your task"
```

### Disable Colors

```bash
myagent --no-color
```

## Tips & Tricks

### Tip 1: Use Task Mode for Complex Work

For multi-step tasks, use "Execute Task" which opens an editor where you can write detailed instructions.

### Tip 2: Check Status Regularly

Use "View Status" to see:
- How many iterations used
- Files changed
- Commands run
- Tool calls made

### Tip 3: Interrupt Safely

Press Ctrl+C to interrupt long-running tasks. The agent will stop gracefully and you can return to the menu.

### Tip 4: View Changes Before Committing

Use "File Operations" → "Show Changes" to review what the agent modified before committing.

### Tip 5: Chat for Exploration

Use Chat mode when you're not sure what you want. Have a conversation to explore options, then switch to Task mode to execute.

## Troubleshooting

### Issue: Menu not appearing

**Solution:** Make sure `inquirer` is installed:
```bash
pip install inquirer
```

### Issue: Colors not working

**Solution:** Your terminal might not support colors. Use:
```bash
myagent --no-color
```

### Issue: Mouse clicks not working

**Solution:** Mouse support depends on your terminal. Arrow keys always work.

### Issue: Need to see logs

**Solution:** Use verbose mode:
```bash
myagent --verbose
```

### Issue: Import errors

**Solution:** Reinstall in editable mode:
```bash
pip install -e .
```

## Comparison

### Old Way
```bash
$ myagent
> fix the auth bug
2024-01-20 10:30:45 - myagent.agent - INFO - Starting task
2024-01-20 10:30:46 - myagent.tools - DEBUG - Reading file
→ read_file(path='auth.py', start_line=None, end_line=None)
✓ Success
[... hundreds of lines of logs ...]
```

### New Way
```bash
$ myagent
? What would you like to do? Execute Task
? Enter your task: fix the auth bug

Task: fix the auth bug

  → Reading auth.py
  → Editing auth.py

Response: Fixed the bug by...

  ✓ Modified 1 file(s)
  Completed in 2.1s
```

Much cleaner! 🎉

## What's Next?

After getting familiar with the basics:

1. Try different menu options
2. Experiment with Chat mode
3. Use File Operations to explore your codebase
4. Configure your preferred provider/model
5. Let the agent help you build! 🚀

## Need Help?

- Run `myagent` and select "❓ Help"
- Check `UI_ENHANCEMENTS.md` for detailed documentation
- Enable `--verbose` to see what's happening under the hood

Enjoy the new interface! 🎨
