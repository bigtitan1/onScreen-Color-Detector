import pyautogui
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import ImageGrab
import numpy as np
import webcolors
import csv
import keyboard
import json




# Global Variables
save_file_path = None
user_shortcut = None
last_color_data = None

# Setup CTk Appearance
ctk.set_appearance_mode("Dark")  # or "Light"
ctk.set_default_color_theme("dark-blue")

# Get average color from screen
def get_avg_color(x, y, area):
    half = area // 2
    bbox = (x - half, y - half, x + half, y + half)
    img = ImageGrab.grab(bbox=bbox)
    img_np = np.array(img)
    avg_color = img_np.mean(axis=(0, 1)).astype(int)
    return tuple(avg_color)

# Accurate color name finder
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


def load_settings():
    global user_shortcut
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            if "shortcut" in settings:
                user_shortcut = settings["shortcut"]
                keyboard.add_hotkey(user_shortcut, save_color_to_file)
                shortcut_entry.insert(0, user_shortcut)
                shortcut_status.configure(text=f"Shortcut '{user_shortcut}' loaded", text_color="green")
    except FileNotFoundError:
        pass


def show_toast(message, duration=1500):
    toast = ctk.CTkToplevel(root)
    toast.title("Notification")
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.attributes("-alpha", 0.9)  # Slight transparency

    # Size and position — bottom-right corner
    width, height = 220, 50
    x = root.winfo_x() + root.winfo_width() - width - 20
    y = root.winfo_y() + root.winfo_height() - height - 20
    toast.geometry(f"{width}x{height}+{x}+{y}")

    # Background and message
    frame = ctk.CTkFrame(toast, fg_color="#2a2a2a", corner_radius=10)
    frame.pack(expand=True, fill="both", padx=5, pady=5)

    label = ctk.CTkLabel(frame, text=message, text_color="white", font=("Segoe UI", 12))
    label.pack(padx=10, pady=10)

    # Auto-close
    toast.after(duration, toast.destroy)


# Live update color info
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

    color_label.configure(text=display_text)
    color_preview.configure(fg_color=hex_code)

    tooltip_label.configure(text=display_text)
    tooltip_window.geometry(f"+{x + 15}+{y + 20}")

    last_color_data = (color_name, rgb, hex_code)
    root.after(200, update_color_info)

# Save to file
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
        show_toast(f"{color_name} saved!")


    except Exception as e:
        messagebox.showerror("Error", str(e))

# File browser
def browse_file():
    global save_file_path
    path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV or TXT", "*.csv *.txt")])
    if path:
        save_file_path = path
        file_label.configure(text=f"Selected: {path}")

# Keyboard shortcut setup
def set_shortcut():
    global user_shortcut
    shortcut = shortcut_entry.get()
    if shortcut:
        try:
            if user_shortcut:
                keyboard.remove_hotkey(user_shortcut)
            keyboard.add_hotkey(shortcut, save_color_to_file)
            user_shortcut = shortcut
            shortcut_status.configure(text=f"Shortcut '{shortcut}' set!", text_color="green")
            save_settings()
        except Exception as e:
            shortcut_status.configure(text=f"Error: {str(e)}", text_color="red")
            


def save_settings():
    with open("settings.json", "w") as f:
        json.dump({"shortcut": user_shortcut}, f)

# Toggle features panel
def toggle_features():
    if feature_frame.winfo_ismapped():
        feature_frame.grid_remove()
    else:
        feature_frame.grid(row=6, column=1, columnspan=2, padx=20, pady=10, sticky="ew")

# GUI setup
root = ctk.CTk()
root.title("Color Assistant")
root.geometry("700x480")
root.resizable(False, False)

color_label = ctk.CTkLabel(root, text="Initializing...", font=('Segoe UI', 16))
color_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="ew")

hex_var = ctk.BooleanVar()
hex_check = ctk.CTkCheckBox(root, text="Show HEX Code", variable=hex_var)
hex_check.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")

