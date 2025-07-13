import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import colorchooser
from tkinter import messagebox
import re


class ColorContrastChecker(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self._build_ui()

    def _build_ui(self):
        padding = {'padx': 10, 'pady': 10}

        # ====== First Color ======
        ttk.Label(self, text="Color 1 (HEX):").grid(row=0, column=0, sticky="w", **padding)
        self.color1_entry = ttk.Entry(self, width=15)
        self.color1_entry.grid(row=0, column=1, **padding)
        ttk.Button(self, text="Pick", command=self._pick_color1).grid(row=0, column=2, **padding)
        self.color1_preview = ttk.Frame(self, width=50, height=25)
        self.color1_preview.grid(row=0, column=3, **padding)
        self.color1_preview.grid_propagate(False)

        # ====== Second Color ======
        ttk.Label(self, text="Color 2 (HEX):").grid(row=1, column=0, sticky="w", **padding)
        self.color2_entry = ttk.Entry(self, width=15)
        self.color2_entry.grid(row=1, column=1, **padding)
        ttk.Button(self, text="Pick", command=self._pick_color2).grid(row=1, column=2, **padding)
        self.color2_preview = ttk.Frame(self, width=50, height=25)
        self.color2_preview.grid(row=1, column=3, **padding)
        self.color2_preview.grid_propagate(False)

        # ====== Calculate Button ======
        ttk.Button(self, text="Calculate Contrast", bootstyle="success", command=self._calculate_contrast).grid(
            row=2, column=0, columnspan=4, pady=20
        )

        # ====== Result Labels ======
        self.result_label = ttk.Label(self, text="", font=('Segoe UI', 12))
        self.result_label.grid(row=3, column=0, columnspan=4)

        self.rating_label = ttk.Label(self, text="", font=('Segoe UI', 12))
        self.rating_label.grid(row=4, column=0, columnspan=4, pady=(5, 10))

    def _pick_color1(self):
        color_code = colorchooser.askcolor(title="Choose Color 1")[1]
        if color_code:
            self.color1_entry.delete(0, 'end')
            self.color1_entry.insert(0, color_code)
            self._update_preview(self.color1_preview, color_code)

    def _pick_color2(self):
        color_code = colorchooser.askcolor(title="Choose Color 2")[1]
        if color_code:
            self.color2_entry.delete(0, 'end')
            self.color2_entry.insert(0, color_code)
            self._update_preview(self.color2_preview, color_code)

    def _update_preview(self, preview_frame, color):
        try:
            preview_frame.configure(style=None)  # Remove previous style if exists
            style_name = f"Preview.TFrame.{color}"
            style = ttk.Style()
            style.configure(style_name, background=color)
            preview_frame.configure(style=style_name)
        except:
            pass

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.strip().lstrip('#')
        if len(hex_color) != 6 or not re.match(r'^[0-9a-fA-F]{6}$', hex_color):
            raise ValueError("Invalid HEX color format")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _calculate_luminance(self, rgb):
        def channel_lum(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = rgb
        return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

    def _calculate_contrast(self):
        hex1 = self.color1_entry.get().strip()
        hex2 = self.color2_entry.get().strip()

        try:
            rgb1 = self._hex_to_rgb(hex1)
            rgb2 = self._hex_to_rgb(hex2)
            self._update_preview(self.color1_preview, f"#{hex1.lstrip('#')}")
            self._update_preview(self.color2_preview, f"#{hex2.lstrip('#')}")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        lum1 = self._calculate_luminance(rgb1)
        lum2 = self._calculate_luminance(rgb2)
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        ratio = round((lighter + 0.05) / (darker + 0.05), 2)

        self.result_label.config(text=f"Contrast Ratio: {ratio}:1")

        if ratio >= 7:
            rating = "✔ AAA (Excellent)"
        elif ratio >= 4.5:
            rating = "✔ AA (Good)"
        elif ratio >= 3:
            rating = "▲ AA Large Text (Minimum)"
        else:
            rating = "✘ Fail (Low contrast)"

        self.rating_label.config(text=f"WCAG Rating: {rating}")


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ColorContrastChecker(master=root)
    app.pack(fill="both", expand=True)
    root.mainloop()
