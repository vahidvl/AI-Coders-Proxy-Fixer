# 🚀 AI Coders Proxy Fixer
<div align="center">
![Windows](https://img.shields.io/badge/OS-Windows-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Portable](https://img.shields.io/badge/Portable-Yes-success) ![Status](https://img.shields.io/badge/Status-Active-brightgreen)
</div>
<div align="center">
  <b><a href="README_fa.md">🇮🇷 مطالعه به زبان فارسی (Read in Persian)</a></b>
</div>

> A lightweight, open-source proxy manager designed specifically to resolve geoblocking, network timeouts, and corporate firewall restrictions for modern AI coding assistants.

⭐️ **If this tool saves you hours of debugging, please consider giving it a STAR! It helps other developers discover this solution.** ⭐️

<div align="center">
  <img src="assets/ui_sample.jpg" alt="UI Screenshot" width="600"/>
</div>

## 🌍 The Problem

Developers living in heavily restricted regions or working behind strict corporate firewalls frequently encounter severe connectivity issues with AI coding assistants. Standard VPNs and SOCKS5 proxies often fail because they disrupt internal Language Server routing (e.g., routing `localhost` traffic through the proxy).

This results in frustrating errors such as:
- ❌ `User location is not supported for the API use.` (HTTP 400 Bad Request)
- ❌ `Post "https://cloudcode-pa.googleapis.com/...": EOF`
- ❌ `Failed to check terminal shell support` (VS Code & Antigravity IDE)
- ❌ `ETIMEDOUT` or `Connection Refused` in Cursor
- ❌ Unresponsive Autonomous Agents

<div align="center">
  <img src="assets/agent_terminated.png" alt="Agent Terminated Error" width="48%"/>
  <img src="assets/cloudcode_eof.png" alt="CloudCode EOF Error" width="48%"/>
</div>

## 🎯 The Solution

**AI Coders Proxy Fixer** is a portable Windows GUI application that automates the complex network routing required to make AI assistants work seamlessly behind a proxy.

It intelligently injects proxy configurations into your IDEs while applying strict exception rules (bypassing `localhost` and `127.0.0.1`) to ensure local language servers never crash.

### ✨ Key Features
- **One-Click Toggle:** Enable or disable proxy routing globally with a single click.
- **Deep IDE Integration:** Automatically configures `settings.json` for **VS Code, Cursor, Void, and Antigravity IDE**.
- **System-Wide Variables:** Seamlessly sets Windows Environment Variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`).
- **Git Proxy Configuration:** Fixes hanging `git push` and `git pull` commands.
- **Unobtrusive:** Minimizes to the Windows System Tray for quick access.
- **100% Portable:** No installation required.

## 🛠️ Installation & Usage

1. Navigate to the [Releases](../../releases) page and download `AI_Coders_Proxy_Manager.exe`.
2. Run the executable (No installation required).
3. Enter your local proxy IP and Port (e.g., `127.0.0.1` and `10808` for v2ray/Nekoray clients).
4. Click **Enable Proxy**.
5. **Important:** Restart your IDE or terminal to allow the new environment variables to load.

## 📖 Documentation
For a deep dive into the specific AI coding errors this tool resolves (including log excerpts and community links), please review our comprehensive [Error Documentation](docs/ERRORS.md).

---
*Built by a developer, for developers. Code without borders.*
