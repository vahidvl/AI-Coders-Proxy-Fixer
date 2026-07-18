import os
import sys
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import customtkinter as ctk

from proxy_core import ProxyManagerCore

# Setup the CustomTkinter aesthetic
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ProxyManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Coders Proxy Manager")
        self.geometry("450x380")
        self.resizable(False, False)
        
        # Make sure app minimizes to tray when closing
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # Init core logic
        self.core = ProxyManagerCore()
        self.is_proxy_enabled = self.core.check_status()
        
        self.setup_ui()
        self.setup_tray()
        
    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(
            self, 
            text="AI Coders Proxy Manager", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header.pack(pady=(25, 5))
        
        self.subtitle = ctk.CTkLabel(
            self, 
            text="Bypass network restrictions for AI IDEs", 
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.subtitle.pack(pady=(0, 20))
        
        # Configuration Frame
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(pady=10, padx=20, fill="x")
        
        # Address and Port fields
        self.ip_label = ctk.CTkLabel(self.config_frame, text="Proxy IP:")
        self.ip_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.ip_entry = ctk.CTkEntry(self.config_frame, width=150)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.port_label = ctk.CTkLabel(self.config_frame, text="Port:")
        self.port_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.port_entry = ctk.CTkEntry(self.config_frame, width=150)
        self.port_entry.insert(0, "10808")
        self.port_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Status Label
        status_text = "ENABLED" if self.is_proxy_enabled else "DISABLED"
        status_color = "green" if self.is_proxy_enabled else "red"
        
        self.status_label = ctk.CTkLabel(
            self, 
            text=f"Current Status: {status_text}", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=status_color
        )
        self.status_label.pack(pady=15)
        
        # Action Button
        btn_text = "Disable Proxy" if self.is_proxy_enabled else "Enable Proxy"
        btn_color = "#C62828" if self.is_proxy_enabled else "#2E7D32"
        btn_hover = "#B71C1C" if self.is_proxy_enabled else "#1B5E20"
        
        self.toggle_btn = ctk.CTkButton(
            self, 
            text=btn_text, 
            fg_color=btn_color,
            hover_color=btn_hover,
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            command=self.toggle_proxy
        )
        self.toggle_btn.pack(pady=10)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            self, 
            text="App is running in the background. Check system tray.", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack(side="bottom", pady=10)
        
    def generate_icon(self, color1, color2):
        # Generate a dynamic icon for the system tray
        image = Image.new('RGB', (64, 64), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (16, 16, 48, 48),
            fill=color2
        )
        return image
        
    def setup_tray(self):
        icon_image = self.generate_icon('black', 'green' if self.is_proxy_enabled else 'red')
        
        menu = (
            item('Show Window', self.show_window),
            item('Toggle Proxy', self.tray_toggle_proxy),
            item('Exit', self.quit_app)
        )
        
        self.tray_icon = pystray.Icon("AI Proxy", icon_image, "AI Proxy Manager", menu)
        
    def run_tray(self):
        self.tray_icon.run()
        
    def hide_window(self):
        self.withdraw()
        
    def show_window(self, icon=None, item=None):
        self.after(0, self.deiconify)
        
    def quit_app(self, icon=None, item=None):
        self.tray_icon.stop()
        self.destroy()
        
    def toggle_proxy(self):
        self.core.proxy_address = self.ip_entry.get().strip()
        self.core.proxy_port = self.port_entry.get().strip()
        self.core.full_proxy_url = f"http://{self.core.proxy_address}:{self.core.proxy_port}"
        self.core.socks_proxy_url = f"socks5h://{self.core.proxy_address}:{self.core.proxy_port}"
        
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
            
    def tray_toggle_proxy(self, icon, item):
        # We need to run this in the main thread to update UI
        self.after(0, self.toggle_proxy)
        
    def update_ui_state(self):
        # Update text and colors based on state
        if self.is_proxy_enabled:
            self.status_label.configure(text="Current Status: ENABLED", text_color="green")
            self.toggle_btn.configure(text="Disable Proxy", fg_color="#C62828", hover_color="#B71C1C")
            new_icon = self.generate_icon('black', 'green')
        else:
            self.status_label.configure(text="Current Status: DISABLED", text_color="red")
            self.toggle_btn.configure(text="Enable Proxy", fg_color="#2E7D32", hover_color="#1B5E20")
            new_icon = self.generate_icon('black', 'red')
            
        self.tray_icon.icon = new_icon

if __name__ == "__main__":
    app = ProxyManagerApp()
    
    # Start tray icon in a separate thread so it doesn't block tkinter mainloop
    tray_thread = threading.Thread(target=app.run_tray, daemon=True)
    tray_thread.start()
    
    app.mainloop()
