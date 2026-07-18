import os
import winreg
import subprocess
import json
from pathlib import Path
from typing import List, Tuple

class ProxyManagerCore:
    """
    Core logic for managing system, Git, and IDE proxies.
    Designed specifically to fix connection issues for AI coding assistants
    like Claude Code, Codex, Antigravity IDE, and Cursor.
    """
    
    def __init__(self, proxy_address: str = "127.0.0.1", proxy_port: str = "10808"):
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.full_proxy_url = f"http://{self.proxy_address}:{self.proxy_port}"
        self.socks_proxy_url = f"socks5h://{self.proxy_address}:{self.proxy_port}"
        
        # Localhost bypass list
        self.no_proxy_list = "localhost,127.0.0.1,::1"
        self.no_proxy_array = ["localhost", "127.0.0.1", "::1"]
        
        # Supported IDEs based on their AppData roaming paths
        self.ide_paths = [
            "Code/User/settings.json",              # VS Code
            "Cursor/User/settings.json",            # Cursor
            "Void/User/settings.json",              # Void
            "Antigravity IDE/User/settings.json"    # Antigravity IDE
        ]

    def check_status(self) -> bool:
        """
        Check if the system proxy is currently enabled via the Windows Registry.
        """
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            )
            proxy_enable, _ = winreg.QueryValueEx(reg_key, "ProxyEnable")
            winreg.CloseKey(reg_key)
            return proxy_enable == 1
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking status: {e}")
            return False

    def enable_proxy(self) -> Tuple[bool, str]:
        """Enables system-wide, git, and IDE proxies."""
        try:
            self._set_env_vars()
            self._set_system_proxy()
            self._set_git_proxy()
            self._update_ide_settings(enable=True)
            return True, f"Proxy successfully enabled through {self.full_proxy_url}"
        except Exception as e:
            return False, f"Failed to enable proxy: {str(e)}"

    def disable_proxy(self) -> Tuple[bool, str]:
        """Disables all proxies and restores defaults."""
        try:
            self._clear_env_vars()
            self._clear_system_proxy()
            self._clear_git_proxy()
            self._update_ide_settings(enable=False)
            return True, "Proxy successfully disabled. Direct connection restored."
        except Exception as e:
            return False, f"Failed to disable proxy: {str(e)}"

    def _set_env_vars(self):
        # We use setx to make the changes persistent across terminal sessions
        subprocess.run(['setx', 'HTTP_PROXY', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['setx', 'HTTPS_PROXY', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['setx', 'ALL_PROXY', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['setx', 'NO_PROXY', self.no_proxy_list], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Also set in current process environment
        os.environ['HTTP_PROXY'] = self.full_proxy_url
        os.environ['HTTPS_PROXY'] = self.full_proxy_url
        os.environ['ALL_PROXY'] = self.full_proxy_url
        os.environ['NO_PROXY'] = self.no_proxy_list

    def _clear_env_vars(self):
        # Clearing environment variables in registry
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'HTTP_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'HTTPS_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'ALL_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'NO_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY']:
            if var in os.environ:
                del os.environ[var]

    def _set_system_proxy(self):
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
            0, 
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(reg_key, "ProxyServer", 0, winreg.REG_SZ, f"{self.proxy_address}:{self.proxy_port}")
        winreg.SetValueEx(reg_key, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.0.0.1;::1;<local>")
        winreg.CloseKey(reg_key)

    def _clear_system_proxy(self):
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
            0, 
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        try:
            winreg.DeleteValue(reg_key, "ProxyServer")
            winreg.DeleteValue(reg_key, "ProxyOverride")
        except FileNotFoundError:
            pass # Already deleted
        winreg.CloseKey(reg_key)

    def _set_git_proxy(self):
        subprocess.run(['git', 'config', '--global', 'http.proxy', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['git', 'config', '--global', 'https.proxy', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def _clear_git_proxy(self):
        subprocess.run(['git', 'config', '--global', '--unset', 'http.proxy'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['git', 'config', '--global', '--unset', 'https.proxy'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def _update_ide_settings(self, enable: bool):
        appdata = os.environ.get('APPDATA', '')
        if not appdata:
            return
            
        base_path = Path(appdata)
        for rel_path in self.ide_paths:
            settings_file = base_path / rel_path
            if not settings_file.exists():
                continue
                
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    data = json.loads(content) if content.strip() else {}
            except json.JSONDecodeError:
                # If the JSON is completely broken, we skip it
                print(f"Skipping {settings_file} due to malformed JSON.")
                continue

            if enable:
                data['http.proxy'] = self.full_proxy_url
                data['http.proxySupport'] = 'override'
                data['http.noProxy'] = self.no_proxy_array
                
                # Antigravity specific language server bypass
                if "Antigravity IDE" in rel_path.parts:
                    if "codeiumDev.languageServerEnv" not in data:
                        data["codeiumDev.languageServerEnv"] = {}
                    data["codeiumDev.languageServerEnv"]["HTTPS_PROXY"] = self.socks_proxy_url
                    data["codeiumDev.languageServerEnv"]["HTTP_PROXY"] = self.socks_proxy_url
                    data["codeiumDev.languageServerEnv"]["NO_PROXY"] = "localhost,127.0.0.1"

                # Fixing the 'failed to check terminal shell support' error
                data['terminal.integrated.shellIntegration.enabled'] = False
            else:
                data.pop('http.proxy', None)
                data.pop('http.proxySupport', None)
                data.pop('http.noProxy', None)
                data.pop('terminal.integrated.shellIntegration.enabled', None)
                
                if "Antigravity IDE" in rel_path.parts and "codeiumDev.languageServerEnv" in data:
                    env = data["codeiumDev.languageServerEnv"]
                    env.pop("HTTPS_PROXY", None)
                    env.pop("HTTP_PROXY", None)
                    env.pop("NO_PROXY", None)

            # Write it back nicely formatted
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
