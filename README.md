# MyBB PR Automation

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Selenium](https://img.shields.io/badge/Selenium-Automation-green) ![Google%20Apps%20Script](https://img.shields.io/badge/Google%20Apps%20Script-Integration-orange) ![GitHub%20Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-blueviolet)

> End-to-end automation bot for reciprocal post exchanges between MyBB forums.

> Logs in, extracts and reposts ad content, tracks partner activity, and handles configurable forum logic with error reporting.

---

## ⚙️ Key Features
- Multi-forum login & posting automation  
- Dynamic ad-topic detection and reposting  
- Configurable forum settings & posting limits  
- Input from **Google Sheet or local list**  
- GitHub Actions workflow for manual or scheduled runs

---

## 🧩 Google Sheets & Script
The bot can read target forums directly from a connected Google Sheet.  
A companion script **`mybb-forum-scanner.gs`**  scans listed forums for new ad threads and updates the sheet automatically.  
It detects relevant topics by keywords (in ru) and highlights new ones for posting.

---

## 🧱 Stack
Python · Selenium · Google Apps Script · GitHub Actions

---

## 📝 License
MIT — free to use and modify.
