import tkinter as tk
from tkinter import Listbox, Button, font, Scrollbar, Menu
import pygetwindow as gw
import configparser
import os
import sys

def on_exit():
    root.destroy()

def on_move_resize(window_title, x, y, width, height):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window = window[0]

        # Restore the window if it is minimized
        if window.isMinimized:
            window.restore()
            
        window.moveTo(x, y)
        window.resizeTo(width, height)

def create_button(button_id, x, y, width, height, text):
    return Button(
        frame_below_listbox,
        text=text,
        bg='#666',
        bd=0,
        width=13,
        height=3,
        command=lambda b=button_id, x=x, y=y, width=width, height=height: on_move_resize(listbox.get(tk.ACTIVE), x, y, width, height),
    )

def refresh_listbox(event=None):
    listbox.delete(0, tk.END)
    open_windows = get_open_windows()
    for i, window_title in enumerate(open_windows):
        listbox.insert(tk.END, window_title)
        # Set alternating colors after inserting items
        bg_color = '#555' if i % 2 == 0 else '#444'
        listbox.itemconfig(i, {'bg': bg_color})

def load_config():
    config = configparser.ConfigParser()

    # Determine the base directory in both scenarios
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.abspath(os.path.dirname(__file__))

    config_file_path = os.path.join(base_dir, 'config.ini')

    try:
        config.read(config_file_path)

        for button_id in range(1, 6):
            button_section = f'Button{button_id}'

            # Check if the section exists before trying to read values
            if config.has_section(button_section):
                x = int(config.get(button_section, 'x'))
                y = int(config.get(button_section, 'y'))
                width = int(config.get(button_section, 'width'))
                height = int(config.get(button_section, 'height'))
                text = config.get(button_section, 'text')

                button = create_button(button_id, x, y, width, height, text)
                button.pack(side=tk.LEFT, padx=1, pady=1, fill=tk.BOTH, expand=True)
            else:
                print(f"Section '{button_section}' not found in config.ini")

        status_label.config(text='Config loaded successfully', fg='green')

    except (KeyError, ValueError) as e:
        status_label.config(text=f'Error loading config: {e}', fg='red')

def restart_application():
    root.destroy()
    python = sys.executable
    os.execl(python, python, *sys.argv)

def open_ini_path():
    # Determine the base directory in both scenarios
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.abspath(os.path.dirname(__file__))

    config_file_path = os.path.join(base_dir, 'config.ini')

    try:
        # Open the file path using the default file explorer
        os.startfile(config_file_path)
    except AttributeError:
        # For non-Windows systems, use other methods
        import subprocess
        subprocess.run(["xdg-open", config_file_path])


# Get open windows
def get_open_windows():
    return [title for title in gw.getAllTitles() if title]

# root window
root = tk.Tk()
root.title('MOVER')

# Set the window to stay on top
root.attributes('-topmost', True)

# Set the font for the entire application
app_font = font.Font(family='Lucida Console', size=10)
root.option_add("*Font", app_font)

# Make the app non-resizable
root.resizable(False, False)


# Determine screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the center coordinates
center_x = int((screen_width - root.winfo_reqwidth()) / 2)
center_y = int((screen_height - root.winfo_reqheight()) / 2)

# Set size and position
root.geometry(f"560x420+{center_x}+{center_y}")

# Big box color
root.configure(bg='#222')  # or root['bg'] = '#444'

# create a status label
status_label = tk.Label(root, text='', fg='green', bg='#222')
status_label.pack(pady=(4, 2))

frame = tk.Frame(root, bg='#222') #yoyomane
frame.pack(side=tk.TOP, ipady=10)
        
# create a Listbox
listbox = Listbox(frame, bg='#333', fg='#AAA', selectbackground='#555', width=100, height=23, bd=0, borderwidth=0, highlightthickness=0)
listbox.pack(pady=0, padx=7, expand=True, fill=tk.BOTH)


# Configure the Listbox to hide the scrollbar visibility
listbox.config(yscrollcommand=lambda *args: None)


# create a Frame below the Listbox
frame_below_listbox = tk.Frame(root, bg='#222', bd=1, width=100)
frame_below_listbox.pack(pady=(0, 5), padx=5, expand=False, side=tk.BOTTOM)

# bind listbox click event to refresh
status_label.bind('<ButtonRelease-1>', refresh_listbox)

# bind label click event to update buttons
status_label.bind('<ButtonRelease-1>', lambda event: restart_application())

status_label.bind('<Button-3>', lambda event: open_ini_path())

# load config and create buttons
load_config()

# create and add the move/resize buttons
refresh_listbox()

root.mainloop()
