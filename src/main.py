import os
import sys
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
from scanner import scan_proxy_ports, TargetType, DetectedTarget

_mutex_handle = None

def ensure_single_instance():
    """Ensure only one instance of the app runs at a time using Windows Named Mutex."""
    global _mutex_handle
    MUTEX_NAME = "Local\\AICodersProxyFixerMutex_v2"
    ERROR_ALREADY_EXISTS = 183

    try:
        # Set AppUserModelID so Windows Taskbar uses our custom app icon
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AICodersProxyFixer.App.v2")
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
                "AI Coders Proxy Fixer is already running in your System Tray!\n\nPlease check the bottom-right corner of your taskbar.",
                "AI Coders Proxy Fixer - Already Running",
                MB_OK | MB_ICONINFORMATION
            )
            sys.exit(0)
    except Exception as e:
        print(f"Mutex error: {e}")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

PRESETS = {
    "v2rayN (10808)": ("127.0.0.1", "10808"),
    "Clash / Mihomo (7890)": ("127.0.0.1", "7890"),
    "Hiddify (2080)": ("127.0.0.1", "2080"),
    "Custom": ("127.0.0.1", "10808"),
}

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
        icon_symbol = "💻"
        if "Antigravity" in self.target.name:
            icon_symbol = "🚀"
        elif "VS Code" in self.target.name:
            icon_symbol = "🟦"
        elif "Cursor" in self.target.name:
            icon_symbol = "🔮"
        elif "PowerShell" in self.target.name:
            icon_symbol = "⚡"
        elif "Git Bash" in self.target.name:
            icon_symbol = "🐚"
        elif "Claude" in self.target.name:
            icon_symbol = "🤖"

        icon_label = ctk.CTkLabel(self, text=icon_symbol, font=ctk.CTkFont(size=16))
        icon_label.pack(side="left", padx=(12, 6), pady=8)

        name_label = ctk.CTkLabel(
            self,
            text=f"{self.target.name}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", padx=4, pady=8)

        type_color = "#1E88E5" if self.target.target_type == TargetType.IDE else ("#8E24AA" if self.target.target_type == TargetType.SHELL else "#F57C00")
        type_badge = ctk.CTkLabel(
            self,
            text=f" {self.target.target_type} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=type_color,
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
        print("[DEBUG] Step 1: Entering ProxyManagerApp.__init__", flush=True)
        super().__init__()

        print("[DEBUG] Step 2: Setting title and geometry", flush=True)
        self.title("AI Coders Proxy Fixer v2.0 - Real AI Matrix Dashboard")
        self.geometry("680x880")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        print("[DEBUG] Step 3: Initializing ProxyManagerCore", flush=True)
        self.core = ProxyManagerCore()
        self.is_proxy_enabled = self.core.check_status()

        print("[DEBUG] Step 4: Calling setup_ui", flush=True)
        self.setup_ui()
        print("[DEBUG] Step 5: Calling setup_icon", flush=True)
        self.setup_icon()
        print("[DEBUG] Step 6: Calling setup_tray", flush=True)
        self.setup_tray()
        print("[DEBUG] Step 7: Calling rescan_targets", flush=True)
        self.rescan_targets()
        print("[DEBUG] Step 8: ProxyManagerApp.__init__ finished", flush=True)

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
            text_color="#B388FF",
            corner_radius=6
        )
        ver_badge.pack(side="left", padx=(0, 6))

        about_btn = ctk.CTkButton(
            badge_row,
            text="ℹ️ About",
            width=65,
            height=22,
            fg_color="#2A2A3C",
            hover_color="#3A3A52",
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.show_about_dialog
        )
        about_btn.pack(side="left")

        self.live_pulse_label = ctk.CTkLabel(
            badge_box,
            text="● ONLINE" if self.is_proxy_enabled else "○ OFFLINE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00E676" if self.is_proxy_enabled else "#FF5252"
        )
        self.live_pulse_label.pack(anchor="e")

        # 2. Main Content Wrapper
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Stat Summary Cards (3 Columns)
        stat_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        stat_frame.pack(fill="x", pady=(0, 10))
        stat_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat")

        self.stat_scanned = StatCard(stat_frame, "SCANNED", "0 Found", "🔍", "#00E5FF")
        self.stat_scanned.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.stat_patched = StatCard(stat_frame, "PATCHED", "0 Active", "🛡️", "#00E676")
        self.stat_patched.grid(row=0, column=1, padx=5, sticky="ew")

        self.stat_port = StatCard(stat_frame, "ACTIVE PORT", f"{self.core.proxy_port}", "🔌", "#FFD600")
        self.stat_port.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # 3. Preset & Config Card
        config_card = ctk.CTkFrame(main_content, fg_color="#181824", corner_radius=10, border_width=1, border_color="#2A2A3C")
        config_card.pack(fill="x", pady=5)

        c_header = ctk.CTkFrame(config_card, fg_color="transparent")
        c_header.pack(fill="x", padx=12, pady=(10, 5))

        c_title = ctk.CTkLabel(c_header, text="Proxy Configuration & Presets", font=ctk.CTkFont(size=13, weight="bold"), text_color="#E0E0E0")
        c_title.pack(side="left")

        self.autodetect_btn = ctk.CTkButton(
            c_header,
            text="⚡ Auto-Detect Port",
            width=130,
            height=26,
            fg_color="#0288D1",
            hover_color="#01579B",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.autodetect_port
        )
        self.autodetect_btn.pack(side="right")

        c_body = ctk.CTkFrame(config_card, fg_color="transparent")
        c_body.pack(fill="x", padx=12, pady=(0, 10))

        preset_label = ctk.CTkLabel(c_body, text="Preset:", font=ctk.CTkFont(size=12))
        preset_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")

        self.preset_option = ctk.CTkOptionMenu(
            c_body,
            values=list(PRESETS.keys()),
            command=self.on_preset_change,
            width=170
        )
        self.preset_option.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ip_label = ctk.CTkLabel(c_body, text="IP:", font=ctk.CTkFont(size=12))
        ip_label.grid(row=0, column=2, padx=(15, 5), pady=5, sticky="w")

        self.ip_entry = ctk.CTkEntry(c_body, width=110)
        self.ip_entry.insert(0, self.core.proxy_address)
        self.ip_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        port_label = ctk.CTkLabel(c_body, text="Port:", font=ctk.CTkFont(size=12))
        port_label.grid(row=0, column=4, padx=(15, 5), pady=5, sticky="w")

        self.port_entry = ctk.CTkEntry(c_body, width=80)
        self.port_entry.insert(0, self.core.proxy_port)
        self.port_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # 4. Master Control & Real AI Matrix Latency Grid
        ctrl_card = ctk.CTkFrame(main_content, fg_color="#181824", corner_radius=10, border_width=1, border_color="#2A2A3C")
        ctrl_card.pack(fill="x", pady=8)

        btn_text = "🔴 Disable All Proxies" if self.is_proxy_enabled else "🟢 Enable & Patch All Proxies"
        btn_color = "#C62828" if self.is_proxy_enabled else "#2E7D32"
        btn_hover = "#B71C1C" if self.is_proxy_enabled else "#1B5E20"

        self.toggle_btn = ctk.CTkButton(
            ctrl_card,
            text=btn_text,
            fg_color=btn_color,
            hover_color=btn_hover,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.toggle_proxy
        )
        self.toggle_btn.pack(fill="x", padx=15, pady=12)

        # Real AI Endpoint Latency Matrix Section
        lat_header = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        lat_header.pack(fill="x", padx=15, pady=(0, 6))

        lat_title = ctk.CTkLabel(lat_header, text="Real AI Endpoints Matrix & Geoblock Status", font=ctk.CTkFont(size=12, weight="bold"), text_color="#AAAAAA")
        lat_title.pack(side="left")

        self.test_btn = ctk.CTkButton(
            lat_header,
            text="⚡ Test AI Endpoints",
            width=130,
            height=24,
            fg_color="#1565C0",
            hover_color="#0D47A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.test_latency
        )
        self.test_btn.pack(side="right")

        # Latency Matrix Cards Container (2 Rows x 3 Columns)
        lat_grid = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        lat_grid.pack(fill="x", padx=15, pady=(0, 12))
        lat_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="lat")

        self.lat_cards = {
            "Claude API": LatencyCard(lat_grid, "Claude API"),
            "Google Cloud Code": LatencyCard(lat_grid, "Google Cloud Code"),
            "Google Gemini": LatencyCard(lat_grid, "Google Gemini"),
            "OpenAI / Codex": LatencyCard(lat_grid, "OpenAI / Codex"),
            "Cursor AI": LatencyCard(lat_grid, "Cursor AI"),
            "Codeium Backend": LatencyCard(lat_grid, "Codeium Backend")
        }

        # Grid placement
        self.lat_cards["Claude API"].grid(row=0, column=0, padx=(0, 4), pady=(0, 4), sticky="ew")
        self.lat_cards["Google Cloud Code"].grid(row=0, column=1, padx=4, pady=(0, 4), sticky="ew")
        self.lat_cards["Google Gemini"].grid(row=0, column=2, padx=(4, 0), pady=(0, 4), sticky="ew")

        self.lat_cards["OpenAI / Codex"].grid(row=1, column=0, padx=(0, 4), pady=(4, 0), sticky="ew")
        self.lat_cards["Cursor AI"].grid(row=1, column=1, padx=4, pady=(4, 0), sticky="ew")
        self.lat_cards["Codeium Backend"].grid(row=1, column=2, padx=(4, 0), pady=(4, 0), sticky="ew")

        # 5. Target List Dashboard Header
        tgt_header = ctk.CTkFrame(main_content, fg_color="transparent")
        tgt_header.pack(fill="x", pady=(5, 2))

        tgt_title = ctk.CTkLabel(tgt_header, text="Scanned IDEs, Shells & CLIs", font=ctk.CTkFont(size=14, weight="bold"))
        tgt_title.pack(side="left")

        rescan_btn = ctk.CTkButton(
            tgt_header,
            text="↻ Rescan System",
            width=110,
            height=24,
            fg_color="#37474F",
            hover_color="#455A64",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.rescan_targets
        )
        rescan_btn.pack(side="right")

        self.targets_container = ctk.CTkScrollableFrame(main_content, height=260, corner_radius=10, fg_color="#12121A", border_width=1, border_color="#2A2A3C")
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
            text="AI Coders Proxy Fixer v2.0.0",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        info_label.pack(side="right")

        self.setup_ui()
        self.setup_icon()
        self.setup_tray()
        self.rescan_targets()

    def setup_icon(self):
        icon_path = Path(__file__).parent.parent / "assets" / "app_icon.ico"
        if not icon_path.exists() and getattr(sys, 'frozen', False):
            icon_path = Path(sys._MEIPASS) / "assets" / "app_icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

    def generate_icon(self, is_enabled: bool):
        icon_path = Path(__file__).parent.parent / "assets" / "app_icon.ico"
        if not icon_path.exists() and getattr(sys, 'frozen', False):
            icon_path = Path(sys._MEIPASS) / "assets" / "app_icon.ico"

        if icon_path.exists():
            try:
                base_img = Image.open(str(icon_path)).convert('RGBA').resize((64, 64))
                dc = ImageDraw.Draw(base_img)
                dot_color = (0, 230, 118, 255) if is_enabled else (255, 82, 82, 255)
                dc.ellipse((44, 44, 60, 60), fill=dot_color, outline=(18, 18, 26, 255), width=2)
                return base_img
            except Exception:
                pass

        # Fallback if icon fails to load
        color1 = (18, 18, 26)
        color2 = (0, 230, 118) if is_enabled else (255, 82, 82)
        image = Image.new('RGB', (64, 64), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=color2)
        return image

    def setup_tray(self):
        icon_image = self.generate_icon(self.is_proxy_enabled)
        menu = (
            item('Show Window', self.show_window),
            item('Toggle Proxy', self.tray_toggle_proxy),
            item('Exit', self.quit_app)
        )
        self.tray_icon = pystray.Icon("AI Proxy", icon_image, "AI Proxy Fixer v2.0", menu)
        try:
            self.tray_icon.run_detached()
        except Exception:
            pass

    def hide_window(self):
        self.withdraw()

    def show_window(self, icon=None, item=None):
        self.after(0, self.deiconify)
        self.after(0, self.lift)
        self.after(0, self.focus_force)

    def quit_app(self, icon=None, item=None):
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
            self.stat_port.update_val(port)

    def autodetect_port(self):
        active_ports = scan_proxy_ports()
        if active_ports:
            port, name = active_ports[0]
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, str(port))
            self.stat_port.update_val(str(port), "#00E676")
        else:
            self.stat_port.update_val("None 🔴", "#FF5252")

    def rescan_targets(self):
        for widget in self.targets_container.winfo_children():
            widget.destroy()

        targets = self.core.scanner.scan_all()
        installed_count = sum(1 for t in targets if t.is_installed)
        patched_count = sum(1 for t in targets if t.is_patched)

        self.stat_scanned.update_val(f"{installed_count} Found")
        self.stat_patched.update_val(f"{patched_count} Active", "#00E676" if patched_count > 0 else "#8E8EA0")

        for target in targets:
            row = TargetRowFrame(self.targets_container, target, self.on_target_patch_click)
            row.pack(fill="x", pady=3, padx=4)

    def on_target_patch_click(self, target: DetectedTarget):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        self.core.set_proxy_config(ip, port)

        if target.is_patched:
            ok, msg = self.core.patcher.unpatch_target(target.name, target.config_path)
        else:
            ok, msg = self.core.patcher.patch_target(target.name, target.config_path)

        self.rescan_targets()

    def toggle_proxy(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        self.core.set_proxy_config(ip, port)

        if self.is_proxy_enabled:
            success, msg = self.core.disable_proxy()
            if success:
                self.is_proxy_enabled = False
        else:
            success, msg = self.core.enable_proxy()
            if success:
                self.is_proxy_enabled = True

        if success:
            self.update_ui_state()
            self.rescan_targets()

    def tray_toggle_proxy(self, icon, item):
        self.after(0, self.toggle_proxy)

    def update_ui_state(self):
        if self.is_proxy_enabled:
            self.live_pulse_label.configure(text="● ONLINE", text_color="#00E676")
            self.toggle_btn.configure(text="🔴 Disable All Proxies", fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            self.live_pulse_label.configure(text="○ OFFLINE", text_color="#FF5252")
            self.toggle_btn.configure(text="🟢 Enable & Patch All Proxies", fg_color="#2E7D32", hover_color="#1B5E20")
        self.tray_icon.icon = self.generate_icon(self.is_proxy_enabled)

    def test_latency(self):
        for card in self.lat_cards.values():
            card.value_label.configure(text="Pinging...", text_color="#AAAAAA")
        self.update_idletasks()

        threading.Thread(target=self._run_latency_test, daemon=True).start()

    def _run_latency_test(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        self.core.set_proxy_config(ip, port)

        results = self.core.test_api_latency()
        for name, card in self.lat_cards.items():
            if name in results:
                ms, status = results[name]
                self.after(0, lambda c=card, m=ms, s=status: c.set_latency_status(m, s))

    def toggle_autostart(self):
        enable = bool(self.autostart_checkbox.get())
        self.core.set_start_with_windows(enable)

    def show_about_dialog(self):
        about_win = ctk.CTkToplevel(self)
        about_win.title("About Developer")
        about_win.geometry("420x340")
        about_win.resizable(False, False)
        about_win.attributes("-topmost", True)
        about_win.grab_set()

        frame = ctk.CTkFrame(about_win, fg_color="#12121A", corner_radius=12, border_width=1, border_color="#2A2A3C")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        title = ctk.CTkLabel(frame, text="⚡ AI Coders Proxy Fixer", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00E5FF")
        title.pack(pady=(15, 5))

        ver = ctk.CTkLabel(frame, text="v2.1.0 (Super Release)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#B388FF")
        ver.pack(pady=(0, 15))

        desc = ctk.CTkLabel(
            frame,
            text="Automated IDE Patcher & WinInet Proxy Router\nBuilt with ❤️ for developers so they code without borders.",
            font=ctk.CTkFont(size=11),
            text_color="#E0E0E0",
            justify="center"
        )
        desc.pack(pady=5)

        dev_label = ctk.CTkLabel(frame, text="👨‍💻 Developer: Vahid Valadi (vahidvl)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#FFFFFF")
        dev_label.pack(pady=(10, 2))

        email_label = ctk.CTkLabel(frame, text="📧 vahidvaladi.mail@gmail.com", font=ctk.CTkFont(size=12), text_color="#8E8EA0")
        email_label.pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        gh_btn = ctk.CTkButton(
            btn_frame,
            text="🌐 GitHub Repository",
            fg_color="#311B92",
            hover_color="#4527A0",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: webbrowser.open("https://github.com/vahidvl/AI-Coders-Proxy-Fixer")
        )
        gh_btn.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(
            btn_frame,
            text="Close",
            width=80,
            fg_color="#2A2A3C",
            hover_color="#3A3A52",
            command=about_win.destroy
        )
        close_btn.pack(side="left", padx=5)

if __name__ == "__main__":
    import traceback
    crash_log = Path(os.environ.get('USERPROFILE', '.')) / "ai_proxy_fixer_crash.log"
    try:
        # ensure_single_instance() # Temporarily disabled to rule out Mutex lockouts
        app = ProxyManagerApp()
        app.mainloop()
    except Exception as e:
        with open(crash_log, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        ctypes.windll.user32.MessageBoxW(0, f"Error starting app:\n\n{str(e)}\n\nSee log: {crash_log}", "Startup Error", 0x10)
