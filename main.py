import pyautogui
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Toplevel, messagebox
from PIL import ImageGrab
import numpy as np
import webcolors
import webbrowser
import sys
import os

# External modules
import color_contrast
import color_harmony_gen
import color_saver



def resource_path(relative_path):
    try:
        return os.path.join(sys._MEIPASS, relative_path)
    except Exception:
        return os.path.abspath(relative_path)



class ColorAssistantApp(ttk.Window):
    def __init__(self):
        super().__init__(title="PixPick", themename="darkly", size=(800, 520))
        self.iconbitmap(resource_path("pixpick.ico"))

        self.resizable(False, False)

        self.last_color_data = None
        self._style = ttk.Style()  # ✅ Local style object

        self._build_ui()
        self._update_color_info()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.hex_var = ttk.BooleanVar(value=True)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True)

        # Tabs
        self.main_frame = ttk.Frame(self.notebook, padding=10)
        self.harmony_frame = ttk.Frame(self.notebook)
        self.contrast_frame = ttk.Frame(self.notebook)
        self.save_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.main_frame, text="Color Detection")
        self.notebook.add(self.harmony_frame, text="Color Harmony")
        self.notebook.add(self.contrast_frame, text="Contrast Checker")
        self.notebook.add(self.save_frame, text="Save Colors")

        # Initialize each tab
        self._init_main_tab()
        self._embed_tools()

        footer = ttk.Label(self, text="Made by Bigtitan aka Yash Kalra", font=("Segoe UI", 9, "italic"))
        footer.pack(padx=0 ,pady=(0, 10))

    def _init_main_tab(self):
        ttk.Label(self.main_frame, text="Current Color:", font=("Segoe UI", 14)).grid(row=0, column=0, sticky="w", columnspan=2)

        self.color_label = ttk.Label(self.main_frame, text="Detecting...", font=("Segoe UI", 12))
        self.color_label.grid(row=1, column=0, sticky="w", columnspan=2, pady=(0, 10))

        ttk.Checkbutton(self.main_frame, text="Show HEX Code", variable=self.hex_var).grid(row=2, column=0, sticky="w")

        ttk.Label(self.main_frame, text="Pointer Area (px):").grid(row=3, column=0, sticky="w")
        self.area_slider = ttk.Scale(self.main_frame, from_=5, to=50, orient=HORIZONTAL)
        self.area_slider.set(10)
        self.area_slider.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        self.preview_box = ttk.Frame(self.main_frame, width=150, height=80, style="info.TFrame")
        self.preview_box.grid(row=2, column=1, rowspan=3, padx=20)
        self.preview_box.grid_propagate(False)

        self.tooltip = Toplevel(self)
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)
        self.tooltip_label = ttk.Label(self.tooltip, text="", background="black", foreground="white")
        self.tooltip_label.pack()

       

    def _embed_tools(self):
        color_harmony_gen.ColorHarmonyGenerator(self.harmony_frame).pack(fill=BOTH, expand=True)
        color_contrast.ColorContrastChecker(self.contrast_frame).pack(fill=BOTH, expand=True)
        color_saver.ColorSaver(
            parent=self.save_frame,
            get_color_data=self._get_latest_color_data
        ).pack(fill=BOTH, expand=True)

    def _update_color_info(self):
        x, y = pyautogui.position()
        area = max(2, int(self.area_slider.get()))
        rgb = self._get_avg_color(x, y, area)
        hex_code = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        name = self._get_color_name(rgb)

        display_text = name
        if self.hex_var.get():
            display_text += f" | {hex_code}"

        self.color_label.config(text=display_text)
        self.preview_box.config(style="preview.TFrame")
        self._style.configure("preview.TFrame", background=hex_code)
        self.tooltip.geometry(f"+{x+15}+{y+20}")
        self.tooltip_label.config(text=display_text, background=hex_code)
        text_color = self._get_contrasting_text_color(rgb)
        self.tooltip.geometry(f"+{x+15}+{y+20}")
        self.tooltip_label.config(text=display_text, background=hex_code, foreground=text_color)

        self.last_color_data = (name, rgb, hex_code)
        self.after(200, self._update_color_info)

    def _get_avg_color(self, x, y, area):
        screen_w, screen_h = pyautogui.size()
        half = area // 2
        left, top = max(0, x - half), max(0, y - half)
        right, bottom = min(screen_w, x + half), min(screen_h, y + half)

        if right <= left or bottom <= top:
            return (255, 255, 255)

        img = ImageGrab.grab(bbox=(left, top, right, bottom))
        img_np = np.array(img)
        avg = img_np.mean(axis=(0, 1)).astype(int)
        return tuple(avg)

    def _get_color_name(self, rgb):
        try:
            return webcolors.rgb_to_name(rgb)
        except ValueError:
            min_distance = float('inf')
            closest_name = "Unknown"
            for name in webcolors.names("css3"):
                hex_code = webcolors.name_to_hex(name)
                r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
                dist = (r_c - rgb[0])**2 + (g_c - rgb[1])**2 + (b_c - rgb[2])**2
                if dist < min_distance:
                    min_distance = dist
                    closest_name = name
            return closest_name

    def _get_contrasting_text_color(self, rgb):
        # Calculate perceived brightness
        brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
        return "black" if brightness > 186 else "white"
    
    def _get_latest_color_data(self):
        return self.last_color_data

    def _on_close(self):
        if messagebox.askokcancel("Exit", "Exit the app?"):
            self.destroy()

    


if __name__ == "__main__":
    app = ColorAssistantApp()
    app.mainloop()
