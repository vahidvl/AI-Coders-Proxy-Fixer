import os
import sys
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import customtkinter as ctk

from proxy_core import ProxyManagerCore
from scanner import scan_proxy_ports, TargetType, DetectedTarget

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

PRESETS = {
    "v2rayN (10808)": ("127.0.0.1", "10808"),
    "Clash / Mihomo (7890)": ("127.0.0.1", "7890"),
    "Hiddify (2080)": ("127.0.0.1", "2080"),
    "Custom": ("127.0.0.1", "10808"),
}

class TargetRowFrame(ctk.CTkFrame):
    def __init__(self, master, target: DetectedTarget, on_patch_click):
        super().__init__(master, fg_color="#2B2B2B", corner_radius=6)
        self.target = target
        self.on_patch_click = on_patch_click
        self.setup_ui()

    def setup_ui(self):
        # Target Name & Type
        name_label = ctk.CTkLabel(
            self,
            text=f"{self.target.name}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", padx=(12, 5), pady=8)

        type_color = "#1565C0" if self.target.target_type == TargetType.IDE else ("#6A1B9A" if self.target.target_type == TargetType.SHELL else "#E65100")
        type_badge = ctk.CTkLabel(
            self,
            text=f" {self.target.target_type} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=type_color,
            corner_radius=4
        )
        type_badge.pack(side="left", padx=5, pady=8)

        # Status Badge
        if not self.target.is_installed:
            status_text = "Not Found"
            status_color = "#424242"
        elif self.target.is_patched:
            status_text = "🟢 Patched"
            status_color = "#1B5E20"
        else:
            status_text = "🟡 Unpatched"
            status_color = "#F57F17"

        status_label = ctk.CTkLabel(
            self,
            text=f" {status_text} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=status_color,
            corner_radius=4
        )
        status_label.pack(side="left", padx=10, pady=8)

        # Action Button
        if self.target.is_installed:
            btn_text = "Unpatch" if self.target.is_patched else "Patch"
            btn_color = "#C62828" if self.target.is_patched else "#2E7D32"
            btn_hover = "#B71C1C" if self.target.is_patched else "#1B5E20"

            action_btn = ctk.CTkButton(
                self,
                text=btn_text,
                width=75,
                height=26,
                fg_color=btn_color,
                hover_color=btn_hover,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda: self.on_patch_click(self.target)
            )
            action_btn.pack(side="right", padx=12, pady=8)

class ProxyManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Coders Proxy Fixer")
        self.geometry("620x720")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.core = ProxyManagerCore()
        self.is_proxy_enabled = self.core.check_status()

        self.setup_ui()
        self.setup_tray()

        # Initial Scan
        self.rescan_targets()

    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        title_label = ctk.CTkLabel(
            header_frame,
            text="AI Coders Proxy Fixer",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(side="top", anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="System-wide Proxy Router & Automated IDE Patcher",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle.pack(side="top", anchor="w")

        # 1. Preset & Configuration Card
        config_card = ctk.CTkFrame(self, corner_radius=10)
        config_card.pack(fill="x", padx=20, pady=8)

        preset_label = ctk.CTkLabel(config_card, text="Preset Profile:", font=ctk.CTkFont(weight="bold"))
        preset_label.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self.preset_option = ctk.CTkOptionMenu(
            config_card,
            values=list(PRESETS.keys()),
            command=self.on_preset_change,
            width=180
        )
        self.preset_option.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.autodetect_btn = ctk.CTkButton(
            config_card,
            text="Auto-Detect Port",
            width=130,
            fg_color="#0288D1",
            hover_color="#01579B",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.autodetect_port
        )
        self.autodetect_btn.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # IP & Port inputs
        ip_label = ctk.CTkLabel(config_card, text="IP:")
        ip_label.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        self.ip_entry = ctk.CTkEntry(config_card, width=130)
        self.ip_entry.insert(0, self.core.proxy_address)
        self.ip_entry.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

        port_label = ctk.CTkLabel(config_card, text="Port:")
        port_label.grid(row=1, column=1, padx=(145, 0), pady=(0, 10), sticky="w")

        self.port_entry = ctk.CTkEntry(config_card, width=90)
        self.port_entry.insert(0, self.core.proxy_port)
        self.port_entry.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="w")

        # 2. Main Master Controls Card
        control_card = ctk.CTkFrame(self, corner_radius=10)
        control_card.pack(fill="x", padx=20, pady=8)

        status_text = "ENABLED" if self.is_proxy_enabled else "DISABLED"
        status_color = "#2E7D32" if self.is_proxy_enabled else "#C62828"

        self.status_label = ctk.CTkLabel(
            control_card,
            text=f"System Proxy Status: {status_text}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=status_color
        )
        self.status_label.pack(pady=(12, 8))

        btn_text = "Disable All Proxies" if self.is_proxy_enabled else "Enable & Patch All Proxies"
        btn_color = "#C62828" if self.is_proxy_enabled else "#2E7D32"
        btn_hover = "#B71C1C" if self.is_proxy_enabled else "#1B5E20"

        self.toggle_btn = ctk.CTkButton(
            control_card,
            text=btn_text,
            fg_color=btn_color,
            hover_color=btn_hover,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=38,
            command=self.toggle_proxy
        )
        self.toggle_btn.pack(fill="x", padx=20, pady=(0, 10))

        # Latency & Connection Test Bar
        latency_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        latency_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.test_btn = ctk.CTkButton(
            latency_frame,
            text="Test Latency",
            width=120,
            fg_color="#1565C0",
            hover_color="#0D47A1",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.test_latency
        )
        self.test_btn.pack(side="left", padx=(0, 10))

        self.latency_label = ctk.CTkLabel(
            latency_frame,
            text="Click 'Test Latency' to ping AI endpoints",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.latency_label.pack(side="left", padx=5)

        # 3. Scanned Targets Dashboard
        scanner_header = ctk.CTkFrame(self, fg_color="transparent")
        scanner_header.pack(fill="x", padx=20, pady=(10, 0))

        sec_title = ctk.CTkLabel(
            scanner_header,
            text="Detected IDEs, CLIs & Shells",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        sec_title.pack(side="left")

        rescan_btn = ctk.CTkButton(
            scanner_header,
            text="↻ Rescan",
            width=80,
            height=24,
            fg_color="#424242",
            hover_color="#616161",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.rescan_targets
        )
        rescan_btn.pack(side="right")

        self.targets_container = ctk.CTkScrollableFrame(self, height=210, corner_radius=10)
        self.targets_container.pack(fill="x", padx=20, pady=8)

        # 4. Footer & Options
        footer_card = ctk.CTkFrame(self, fg_color="transparent")
        footer_card.pack(fill="x", padx=20, pady=(5, 10))

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
            text="App runs in background system tray",
            font=ctk.CTkFont(size=11),
            text_color="gray"
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
        self.tray_icon = pystray.Icon("AI Proxy", icon_image, "AI Proxy Fixer", menu)

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

    def autodetect_port(self):
        active_ports = scan_proxy_ports()
        if active_ports:
            port, name = active_ports[0]
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, str(port))
            self.latency_label.configure(text=f"Detected: {name} on port {port} 🟢", text_color="#2E7D32")
        else:
            self.latency_label.configure(text="No active proxy port detected! Check v2rayN/Clash. 🔴", text_color="#C62828")

    def rescan_targets(self):
        for widget in self.targets_container.winfo_children():
            widget.destroy()

        targets = self.core.scanner.scan_all()
        for target in targets:
            row = TargetRowFrame(self.targets_container, target, self.on_target_patch_click)
            row.pack(fill="x", pady=4, padx=5)

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
            self.status_label.configure(text="System Proxy Status: ENABLED", text_color="#2E7D32")
            self.toggle_btn.configure(text="Disable All Proxies", fg_color="#C62828", hover_color="#B71C1C")
            new_icon = self.generate_icon('black', 'green')
        else:
            self.status_label.configure(text="System Proxy Status: DISABLED", text_color="#C62828")
            self.toggle_btn.configure(text="Enable & Patch All Proxies", fg_color="#2E7D32", hover_color="#1B5E20")
            new_icon = self.generate_icon('black', 'red')
        self.tray_icon.icon = new_icon

    def test_latency(self):
        self.latency_label.configure(text="Pinging Google, Claude API & Cloud Code...", text_color="gray")
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

        txt = f"Google: {g_ms if g_ms else '❌'}ms | Claude: {c_ms if c_ms else '❌'}ms | CloudCode: {m_ms if m_ms else '❌'}ms"
        color = "#2E7D32" if g_ms or c_ms else "#C62828"

        self.after(0, lambda: self.latency_label.configure(text=txt, text_color=color))

    def toggle_autostart(self):
        enable = bool(self.autostart_checkbox.get())
        self.core.set_start_with_windows(enable)

if __name__ == "__main__":
    app = ProxyManagerApp()
    tray_thread = threading.Thread(target=app.run_tray, daemon=True)
    tray_thread.start()
    app.mainloop()
