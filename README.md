# 🚀 Git Auto Commit Assistant

This project provides a smart CLI tool that automatically analyzes changes in any local Git repository, generates meaningful commit messages using the Gemini 2.0 API, and manages versioning and metadata (timestamp, author, Python environment) — all in one step.

## ✨ Features

* 🔍 Detects **untracked, modified, and staged** file changes
* 🧐 Generates **Conventional Commit** messages using Gemini LLM (v2.0 Flash)
* 💾 Includes commit **version**, **timestamp**, **author**, and **Python environment** info
* 📝 Optionally displays inline `git diff` summaries (with length truncation)
* 🌐 Offers global CLI shortcut via softlink (e.g., `gcom`)
* 📤 Automatically pushes to GitHub after confirmation
* 🛉 Automatically handles `.git/*.lock` conflicts for smoother automation

## 📦 Requirements

* Python 3.8+
* Git installed and accessible in `PATH`
* Access to [Gemini 2.0 API](https://ai.google.dev/)
* A valid `.env` file with your API key

## 🛠️ Installation

```bash
git clone https://github.com/ybenzou/git-commit.git
cd git-commit
pip install -r requirements.txt
```

### 🔐 Create `.env` file

```env
GEMINI_API_KEY=your_api_key_here
```

## ⚡ Usage

### Run in any Git project directory:

```bash
python /full/path/to/git-commit/commit_planner.py
```

It will:

1. Detect local file changes
2. Call Gemini to generate a commit message
3. Ask you for confirmation
4. Commit + push changes
5. Bump version in `version.txt`

## 🔗 Optional: Global CLI Shortcut (`gcom`)

```bash
mkdir -p ~/Tools
echo -e '#!/bin/bash\npython /full/path/to/git-commit/commit_planner.py' > ~/Tools/gcom
chmod +x ~/Tools/gcom
sudo ln -s ~/Tools/gcom /usr/local/bin/gcom
```

Then use from anywhere:

```bash
cd /your/other/project
gcom
```

## 📂 Versioning

The tool manages a local `version.txt` file (semver style like `0.1.2`) and bumps the patch version after each successful push.

## 📸 Demo

![Demo Screenshot](./public/auto-commit-demo.png)

## 🧠 Powered by

* [Gemini 2.0 Flash](https://ai.google.dev/)
* Git CLI
* Python 3.x
* `python-dotenv`, `subprocess`, `datetime`, and more

## 📄 License

MIT License © 2025 ybenzou
