import os
import sys
import winreg
import subprocess
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from scanner import ScannerEngine, DetectedTarget, scan_proxy_ports
from patchers import TargetPatcher

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "AICodersProxyFixer"

class ProxyManagerCore:
    """
    Core logic for managing system, Git, Shells, and IDE proxies.
    Designed specifically to fix connection issues for AI coding assistants
    like Claude Code, Codex, Antigravity IDE, and Cursor.
    """

    def __init__(self, proxy_address: str = "127.0.0.1", proxy_port: str = "10808"):
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self._update_urls()

        self.scanner = ScannerEngine()
        self.patcher = TargetPatcher(self.proxy_address, self.proxy_port)

    def set_proxy_config(self, proxy_address: str, proxy_port: str):
        self.proxy_address = proxy_address.strip()
        self.proxy_port = proxy_port.strip()
        self._update_urls()
        self.patcher = TargetPatcher(self.proxy_address, self.proxy_port)

    def _update_urls(self):
        self.full_proxy_url = f"http://{self.proxy_address}:{self.proxy_port}"
        self.socks_proxy_url = f"socks5h://{self.proxy_address}:{self.proxy_port}"
        self.no_proxy_list = "localhost,127.0.0.1,::1"

    def check_status(self) -> bool:
        """Check if the system proxy is currently enabled via the Windows Registry."""
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
        """Enables system-wide, git, shells, and detected IDE proxies."""
        try:
            self._set_env_vars()
            self._set_system_proxy()
            self._set_git_proxy()
            self.patch_all_detected()
            return True, f"Proxy successfully enabled through {self.full_proxy_url}"
        except Exception as e:
            return False, f"Failed to enable proxy: {str(e)}"

    def disable_proxy(self) -> Tuple[bool, str]:
        """Disables all proxies and restores defaults."""
        try:
            self._clear_env_vars()
            self._clear_system_proxy()
            self._clear_git_proxy()
            self.unpatch_all_detected()
            return True, "Proxy successfully disabled. Direct connection restored."
        except Exception as e:
            return False, f"Failed to disable proxy: {str(e)}"

    def patch_all_detected(self) -> List[Tuple[str, bool, str]]:
        results = []
        targets = self.scanner.scan_all()
        for target in targets:
            if target.is_installed and target.config_path:
                ok, msg = self.patcher.patch_target(target.name, target.config_path)
                results.append((target.name, ok, msg))
        return results

    def unpatch_all_detected(self) -> List[Tuple[str, bool, str]]:
        results = []
        targets = self.scanner.scan_all()
        for target in targets:
            if target.config_path:
                ok, msg = self.patcher.unpatch_target(target.name, target.config_path)
                results.append((target.name, ok, msg))
        return results

    def test_api_latency(self) -> Dict[str, Tuple[Optional[int], str]]:
        """
        Test real HTTP/HTTPS round-trip latency and geoblock status to AI coding endpoints through the proxy.
        Returns: {endpoint_name: (latency_ms, status_label)}
        """
        endpoints = {
            "Claude API": "https://api.anthropic.com",
            "Google Cloud Code": "https://cloudcode-pa.googleapis.com",
            "Google Gemini": "https://generativelanguage.googleapis.com",
            "OpenAI / Codex": "https://api.openai.com",
            "Cursor AI": "https://api2.cursor.sh",
            "Codeium Backend": "https://web-backend.codeium.com"
        }
        results = {}
        proxy_url = self.full_proxy_url

        try:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            opener = urllib.request.build_opener(proxy_handler)

            for name, url in endpoints.items():
                start_time = time.time()
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'AI-Coders-Proxy-Fixer/2.0'})
                    with opener.open(req, timeout=3.5) as response:
                        latency_ms = int((time.time() - start_time) * 1000)
                        results[name] = (latency_ms, "OK")
                except urllib.error.HTTPError as e:
                    latency_ms = int((time.time() - start_time) * 1000)
                    if e.code in [400, 403]:
                        # Geoblocked or region restricted
                        results[name] = (latency_ms, "Geoblocked")
                    else:
                        # Connected to server (got HTTP response status)
                        results[name] = (latency_ms, f"HTTP {e.code}")
                except Exception:
                    results[name] = (None, "Timeout")
        except Exception:
            for name in endpoints:
                results[name] = (None, "Error")

        return results

    def set_start_with_windows(self, enable: bool) -> Tuple[bool, str]:
        """Configure app auto-start via Windows Registry HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                REG_RUN_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            if enable:
                # Use current executable or python script path
                exe_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                winreg.SetValueEx(key, APP_REG_NAME, 0, winreg.REG_SZ, exe_path)
                msg = "Start with Windows enabled."
            else:
                try:
                    winreg.DeleteValue(key, APP_REG_NAME)
                except FileNotFoundError:
                    pass
                msg = "Start with Windows disabled."
            winreg.CloseKey(key)
            return True, msg
        except Exception as e:
            return False, f"Failed to set Windows startup: {str(e)}"

    def check_start_with_windows(self) -> bool:
        """Check if Windows Auto-Start is enabled in Registry."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, APP_REG_NAME)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def _set_env_vars(self):
        subprocess.run(['setx', 'HTTP_PROXY', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['setx', 'HTTPS_PROXY', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['setx', 'ALL_PROXY', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['setx', 'NO_PROXY', self.no_proxy_list], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

        os.environ['HTTP_PROXY'] = self.full_proxy_url
        os.environ['HTTPS_PROXY'] = self.full_proxy_url
        os.environ['ALL_PROXY'] = self.full_proxy_url
        os.environ['NO_PROXY'] = self.no_proxy_list

    def _clear_env_vars(self):
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'HTTP_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'HTTPS_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'ALL_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['REG', 'delete', 'HKCU\\Environment', '/F', '/V', 'NO_PROXY'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY']:
            if var in os.environ:
                del os.environ[var]

    def _notify_windows_proxy_changed(self):
        try:
            import ctypes
            INTERNET_OPTION_SETTINGS_CHANGED = 39
            INTERNET_OPTION_REFRESH = 37
            wininet = ctypes.windll.wininet
            wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
            wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
        except Exception as e:
            print(f"WinInet refresh error: {e}")

        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.c_ulong()
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 2000, ctypes.byref(result)
            )
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Internet Settings", SMTO_ABORTIFHUNG, 2000, ctypes.byref(result)
            )
        except Exception as e:
            print(f"SettingChange broadcast error: {e}")

    def _set_system_proxy(self):
        reg_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(reg_key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(reg_key, "ProxyServer", 0, winreg.REG_SZ, f"{self.proxy_address}:{self.proxy_port}")
        winreg.SetValueEx(reg_key, "ProxyOverride", 0, winreg.REG_SZ, "<local>;127.0.0.1;localhost;::1")
        winreg.CloseKey(reg_key)
        self._notify_windows_proxy_changed()

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
            pass
        winreg.CloseKey(reg_key)
        self._notify_windows_proxy_changed()

    def _set_git_proxy(self):
        subprocess.run(['git', 'config', '--global', 'http.proxy', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['git', 'config', '--global', 'https.proxy', self.full_proxy_url], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def _clear_git_proxy(self):
        subprocess.run(['git', 'config', '--global', '--unset', 'http.proxy'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(['git', 'config', '--global', '--unset', 'https.proxy'], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
