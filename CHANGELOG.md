# 📜 Changelog

All notable changes to **AI Coders Proxy Fixer** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-07-21 🛡️ (Single-File Standalone & Single Instance Release)

### ✨ Added
- **Single-File Standalone Executable (`AI_Coders_Proxy_Fixer.exe`):** Built with PyInstaller `--onefile` mode. Embeds all DLLs and dependencies into a single portable `.exe` file. Users can place it anywhere (Desktop, Downloads, USB) without missing `_internal` DLL errors.
- **Windows Single Instance Guarantee:** Uses a Windows Named Mutex (`CreateMutexW`) to prevent multiple instances from opening concurrently. Displays a helpful notification if the app is already running in the System Tray.
- **Custom Application Icon (`assets/app_icon.ico`):** High-resolution custom icon embedded into the executable and taskbar.
- **Expanded Target Coverage:** Added Windsurf IDE, OpenAI Codex / Copilot CLI, Continue.dev, and Aider AI CLI patchers.

---

## [2.0.1] - 2026-07-21 🎨 (Futuristic Dashboard UI Overhaul)

### 🎨 UI & Aesthetics
- **Futuristic AI Dashboard:** Redesigned CustomTkinter interface to match high-tech futuristic AI aesthetics with deep dark background (`#12121A`), neon indicators, and rounded target cards.
- **Top Summary Stat Cards:** Live stat counters for `SCANNED` targets, `PATCHED` active targets, and `ACTIVE PORT`.
- **Individual Latency Cards:** Separate latency status cards for **Google**, **Claude API**, and **Cloud Code API** with color-coded response times.

---

## [2.0.0] - 2026-07-21 🚀 (Super Upgrade)

### ✨ Added
- **Smart OS Scanner Engine (`scanner.py`):** Automatically detects installed code editors, AI CLIs, and Shell Profiles.
- **Active Proxy Port Auto-Detector:** Scans common local proxy ports (`10808` v2rayN, `7890` Clash, `2080` Hiddify).
- **Instant System Proxy & WinInet Refresh:** Uses `wininet.dll`'s `InternetSetOptionW` and broadcasts `WM_SETTINGCHANGE`.
- **Start with Windows Toggle:** Option to auto-start silently in the Windows System Tray on system boot.
