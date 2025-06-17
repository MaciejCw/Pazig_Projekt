import tkinter as tk
from PIL import Image, ImageTk

class HomePage:
    def __init__(self, master, go_to_fridge_callback, go_to_recipes_callback):
        self.master = master
        self.go_to_fridge_callback = go_to_fridge_callback
        self.go_to_recipes_callback = go_to_recipes_callback
        self.master.title("Smart Fridge")
        self.master.geometry("800x600")
        self.master.minsize(400, 300)

        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.background_image = Image.open("MainPage.jpeg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        self.title_label = tk.Label(
            self.canvas,
            text="Witaj w inteligentnej lodówce!",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#007acc",  
            padx=20,
            pady=10,
            bd=0
)


        self.fridge_button = tk.Button(
            self.canvas,
            text="Lodówka",
            command=self.fridge_action,
            font=("Arial", 14, "bold"),
            bg="#007acc",
            fg="white",
            activebackground="#005f99",
            activeforeground="white",
            padx=20,
            pady=8,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        self.recipes_button = tk.Button(
            self.canvas,
            text="Przepisy",
            command=self.recipes_action,
            font=("Arial", 14, "bold"),
            bg="#007acc",
            fg="white",
            activebackground="#005f99",
            activeforeground="white",
            padx=20,
            pady=8,
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        self.buttons = [self.fridge_button, self.recipes_button]

        # ✅ Hover efekt — działa poprawnie
        for btn in self.buttons:
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(b))

        self.title_window = self.canvas.create_window(0, 0, window=self.title_label)
        self.recipes_window = self.canvas.create_window(0, 0, window=self.recipes_button)
        self.fridge_window = self.canvas.create_window(0, 0, window=self.fridge_button)

        self.master.bind("<Configure>", self.on_resize)
        self.master.after(1, lambda: self.on_resize(None))

    def on_enter(self, button):
        button.config(bg="#005f99")

    def on_leave(self, button):
        button.config(bg="#007acc")

    def on_resize(self, event):
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        resized_bg = self.background_image.resize((width, height), resample=Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.background_photo)

        self.canvas.coords(self.title_window, width // 2, int(height * 0.15))
        self.canvas.coords(self.recipes_window, width // 2, height // 2)
        self.canvas.coords(self.fridge_window, width // 2, int(height * 0.7))

    def fridge_action(self):
        self.go_to_fridge_callback()

    def recipes_action(self):
        self.go_to_recipes_callback()
