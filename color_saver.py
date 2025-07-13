import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Toplevel
import keyboard
import csv


class ColorSaver(ttk.Frame):
    def __init__(self, parent, get_color_data):
        super().__init__(parent, padding=10)
        self.get_color_data = get_color_data
        self.save_path = None
        self.user_shortcut = None

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Save Colors to File", font=("Segoe UI", 12)).pack(anchor="w")

        ttk.Button(self, text="Choose Save File", command=self._browse_file).pack(pady=(10, 5), anchor="w")
        self.file_label = ttk.Label(self, text="No file selected")
        self.file_label.pack(anchor="w")

        ttk.Label(self, text="Set Shortcut (e.g. ctrl+shift+s):").pack(anchor="w", pady=(10, 0))
        self.shortcut_entry = ttk.Entry(self, width=25)
        self.shortcut_entry.pack(anchor="w")

        ttk.Button(self, text="Set Shortcut", command=self._set_shortcut).pack(pady=5, anchor="w")
        self.status = ttk.Label(self, text="", font=("Segoe UI", 9))
        self.status.pack(anchor="w", pady=(5, 0))

    def _browse_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            self.save_path = path
            self.file_label.config(text=path)

    def _set_shortcut(self):
        shortcut = self.shortcut_entry.get()
        if shortcut:
            try:
                if self.user_shortcut:
                    keyboard.remove_hotkey(self.user_shortcut)
                keyboard.add_hotkey(shortcut, self._save_color)
                self.user_shortcut = shortcut
                self.status.config(text=f"Shortcut '{shortcut}' set!", foreground="green")
            except Exception as e:
                self.status.config(text=str(e), foreground="red")

    def _save_color(self):
        if not self.save_path or not self.get_color_data():
            messagebox.showerror("Error", "No file selected or color detected.")
            return

        name, rgb, hex_code = self.get_color_data()
        try:
            with open(self.save_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, str(rgb), hex_code])
            self._show_toast(f"{name} saved!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _show_toast(self, message):
        toast = Toplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.geometry("200x40+100+100")
        ttk.Label(toast, text=message, style="success.TLabel", padding=10).pack(fill="both", expand=True)
        toast.after(1500, toast.destroy)
