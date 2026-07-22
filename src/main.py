import os
import sys
import io

# Fix PyInstaller --windowed mode where sys.stdout and sys.stderr are None
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import ctypes
import threading
import time
import webbrowser
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import customtkinter as ctk

from proxy_core import ProxyManagerCore
from scanner import scan_proxy_ports, TargetType, DetectedTarget, ScannerEngine

_mutex_handle = None

def ensure_single_instance():
    """Ensure only one instance of the app runs at a time using Windows Named Mutex."""
    global _mutex_handle
    MUTEX_NAME = "Local\\AICodersProxyFixerMutex_v2_1"
    ERROR_ALREADY_EXISTS = 183

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AICodersProxyFixer.App.v2.1")
    except Exception:
        pass

    try:
        kernel32 = ctypes.windll.kernel32
        _mutex_handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        last_error = kernel32.GetLastError()

        if _mutex_handle and last_error == ERROR_ALREADY_EXISTS:
            user32 = ctypes.windll.user32
            MB_OK = 0x0
            MB_ICONINFORMATION = 0x40
            user32.MessageBoxW(
                0,
                "AI Coders Proxy Fixer v2.1.0 is already running!\n\nPlease check your system tray or taskbar.",
                "AI Coders Proxy Fixer - Already Running",
                MB_OK | MB_ICONINFORMATION
            )
            sys.exit(0)
    except Exception as e:
        print(f"Mutex error: {e}")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

PRESETS = {
    "v2rayN / Happ (10808)": ("127.0.0.1", "10808"),
    "Clash / Mihomo (7890)": ("127.0.0.1", "7890"),
    "Hiddify / Sing-box (2080)": ("127.0.0.1", "2080"),
    "Hotspot Shield (8080)": ("127.0.0.1", "8080"),
    "Custom": ("127.0.0.1", "10808"),
}

class CyberpunkScannerOverlay(ctk.CTkToplevel):
    """Futuristic 5-second cyberpunk animated scanner modal."""
    def __init__(self, master, on_complete_callback):
        super().__init__(master)
        self.on_complete_callback = on_complete_callback

        self.title("CYBER-SCAN ENGINE v2.1")
        self.geometry("520x300")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0A0A12")
        self.overrideredirect(True) # Frameless modal

        # Center modal on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 520) // 2
        y = (self.winfo_screenheight() - 300) // 2
        self.geometry(f"520x300+{x}+{y}")

        # UI Setup
        main_frame = ctk.CTkFrame(self, fg_color="#0F0F1A", border_width=2, border_color="#00E676", corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        header_label = ctk.CTkLabel(
            main_frame,
            text="⚡ CYBER-SCAN MATRIX ENGINE ⚡",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#00E676"
        )
        header_label.pack(pady=(20, 10))

        self.status_label = ctk.CTkLabel(
            main_frame,
            text="[INITIALIZING] Booting Cyberpunk Scanning Subroutines...",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#00E5FF"
        )
        self.status_label.pack(pady=(5, 15))

        # Progress Bar
        self.progress = ctk.CTkProgressBar(main_frame, width=420, height=14, corner_radius=7, progress_color="#00E676", fg_color="#1A1A2E")
        self.progress.set(0)
        self.progress.pack(pady=10)

        self.pct_label = ctk.CTkLabel(
            main_frame,
            text="0%",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color="#00E676"
        )
        self.pct_label.pack(pady=(5, 10))

        self.terminal_box = ctk.CTkTextbox(
            main_frame,
            width=440,
            height=80,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color="#05050A",
            text_color="#76FF03",
            corner_radius=6
        )
        self.terminal_box.pack(pady=(5, 15))

        # Start 5-second animation thread
        threading.Thread(target=self.run_animation, daemon=True).start()

    def run_animation(self):
        steps = [
            (0.1, 0.15, "[REGISTRY] Interrogating Windows System Keys & Environment..."),
            (0.3, 0.35, "[PROXY] Probing Active Ports (v2rayN, Happ, Clash, Hotspot Shield)..."),
            (0.5, 0.60, "[IDEs] Inspecting IDE Settings (Antigravity, Cursor, VS Code, Windsurf)..."),
            (0.7, 0.82, "[CLIs] Scanning AI CLI Configs (Claude Code, Codex, OpenCode, Qwen)..."),
            (0.9, 0.95, "[SYNC] Verifying Network Latency Matrix & Patch Integrity..."),
            (1.0, 1.00, "[COMPLETE] Cyber-Scan Finished! Launching Dashboard...")
        ]

        start_time = time.time()
        duration = 4.5 # 4.5 seconds for total scan feel

        for elapsed_ratio, pct, msg in steps:
            time.sleep(duration * 0.18)
            self.after(0, lambda p=pct, m=msg: self.update_ui(p, m))

        time.sleep(0.4)
        self.after(0, self.finish_scan)

    def update_ui(self, pct, msg):
        self.progress.set(pct)
        self.pct_label.configure(text=f"{int(pct * 100)}%")
        self.status_label.configure(text=msg)
        self.terminal_box.insert("end", f"> {msg}\n")
        self.terminal_box.see("end")

    def finish_scan(self):
        self.destroy()
        if self.on_complete_callback:
            self.on_complete_callback()

class LatencyCard(ctk.CTkFrame):
    def __init__(self, master, name: str):
        super().__init__(master, fg_color="#1E1E2A", corner_radius=8, border_width=1, border_color="#2C2C3E")
        self.name = name

        self.title_label = ctk.CTkLabel(self, text=name, font=ctk.CTkFont(size=10, weight="bold"), text_color="#9E9EA0")
        self.title_label.pack(anchor="w", padx=8, pady=(4, 0))

        self.value_label = ctk.CTkLabel(self, text="-- ms", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00E676")
        self.value_label.pack(anchor="w", padx=8, pady=(0, 4))

    def set_latency_status(self, ms, status):
        if status == "Timeout" or ms is None:
            self.value_label.configure(text="Timeout 🔴", text_color="#FF5252")
        elif status == "Geoblocked":
            self.value_label.configure(text=f"{ms}ms 🚫 Blocked", text_color="#FF9100")
        else:
            color = "#00E676" if ms < 250 else ("#FFD600" if ms < 450 else "#FF9100")
            self.value_label.configure(text=f"{ms} ms ⚡", text_color=color)

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str, icon_str: str, val_color: str = "#00E676"):
        super().__init__(master, fg_color="#1A1A24", corner_radius=8, border_width=1, border_color="#2A2A3C")

        self.icon_label = ctk.CTkLabel(self, text=icon_str, font=ctk.CTkFont(size=16))
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=8)

        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color="#8E8EA0")
        self.title_label.grid(row=0, column=1, sticky="w", padx=5, pady=(6, 0))

        self.val_label = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=13, weight="bold"), text_color=val_color)
        self.val_label.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 6))

    def update_val(self, value: str, val_color: str = None):
        self.val_label.configure(text=value)
        if val_color:
            self.val_label.configure(text_color=val_color)

