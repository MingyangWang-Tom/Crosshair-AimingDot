import tkinter as tk
from tkinter import colorchooser
from pynput import mouse

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aiming Dot Controller")

        self.dot_window = None  # Reference to the dot window
        self.mouse_listener = None

        self.dot_color = tk.StringVar(value="#FF0000")
        self.dot_x = tk.IntVar(value=self.root.winfo_screenwidth() // 2)
        self.dot_y = tk.IntVar(value=self.root.winfo_screenheight() // 2)
        self.dot_size = tk.IntVar(value=10)

        tk.Label(self.root, text="Dot X Coordinate:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.dot_x).pack(pady=5)

        tk.Label(self.root, text="Dot Y Coordinate:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.dot_y).pack(pady=5)

        tk.Label(self.root, text="Dot Size:").pack(pady=5)
        tk.Scale(self.root, from_=5, to=50, orient=tk.HORIZONTAL, variable=self.dot_size).pack(pady=5)

        tk.Button(self.root, text="Choose Color", command=self.choose_color).pack(pady=5)
        tk.Label(self.root, textvariable=self.dot_color).pack(pady=5)

        tk.Button(self.root, text="Show Dot", command=self.show_dot).pack(pady=10)

        # Toggle right-click behavior button
        self.toggle_btn = tk.Button(self.root, text="Enable Right-Click Hide", command=self.toggle_mouse_listener)
        self.toggle_btn.pack(pady=10)

        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=10)

        self.root.mainloop()

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.dot_color.set(color)

    def show_dot(self):
        # Destroy the old dot window if it exists
        if self.dot_window:
            self.dot_window.destroy()

        self.dot_window = tk.Toplevel(self.root)
        self.dot_window.overrideredirect(True)
        size = self.dot_size.get()
        self.dot_window.geometry(f"+{self.dot_x.get()-size//2}+{self.dot_y.get()-size//2}")
        self.dot_window.wm_attributes("-topmost", True)
        self.dot_window.wm_attributes("-transparentcolor", "white")

        canvas = tk.Canvas(self.dot_window, width=size, height=size, bg="white", bd=0, highlightthickness=0)
        canvas.pack()
        canvas.create_oval(0, 0, size, size, fill=self.dot_color.get())

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

if __name__ == "__main__":
    App()
