import os
import sys
import threading
import time
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import customtkinter as ctk

from proxy_core import ProxyManagerCore
from scanner import scan_proxy_ports, TargetType, DetectedTarget

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
        super().__init__(master, fg_color="#1E1E1E", corner_radius=8, border_width=1, border_color="#333333")
        self.name = name
        
        self.title_label = ctk.CTkLabel(self, text=name, font=ctk.CTkFont(size=11, weight="bold"), text_color="#AAAAAA")
        self.title_label.pack(anchor="w", padx=10, pady=(6, 0))
        
        self.value_label = ctk.CTkLabel(self, text="-- ms", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00E676")
        self.value_label.pack(anchor="w", padx=10, pady=(0, 6))

    def set_latency(self, ms):
        if ms is None:
            self.value_label.configure(text="Offline 🔴", text_color="#FF5252")
        else:
            color = "#00E676" if ms < 150 else ("#FFD600" if ms < 350 else "#FF9100")
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
        # Icon representation based on target name
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

        # Target Name
        name_label = ctk.CTkLabel(
            self,
            text=f"{self.target.name}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", padx=4, pady=8)

        # Type Badge
        type_color = "#1E88E5" if self.target.target_type == TargetType.IDE else ("#8E24AA" if self.target.target_type == TargetType.SHELL else "#F57C00")
        type_badge = ctk.CTkLabel(
            self,
            text=f" {self.target.target_type} ",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=type_color,
            corner_radius=4
        )
        type_badge.pack(side="left", padx=6, pady=8)

        # Status Badge
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

        # Action Button
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

        self.title("AI Coders Proxy Fixer v2.0 - Futuristic Dashboard")
        self.geometry("660x760")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.core = ProxyManagerCore()
        self.is_proxy_enabled = self.core.check_status()

        self.setup_ui()
        self.setup_tray()
        self.rescan_targets()

    def setup_ui(self):
        # 1. Header Banner
        header_banner = ctk.CTkFrame(self, fg_color="#12121A", corner_radius=0, height=75)
        header_banner.pack(fill="x", side="top")

        header_content = ctk.CTkFrame(header_banner, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=10)

        # Logo & App Title
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

        # Version & Live Status Badge
        badge_box = ctk.CTkFrame(header_content, fg_color="transparent")
        badge_box.pack(side="right")

        ver_badge = ctk.CTkLabel(
            badge_box,
            text=" v2.0.0 ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#311B92",
            text_color="#B388FF",
            corner_radius=6
        )
        ver_badge.pack(anchor="e", pady=(0, 4))

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
        c_header_right = ctk.CTkFrame(c_header, fg_color="transparent")
        c_header_right.pack(side="right")
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

        # 4. Master Control & Latency Grid
        ctrl_card = ctk.CTkFrame(main_content, fg_color="#181824", corner_radius=10, border_width=1, border_color="#2A2A3C")
        ctrl_card.pack(fill="x", pady=8)

        # Master Toggle Button
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

        # Latency Tester Section
        lat_header = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        lat_header.pack(fill="x", padx=15, pady=(0, 6))

        lat_title = ctk.CTkLabel(lat_header, text="Real-Time AI API Latency", font=ctk.CTkFont(size=12, weight="bold"), text_color="#AAAAAA")
        lat_title.pack(side="left")

        self.test_btn = ctk.CTkButton(
            lat_header,
            text="⚡ Test Latency",
            width=110,
            height=24,
            fg_color="#1565C0",
            hover_color="#0D47A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.test_latency
        )
        self.test_btn.pack(side="right")

        # Latency Cards Container (3 columns)
        lat_grid = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        lat_grid.pack(fill="x", padx=15, pady=(0, 12))
        lat_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="lat")

        self.lat_google = LatencyCard(lat_grid, "Google")
        self.lat_google.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.lat_claude = LatencyCard(lat_grid, "Claude API")
        self.lat_claude.grid(row=0, column=1, padx=4, sticky="ew")

        self.lat_cloudcode = LatencyCard(lat_grid, "Cloud Code API")
        self.lat_cloudcode.grid(row=0, column=2, padx=(4, 0), sticky="ew")

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

        self.targets_container = ctk.CTkScrollableFrame(main_content, height=200, corner_radius=10, fg_color="#12121A", border_width=1, border_color="#2A2A3C")
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

    def generate_icon(self, color1, color2):
        image = Image.new('RGB', (64, 64), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=color2)
        return image

    def setup_tray(self):
        icon_image = self.generate_icon('black', 'green' if self.is_proxy_enabled else 'red')
        menu = (
            item('Show Window', self.show_window),
            item('Toggle Proxy', self.tray_toggle_proxy),
            item('Exit', self.quit_app)
        )
        self.tray_icon = pystray.Icon("AI Proxy", icon_image, "AI Proxy Fixer v2.0", menu)

    def run_tray(self):
        self.tray_icon.run()

    def hide_window(self):
        self.withdraw()

    def show_window(self, icon=None, item=None):
        self.after(0, self.deiconify)

    def quit_app(self, icon=None, item=None):
        self.tray_icon.stop()
        self.destroy()

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
            new_icon = self.generate_icon('black', 'green')
        else:
            self.live_pulse_label.configure(text="○ OFFLINE", text_color="#FF5252")
            self.toggle_btn.configure(text="🟢 Enable & Patch All Proxies", fg_color="#2E7D32", hover_color="#1B5E20")
            new_icon = self.generate_icon('black', 'red')
        self.tray_icon.icon = new_icon

    def test_latency(self):
        self.lat_google.value_label.configure(text="Pinging...", text_color="#AAAAAA")
        self.lat_claude.value_label.configure(text="Pinging...", text_color="#AAAAAA")
        self.lat_cloudcode.value_label.configure(text="Pinging...", text_color="#AAAAAA")
        self.update_idletasks()

        threading.Thread(target=self._run_latency_test, daemon=True).start()

    def _run_latency_test(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        self.core.set_proxy_config(ip, port)

        results = self.core.test_api_latency()
        g_ms = results.get("Google")
        c_ms = results.get("Claude API")
        m_ms = results.get("Cloud Code API")

        self.after(0, lambda: self.lat_google.set_latency(g_ms))
        self.after(0, lambda: self.lat_claude.set_latency(c_ms))
        self.after(0, lambda: self.lat_cloudcode.set_latency(m_ms))

    def toggle_autostart(self):
        enable = bool(self.autostart_checkbox.get())
        self.core.set_start_with_windows(enable)

if __name__ == "__main__":
    app = ProxyManagerApp()
    tray_thread = threading.Thread(target=app.run_tray, daemon=True)
    tray_thread.start()
    app.mainloop()
