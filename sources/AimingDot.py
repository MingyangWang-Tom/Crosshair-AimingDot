import tkinter as tk
from tkinter import colorchooser, ttk
from pynput import mouse
import pystray
from PIL import Image, ImageDraw
import threading


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aiming Dot Controller")
        self.root.geometry('350x520')  # adjusted size
        self.root.configure(bg='#333')  # dark background

        # Use ttk for better looking widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', background='#555', foreground='white', padding=10)
        style.map('TButton', background=[('active', '#777')])

        self.dot_window = None  # Reference to the dot window
        self.mouse_listener = None

        self.dot_color = tk.StringVar(value="#FF0000")
        self.dot_x = tk.IntVar(value=self.root.winfo_screenwidth() // 2)
        self.dot_y = tk.IntVar(value=self.root.winfo_screenheight() // 2)
        self.dot_size = tk.IntVar(value=10)

        # Create and place the widgets
        ttk.Label(self.root, text="Dot X Coordinate:", foreground='white', background='#333').pack(pady=10)
        ttk.Entry(self.root, textvariable=self.dot_x).pack(pady=3, padx=20, fill='x')

        ttk.Label(self.root, text="Dot Y Coordinate:", foreground='white', background='#333').pack(pady=10)
        ttk.Entry(self.root, textvariable=self.dot_y).pack(pady=3, padx=20, fill='x')

        ttk.Label(self.root, text="Dot Size:", foreground='white', background='#333').pack(pady=10)
        ttk.Scale(self.root, from_=3, to=20, orient=tk.HORIZONTAL, variable=self.dot_size).pack(pady=5, padx=20,
                                                                                                fill='x')

        ttk.Button(self.root, text="Choose Color", command=self.choose_color).pack(pady=10)
        ttk.Label(self.root, textvariable=self.dot_color, foreground='white', background='#333').pack(pady=5)

        ttk.Button(self.root, text="Show Dot", command=self.show_dot).pack(pady=5)
        ttk.Button(self.root, text="Hide Dot", command=self.hide_dot).pack(pady=5)

        # Toggle right-click behavior button
        self.toggle_btn = ttk.Button(self.root, text="Enable Right-Click Hide", command=self.toggle_mouse_listener)
        self.toggle_btn.pack(pady=5)

        ttk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=15)

        self.tray_icon = None
        icon_image = self.create_icon()
        self.tray_icon = pystray.Icon("name", icon_image, "Aiming Dot Controller", self.create_menu())

        # This binds the close button to minimize to tray instead of quitting
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)

        self.root.mainloop()

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.dot_color.set(color)

    def show_dot(self):
        if self.dot_window:
            self.dot_window.destroy()

        self.dot_window = tk.Toplevel(self.root)
        self.dot_window.overrideredirect(True)
        size = self.dot_size.get()
        self.dot_window.geometry(f"+{self.dot_x.get() - size // 2}+{self.dot_y.get() - size // 2}")
        self.dot_window.wm_attributes("-topmost", True)
        self.dot_window.wm_attributes("-transparentcolor", "white")

        # Using a 1 pixel padding prevents small dots from being clipped or
        # appearing squared due to window borders.
        canvas = tk.Canvas(
            self.dot_window,
            width=size + 2,
            height=size + 2,
            bg="white",
            bd=0,
            highlightthickness=0,
        )
        canvas.pack()
        canvas.create_oval(
            1,
            1,
            size + 1,
            size + 1,
            fill=self.dot_color.get(),
            outline="",
        )

    def toggle_mouse_listener(self):
        if self.mouse_listener and self.mouse_listener.running:
            self.mouse_listener.stop()
            self.toggle_btn.config(text="Enable Right-Click Hide")
        else:
            self.mouse_listener = mouse.Listener(on_click=self.handle_click)
            self.mouse_listener.start()
            self.toggle_btn.config(text="Disable Right-Click Hide")

    def handle_click(self, x, y, button, pressed):
        if button == mouse.Button.right:
            if pressed:
                self.hide_dot()
            else:
                self.reveal_dot()

    def hide_dot(self):
        if self.dot_window:
            self.dot_window.withdraw()

    def reveal_dot(self):
        if self.dot_window:
            self.dot_window.deiconify()

    # Create an icon for the system tray
    def create_icon(self):
        width = 64
        height = 64
        color1 = "white"
        color2 = "black"

        image = Image.new("RGB", (width, height), color1)
        dc = ImageDraw.Draw(image)
        # Draw a simple cross for the tray icon. Using lines avoids the issue of
        # accidentally creating zero-height or zero-width rectangles.
        dc.line((width // 2, 0, width // 2, height), fill=color2)
        dc.line((0, height // 2, width, height // 2), fill=color2)

        return image

    # Create menu for the system tray icon
    def create_menu(self):
        return (pystray.MenuItem('Open', self.show_from_tray),
                pystray.MenuItem('Exit', self.exit_app))

    # Function to show the main window from tray
    def show_from_tray(self, icon, item):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.root.deiconify()

    # Minimize main window to system tray
    def minimize_to_tray(self):
        self.root.withdraw()
        icon_image = self.create_icon()
        self.tray_icon = pystray.Icon("name", icon_image, "Aiming Dot Controller", self.create_menu())
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    # Exiting the app
    def exit_app(self, icon, item):
        if self.mouse_listener and self.mouse_listener.running:
            self.mouse_listener.stop()
        if self.dot_window:
            self.dot_window.destroy()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()


if __name__ == "__main__":
    App()
