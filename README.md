# MyBB PR Automation

> End-to-end automation script for reciprocal post exchanges between MyBB forums.  
> The bot authenticates on multiple sites, extracts and reposts PR content, detects partner activity, and records results automatically.  
> Includes CSV and Google Sheets synchronization, error handling, and configurable forum-specific logic.

---

## ⚙️ Features
- Automatic login and session handling across partner forums  
- Ad extraction and reposting with dynamic topic detection  
- Google Sheets integration for progress tracking  
- Detailed logging and per-forum configuration  
- Robust error handling and resume logic  
- YAML workflow for CI-based runs

---

## 🧩 Automation via GitHub Actions
This repository includes a **`run-bot.yml`** workflow that runs the bot in GitHub Actions.  
You can:
- **Run manually** via “Run workflow”  
- Or add a **schedule** for automatic execution (e.g., once per day)
