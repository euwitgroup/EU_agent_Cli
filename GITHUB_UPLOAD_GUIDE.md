# GitHub Upload Guide for MyAgent

## 🚀 Step-by-Step: Upload Your Project to GitHub

### Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com)
2. Click the **+** icon (top right) → **New repository**
3. Fill in:
   - **Repository name:** `myagent` (or your preferred name)
   - **Description:** `AI-powered autonomous coding agent for terminal`
   - **Public** or **Private** (your choice)
   - ✅ Do NOT check "Initialize with README" (you already have one)
4. Click **Create repository**

### Step 2: Prepare Your Local Project

Open PowerShell in your project folder:

```powershell
cd C:\Users\euwit\Desktop\EU_agent
```

### Step 3: Remove Sensitive Data

**IMPORTANT:** Make sure `.env` is in `.gitignore` (it should be already):

```powershell
# Check if .env is listed
type .gitignore | findstr ".env"
```

If `.env` is NOT listed, add it:

```powershell
echo .env >> .gitignore
```

### Step 4: Initialize Git Repository

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Check what will be committed (make sure .env is NOT listed)
git status

# Commit your files
git commit -m "Initial commit: MyAgent - AI coding agent"
```

### Step 5: Connect to GitHub

Replace `YOUR_USERNAME` and `REPO_NAME` with your actual GitHub username and repository name:

```powershell
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 6: Verify Upload

1. Go to your GitHub repository URL
2. Refresh the page
3. You should see all your files!

---

## 🔐 Important: Protect Your API Keys

### Before Uploading, Double-Check:

```powershell
# Make sure .env is in .gitignore
type .gitignore

# Make sure .env is NOT tracked
git status

# If .env appears in git status, remove it:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

### If You Accidentally Committed .env:

```powershell
# Remove from git history
git rm --cached .env
echo .env >> .gitignore
git add .gitignore
git commit -m "Remove .env and add to .gitignore"
git push
```

**IMPORTANT:** If you pushed your API key, rotate it immediately:
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys

---

## 📝 Update Your README

Before pushing, update the README with your GitHub URL:

1. Open `README.md`
2. Replace `YOUR_USERNAME` with your GitHub username
3. Save and commit:

```powershell
git add README.md
git commit -m "Update README with GitHub URL"
git push
```

---

## 🏷️ Create a Release (Optional)

Create a release for easy downloading:

1. Go to your GitHub repo
2. Click **Releases** (right sidebar)
3. Click **Create a new release**
4. Tag: `v1.0.0`
5. Title: `MyAgent v1.0.0 - Initial Release`
6. Description:
```markdown
## MyAgent v1.0.0

AI-powered autonomous coding agent for terminal.

### Features
- Multi-provider support (OpenAI, Anthropic, Custom)
- Interactive REPL with auto-complete
- File operations, search, and command execution
- Git integration and test runner
- Rate limit handling with auto-retry
- Beautiful terminal UI

### Installation
See [INSTALLATION.md](INSTALLATION.md)

### Quick Start
\`\`\`bash
pip install -e .
python -m myagent provider add --provider anthropic
python -m myagent main
\`\`\`
```
7. Click **Publish release**

---

## 📋 Recommended Repository Structure

Your repository should have:

```
myagent/
├── .github/               (optional: workflows, issue templates)
├── src/
│   └── myagent/
├── tests/
├── .env.example           ✅ (Example config - safe to share)
├── .env                   ❌ (NOT in git - in .gitignore)
├── .gitignore            ✅ (Must include .env)
├── README.md             ✅ (Main documentation)
├── INSTALLATION.md       ✅ (Installation guide)
├── TESTING.md            ✅ (Testing guide)
├── pyproject.toml        ✅ (Dependencies)
├── LICENSE               ✅ (Optional: MIT, Apache, etc.)
└── requirements.txt      (Optional: for pip)
```

---

## 🌟 Make Your Repo Stand Out

### Add a LICENSE

```powershell
# Create LICENSE file (example: MIT License)
@"
MIT License

Copyright (c) 2024 YOUR_NAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@ | Out-File -FilePath LICENSE -Encoding UTF8

git add LICENSE
git commit -m "Add MIT License"
git push
```

### Add Topics (Tags)

On GitHub:
1. Go to your repository
2. Click the ⚙️ gear icon next to "About"
3. Add topics: `ai`, `coding-agent`, `cli`, `python`, `automation`, `openai`, `anthropic`, `claude`

### Add a Nice README Badge

Add to top of README.md:

```markdown
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-128%20passing-brightgreen)]()
```

---

## 🔄 Keeping Your Repo Updated

After making changes:

```powershell
# Check what changed
git status

# Add changed files
git add .

# Commit with message
git commit -m "Add new feature: XYZ"

# Push to GitHub
git push
```

---

## 👥 For Users: How to Download and Run

Share this with users:

### Quick Start for Users

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/myagent.git
cd myagent

# Install
pip install -e .

# Configure
python -m myagent provider add --provider anthropic

# Run
python -m myagent main
```

---

## 📸 Add Screenshots (Optional)

1. Take screenshots of your UI
2. Create `screenshots/` folder
3. Add to README:

```markdown
## Screenshots

![MyAgent Welcome Screen](screenshots/welcome.png)
![Interactive Mode](screenshots/interactive.png)
```

---

## ✅ Checklist Before Pushing

- [ ] `.env` is in `.gitignore`
- [ ] No API keys in committed files
- [ ] README.md has correct GitHub URLs
- [ ] LICENSE file added
- [ ] All tests passing (`pytest tests/`)
- [ ] INSTALLATION.md is complete
- [ ] .env.example has example values (not real keys)

---

## 🎉 You're Done!

Your project is now on GitHub! Share the link:

```
https://github.com/YOUR_USERNAME/myagent
```

Users can now:
- Clone your repository
- Install and run MyAgent
- Contribute to the project
- Report issues
- Star your repo ⭐

Congratulations! 🚀
