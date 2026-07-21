<h1 align="center">🚀 AI Coders Proxy Fixer v2.0</h1>

<div align="center">
  <img src="https://img.shields.io/badge/Version-v2.0.0--Super--Upgrade-orange" alt="Version"/>
  <img src="https://img.shields.io/badge/OS-Windows-blue" alt="Windows"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
  <img src="https://img.shields.io/badge/Portable-Yes-success" alt="Portable"/>
  <img src="https://img.shields.io/badge/Tests-8%20Passed-brightgreen" alt="Tests"/>
  <br/><br/>
  <b><a href="README_fa.md">🇮🇷 مطالعه به زبان فارسی (Read in Persian)</a> | <a href="CHANGELOG.md">📜 Read Changelog</a></b>
</div>

> A lightweight, open-source proxy router & automated IDE patcher designed specifically to resolve geoblocking, network timeouts, and corporate firewall restrictions for modern AI coding assistants.

⭐️ **If this tool saves you hours of debugging, please consider giving it a STAR! It helps other developers discover this solution.** ⭐️

<div align="center">
  <img src="assets/ui_sample.jpg" alt="UI Dashboard v2.0" width="650"/>
</div>

## 🚀 What's New in v2.0?

Version 2.0 transforms AI Coders Proxy Fixer into a **smart automated OS scanner & multi-target patcher**:
- 🔍 **Smart OS Scanner:** Automatically detects installed IDEs (VS Code, Cursor, Antigravity IDE, Void, VS Code Insiders, Sublime Text), AI CLIs (Claude Code, Ollama), and Shell Profiles (PowerShell, Git Bash).
- 🔌 **Active Proxy Port Auto-Detector:** Scans and auto-detects active local proxy ports (`10808` v2rayN, `7890` Clash, `2080` Hiddify).
- ⚡ **Instant WinInet Proxy Refresh:** Uses `wininet.dll` and broadcasts `WM_SETTINGCHANGE` so Windows, Edge, Chrome, and Electron apps reload proxy settings instantly **without restarting browsers or killing tasks in Task Manager**.
- 📊 **Real AI API Latency Tester:** Live ping latency measurement (in ms) to Google, Anthropic API (`api.anthropic.com`), and Cloud Code API.
- 🎯 **Targeted & Batch Patching:** Individual or one-click `Patch All` for detected IDEs and shell profiles.
- 💻 **Start with Windows:** Option to run silently in the system tray on Windows startup.

---

## 🌍 The Problem

Developers living in heavily restricted regions or working behind strict corporate firewalls frequently encounter severe connectivity issues with AI coding assistants. Standard VPNs and SOCKS5 proxies often fail because they disrupt internal Language Server routing (e.g., routing `localhost` traffic through the proxy).

This results in frustrating errors such as:
- ❌ `User location is not supported for the API use.` (HTTP 400 Bad Request)
- ❌ `Post "https://cloudcode-pa.googleapis.com/...": EOF`
- ❌ `Failed to check terminal shell support` (VS Code & Antigravity IDE)
- ❌ `ETIMEDOUT` or `Connection Refused` in Cursor
- ❌ Unresponsive Autonomous Agents & OAuth Redirect Loops

<div align="center">
  <img src="assets/agent_terminated.png" alt="Agent Terminated Error" width="48%"/>
  <img src="assets/cloudcode_eof.png" alt="CloudCode EOF Error" width="48%"/>
</div>

## 🎯 The Solution

**AI Coders Proxy Fixer** automates the complex network routing required to make AI assistants work seamlessly behind a proxy.

It intelligently injects proxy configurations into your IDEs and shells while applying strict exception rules (bypassing `localhost` and `127.0.0.1`) to ensure local language servers never crash.

### ✨ Key Features
- **Preset Profiles:** One-click presets for v2rayN, Clash, Hiddify, and Custom setups.
- **Deep IDE Integration:** Automatically configures `settings.json` for **VS Code, Cursor, Void, VS Code Insiders, and Antigravity IDE**.
- **Shell Profile Integration:** Safely injects proxy exports into PowerShell `$PROFILE` and Git Bash `~/.bashrc`.
- **System-Wide Variables:** Seamlessly sets Windows Environment Variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`).
- **Git Proxy Configuration:** Fixes hanging `git push` and `git pull` commands.
- **Unobtrusive & Portable:** Minimizes to system tray and requires zero installation.

## 🛠️ Installation & Usage

1. Navigate to the [Releases](../../releases) page and download `AI_Coders_Proxy_Manager.exe`.
2. Run the executable (No installation required).
3. Click **Auto-Detect Port** or select your preset profile.
4. Click **Enable & Patch All Proxies** (or patch individual IDEs in the Dashboard).
5. Click **Test Latency** to verify live connection to Anthropic & Google APIs!

## 📖 Documentation
Check out [docs/ERRORS.md](docs/ERRORS.md) for deep dives into specific AI coding errors, or read our full [CHANGELOG.md](CHANGELOG.md) for version history.

---
*Built by a developer, for developers. Code without borders.*
