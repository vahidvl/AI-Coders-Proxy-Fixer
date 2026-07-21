import os
import json
from pathlib import Path
from typing import Tuple, List

BLOCK_BEGIN = "# BEGIN AI-CODERS-PROXY"
BLOCK_END = "# END AI-CODERS-PROXY"

class TargetPatcher:
    def __init__(self, proxy_address: str = "127.0.0.1", proxy_port: str = "10808"):
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.full_proxy_url = f"http://{self.proxy_address}:{self.proxy_port}"
        self.socks_proxy_url = f"socks5h://{self.proxy_address}:{self.proxy_port}"
        self.no_proxy_list = "localhost,127.0.0.1,::1"
        self.no_proxy_array = ["localhost", "127.0.0.1", "::1"]

    def patch_target(self, name: str, config_path: Path) -> Tuple[bool, str]:
        """Route to appropriate patcher based on target type/name."""
        if not config_path:
            return False, "Target configuration path does not exist."

        try:
            if "profile.ps1" in str(config_path):
                return self.patch_powershell(config_path)
            elif ".bashrc" in str(config_path):
                return self.patch_bash(config_path)
            elif ".claude.json" in str(config_path):
                return self.patch_claude_cli(config_path)
            else:
                # Default to IDE JSON settings patcher
                return self.patch_ide(config_path, is_antigravity=("Antigravity" in name or "Antigravity" in str(config_path)))
        except Exception as e:
            return False, f"Failed to patch {name}: {str(e)}"

    def unpatch_target(self, name: str, config_path: Path) -> Tuple[bool, str]:
        """Route to appropriate unpatcher based on target type/name."""
        if not config_path or not config_path.exists():
            return True, f"{name} is already unpatched."

        try:
            if "profile.ps1" in str(config_path) or ".bashrc" in str(config_path):
                return self.unpatch_shell(config_path)
            elif ".claude.json" in str(config_path):
                return self.unpatch_claude_cli(config_path)
            else:
                return self.unpatch_ide(config_path, is_antigravity=("Antigravity" in name or "Antigravity" in str(config_path)))
        except Exception as e:
            return False, f"Failed to unpatch {name}: {str(e)}"

    def patch_ide(self, config_path: Path, is_antigravity: bool = False) -> Tuple[bool, str]:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if config_path.exists():
            try:
                content = config_path.read_text(encoding='utf-8')
                if content.strip():
                    data = json.loads(content)
            except json.JSONDecodeError:
                pass

        data['http.proxy'] = self.full_proxy_url
        data['http.proxySupport'] = 'override'
        data['http.noProxy'] = self.no_proxy_array
        data['terminal.integrated.shellIntegration.enabled'] = False

        if is_antigravity:
            if "codeiumDev.languageServerEnv" not in data:
                data["codeiumDev.languageServerEnv"] = {}
            data["codeiumDev.languageServerEnv"]["HTTPS_PROXY"] = self.socks_proxy_url
            data["codeiumDev.languageServerEnv"]["HTTP_PROXY"] = self.socks_proxy_url
            data["codeiumDev.languageServerEnv"]["NO_PROXY"] = self.no_proxy_list

        config_path.write_text(json.dumps(data, indent=4), encoding='utf-8')
        return True, f"Successfully patched IDE settings at {config_path.name}"

    def unpatch_ide(self, config_path: Path, is_antigravity: bool = False) -> Tuple[bool, str]:
        if not config_path.exists():
            return True, "File does not exist."

        try:
            content = config_path.read_text(encoding='utf-8')
            data = json.loads(content) if content.strip() else {}
        except Exception:
            return False, "Failed to read JSON file."

        data.pop('http.proxy', None)
        data.pop('http.proxySupport', None)
        data.pop('http.noProxy', None)
        data.pop('terminal.integrated.shellIntegration.enabled', None)

        if is_antigravity and "codeiumDev.languageServerEnv" in data:
            env = data["codeiumDev.languageServerEnv"]
            env.pop("HTTPS_PROXY", None)
            env.pop("HTTP_PROXY", None)
            env.pop("NO_PROXY", None)

        config_path.write_text(json.dumps(data, indent=4), encoding='utf-8')
        return True, f"Successfully unpatched {config_path.name}"

    def patch_powershell(self, profile_path: Path) -> Tuple[bool, str]:
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        content = profile_path.read_text(encoding='utf-8') if profile_path.exists() else ""
        
        # Remove old block if exists
        lines = [line for line in content.splitlines() if not (BLOCK_BEGIN in line or BLOCK_END in line or "$env:HTTP_PROXY" in line or "$env:HTTPS_PROXY" in line or "$env:NO_PROXY" in line)]
        
        ps_block = f"{BLOCK_BEGIN}\n$env:HTTP_PROXY=\"{self.full_proxy_url}\"\n$env:HTTPS_PROXY=\"{self.full_proxy_url}\"\n$env:NO_PROXY=\"{self.no_proxy_list}\"\n{BLOCK_END}"
        new_content = "\n".join(lines).strip() + "\n\n" + ps_block + "\n"
        
        profile_path.write_text(new_content, encoding='utf-8')
        return True, "Successfully patched PowerShell profile."

    def patch_bash(self, bashrc_path: Path) -> Tuple[bool, str]:
        bashrc_path.parent.mkdir(parents=True, exist_ok=True)
        content = bashrc_path.read_text(encoding='utf-8') if bashrc_path.exists() else ""

        lines = [line for line in content.splitlines() if not (BLOCK_BEGIN in line or BLOCK_END in line or "export HTTP_PROXY=" in line or "export HTTPS_PROXY=" in line or "export NO_PROXY=" in line)]

        bash_block = f"{BLOCK_BEGIN}\nexport HTTP_PROXY=\"{self.full_proxy_url}\"\nexport HTTPS_PROXY=\"{self.full_proxy_url}\"\nexport NO_PROXY=\"{self.no_proxy_list}\"\n{BLOCK_END}"
        new_content = "\n".join(lines).strip() + "\n\n" + bash_block + "\n"

        bashrc_path.write_text(new_content, encoding='utf-8')
        return True, "Successfully patched Git Bash .bashrc"

    def unpatch_shell(self, shell_path: Path) -> Tuple[bool, str]:
        if not shell_path.exists():
            return True, "Profile file does not exist."

        content = shell_path.read_text(encoding='utf-8')
        lines = [line for line in content.splitlines() if not (BLOCK_BEGIN in line or BLOCK_END in line or "HTTP_PROXY" in line or "HTTPS_PROXY" in line or "NO_PROXY" in line)]
        shell_path.write_text("\n".join(lines).strip() + "\n", encoding='utf-8')
        return True, f"Successfully unpatched {shell_path.name}"

    def patch_claude_cli(self, config_path: Path) -> Tuple[bool, str]:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding='utf-8'))
            except Exception:
                pass

        data['httpProxy'] = self.full_proxy_url
        data['httpsProxy'] = self.full_proxy_url
        config_path.write_text(json.dumps(data, indent=4), encoding='utf-8')
        return True, "Successfully patched Claude Code CLI config"

    def unpatch_claude_cli(self, config_path: Path) -> Tuple[bool, str]:
        if not config_path.exists():
            return True, "Config file does not exist."

        try:
            data = json.loads(config_path.read_text(encoding='utf-8'))
            data.pop('httpProxy', None)
            data.pop('httpsProxy', None)
            config_path.write_text(json.dumps(data, indent=4), encoding='utf-8')
            return True, "Successfully unpatched Claude Code CLI config"
        except Exception as e:
            return False, f"Failed to unpatch Claude CLI: {str(e)}"
