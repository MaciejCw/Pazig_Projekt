import tkinter as tk
from PIL import Image, ImageTk
from db_setup import initialize_database
import sqlite3
class FridgePage:
    def __init__(self, master, go_home_callback, go_recipes_callback):
        self.master = master
        self.go_home_callback = go_home_callback
        self.go_recipes_callback = go_recipes_callback

        initialize_database()
        
        
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        
        self.background_image = Image.open("Fridge.jpeg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        
        self.ingredient_listbox = tk.Listbox(self.canvas, font=("Arial", 12), height=20, width=30, activestyle='none')
        self.ingredient_listbox.config(state="disabled")  

       
        self.add_button = tk.Button(self.canvas, text="Dodaj składnik", font=("Arial", 12), bg="#333", fg="white", relief="flat", command=self.add_ingredient)
        self.remove_button = tk.Button(self.canvas, text="Usuń składnik", font=("Arial", 12), bg="#333", fg="white", relief="flat", command=self.remove_ingredient)
        self.edit_button = tk.Button(self.canvas, text="Edytuj składnik", font=("Arial", 12), bg="#333", fg="white", relief="flat", command=self.edit_ingredient)
        self.home_button = tk.Button(self.canvas, text="Home Page", font=("Arial", 12), bg="#555", fg="white", relief="flat", command=self.go_home_callback)
        self.recipes_button = tk.Button(self.canvas, text="Recipies", font=("Arial", 12), bg="#555", fg="white", relief="flat", command=self.go_recipes_callback)

        
        self.listbox_window = self.canvas.create_window(0, 0, window=self.ingredient_listbox, anchor="nw")
        self.buttons = [
            self.add_button,
            self.remove_button,
            self.edit_button,
            self.recipes_button,
            self.home_button
            
        ]
        for btn in self.buttons:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555"))  
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#333" if b in self.buttons[:4] else "#444"))  
        self.button_windows = [self.canvas.create_window(0, 0, window=btn, anchor="ne") for btn in self.buttons]

        self.master.bind("<Configure>", self.on_resize)
        self.master.after(1, lambda: self.on_resize(None))
        self.refresh_ingredient_list()

    def on_resize(self, event):
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        resized_bg = self.background_image.resize((width, height), resample=Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.background_photo)

        
        self.canvas.coords(self.listbox_window, 20, int(height * 0.2))

        
        spacing = 50
        start_y = int(height * 0.25)
        for i, window in enumerate(self.button_windows):
            self.canvas.coords(window, width - 20, start_y + i * spacing)
    def refresh_ingredient_list(self):
        conn = sqlite3.connect("fridge.db")
        c = conn.cursor()
        c.execute("SELECT name, amount, unit FROM ingredients")
        rows = c.fetchall()
        conn.close()

        self.ingredient_listbox.config(state="normal")
        self.ingredient_listbox.delete(0, tk.END)
        for row in rows:
            self.ingredient_listbox.insert(tk.END, f"{row[0]}: {row[1]} {row[2]}")
        self.ingredient_listbox.config(state="disabled")


    def add_ingredient(self):
        def confirm_add(selected_unit):
            name = name_entry.get().strip()
            try:
                amount = int(amount_entry.get())
            except ValueError:
                return
            if name:
                conn = sqlite3.connect("fridge.db")
                c = conn.cursor()
                c.execute("INSERT INTO ingredients (name, amount, unit) VALUES (?, ?, ?)", (name, amount, selected_unit))
                conn.commit()
                conn.close()
                top.destroy()
                self.refresh_ingredient_list()


        top = tk.Toplevel(self.master)
        top.title("Dodaj składnik")

        tk.Label(top, text="Nazwa:").pack()
        name_entry = tk.Entry(top)
        name_entry.pack()

        tk.Label(top, text="Ilość:").pack()
        amount_entry = tk.Entry(top)
        amount_entry.pack()

        tk.Label(top, text="Jednostka:").pack()
        unit_var = tk.StringVar(top)
        unit_var.set("szt.")  
        tk.OptionMenu(top, unit_var, "szt.", "ml", "g", "kg", "l", "opak.").pack()

        tk.Button(top, text="Dodaj", command=lambda: confirm_add(unit_var.get())).pack(pady=5)


    def remove_ingredient(self):
        def confirm_delete():
            checked = [var for var, row in zip(vars_list, items) if var.get()]
            ids_to_delete = [row[0] for var, row in zip(vars_list, items) if var.get()]
            if ids_to_delete:
                conn = sqlite3.connect("fridge.db")
                c = conn.cursor()
                c.executemany("DELETE FROM ingredients WHERE id=?", [(id,) for id in ids_to_delete])
                conn.commit()
                conn.close()
                top.destroy()
                self.refresh_ingredient_list()

        top = tk.Toplevel(self.master)
        top.title("Usuń składniki")

        conn = sqlite3.connect("fridge.db")
        c = conn.cursor()
        c.execute("SELECT id, name, amount FROM ingredients")
        items = c.fetchall()
        conn.close()

        vars_list = []
        for row in items:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(top, text=f"{row[1]} ({row[2]})", variable=var)
            cb.pack(anchor="w")
            vars_list.append(var)

        tk.Button(top, text="Usuń zaznaczone", bg="red", fg="white", command=confirm_delete).pack(pady=5)


    def edit_ingredient(self):
        def update_amount():
            selected_name = selected.get()
            try:
                new_amount = int(new_amount_entry.get())
            except ValueError:
                return
            conn = sqlite3.connect("fridge.db")
            c = conn.cursor()
            c.execute("UPDATE ingredients SET amount=? WHERE name=?", (new_amount, selected_name))
            conn.commit()
            conn.close()
            top.destroy()
            self.refresh_ingredient_list()

        top = tk.Toplevel(self.master)
        top.title("Edytuj składnik")

        conn = sqlite3.connect("fridge.db")
        c = conn.cursor()
        c.execute("SELECT name FROM ingredients")
        names = [row[0] for row in c.fetchall()]
        conn.close()

        tk.Label(top, text="Wybierz składnik:").pack()
        selected = tk.StringVar(top)
        if names:
            selected.set(names[0])
        tk.OptionMenu(top, selected, *names).pack()

        tk.Label(top, text="Nowa ilość:").pack()
        new_amount_entry = tk.Entry(top)
        new_amount_entry.pack()

        tk.Button(top, text="Zapisz", command=update_amount).pack(pady=5)

