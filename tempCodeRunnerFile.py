import pyautogui
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import ImageGrab
import numpy as np
import webcolors
import csv
import keyboard

# Global Variables
save_file_path = None
user_shortcut = None
last_color_data = None
dark_mode = True

# Color Themes
theme = {
    "dark": {
        "bg": "#2c2c2c",
        "fg": "#ffffff",
        "highlight": "#3e3e3e",
        "button_bg": "#444",
        "entry_bg": "#3a3a3a",
        "preview_border": "#888"
    },
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "highlight": "#e0e0e0",
        "button_bg": "#ddd",
        "entry_bg": "#ffffff",
        "preview_border": "#ccc"
    }
}

# Get average color from screen
def get_avg_color(x, y, area):
    half = area // 2
    bbox = (x - half, y - half, x + half, y + half)
    img = ImageGrab.grab(bbox=bbox)
    img_np = np.array(img)
    avg_color = img_np.mean(axis=(0, 1)).astype(int)
    return tuple(avg_color)

# Closest color name logic
def get_color_name(rgb):
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

# Update color info
def update_color_info():
    global last_color_data
    x, y = pyautogui.position()
    area = int(area_slider.get())
    rgb = get_avg_color(x, y, area)
    color_name = get_color_name(rgb)
    hex_code = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    display_text = f"{color_name}"
    if hex_var.get():
        display_text += f" | {hex_code}"
    color_label.config(text=display_text)
    color_preview.config(bg=hex_code)
    tooltip_label.config(
        text=display_text,
        bg=hex_code,
        fg='black' if sum(rgb) > 382 else 'white'
    )
    tooltip_window.geometry(f"+{x + 15}+{y + 20}")
    last_color_data = (color_name, rgb, hex_code)
    root.after(200, update_color_info)

# Save color info

def save_color_to_file():
    if not save_file_path or not last_color_data:
        messagebox.showerror("Error", "No file selected or color detected.")
        return
    color_name, rgb, hex_code = last_color_data
    try:
        if save_file_path.endswith(".csv"):
            with open(save_file_path, "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([color_name, str(rgb), hex_code])
        else:
            with open(save_file_path, "a") as f:
                f.write(f"{color_name} | RGB: {rgb} | HEX: {hex_code}\n")
        shortcut_status.config(text="Color saved!", fg="green")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# File browse

def browse_file():
    global save_file_path
    filetypes = [("CSV or TXT", "*.csv *.txt")]
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes)
    if path:
        save_file_path = path
        file_label.config(text=f"Selected: {path}")

# Set keyboard shortcut

def set_shortcut():
    global user_shortcut
    shortcut = shortcut_entry.get()
    if shortcut:
        try:
            if user_shortcut:
                keyboard.remove_hotkey(user_shortcut)
            keyboard.add_hotkey(shortcut, save_color_to_file)
            user_shortcut = shortcut
            shortcut_status.config(text=f"Shortcut '{shortcut}' set!", fg="green")
        except Exception as e:
            shortcut_status.config(text=f"Error: {str(e)}", fg="red")

# Toggle additional features

def toggle_features():
    if feature_frame.winfo_ismapped():
        feature_frame.grid_remove()
    else:
        feature_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

# Toggle dark mode

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

# Apply theme

def apply_theme():
    scheme = theme["dark" if dark_mode else "light"]
    root.config(bg=scheme["bg"])
    for widget in root.winfo_children():
        update_widget_theme(widget, scheme)
    for widget in feature_frame.winfo_children():
        update_widget_theme(widget, scheme)
    color_preview.config(highlightbackground=scheme["preview_border"], highlightthickness=1, bd=0)

# Update widget theme

def update_widget_theme(widget, scheme):
    widget_type = widget.winfo_class()

    # Basic styling for classic tk widgets
    if widget_type in ["Label", "Button", "Checkbutton", "Frame", "Toplevel"]:
        widget.configure(bg=scheme["bg"], fg=scheme["fg"])
        if widget_type != "Toplevel":  # Toplevel doesn't support `fg`
            try:
                widget.configure(highlightthickness=0)
            except:
                pass

    # Specific styling for certain widgets
    if widget_type == "Label":
        widget.configure(font=("Segoe UI", 11))
    elif widget_type == "Button":
        widget.configure(relief="flat", font=("Segoe UI", 10, "bold"))
    elif widget_type == "Checkbutton":
        widget.configure(selectcolor=scheme["bg"], font=("Segoe UI", 10))

    # Recursively update child widgets
    for child in widget.winfo_children():
        update_widget_theme(child, scheme)


# GUI setup
root = tk.Tk()
root.title("Color Assistant")
root.geometry("500x420")
root.resizable(False, False)

color_label = tk.Label(root, text="Initializing...", font=('Segoe UI', 16), anchor="w")
color_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

hex_var = tk.BooleanVar()
hex_check = tk.Checkbutton(root, text="Show HEX Code", variable=hex_var, font=("Segoe UI", 10))
hex_check.grid(row=1, column=0, sticky="w", padx=10)

tk.Label(root, text="Pointer Area (px)", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))

area_slider = ttk.Scale(root, from_=1, to=50, orient="horizontal", length=250)
area_slider.set(10)
area_slider.grid(row=3, column=0, columnspan=2, padx=10)

color_preview = tk.Label(root, width=20, height=5, bg="#ffffff", relief="flat", borderwidth=1)
color_preview.grid(row=1, column=1, rowspan=3, padx=(10, 15), pady=10, sticky="nsew")

feature_button = tk.Button(root, text="Additional Features", command=toggle_features, font=("Segoe UI", 10), padx=10, pady=5)
feature_button.grid(row=4, column=0, columnspan=2, pady=(5, 0))

dark_button = tk.Button(root, text="Toggle Dark Mode", command=toggle_dark_mode, font=("Segoe UI", 10), padx=10, pady=5)
dark_button.grid(row=5, column=0, columnspan=2, pady=(5, 0))

# Features frame
feature_frame = tk.Frame(root, relief="flat", borderwidth=2, padx=10, pady=10)
file_button = tk.Button(feature_frame, text="Browse & Save File", command=browse_file, font=("Segoe UI", 10), padx=10, pady=5)
file_button.grid(row=0, column=0, sticky="w")

file_label = tk.Label(feature_frame, text="No file selected", font=("Segoe UI", 8), wraplength=300)
file_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))

tk.Label(feature_frame, text="Set Shortcut (e.g. ctrl+shift+c):", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=(5, 0))

shortcut_entry = tk.Entry(feature_frame, width=20, font=("Segoe UI", 10))
shortcut_entry.grid(row=3, column=0, sticky="w")

shortcut_set_button = tk.Button(feature_frame, text="Set", command=set_shortcut, font=("Segoe UI", 10), padx=10)
shortcut_set_button.grid(row=3, column=1, sticky="w", padx=5)

shortcut_status = tk.Label(feature_frame, text="", font=("Segoe UI", 9))
shortcut_status.grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))

feature_frame.grid_remove()

# Tooltip
tooltip_window = tk.Toplevel(root)
tooltip_window.overrideredirect(True)
tooltip_window.attributes("-topmost", True)
tooltip_window.attributes("-alpha", 0.8)
tooltip_window.config(bg="black")

tooltip_label = tk.Label(tooltip_window, text="", font=("Segoe UI", 10), fg="white", bg="black", padx=5, pady=2)
tooltip_label.pack()

apply_theme()
update_color_info()
root.mainloop()