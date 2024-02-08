import tkinter as tk
from tkinter import Listbox, Button, font, Scrollbar, Menu
import pygetwindow as gw
import configparser
import os
import sys

window_blacklist = []

def on_exit():
    root.destroy()

def on_move_resize(window_title, x, y, width, height):
    window = gw.getWindowsWithTitle(window_title)
    if window:
        window = window[0]

        # restore the window if it is minimized
        if window.isMinimized:
            window.restore()
            
        window.moveTo(x, y)
        window.resizeTo(width, height)

def create_button(button_id, button_bg, x, y, width, height, text):
    button = Button(
        button_frame,
        text=text,
        bg=button_bg,
        fg='#AAA',
        bd=0,
        height=2,
        font=('Lucida Console', 8)
    )
    # button.config(width=button_width)
    if text!='':
        button.config(command=lambda b=button_id, x=x, y=y, width=width, height=height: on_move_resize(listbox.get(tk.ACTIVE), x, y, width, height))
    return button


def refresh_listbox(event=None):
    listbox.delete(0, tk.END)

    open_windows = get_open_windows()
    for i, window_title in enumerate(open_windows):
        if any(name in window_title for name in window_blacklist):
            continue  # Skip this window if it matches any blacklisted name
        
        listbox.insert(tk.END, window_title)

    for i in range(listbox.size()):
        bg_color = '#555' if i % 2 == 0 else '#444'
        listbox.itemconfig(i, {'bg': bg_color})


def load_config():
    global window_blacklist
    config = configparser.ConfigParser(strict=False)

    # determine the base directory in both scenarios
    if getattr(sys, 'frozen', False):
        # running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # running as script
        base_dir = os.path.abspath(os.path.dirname(__file__))

    # create a close button at the top right corner of the window
    close_button = Button(root, text="X", bg='#402828', fg='#666', bd=0, command=on_exit, width=2, padx=8)
    close_button.place(relx=0.985, rely=0.01, anchor="ne")
            
    config_file_path = os.path.join(base_dir, 'config.ini')

    try:
        config.read(config_file_path)

        exclude_window_names_string = config.get('Mover', 'exclude_window_names')
        window_blacklist = exclude_window_names_string.strip('][').replace('"', '').split(', ')

        max_button_id = max(int(section[6:]) for section in config.sections() if section.startswith('Button'))

        for button_id in range(1, max_button_id + 1):
            button_section = f'Button{button_id}'

            # check if the section exists before trying to read values
            if config.has_section(button_section):
                x = int(config.get(button_section, 'x'))
                y = int(config.get(button_section, 'y'))
                width = int(config.get(button_section, 'width'))
                height = int(config.get(button_section, 'height'))
                text = config.get(button_section, 'text')

                button_bg = ''
                if ((button_id-1)%5 + int((button_id-1)/5))%2:
                    button_bg = '#535460'
                else:
                    button_bg = '#585860'

                button = create_button(button_id, button_bg, x, y, width, height, text)
                button.grid(row=int((button_id-1)/5), column=(button_id-1)%5, sticky="ew", padx=1, pady=1)
                #button.pack(side=tk.LEFT, padx=1, pady=1)
            else:
                # print(f"Section '{button_section}' not found in config.ini")
                button = create_button(button_id, '#323232', x, y, width, height, '')
                button.grid(row=int((button_id-1)/5), column=(button_id-1)%5, sticky="ew", padx=1, pady=1)

        mover_settings = 'Mover'
        if config.has_section(mover_settings):
            width = int(config.get(mover_settings, 'width'))
            height = int(config.get(mover_settings, 'height'))
            x_off = int(config.get(mover_settings, 'x'))
            y_off = int(config.get(mover_settings, 'y'))
            set_app_size(int((max_button_id-1)/5), width, height, x_off, y_off)

        status_label.config(text='Config loaded successfully', fg='green')
        
    except (KeyError, ValueError) as e:
        status_label.config(text=f'Error loading config: {e}', fg='red')

def restart_application():
    root.destroy()
    python = sys.executable
    os.execl(python, python, *sys.argv)