ctk.CTkLabel(root, text="Pointer Area (px):").grid(row=2, column=0, padx=20, pady=(5, 0), sticky="w")
area_slider = ctk.CTkSlider(root, from_=1, to=50, number_of_steps=49)
area_slider.set(10)
area_slider.grid(row=3, column=1, columnspan=2, padx=20, pady=(0, 10))

color_preview = ctk.CTkFrame(root, width=180, height=100, fg_color="#ffffff", corner_radius=12)
color_preview.grid(row=1, column=3, rowspan=3, padx=10, pady=10, sticky="nsew")

feature_button = ctk.CTkButton(root, text="Additional Features", command=toggle_features)
feature_button.grid(row=4, column=1, columnspan=2, pady=(5, 0))

# Feature panel
feature_frame = ctk.CTkFrame(root, corner_radius=10)
file_button = ctk.CTkButton(feature_frame, text="Browse & Save File", command=browse_file)
file_button.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
file_label = ctk.CTkLabel(feature_frame, text="No file selected", font=("Arial", 10), wraplength=300)
file_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

ctk.CTkLabel(feature_frame, text="Set Shortcut (e.g. ctrl+shift+c):").grid(row=2, column=0, sticky="w", padx=5, pady=(5, 0))
shortcut_entry = ctk.CTkEntry(feature_frame, width=180)
shortcut_entry.grid(row=3, column=0, sticky="w", padx=5)
shortcut_set_button = ctk.CTkButton(feature_frame, text="Set", command=set_shortcut, width=50)
shortcut_set_button.grid(row=3, column=1, sticky="w", padx=5)
shortcut_status = ctk.CTkLabel(feature_frame, text="", font=("Arial", 10))
shortcut_status.grid(row=4, column=0, columnspan=2, sticky="w", padx=5)

feature_frame.grid_remove()

def toggle_minimized_mode():
    root.withdraw()  # Hide main window
    minimized_window = ctk.CTkToplevel()
    minimized_window.geometry("200x80+100+100")
    minimized_window.title("Color Preview")
    minimized_window.overrideredirect(False)
    minimized_window.attributes("-topmost", True)

    color_box = ctk.CTkLabel(minimized_window, width=30, height=30, text="")
    color_box.grid(row=0, column=0, padx=10, pady=10)

    color_text = ctk.CTkLabel(minimized_window, text="Fetching...")
    color_text.grid(row=0, column=1, padx=10)

    def update_minimized_color():
        if not minimized_window.winfo_exists():
            root.deiconify()  # Restore main window if closed
            return
        x, y = pyautogui.position()
        area = int(area_slider.get())
        rgb = get_avg_color(x, y, area)
        hex_code = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        name = get_color_name(rgb)
        color_box.configure(fg_color=hex_code)
        color_text.configure(text=f"{name}\n{hex_code}")
        minimized_window.after(200, update_minimized_color)

    update_minimized_color()

    def close_minimized():
        minimized_window.destroy()
        root.deiconify()  # Restore main window

    # Add a close button
    close_btn = ctk.CTkButton(minimized_window, text="Restore", command=close_minimized, width=60, height=20)
    close_btn.grid(row=1, column=0, columnspan=2, pady=(0, 10))
    
minimize_btn = ctk.CTkButton(root, text="Minimize View", command=toggle_minimized_mode)
minimize_btn.grid(row=0, column=3, columnspan=2, pady=5)


# Tooltip
tooltip_window = ctk.CTkToplevel(root)
tooltip_window.overrideredirect(True)
tooltip_window.attributes("-topmost", True)
tooltip_window.attributes("-alpha", 0.8)
tooltip_label = ctk.CTkLabel(tooltip_window, text="", font=("Segoe UI", 10), text_color="white")
tooltip_label.pack()

update_color_info()
load_settings()
root.mainloop()