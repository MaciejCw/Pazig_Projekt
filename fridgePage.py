import tkinter as tk
from PIL import Image, ImageTk

class FridgePage:
    def __init__(self, master, go_home_callback, go_recipes_callback):
        self.master = master
        self.go_home_callback = go_home_callback
        self.go_recipes_callback = go_recipes_callback

        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Tło
        self.background_image = Image.open("Fridge.jpeg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # Lista składników (niedostępna do edycji)
        self.ingredient_listbox = tk.Listbox(self.canvas, font=("Arial", 12), height=20, width=30, activestyle='none')
        self.ingredient_listbox.insert(tk.END, "Składnik 1")
        self.ingredient_listbox.insert(tk.END, "Składnik 2")
        self.ingredient_listbox.config(state="disabled")  # blokuje interakcję

        # Przyciski
        self.add_button = tk.Button(self.canvas, text="Dodaj składnik", font=("Arial", 12), bg="#333", fg="white", relief="flat", command=self.add_ingredient)
        self.remove_button = tk.Button(self.canvas, text="Usuń składnik", font=("Arial", 12), bg="#333", fg="white", relief="flat", command=self.remove_ingredient)
        self.edit_button = tk.Button(self.canvas, text="Edytuj składnik", font=("Arial", 12), bg="#333", fg="white", relief="flat", command=self.edit_ingredient)
        self.home_button = tk.Button(self.canvas, text="Home Page", font=("Arial", 12), bg="#555", fg="white", relief="flat", command=self.go_home_callback)
        self.recipes_button = tk.Button(self.canvas, text="Recipies", font=("Arial", 12), bg="#555", fg="white", relief="flat", command=self.go_recipes_callback)

        # Canvas window
        self.listbox_window = self.canvas.create_window(0, 0, window=self.ingredient_listbox, anchor="nw")
        self.buttons = [
            self.add_button,
            self.remove_button,
            self.edit_button,
            self.home_button,
            self.recipes_button
        ]
        for btn in self.buttons:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555"))  # ciemniejsze tło
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#333" if b in self.buttons[:4] else "#444"))  # oryginalny kolor
        self.button_windows = [self.canvas.create_window(0, 0, window=btn, anchor="ne") for btn in self.buttons]

        self.master.bind("<Configure>", self.on_resize)
        self.master.after(1, lambda: self.on_resize(None))

    def on_resize(self, event):
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        resized_bg = self.background_image.resize((width, height), resample=Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.background_photo)

        # Lista po lewej
        self.canvas.coords(self.listbox_window, 20, int(height * 0.2))

        # Przyciski po prawej
        spacing = 50
        start_y = int(height * 0.25)
        for i, window in enumerate(self.button_windows):
            self.canvas.coords(window, width - 20, start_y + i * spacing)

    def add_ingredient(self):
        pass

    def remove_ingredient(self):
        pass

    def edit_ingredient(self):
        pass