def open_ini_path():
    # determine the base directory in both scenarios
    if getattr(sys, 'frozen', False):
        # running as compiled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # running as script
        base_dir = os.path.abspath(os.path.dirname(__file__))

    config_file_path = os.path.join(base_dir, 'config.ini')

    try:
        # open the file path using the default file explorer
        os.startfile(config_file_path)
    except AttributeError:
        # for non-Windows systems, use other methods
        import subprocess
        subprocess.run(["xdg-open", config_file_path])

# Get open windows
def get_open_windows():
    return [title for title in gw.getAllTitles() if title]

def set_app_size(rows, width, height, x, y):
    # determine screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate the center coordinates
    center_x = int((screen_width - root.winfo_reqwidth()) / 2 + x)
    center_y = int((screen_height - root.winfo_reqheight()) / 2 + y)

    # get the first button widget
    first_button = button_frame.winfo_children()[0]

    # get the height of the first button
    button_height = first_button.winfo_reqheight()
    
    adjusted_height = 5+height+(rows+1)*(2+button_height)

    # set size and position
    root.geometry(f"{width}x{adjusted_height}+{center_x}+{center_y}")

def start_drag(event):
    global last_x, last_y
    last_x = event.x_root
    last_y = event.y_root

def do_drag(event):
    global last_x, last_y
    new_x = root.winfo_x() + (event.x_root - last_x)
    new_y = root.winfo_y() + (event.y_root - last_y)
    root.geometry(f"+{new_x}+{new_y}")
    last_x = event.x_root
    last_y = event.y_root

# root window
root = tk.Tk()
root.title('Mover (unregistered)')

# create a frame to contain all widgets with a border
root_bgHaxyBorder = tk.Frame(root, bd=0, padx=1, pady=1, relief='solid', bg='#333')
root_bgHaxyBorder.pack(expand=True, fill=tk.BOTH)

# create a frame to contain all widgets with a border
root_frame = tk.Frame(root_bgHaxyBorder, bd=0, relief='solid', bg='#222')
root_frame.pack(expand=True, fill=tk.BOTH)

# set the window to stay on top
root.attributes('-topmost', True)

# set the font for the entire application
app_font = font.Font(family='Lucida Console', size=10)
root.option_add("*Font", app_font)

# Make the app non-resizable
root.resizable(False, False)

# Big box color
root.configure(bg='#222')  # or root['bg'] = '#444'

# create a status label
status_label = tk.Label(root_frame, text='', fg='green', bg='#222')
status_label.pack(pady=(6, 0))

frame = tk.Frame(root_frame, bg='#222') #yoyomane
frame.pack(side=tk.TOP, ipady=10)
        
# create a Listbox
listbox = Listbox(frame, bg='#323232', fg='#AAA', selectbackground='#535460', width=100, height=23, bd=0, borderwidth=0, highlightthickness=0)
listbox.pack(pady=(3, 0), padx=(9,8), expand=True, fill=tk.BOTH)

# configure the Listbox to hide the scrollbar visibility
listbox.config(yscrollcommand=lambda *args: None)

# create a Frame below the Listbox
frame_below_listbox = tk.Frame(root_frame, bg='#222', bd=1, width=100)
frame_below_listbox.pack(padx=7, fill=tk.BOTH, side=tk.BOTTOM)

# create a sub-frame inside frame_below_listbox to hold the buttons
button_frame = tk.Frame(frame_below_listbox, bg='#292929')
button_frame.pack(pady=(0, 7), fill=tk.BOTH, expand=True)

# Configure grid columns to be flexible
for i in range(5):  # Assuming 5 columns
    button_frame.grid_columnconfigure(i, weight=1)

# bind listbox click event to refresh
status_label.bind('<ButtonRelease-1>', refresh_listbox)

# bind label click event to update buttons
status_label.bind('<Button-2>', lambda event: restart_application())
status_label.bind('<Button-3>', lambda event: open_ini_path())

# load config and create buttons
load_config()

# create and add the move/resize buttons
refresh_listbox()

# Set the path to your icon file
icon_path = "icon.ico"

# Set the icon for the application
root.iconbitmap(icon_path)

# Hide the title bar
root.overrideredirect(True)

# Bind mouse events to start and continue dragging
root.bind("<Button-1>", start_drag)
root.bind("<B1-Motion>", do_drag)

root.mainloop()
