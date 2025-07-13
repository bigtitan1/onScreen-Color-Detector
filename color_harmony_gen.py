import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar
from tkinter.colorchooser import askcolor
import colorsys


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def adjust_hue(rgb, degree):
    r, g, b = [x / 255.0 for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + degree) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return int(r * 255), int(g * 255), int(b * 255)


def get_harmony_colors(base_hex, harmony_type):
    base_rgb = hex_to_rgb(base_hex)
    if harmony_type == "Complementary":
        return [base_hex, rgb_to_hex(adjust_hue(base_rgb, 0.5))]
    elif harmony_type == "Analogous":
        return [rgb_to_hex(adjust_hue(base_rgb, shift)) for shift in (-0.08, -0.04, 0, 0.04, 0.08)]
    elif harmony_type == "Triadic":
        return [rgb_to_hex(adjust_hue(base_rgb, shift)) for shift in (0, 1 / 3, 2 / 3)]
    elif harmony_type == "Tetradic":
        return [rgb_to_hex(adjust_hue(base_rgb, shift)) for shift in (0, 0.25, 0.5, 0.75)]
    elif harmony_type == "Split Complementary":
        return [rgb_to_hex(adjust_hue(base_rgb, shift)) for shift in (0, 0.42, 0.58)]
    else:
        return [base_hex]


class ColorHarmonyGenerator(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.base_color = StringVar(value="#3498db")
        self.harmony_type = StringVar(value="Analogous")
        self._build_ui()
        self.show_harmonies()

    def _build_ui(self):
        ttk.Label(self, text="Base HEX Color:").pack(pady=(15, 5))
        ttk.Entry(self, textvariable=self.base_color, width=20, font=("Segoe UI", 12)).pack()

        ttk.Button(self, text="Pick Color", command=self.pick_color).pack(pady=5)

        ttk.Label(self, text="Select Harmony Type:").pack(pady=(20, 5))
        options = ["Analogous", "Complementary", "Triadic", "Tetradic", "Split Complementary"]
        dropdown = ttk.Combobox(self, values=options, textvariable=self.harmony_type, state="readonly", width=25)
        dropdown.pack()

        ttk.Button(self, text="Generate", bootstyle=SUCCESS, command=self.show_harmonies).pack(pady=15)

        self.colors_frame = ttk.Frame(self)
        self.colors_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def pick_color(self):
        color = askcolor(title="Choose a color")[1]
        if color:
            self.base_color.set(color)

    def show_harmonies(self):
        for widget in self.colors_frame.winfo_children():
            widget.destroy()

        base_hex = self.base_color.get()
        harmony = self.harmony_type.get()
        colors = get_harmony_colors(base_hex, harmony)

        for i, color in enumerate(colors):
            card = ttk.Frame(self.colors_frame, width=100, height=120)
            card.pack(side="left", padx=10)

            label = "Main" if i == 0 else f"Color {i}"
            ttk.Label(card, text=label, font=("Segoe UI", 9)).pack()

            preview = ttk.Label(card, text="", background=color, width=12, anchor="center")
            preview.pack(pady=(2, 5), ipadx=20, ipady=10)

            ttk.Label(card, text=color.upper(), font=("Segoe UI", 10)).pack()

            ttk.Button(card, text="Copy", width=10,
                       command=lambda c=color: self.clipboard_clear() or self.clipboard_append(c)).pack(pady=(5, 0))


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ColorHarmonyGenerator(master=root)
    app.pack(fill="both", expand=True)
    root.mainloop()
