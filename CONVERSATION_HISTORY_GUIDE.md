# 💾 Conversation History System

## Overview

MyAgent now includes an automatic conversation history system that **saves your sessions** and lets you **continue from where you left off** - even after restarting!

## 🎯 Key Features

✅ **Auto-save** - Every interaction is saved automatically  
✅ **Session restore** - Continue previous conversations on restart  
✅ **History browser** - View past messages with `/history`  
✅ **Session management** - List and manage sessions with `/sessions`  
✅ **Persistent storage** - Sessions stored in `.myagent/history/`  
✅ **Smart prompts** - Optionally restore previous session on startup  

---

## 🚀 How It Works

### Automatic Saving

Every time you interact with MyAgent, your conversation is automatically saved:

```
> Create a hello world script
... agent responds ...
💾 Session auto-saved

> Add error handling
... agent responds ...
💾 Session updated
```

### Continue Previous Session

When you restart MyAgent in the same project:

```bash
python -m myagent main

📜 Found previous session with 8 messages
Would you like to continue from where you left off?

Continue previous session? (y/n): y
✓ Restored 8 messages from previous session

# Now you can continue the conversation!
```

Or start fresh:

```bash
Continue previous session? (y/n): n
Previous session archived as: 20260901_143000
Starting fresh session
```

---

## 📝 Commands

### `/history` - View Conversation

Show the last 20 messages from your current session:

```
> /history

Conversation History (8 messages)

┌──────────────┬─────────────────────────────────────────────────┐
│ Role         │ Content                                        │
├──────────────┼─────────────────────────────────────────────────┤
│ user         │ Create a hello world script                    │
│ assistant    │ I'll create a simple hello world script...     │
│ user         │ Add error handling                             │
│ assistant    │ I'll add try-except blocks...                  │
└──────────────┴─────────────────────────────────────────────────┘

Showing last 20 of 8 total messages
History saved to: C:\project\.myagent\history
```

**Features:**
- Shows up to last 20 messages
- Truncates long messages for readability
- Displays tool calls as summaries
- Shows storage location

### `/sessions` - List Saved Sessions

View all your saved sessions:

```
> /sessions

Saved Sessions (last 10)

┌────┬────────────────────┬─────────────────────┬──────────┬──────────────────┐
│ #  │ Session ID         │ Date                │ Messages │ Last Message     │
├────┼────────────────────┼─────────────────────┼──────────┼──────────────────┤
│ 1  │ 20260901_143000    │ 2026-09-01 14:30:00 │ 12       │ Add unit tests   │
│ 2  │ 20260901_120000    │ 2026-09-01 12:00:00 │ 6        │ Fix the bug      │
│ 3  │ 20260831_160000    │ 2026-08-31 16:00:00 │ 20       │ Create API       │
└────┴────────────────────┴─────────────────────┴──────────┴──────────────────┘

Sessions stored in: C:\project\.myagent\history
```

**Features:**
- Lists most recent 10 sessions
- Shows session ID, date, message count
- Preview of last message
- Shows storage location

---

## 📁 Storage Structure

Sessions are stored in `.myagent/history/` in your project:

```
project/
├── .myagent/
│   └── history/
│       ├── current_session.json      # Active session
│       ├── sessions.json              # Sessions index
│       ├── session_20260901_143000.json  # Archived session
│       └── session_20260901_120000.json  # Archived session
├── src/
└── ...
```

### File Formats

#### current_session.json
The active session being worked on:

```json
{
  "session_id": "20260901_143000",
  "workspace": "C:\\project",
  "timestamp": "2026-09-01T14:30:00",
  "messages": [
    {
      "role": "user",
      "content": "Create a hello world script"
    },
    {
      "role": "assistant",
      "content": "I'll create that for you..."
    }
  ],
  "data": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "summary": {
      "iterations": 2,
      "tool_calls": 3,
      "files_changed": 1
    }
  }
}
```

#### sessions.json
Index of all sessions for quick listing:

```json
{
  "sessions": [
    {
      "session_id": "20260901_143000",
      "timestamp": "2026-09-01T14:30:00",
      "workspace": "C:\\project",
      "message_count": 12,
      "last_message": "Add unit tests for the payment module"
    }
  ]
}
```

---

## 🔄 Workflow Examples

### Example 1: Daily Work

