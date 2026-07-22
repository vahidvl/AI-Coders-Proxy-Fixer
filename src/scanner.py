import os
import socket
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class TargetType:
    IDE = "IDE"
    SHELL = "Shell"
    CLI = "CLI Tool"

class DetectedTarget:
    def __init__(self, name: str, target_type: str, config_path: Optional[Path], is_installed: bool, is_patched: bool = False, details: str = "", icon_symbol: str = "💻", brand_color: str = "#311B92"):
        self.name = name
        self.target_type = target_type
        self.config_path = config_path
        self.is_installed = is_installed
        self.is_patched = is_patched
        self.details = details
        self.icon_symbol = icon_symbol
        self.brand_color = brand_color

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.target_type,
            "path": str(self.config_path) if self.config_path else None,
            "installed": self.is_installed,
            "patched": self.is_patched,
            "details": self.details,
            "icon_symbol": self.icon_symbol,
            "brand_color": self.brand_color
        }

COMMON_PROXY_PORTS = [
    (10808, "v2rayN / Happ Proxy (SOCKS5)"),
    (7890, "Clash / Mihomo / Sing-box (HTTP)"),
    (2080, "Hiddify Next / Sing-box (HTTP)"),
    (8080, "Hotspot Shield (HTTP Proxy)"),
    (10809, "v2rayN / Happ Proxy (HTTP Alt)"),
    (3080, "Happ Proxy (HTTP Alt)"),
    (1070, "Hiddify (HTTP Alt)"),
    (7897, "Clash Meta (SOCKS5 Alt)"),
    (1080, "Hotspot Shield / Standard SOCKS5"),
]

def scan_proxy_ports() -> List[Tuple[int, str]]:
    """Scan local machine for active listening proxy ports."""
    active_ports = []
    for port, name in COMMON_PROXY_PORTS:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.15)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                active_ports.append((port, name))
    return active_ports

