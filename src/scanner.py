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
    def __init__(self, name: str, target_type: str, config_path: Optional[Path], is_installed: bool, is_patched: bool = False, details: str = ""):
        self.name = name
        self.target_type = target_type
        self.config_path = config_path
        self.is_installed = is_installed
        self.is_patched = is_patched
        self.details = details

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.target_type,
            "path": str(self.config_path) if self.config_path else None,
            "installed": self.is_installed,
            "patched": self.is_patched,
            "details": self.details
        }

COMMON_PROXY_PORTS = [
    (10808, "v2rayN (SOCKS5 / HTTP)"),
    (7890, "Clash / Mihomo (HTTP)"),
    (2080, "Hiddify / Sing-Box (HTTP)"),
    (10809, "v2rayN (HTTP Alt)"),
    (1080, "Standard SOCKS5"),
    (7891, "Clash SOCKS5"),
    (8080, "Generic HTTP Proxy"),
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

    def scan_all(self) -> List[DetectedTarget]:
        targets = []
        targets.extend(self.scan_ides())
        targets.extend(self.scan_shells())
        targets.extend(self.scan_clis())
        return targets

    def scan_ides(self) -> List[DetectedTarget]:
        ides = []
        if not self.appdata:
            return ides

        base = Path(self.appdata)
        ide_configs = [
            ("Antigravity IDE", base / "Antigravity IDE" / "User" / "settings.json"),
            ("VS Code", base / "Code" / "User" / "settings.json"),
            ("Cursor", base / "Cursor" / "User" / "settings.json"),
            ("Void Editor", base / "Void" / "User" / "settings.json"),
            ("VS Code Insiders", base / "Code - Insiders" / "User" / "settings.json"),
            ("Sublime Text", base / "Sublime Text" / "Packages" / "User" / "Preferences.sublime-settings"),
        ]

        for name, config_file in ide_configs:
            is_installed = config_file.parent.exists() or config_file.exists()
            is_patched = False
            details = "Not installed"

            if is_installed:
                details = "Installed"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if data.get('http.proxy') or data.get('http.proxySupport') == 'override':
                                is_patched = True
                                details = "Patched (Proxy configured)"
                    except Exception:
                        details = "Installed (Config unreadable)"

            ides.append(DetectedTarget(
                name=name,
                target_type=TargetType.IDE,
                config_path=config_file if config_file.exists() else (config_file.parent if config_file.parent.exists() else None),
                is_installed=is_installed,
                is_patched=is_patched,
                details=details
            ))

        return ides

    def scan_shells(self) -> List[DetectedTarget]:
        shells = []
        if not self.userprofile:
            return shells

        user_dir = Path(self.userprofile)

        # 1. PowerShell Profile
        ps_profile = user_dir / "Documents" / "WindowsPowerShell" / "profile.ps1"
        if not ps_profile.exists():
            ps_profile = user_dir / "Documents" / "PowerShell" / "profile.ps1"

        ps_installed = ps_profile.parent.exists() or ps_profile.exists()
        ps_patched = False
        ps_details = "Not configured"
        if ps_profile.exists():
            try:
                content = ps_profile.read_text(encoding='utf-8')
                if "# BEGIN AI-CODERS-PROXY" in content or "HTTP_PROXY" in content:
                    ps_patched = True
                    ps_details = "Patched"
            except Exception:
                pass

        shells.append(DetectedTarget(
            name="PowerShell Profile",
            target_type=TargetType.SHELL,
            config_path=ps_profile,
            is_installed=ps_installed,
            is_patched=ps_patched,
            details=ps_details
        ))

        # 2. Git Bash (.bashrc)
        bashrc = user_dir / ".bashrc"
        bash_installed = True # Git bash is usually present if git is
        bash_patched = False
        bash_details = "Not configured"
        if bashrc.exists():
            try:
                content = bashrc.read_text(encoding='utf-8')
                if "# BEGIN AI-CODERS-PROXY" in content or "HTTP_PROXY" in content:
                    bash_patched = True
                    bash_details = "Patched"
            except Exception:
                pass

        shells.append(DetectedTarget(
            name="Git Bash (.bashrc)",
            target_type=TargetType.SHELL,
            config_path=bashrc,
            is_installed=bash_installed,
            is_patched=bash_patched,
            details=bash_details
        ))

        return shells

    def scan_clis(self) -> List[DetectedTarget]:
        clis = []
        if not self.userprofile:
            return clis

        user_dir = Path(self.userprofile)

        # 1. Claude Code CLI Config
        claude_cfg = user_dir / ".claude.json"
        is_installed = claude_cfg.exists()
        is_patched = False
        details = "Installed" if is_installed else "Not found"

        if is_installed:
            try:
                data = json.loads(claude_cfg.read_text(encoding='utf-8'))
                if "httpProxy" in data or "proxy" in data:
                    is_patched = True
                    details = "Patched"
            except Exception:
                pass

        clis.append(DetectedTarget(
            name="Claude Code CLI",
            target_type=TargetType.CLI,
            config_path=claude_cfg if is_installed else None,
            is_installed=is_installed,
            is_patched=is_patched,
            details=details
        ))

        return clis