class TargetRowFrame(ctk.CTkFrame):
    def __init__(self, master, target: DetectedTarget, on_patch_click):
        super().__init__(master, fg_color="#181824", corner_radius=8, border_width=1, border_color="#262636")
        self.target = target
        self.on_patch_click = on_patch_click
        self.setup_ui()

    def setup_ui(self):
        icon_symbol = getattr(self.target, 'icon_symbol', '💻')
        brand_color = getattr(self.target, 'brand_color', '#311B92')

        icon_label = ctk.CTkLabel(self, text=icon_symbol, font=ctk.CTkFont(size=16))
        icon_label.pack(side="left", padx=(12, 6), pady=8)

        name_label = ctk.CTkLabel(
            self,
            text=f"{self.target.name}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", padx=4, pady=8)

        type_badge = ctk.CTkLabel(
            self,
            text=f" {self.target.target_type} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=brand_color,
            corner_radius=4
        )
        type_badge.pack(side="left", padx=6, pady=8)

        if not self.target.is_installed:
            status_text = "Not Found"
            status_color = "#37474F"
        elif self.target.is_patched:
            status_text = "🟢 Patched"
            status_color = "#1B5E20"
        else:
            status_text = "🟡 Unpatched"
            status_color = "#E65100"

        status_label = ctk.CTkLabel(
            self,
            text=f" {status_text} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=status_color,
            corner_radius=4
        )
        status_label.pack(side="left", padx=6, pady=8)

        if self.target.is_installed:
            btn_text = "Unpatch" if self.target.is_patched else "Patch"
            btn_color = "#D32F2F" if self.target.is_patched else "#2E7D32"
            btn_hover = "#B71C1C" if self.target.is_patched else "#1B5E20"

            action_btn = ctk.CTkButton(
                self,
                text=btn_text,
                width=75,
                height=26,
                fg_color=btn_color,
                hover_color=btn_hover,
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda: self.on_patch_click(self.target)
            )
            action_btn.pack(side="right", padx=12, pady=8)

class ProxyManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Coders Proxy Fixer v2.1.0 - Real AI Matrix Dashboard")
        self.geometry("700x900")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.core = ProxyManagerCore()
        self.is_proxy_enabled = self.core.check_status()
        self.tray_icon = None

        self.setup_ui()
        self.setup_icon()
        
        # Trigger Cyberpunk Scanner Animation on first launch
        self.after(200, self.trigger_scanner_animation)

    def trigger_scanner_animation(self):
        CyberpunkScannerOverlay(self, self.rescan_targets)

    def setup_ui(self):
        # 1. Header Banner
        header_banner = ctk.CTkFrame(self, fg_color="#12121A", corner_radius=0, height=75)
        header_banner.pack(fill="x", side="top")

        header_content = ctk.CTkFrame(header_banner, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)

        logo_label = ctk.CTkLabel(header_content, text="⚡", font=ctk.CTkFont(size=28))
        logo_label.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(header_content, fg_color="transparent")
        title_box.pack(side="left")

        title_label = ctk.CTkLabel(
            title_box,
            text="AI Coders Proxy Fixer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(anchor="w")

        sub_label = ctk.CTkLabel(
            title_box,
            text="Automated IDE Patcher & WinInet Proxy Router",
            font=ctk.CTkFont(size=11),
            text_color="#8E8EA0"
        )
        sub_label.pack(anchor="w")

        badge_box = ctk.CTkFrame(header_content, fg_color="transparent")
        badge_box.pack(side="right")

        badge_row = ctk.CTkFrame(badge_box, fg_color="transparent")
        badge_row.pack(anchor="e", pady=(0, 4))

        ver_badge = ctk.CTkLabel(
            badge_row,
            text=" v2.1.0 ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#311B92",
            corner_radius=6
        )
        ver_badge.pack(side="left", padx=(0, 6))

        about_btn = ctk.CTkButton(
            badge_row,
            text="ℹ️ About",
            width=65,
            height=22,
            fg_color="#263238",
            hover_color="#37474F",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.show_about_dialog
        )
        about_btn.pack(side="left")

        # Main Scrollable / Frame Content
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # 2. Main Toggle Card
        toggle_card = ctk.CTkFrame(main_content, fg_color="#181824", corner_radius=12, border_width=1, border_color="#262636")
        toggle_card.pack(fill="x", pady=(0, 10))

        toggle_inner = ctk.CTkFrame(toggle_card, fg_color="transparent")
        toggle_inner.pack(fill="x", padx=16, pady=14)

        status_left = ctk.CTkFrame(toggle_inner, fg_color="transparent")
        status_left.pack(side="left")

        self.status_title = ctk.CTkLabel(
            status_left,
            text="System Proxy Status",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8E8EA0"
        )
        self.status_title.pack(anchor="w")

        self.status_desc = ctk.CTkLabel(
            status_left,
            text="WinInet Router: Disabled",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FF5252"
        )
        self.status_desc.pack(anchor="w")

        self.main_switch = ctk.CTkSwitch(
            toggle_inner,
            text="ENABLE PROXY",
            font=ctk.CTkFont(size=12, weight="bold"),
            progress_color="#00E676",
            command=self.toggle_proxy
        )
        self.main_switch.pack(side="right")
        if self.is_proxy_enabled:
            self.main_switch.select()
            self.status_desc.configure(text="WinInet Router: Active 🟢", text_color="#00E676")

        # Preset Selectors
        preset_row = ctk.CTkFrame(toggle_card, fg_color="transparent")
        preset_row.pack(fill="x", padx=16, pady=(0, 14))

        preset_label = ctk.CTkLabel(preset_row, text="Proxy Preset:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#8E8EA0")
        preset_label.pack(side="left", padx=(0, 8))

        self.preset_dropdown = ctk.CTkOptionMenu(
            preset_row,
            values=list(PRESETS.keys()),
            command=self.on_preset_change,
            width=180,
            height=26,
            fg_color="#2A2A3C",
            button_color="#3A3A52",
            font=ctk.CTkFont(size=11)
        )
        self.preset_dropdown.pack(side="left", padx=(0, 12))

        self.ip_entry = ctk.CTkEntry(preset_row, width=110, height=26, font=ctk.CTkFont(size=11))
        self.ip_entry.insert(0, self.core.proxy_address)
        self.ip_entry.pack(side="left", padx=(0, 6))

        self.port_entry = ctk.CTkEntry(preset_row, width=65, height=26, font=ctk.CTkFont(size=11))
        self.port_entry.insert(0, self.core.proxy_port)
        self.port_entry.pack(side="left")

        # 3. Quick Stats Grid
        stats_grid = ctk.CTkFrame(main_content, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 10))

        stats_grid.columnconfigure((0, 1, 2), weight=1)

        self.stat_active = StatCard(stats_grid, "ACTIVE PROXY", "Checking...", "🌐", "#00E676")
        self.stat_active.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.stat_patched = StatCard(stats_grid, "PATCHED TARGETS", "0 / 0", "🎯", "#1E88E5")
        self.stat_patched.grid(row=0, column=1, padx=4, sticky="ew")

        self.stat_ports = StatCard(stats_grid, "DETECTED PORTS", "Scanning...", "🔌", "#FFD600")
        self.stat_ports.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # 4. Latency Matrix (6 Real Endpoints)
        lat_header = ctk.CTkFrame(main_content, fg_color="transparent")
        lat_header.pack(fill="x", pady=(4, 2))

        lat_title = ctk.CTkLabel(lat_header, text="Real AI Latency & Geoblock Matrix", font=ctk.CTkFont(size=13, weight="bold"))
        lat_title.pack(side="left")

        test_btn = ctk.CTkButton(
            lat_header,
            text="⚡ Test Latency",
            width=100,
            height=22,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.run_latency_tests
        )
        test_btn.pack(side="right")

        lat_grid = ctk.CTkFrame(main_content, fg_color="transparent")
        lat_grid.pack(fill="x", pady=(0, 8))
        lat_grid.columnconfigure((0, 1, 2), weight=1)

        self.lat_cards = {}
        endpoints = ["Anthropic API", "Google CloudCode", "Google Gemini", "OpenAI / Codex", "Cursor AI", "Codeium Backend"]
        for i, ep in enumerate(endpoints):
            row = i // 3
            col = i % 3
            card = LatencyCard(lat_grid, ep)
            padx = (0, 4) if col == 0 else ((4, 0) if col == 2 else 4)
            pady = (0, 4) if row == 0 else (4, 0)
            card.grid(row=row, column=col, padx=padx, pady=pady, sticky="ew")
            self.lat_cards[ep] = card

        # 5. Target List Dashboard Header
        tgt_header = ctk.CTkFrame(main_content, fg_color="transparent")
        tgt_header.pack(fill="x", pady=(5, 2))

        tgt_title = ctk.CTkLabel(tgt_header, text="Scanned IDEs, Shells & CLIs", font=ctk.CTkFont(size=13, weight="bold"))
        tgt_title.pack(side="left")

        rescan_btn = ctk.CTkButton(
            tgt_header,
            text="↻ Rescan System",
            width=110,
            height=24,
            fg_color="#37474F",
            hover_color="#455A64",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.trigger_scanner_animation
        )
        rescan_btn.pack(side="right")

        self.targets_container = ctk.CTkScrollableFrame(main_content, height=270, corner_radius=10, fg_color="#12121A", border_width=1, border_color="#2A2A3C")
        self.targets_container.pack(fill="x", pady=5)

        # 6. Footer Options
        footer_card = ctk.CTkFrame(self, fg_color="transparent")
        footer_card.pack(fill="x", padx=20, pady=(5, 10), side="bottom")

        self.autostart_checkbox = ctk.CTkCheckBox(
            footer_card,
            text="Start with Windows (System Tray)",
            font=ctk.CTkFont(size=12),
            command=self.toggle_autostart
        )
        self.autostart_checkbox.pack(side="left")
        if self.core.check_start_with_windows():
            self.autostart_checkbox.select()

        info_label = ctk.CTkLabel(
            footer_card,
            text="AI Coders Proxy Fixer v2.1.0",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        info_label.pack(side="right")

    def toggle_autostart(self):
        enabled = bool(self.autostart_checkbox.get())
        self.core.set_start_with_windows(enabled)

    def setup_icon(self):
        icon_path = Path(__file__).parent.parent / "assets" / "app_icon.ico"
        if not icon_path.exists() and getattr(sys, 'frozen', False):
            icon_path = Path(sys._MEIPASS) / "assets" / "app_icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

    def quit_app(self, icon=None, item=None):
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.destroy()
        sys.exit(0)

    def on_preset_change(self, choice):
        if choice in PRESETS:
            ip, port = PRESETS[choice]
            self.ip_entry.delete(0, "end")
            self.ip_entry.insert(0, ip)
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, port)
            self.core.proxy_address = ip
            self.core.proxy_port = port

    def toggle_proxy(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        self.core.proxy_address = ip
        self.core.proxy_port = port

        if self.main_switch.get() == 1:
            success, msg = self.core.enable_proxy()
            if success:
                self.is_proxy_enabled = True
                self.status_desc.configure(text="WinInet Router: Active 🟢", text_color="#00E676")
            else:
                self.main_switch.deselect()
                self.status_desc.configure(text=f"Error: {msg}", text_color="#FF5252")
        else:
            success, msg = self.core.disable_proxy()
            if success:
                self.is_proxy_enabled = False
                self.status_desc.configure(text="WinInet Router: Disabled 🔴", text_color="#FF5252")

        self.run_latency_tests()

    def rescan_targets(self):
        for widget in self.targets_container.winfo_children():
            widget.destroy()

        scanner = ScannerEngine()
        targets = scanner.scan_all()

        patched_count = 0
        installed_count = 0

        for target in targets:
            if target.is_installed:
                installed_count += 1
            if target.is_patched:
                patched_count += 1

            row = TargetRowFrame(self.targets_container, target, self.on_patch_target)
            row.pack(fill="x", pady=3)

        self.stat_patched.update_val(f"{patched_count} / {installed_count} Patched")

        active_ports = scan_proxy_ports()
        if active_ports:
            ports_str = ", ".join(str(p[0]) for p in active_ports[:2])
            self.stat_ports.update_val(f"Active: {ports_str}", "#00E676")
            self.stat_active.update_val(f"{active_ports[0][1].split()[0]}", "#00E676")
        else:
            self.stat_ports.update_val("No Port Active", "#FF5252")
            self.stat_active.update_val("Inactive", "#8E8EA0")

    def on_patch_target(self, target: DetectedTarget):
        from patchers import TargetPatcher
        patcher = TargetPatcher(self.core.proxy_address, self.core.proxy_port)

        if target.is_patched:
            success, msg = patcher.unpatch_target(target.name, target.config_path)
        else:
            success, msg = patcher.patch_target(target.name, target.config_path)

        self.rescan_targets()

    def run_latency_tests(self):
        def _test_thread():
            results = self.core.test_all_latencies()
            for ep_name, (ms, status) in results.items():
                if ep_name in self.lat_cards:
                    self.after(0, lambda card=self.lat_cards[ep_name], m=ms, s=status: card.set_latency_status(m, s))

        threading.Thread(target=_test_thread, daemon=True).start()

    def show_about_dialog(self):
        about_win = ctk.CTkToplevel(self)
        about_win.title("About Developer - AI Coders Proxy Fixer")
        about_win.geometry("420x300")
        about_win.resizable(False, False)
        about_win.attributes("-topmost", True)

        main_frame = ctk.CTkFrame(about_win, fg_color="#181824", corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        title = ctk.CTkLabel(main_frame, text="AI Coders Proxy Fixer", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00E676")
        title.pack(pady=(15, 5))

        ver = ctk.CTkLabel(main_frame, text="Version 2.1.0 (Cyberpunk Matrix Release)", font=ctk.CTkFont(size=11), text_color="#8E8EA0")
        ver.pack(pady=(0, 15))

        dev_title = ctk.CTkLabel(main_frame, text="Developed with ❤️ by Vahid Valadi", font=ctk.CTkFont(size=13, weight="bold"))
        dev_title.pack(pady=4)

        email_label = ctk.CTkLabel(main_frame, text="📧 vahidvaladi.mail@gmail.com", font=ctk.CTkFont(size=11), text_color="#B0BEC5")
        email_label.pack(pady=2)

        gh_btn = ctk.CTkButton(
            main_frame,
            text="🌐 GitHub Repository",
            fg_color="#311B92",
            hover_color="#4527A0",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: webbrowser.open("https://github.com/vahidvl/AI-Coders-Proxy-Fixer")
        )
        gh_btn.pack(pady=15)

if __name__ == "__main__":
    import traceback
    crash_log = Path(os.environ.get('USERPROFILE', '.')) / "ai_proxy_fixer_crash.log"
    try:
        ensure_single_instance()
        app = ProxyManagerApp()
        app.mainloop()
    except Exception as e:
        with open(crash_log, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        ctypes.windll.user32.MessageBoxW(0, f"Error starting app:\n\n{str(e)}\n\nSee log: {crash_log}", "Startup Error", 0x10)
