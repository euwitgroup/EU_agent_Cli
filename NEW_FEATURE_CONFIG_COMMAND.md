# ✨ New Feature: /config Command

## What's New?

Added the **`/config`** command to the interactive REPL, allowing users to edit their provider settings and API keys **without leaving the session**.

## 🎯 Problem Solved

Previously, users had to:
1. Exit the REPL
2. Run `python -m myagent provider add` command
3. Or manually edit the `.env` file
4. Restart the REPL

Now users can configure everything **from within the interactive session**!

## 🚀 How to Use

### Step 1: Enter the Command

While in interactive mode:
```
> /config
```

### Step 2: Choose What to Configure

You'll see a menu:
```
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

### Option 1: Change Provider and API Key

Complete provider switch:
```
Enter choice (1-4): 1

Available providers:
  • anthropic - Anthropic (Claude)
  • openai - OpenAI (GPT)
  • custom - Custom OpenAI-compatible API

Provider name: anthropic
API Key: ••••••••••••••••
Model name: claude-3-5-sonnet-20241022

✓ Provider configured: anthropic
✓ Model set: claude-3-5-sonnet-20241022

Note: Restart the REPL for changes to take effect
```

### Option 2: Change Model Only

Switch to a different model while keeping the same provider:
```
Enter choice (1-4): 2

Fetching available models for anthropic...

Available models:
  • claude-3-5-sonnet-20241022
  • claude-3-5-haiku-20241022
  • claude-3-opus-20240229
  • claude-3-sonnet-20240229
  • claude-3-haiku-20240307

New model name: claude-3-opus-20240229

✓ Model updated: claude-3-opus-20240229

Note: Restart the REPL for changes to take effect
```

### Option 3: Update API Key

Replace the API key for your current provider:
```
Enter choice (1-4): 3

New API key for custom: ••••••••••••••••

✓ API key updated for custom

Note: Restart the REPL for changes to take effect
```

### Option 4: Cancel

Exit without making changes.

## 📝 Features

✅ **Shows current configuration** - See your active provider and model  
✅ **Secure password input** - API keys are hidden when typing  
✅ **Lists available models** - Fetches models from the provider API  
✅ **Auto-updates .env** - Changes saved automatically  
✅ **Clear confirmations** - Know exactly what was changed  
✅ **Error handling** - Validates input and shows helpful errors  

## 🔧 Technical Details

### What Gets Updated

The command modifies your `.env` file with the new settings:

**For provider change:**
- `MYAGENT_PROVIDER=<new-provider>`
- `<PROVIDER>_API_KEY=<your-key>`
- `<PROVIDER>_MODEL=<model-name>`
- `CUSTOM_BASE_URL=<url>` (if custom provider)

**For model change:**
- Updates only the model variable for current provider

**For API key change:**
- Updates only the API key for current provider

### Files Modified

- `.env` - Environment configuration file

### Restart Required

After using `/config`, you need to:
1. Exit the REPL (`/exit` or `Ctrl+D`)
2. Restart: `python -m myagent main`

This is because the configuration is loaded at startup.

## 📋 Command Reference

### All Interactive Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/status` | Show session info |
| **`/config`** | **Edit provider settings and API keys** ⭐ NEW |
| `/clear` | Clear chat history |
| `/reset` | Reset session |
| `/model` | Change model |
| `/provider` | Switch provider |
| `/context` | Show context size |
| `/tools` | List available tools |
| `/diff` | Show git diff |
| `/exit` | Quit REPL |

### Auto-Complete

Type `/` and press **Tab** to see all commands with auto-complete!

## 🎨 UI Integration

The `/config` command is also listed in the welcome menu:

```
Quick Commands (Use arrow keys or type command)

💬 /help      Show all commands    📊 /status    Session info
🧹 /clear     Clear history        🚪 /exit      Quit REPL

⚙️  /config    Edit provider/API    🔧 /model     Change model
🔌 /provider  Switch provider      🛠️  /tools     List tools
```

## 🐛 Troubleshooting

### "Configuration cancelled"
- You pressed `Ctrl+C` or `Ctrl+D` during input
- Just run `/config` again

### "Invalid provider"
- Only `anthropic`, `openai`, and `custom` are supported
- Check spelling (case-insensitive)

### "API key cannot be empty"
- You must provide an API key
- Make sure you paste the full key

### "Could not fetch models"
- Your API key might be invalid
- Network connection might be down
- Provider API might be unavailable
- You can still enter a model name manually

### Changes don't take effect
- Remember to restart the REPL after configuration
- Exit with `/exit` and run `python -m myagent main` again

## 📚 Related Documentation

- **QUICKSTART.md** - Quick reference for all commands
- **INSTALLATION.md** - Initial setup guide
- **README.md** - Full documentation
- **CHANGELOG.md** - All changes in this version

## 🎉 Benefits

### Before `/config`:
```bash
# Had to exit REPL
/exit

# Run CLI command
python -m myagent provider add --provider anthropic
# Enter details...

# Restart REPL
python -m myagent main
```

### After `/config`:
```bash
# Stay in REPL!
> /config
# Choose option, enter details
# Exit and restart when ready
```

**Saves time and keeps you in your flow!** 🚀

---

## 💡 Tips

1. **Test connection first** - After changing settings, use `/status` to verify
2. **Keep old keys** - Back up your `.env` file before major changes
3. **Use Tab completion** - Type `/con` and press Tab to auto-complete `/config`
4. **Check models list** - Option 2 shows available models for your provider

## ✨ Example Workflow

```bash
# Start MyAgent
python -m myagent main

# Work on some tasks
> Create a hello world script
...

# Need to switch to a different model
> /config
Enter choice: 2
New model name: claude-3-opus-20240229
✓ Model updated

# Exit and restart
> /exit

# Start with new model
python -m myagent main
```

---

**Enjoy the new `/config` command!** 🎊

For questions or issues, check the documentation or open an issue on GitHub.
