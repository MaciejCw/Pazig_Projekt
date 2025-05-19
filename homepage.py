import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class HomePage:
    def __init__(self, master):
        self.master = master
        self.master.title("Smart Fridge")
        self.master.geometry("800x600")  # początkowy rozmiar
        self.master.minsize(400, 300)

        # kontener do trzymania tła i reszty
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # załaduj tło
        self.background_image = Image.open("MainPage.jpeg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # Napisy i przyciski jako "window" w Canvas
        self.title_label = ttk.Label(self.master, text="Welcome To Smart Fridge!", font=("Arial", 28, "bold"), background="#ffffff")
        self.fridge_button = ttk.Button(self.master, text="Fridge", command=self.fridge_action)
        self.recipes_button = ttk.Button(self.master, text="Recipies", command=self.recipes_action)

        # Dodaj do canvas jako okna
        self.title_window = self.canvas.create_window(0, 0, window=self.title_label)
        self.fridge_window = self.canvas.create_window(0, 0, window=self.fridge_button)
        self.recipes_window = self.canvas.create_window(0, 0, window=self.recipes_button)

        # obsługa skalowania
        self.master.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # dopasuj tło
        resized_bg = self.background_image.resize((event.width, event.height), Image.ANTIALIAS)
        self.background_photo = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.background_photo)

        # pozycje elementów
        self.canvas.coords(self.title_window, event.width // 2, event.height // 6)
        self.canvas.coords(self.recipes_window, event.width // 2, event.height // 2)
        self.canvas.coords(self.fridge_window, event.width // 2, int(event.height * 0.7))

    def fridge_action(self):
        pass  # tu później dodasz przejście do strony lodówki

    def recipes_action(self):
        pass  # tu później dodasz przejście do przepisów
