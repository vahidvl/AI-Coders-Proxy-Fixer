# 🚀 AI Coders Proxy Fixer & Manager
> The ultimate, lightweight proxy GUI to bypass sanctions, fix network restrictions, and resolve connection timeouts for AI coding assistants (Claude Code, Antigravity IDE, Cursor, OpenAI Codex, and VS Code).

⭐️ **If this tool saves you hours of debugging and frustration, please consider giving it a STAR! It helps other developers find this solution.** ⭐️

## 🌍 Needs Assessment & Target Audience
This project was specifically built for developers living in or traveling to heavily restricted regions (such as **Iran, Russia, China, Syria, Cuba, etc.**), or developers working behind strict corporate firewalls. 

AI Coding assistants are incredible, but they are often geoblocked or have strict TLS/SSL proxy requirements that break when using standard VPNs, v2ray, or Shadowsocks. If you've ever tried to write code and suddenly your AI agent crashes with a `location not supported` or `EOF` error, this tool is for you.

## 🎯 Errors We Instantly Fix
If you've searched Reddit, GitHub Issues, or X (Twitter) for any of these errors, this tool is your permanent fix:

* ❌ **HTTP 400 Bad Request:** `User location is not supported for the API use.`
* ❌ **CloudCode EOF:** `Post "https://cloudcode-pa.googleapis.com/v1internal:loadCodeAssist": EOF`
* ❌ **Agent Crash:** `Agent terminated due to error. You can prompt the model to try again...`
* ❌ `failed to resolve cascade config: neither PlanModel nor RequestedModel specified`
* ❌ `failed to check terminal shell support: internal: internal error`
* ❌ `connection refused` or `ETIMEDOUT` in Cursor / Void
* ❌ Claude Code CLI failing to authenticate via proxy

## ✨ Features
- **1-Click Proxy Toggle:** Turn your proxy routing on or off instantly.
- **System-wide Integration:** Updates Windows Environment Variables (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`).
- **Deep IDE Injection:** Automatically updates proxy settings inside the `settings.json` of **VS Code, Antigravity IDE, Cursor, and Void**, while explicitly bypassing `localhost` to prevent local server crashes.
- **Git Global Config:** Automatically configures Git to use your proxy so `git push` and `git pull` stop hanging.
- **System Tray Ready:** Minimizes to your Windows taskbar. Set it and forget it!
- **100% Portable:** No installation required. Just download the `.exe` and run.

## 🛠 Installation & Usage Guide
1. **Download:** Go to the [Releases](#) tab and download `AI_Coders_Proxy_Manager.exe`.
2. **Run:** Double click the `.exe`. (It's completely portable, no installation needed).
3. **Configure:** Enter your local proxy IP and Port (e.g., `127.0.0.1:10808` for v2rayN or Nekoray).
4. **Activate:** Click **Enable Proxy**.
5. **Restart:** *Close and reopen your IDEs (VS Code, Antigravity) or Terminals to let the new environment variables take effect!*

## 📸 Screenshots & UI
*(Place your screenshots here by uploading them to the `assets/` folder)*
- [UI Screenshot](assets/ui_sample.jpg)
- [Error Before Fix](assets/error_sample.jpg)

## 📖 Deep Dive into Errors & Community Solutions
Check out our [docs/ERRORS.md](docs/ERRORS.md) file for a deep dive into the specific AI coding errors this tool resolves, along with community links and screenshots from Reddit and X.

---
**Made with ❤️ by a developer who just wanted to code in peace.**
**Don't forget to ⭐ Star the repo if it helped you!**