**Day 1 - Morning:**
```bash
python -m myagent main
> Create a new feature for user authentication
... work on feature ...
> /exit
💾 Session saved
```

**Day 1 - Afternoon:**
```bash
python -m myagent main
📜 Found previous session with 10 messages
Continue previous session? (y/n): y
✓ Restored 10 messages

> Continue with the login page
... continues work ...
```

**Day 2:**
```bash
python -m myagent main
📜 Found previous session with 18 messages
Continue previous session? (y/n): n
Previous session archived as: 20260901_090000
Starting fresh session

> Start a new feature for payments
... new work ...
```

### Example 2: Multiple Projects

Each project has its own history:

```bash
cd /project-a
python -m myagent main
# Works on project-a history

cd /project-b  
python -m myagent main
# Works on project-b history (separate!)
```

### Example 3: Review Past Work

```bash
> /sessions
# See all past sessions

> /history
# Review current conversation

> What did we work on earlier?
# Agent has full context from session history
```

---

## ⚙️ Configuration

### Storage Location

By default, history is stored in `.myagent/history/`. This is:
- ✅ **Git-ignored** (already in `.gitignore`)
- ✅ **Project-specific** (each project has own history)
- ✅ **Portable** (moves with your project)

### Privacy

- 🔒 History files are **local only**
- 🔒 Not committed to git (in `.gitignore`)
- 🔒 Stays on your machine
- 🔒 Can be deleted anytime

### Cleanup

To clear history:

```bash
# Clear current session only
> /clear

# Or manually delete history folder
rm -rf .myagent/history
```

---

## 🎛️ Advanced Usage

### Session Lifecycle

1. **Start REPL** → Check for previous session
2. **User chooses** → Continue or start fresh
3. **During session** → Auto-save after each interaction
4. **Exit REPL** → Final save
5. **Next start** → Offer to restore

### What's Saved

Each session includes:
- ✅ All messages (user + assistant)
- ✅ Tool calls and results
- ✅ Session metadata (provider, model)
- ✅ Execution statistics
- ✅ Timestamps

### What's NOT Saved

- ❌ Files created/modified (only paths)
- ❌ Command outputs (only commands)
- ❌ Test results (only summaries)
- ❌ API keys or secrets

---

## 💡 Tips

1. **Always start in same directory** - History is project-specific
2. **Use `/history` to remember context** - See what you were working on
3. **Archive old sessions** - Start fresh when changing topics
4. **Check `/sessions`** - Review past work
5. **Session IDs are timestamps** - Easy to identify when work was done

---

## 🐛 Troubleshooting

### "No previous session found"
- You're in a new project
- History was cleared
- First time using MyAgent in this project
- **Solution**: Just start working, it will save automatically

### "Could not load previous session"
- Session file might be corrupted
- **Solution**: Choose "n" to start fresh, old session will be archived

### "Session auto-save failed"
- Disk full
- Permissions issue
- **Solution**: Check disk space and folder permissions

### History taking up space
- Each session is typically 10-100KB
- **Solution**: Delete `.myagent/history/` folder to free space

---

## 🔐 Security Notes

- History files contain conversation content
- Store API responses and code snippets
- May contain sensitive project information
- **Never commit `.myagent/` to version control**
- Already in `.gitignore` by default

---

## 📊 Statistics

View session stats with `/status`:

```
> /status

Session Status:

Iterations: 5/50
Tool calls: 8
Files changed: 3
Files created: 2
Commands executed: 4

Provider: anthropic
Model: claude-3-5-sonnet-20241022
```

---

## 🎉 Benefits

### Before History System:
```
❌ Lost context on restart
❌ Had to repeat instructions
❌ No record of past work
❌ Couldn't review conversations
```

### After History System:
```
✅ Seamless continuation
✅ Full context preserved
✅ Complete work history
✅ Easy to review and learn
```

---

## 📚 Related Documentation

- **README.md** - Main documentation
- **QUICKSTART.md** - Quick command reference
- **INSTALLATION.md** - Setup guide
- **NEW_FEATURE_CONFIG_COMMAND.md** - Provider configuration

---

## 🆘 Need Help?

- Check `/help` for all commands
- Use `/status` to see session info
- View `/history` to review messages
- List `/sessions` to see past work

---

**Enjoy seamless conversations with MyAgent!** 💬✨

Your work is never lost - pick up right where you left off! 🚀
