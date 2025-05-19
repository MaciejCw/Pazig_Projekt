import tkinter as tk
from PIL import Image, ImageTk

class RecipiesPage:
    def __init__(self, master, go_to_fridge_callback, go_to_home_callback):
        self.master = master
        self.go_to_fridge_callback = go_to_fridge_callback
        self.go_to_home_callback = go_to_home_callback

        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.background_image = Image.open("Fridge.jpeg")  # Możesz zmienić tło na inne
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # Lista przepisów
        self.recipe_listbox = tk.Listbox(self.canvas, font=("Arial", 12), height=15, width=35, activestyle='none')
        self.recipe_listbox.insert(tk.END, "Przepis 1")
        self.recipe_listbox.insert(tk.END, "Przepis 2")
        self.recipe_listbox.config(state="disabled")

        # Przyciski
        self.show_button = tk.Button(self.canvas, text="Wyświetl\ndostępne przepisy", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.show_recipes)
        self.add_button = tk.Button(self.canvas, text="Dodaj przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.add_recipe)
        self.remove_button = tk.Button(self.canvas, text="Usuń przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.remove_recipe)
        self.edit_button = tk.Button(self.canvas, text="Edytuj przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.edit_recipe)
        self.fridge_button = tk.Button(self.canvas, text="Fridge", font=("Arial", 14), bg="#555", fg="white", relief="flat", command=self.go_to_fridge_callback)
        self.home_button = tk.Button(self.canvas, text="Homepage", font=("Arial", 14), bg="#555", fg="white", relief="flat", command=self.go_to_home_callback)

        # Umieszczenie elementów
        self.listbox_window = self.canvas.create_window(0, 0, window=self.recipe_listbox, anchor="nw")
        self.buttons = [
            self.show_button,
            self.add_button,
            self.remove_button,
            self.edit_button,
            self.fridge_button,
            self.home_button
        ]
        self.button_windows = [self.canvas.create_window(0, 0, window=btn, anchor="ne") for btn in self.buttons]

        self.master.bind("<Configure>", self.on_resize)
        self.master.after(1, lambda: self.on_resize(None))

    def on_resize(self, event):
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        resized_bg = self.background_image.resize((width, height), resample=Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.background_photo)

        # Przesunięta i mniejsza lista przepisów
        self.canvas.coords(self.listbox_window, int(width * 0.15), int(height * 0.2))

        # Równomierne rozmieszczenie przycisków po prawej stronie
        spacing = 70  # większy odstęp
        start_y = int(height * 0.25)

        for i, window in enumerate(self.button_windows):
            self.canvas.coords(window, width - 60, start_y + i * spacing)


    def show_recipes(self):
        pass

    def add_recipe(self):
        pass

    def remove_recipe(self):
        pass

    def edit_recipe(self):
        pass