class ScannerEngine:
    def __init__(self):
        self.appdata = os.environ.get('APPDATA', '')
        self.userprofile = os.environ.get('USERPROFILE', '')
        self.localappdata = os.environ.get('LOCALAPPDATA', '')

    def scan_all(self) -> List[DetectedTarget]:
        targets = []
        user_dir = Path(self.userprofile) if self.userprofile else Path.home()
        appdata_dir = Path(self.appdata) if self.appdata else user_dir / "AppData" / "Roaming"

        # 1. Antigravity IDE
        ag_ide_cfg = appdata_dir / "Antigravity IDE" / "User" / "settings.json"
        ag_ide_installed = ag_ide_cfg.parent.exists() or ag_ide_cfg.exists()
        ag_ide_patched = False
        if ag_ide_cfg.exists():
            try:
                data = json.loads(ag_ide_cfg.read_text(encoding='utf-8'))
                if data.get('http.proxy') or data.get('codeiumDev.languageServerEnv', {}).get('HTTP_PROXY'):
                    ag_ide_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Antigravity IDE", TargetType.IDE, ag_ide_cfg, ag_ide_installed, ag_ide_patched, "Installed" if ag_ide_installed else "Not found", "🚀", "#6200EA"))

        # 2. Antigravity CLI
        ag_cli_cfg = user_dir / ".antigravity" / "config.json"
        ag_cli_installed = ag_cli_cfg.parent.exists() or ag_cli_cfg.exists()
        ag_cli_patched = False
        if ag_cli_cfg.exists():
            try:
                data = json.loads(ag_cli_cfg.read_text(encoding='utf-8'))
                if "proxy" in data or "httpProxy" in data:
                    ag_cli_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Antigravity CLI", TargetType.CLI, ag_cli_cfg, ag_cli_installed, ag_cli_patched, "Installed" if ag_cli_installed else "Not found", "⚡", "#7C4DFF"))

        # 3. Claude Code CLI
        claude_cfg = user_dir / ".claude.json"
        claude_installed = claude_cfg.exists()
        claude_patched = False
        if claude_installed:
            try:
                data = json.loads(claude_cfg.read_text(encoding='utf-8'))
                if "httpProxy" in data or "proxy" in data:
                    claude_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Claude Code CLI", TargetType.CLI, claude_cfg, claude_installed, claude_patched, "Installed" if claude_installed else "Not found", "🤖", "#D84315"))

        # 4. OpenAI Codex / Copilot CLI
        codex_cfg = user_dir / ".copilot-cli" / "config.json"
        codex_installed = codex_cfg.parent.exists() or codex_cfg.exists()
        codex_patched = False
        if codex_cfg.exists():
            try:
                data = json.loads(codex_cfg.read_text(encoding='utf-8'))
                if "httpProxy" in data or "proxy" in data:
                    codex_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("OpenAI Codex CLI", TargetType.CLI, codex_cfg, codex_installed, codex_patched, "Installed" if codex_installed else "Not found", "💻", "#00897B"))

        # 5. VS Code
        vsc_cfg = appdata_dir / "Code" / "User" / "settings.json"
        vsc_installed = vsc_cfg.parent.exists() or vsc_cfg.exists()
        vsc_patched = False
        if vsc_cfg.exists():
            try:
                data = json.loads(vsc_cfg.read_text(encoding='utf-8'))
                if data.get('http.proxy'):
                    vsc_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("VS Code", TargetType.IDE, vsc_cfg, vsc_installed, vsc_patched, "Installed" if vsc_installed else "Not found", "🟦", "#1E88E5"))

        # 6. Cursor AI IDE
        cur_cfg = appdata_dir / "Cursor" / "User" / "settings.json"
        cur_installed = cur_cfg.parent.exists() or cur_cfg.exists()
        cur_patched = False
        if cur_cfg.exists():
            try:
                data = json.loads(cur_cfg.read_text(encoding='utf-8'))
                if data.get('http.proxy'):
                    cur_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Cursor AI IDE", TargetType.IDE, cur_cfg, cur_installed, cur_patched, "Installed" if cur_installed else "Not found", "🔮", "#8E24AA"))

        # 7. Windsurf IDE
        ws_cfg = appdata_dir / "Windsurf" / "User" / "settings.json"
        ws_installed = ws_cfg.parent.exists() or ws_cfg.exists()
        ws_patched = False
        if ws_cfg.exists():
            try:
                data = json.loads(ws_cfg.read_text(encoding='utf-8'))
                if data.get('http.proxy'):
                    ws_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Windsurf IDE", TargetType.IDE, ws_cfg, ws_installed, ws_patched, "Installed" if ws_installed else "Not found", "🏄", "#00ACC1"))

        # 8. OpenCode AI
        opencode_cfg = user_dir / ".opencode" / "config.json"
        opencode_installed = opencode_cfg.parent.exists() or opencode_cfg.exists()
        opencode_patched = False
        if opencode_cfg.exists():
            try:
                data = json.loads(opencode_cfg.read_text(encoding='utf-8'))
                if "proxy" in data or "httpProxy" in data:
                    opencode_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("OpenCode AI", TargetType.CLI, opencode_cfg, opencode_installed, opencode_patched, "Installed" if opencode_installed else "Not found", "🌐", "#43A047"))

        # 9. Qwen Coder / Qwen Agent
        qwen_cfg = user_dir / ".qwen" / "config.json"
        qwen_installed = qwen_cfg.parent.exists() or qwen_cfg.exists()
        qwen_patched = False
        if qwen_cfg.exists():
            try:
                data = json.loads(qwen_cfg.read_text(encoding='utf-8'))
                if "proxy" in data or "httpProxy" in data:
                    qwen_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Qwen Coder AI", TargetType.CLI, qwen_cfg, qwen_installed, qwen_patched, "Installed" if qwen_installed else "Not found", "🧠", "#FB8C00"))

        # 10. Continue.dev AI Extension
        cont_cfg = user_dir / ".continue" / "config.json"
        cont_installed = cont_cfg.parent.exists() or cont_cfg.exists()
        cont_patched = False
        if cont_cfg.exists():
            try:
                data = json.loads(cont_cfg.read_text(encoding='utf-8'))
                if "requestOptions" in data and "proxy" in data["requestOptions"]:
                    cont_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Continue.dev AI", TargetType.CLI, cont_cfg, cont_installed, cont_patched, "Installed" if cont_installed else "Not found", "⏩", "#E53935"))

        # 11. Aider AI CLI
        aider_cfg = user_dir / ".aider.conf.yml"
        aider_installed = aider_cfg.exists()
        aider_patched = False
        if aider_cfg.exists():
            try:
                content = aider_cfg.read_text(encoding='utf-8')
                if "http-proxy" in content:
                    aider_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Aider AI CLI", TargetType.CLI, aider_cfg, aider_installed, aider_patched, "Installed" if aider_installed else "Not found", "🐚", "#D81B60"))

        # 12. Supermaven AI
        sm_cfg = user_dir / ".supermaven" / "config.json"
        sm_installed = sm_cfg.parent.exists() or sm_cfg.exists()
        sm_patched = False
        if sm_cfg.exists():
            try:
                data = json.loads(sm_cfg.read_text(encoding='utf-8'))
                if "proxy" in data:
                    sm_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Supermaven AI", TargetType.CLI, sm_cfg, sm_installed, sm_patched, "Installed" if sm_installed else "Not found", "⚡", "#FDD835"))

        # 13. Cline / Roo Code Extensions
        cline_dir = user_dir / ".vscode" / "extensions"
        cline_installed = False
        cline_patched = False
        if cline_dir.exists():
            try:
                for item in cline_dir.iterdir():
                    if "saoudrizwan.claude-dev" in item.name or "roo-cline" in item.name:
                        cline_installed = True
                        break
            except Exception:
                pass
        targets.append(DetectedTarget("Cline / Roo Code", TargetType.IDE, cline_dir if cline_installed else None, cline_installed, cline_patched, "Installed" if cline_installed else "Not found", "🤖", "#8E24AA"))

        # 14. PowerShell Profile
        ps_profile = user_dir / "Documents" / "WindowsPowerShell" / "profile.ps1"
        if not ps_profile.exists():
            ps_profile = user_dir / "Documents" / "PowerShell" / "profile.ps1"
        ps_installed = ps_profile.parent.exists() or ps_profile.exists()
        ps_patched = False
        if ps_profile.exists():
            try:
                content = ps_profile.read_text(encoding='utf-8')
                if "HTTP_PROXY" in content:
                    ps_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("PowerShell Profile", TargetType.SHELL, ps_profile, ps_installed, ps_patched, "Installed" if ps_installed else "Not found", "⚡", "#0277BD"))

        # 15. Git Bash
        bashrc = user_dir / ".bashrc"
        bash_patched = False
        if bashrc.exists():
            try:
                content = bashrc.read_text(encoding='utf-8')
                if "HTTP_PROXY" in content:
                    bash_patched = True
            except Exception:
                pass
        targets.append(DetectedTarget("Git Bash (.bashrc)", TargetType.SHELL, bashrc, True, bash_patched, "Installed", "🐚", "#F4511E"))

        return targets
