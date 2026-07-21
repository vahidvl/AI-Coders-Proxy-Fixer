# 📜 Changelog

All notable changes to **AI Coders Proxy Fixer** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-07-21 🚀 (Super Upgrade)

### ✨ Added
- **Smart OS Scanner Engine (`scanner.py`):** Automatically detects installed code editors (VS Code, Cursor, Antigravity IDE, Void, VS Code Insiders, Sublime Text), AI CLIs (Claude Code, Ollama, LM Studio), and Shell Profiles (PowerShell `$PROFILE`, Git Bash `.bashrc`).
- **Active Proxy Port Auto-Detector:** Scans common local proxy ports (`10808` v2rayN, `7890` Clash, `2080` Hiddify, `10809`, `1080`) to automatically fill the active port.
- **Modular Target Patcher (`patchers.py`):** Enables individual or batch patching (`Patch All`) for specific IDEs, Shells, and CLIs.
- **Preset Profile Dropdown:** One-click presets for v2rayN, Clash, Hiddify, and Custom configurations.
- **Real-Time AI API Latency Tester:** Live ping latency measurement (in ms) to Google, Anthropic API (`api.anthropic.com`), and Cloud Code API (`cloudcode-pa.googleapis.com`).
- **Instant System Proxy & WinInet Refresh:** Uses `wininet.dll`'s `InternetSetOptionW` and broadcasts `WM_SETTINGCHANGE` so Windows, Edge, Chrome, and Electron apps reload proxy settings instantly without restarting browsers or ending tasks in Task Manager.
- **Start with Windows Toggle:** Option to auto-start silently in the Windows System Tray on system boot via `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
- **Automated Unit Testing Suite (`tests/`):** 8 comprehensive automated unit tests covering scanner, patcher, latency, auto-start, and proxy core logic.

### 🐛 Fixed
- Fixed a `Path` attribute error in `proxy_core.py` when evaluating string paths for IDE settings.
- Fixed local OAuth redirect callback loops by optimizing `ProxyOverride` exceptions (`<local>;127.0.0.1;localhost;::1`).
- Fixed system tray window state synchronization issues.

### 🎨 Changed
- Redesigned CustomTkinter Dashboard UI with modern dark mode aesthetic, scrollable target cards, latency badges, and updated window dimensions (`620x720`).
- Updated `README.md` and `README_fa.md` with v2.0 feature showcase, badges, and documentation.

---

## [1.0.0] - 2026-07-18 🌐 (Initial Release)

### ✨ Added
- Initial portable GUI application using CustomTkinter and `pystray`.
- System-wide environment variable management (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`).
- Windows Registry ProxyEnable & ProxyServer toggling.
- Git global proxy configuration (`http.proxy`, `https.proxy`).
- Basic `settings.json` patcher for VS Code, Cursor, Void, and Antigravity IDE.
- Persian & English documentation (`README_fa.md`, `README.md`, `docs/ERRORS.md`).
- Portable `.exe` compilation via PyInstaller.
