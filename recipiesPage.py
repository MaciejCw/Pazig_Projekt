import tkinter as tk
from PIL import Image, ImageTk
from recipe_db import initialize_recipe_database
import sqlite3
class RecipiesPage:
    def __init__(self, master, go_to_fridge_callback, go_to_home_callback):
        self.master = master
        self.go_to_fridge_callback = go_to_fridge_callback
        self.go_to_home_callback = go_to_home_callback

        initialize_recipe_database()
        self.canvas = tk.Canvas(self.master, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.background_image = Image.open("recipies.jpeg")  
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.bg_image_id = self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        
        self.recipe_listbox = tk.Listbox(self.canvas, font=("Arial", 12), height=15, width=35, activestyle='none')
        self.recipe_listbox.config(state="disabled")

        
        self.show_button = tk.Button(self.canvas, text="Wyświetl\ndostępne przepisy", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.show_recipes)
        self.add_button = tk.Button(self.canvas, text="Dodaj przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.add_recipe)
        self.remove_button = tk.Button(self.canvas, text="Usuń przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.remove_recipe)
        self.edit_button = tk.Button(self.canvas, text="Edytuj przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.edit_recipe)
        self.home_button = tk.Button(self.canvas, text="Homepage", font=("Arial", 14), bg="#555", fg="white", relief="flat", command=self.go_to_home_callback)
        self.fridge_button = tk.Button(self.canvas, text="Fridge", font=("Arial", 14), bg="#555", fg="white", relief="flat", command=self.go_to_fridge_callback)
        

        
        self.listbox_window = self.canvas.create_window(0, 0, window=self.recipe_listbox, anchor="nw")
        self.buttons = [
            self.show_button,
            self.add_button,
            self.remove_button,
            self.edit_button,
            self.fridge_button,
            self.home_button
  
        ]
        for btn in self.buttons:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555"))  
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#333" if b in self.buttons[:4] else "#444"))  # oryginalny kolor
        self.button_windows = [self.canvas.create_window(0, 0, window=btn, anchor="ne") for btn in self.buttons]

        self.master.bind("<Configure>", self.on_resize)
        self.master.after(1, lambda: self.on_resize(None))
        self.refresh_recipe_list()
    def on_resize(self, event):
        width = self.master.winfo_width()
        height = self.master.winfo_height()

        resized_bg = self.background_image.resize((width, height), resample=Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_image_id, image=self.background_photo)

        
        self.canvas.coords(self.listbox_window, int(width * 0.15), int(height * 0.2))

        
        spacing = 70  
        start_y = int(height * 0.25)

        for i, window in enumerate(self.button_windows):
            self.canvas.coords(window, width - 60, start_y + i * spacing)


    def show_recipes(self):

        pass

    def add_recipe(self):
        top = tk.Toplevel(self.master)
        top.title("Dodaj przepis")

        def browse_image():
            from tkinter import filedialog
            path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg *.png *.jpeg")])
            if path:
                image_entry.delete(0, tk.END)
                image_entry.insert(0, path)

        def confirm_add():
            name = name_entry.get().strip()
            ingredients = ingredients_text.get("1.0", tk.END).strip()
            instructions = instructions_text.get("1.0", tk.END).strip()
            image_path = image_entry.get().strip()

            if not name or not ingredients:
                return
            
            ingredients_raw = ingredients_text.get("1.0", tk.END).strip()
            ingredients = []
            for item in ingredients_raw.split(";"):
                parts = item.strip().split(":")
                if len(parts) == 3:
                    ing_name, ing_amount, ing_unit = parts
                try:
                    ing_amount = float(ing_amount)
                    ingredients.append((ing_name.strip(), ing_amount, ing_unit.strip()))
                except ValueError:
                    continue  

            conn = sqlite3.connect("recipes.db")
            c = conn.cursor()
            c.execute("INSERT INTO recipes (name, instructions, image_path) VALUES (?, ?, ?)", (name, instructions, image_path))
            recipe_id = c.lastrowid

            for ing_name, ing_amount, ing_unit in ingredients:
                c.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_name, amount, unit) VALUES (?, ?, ?, ?)",
              (recipe_id, ing_name, ing_amount, ing_unit))
                
            conn.commit()
            conn.close()
            top.destroy()
            self.refresh_recipe_list()

        tk.Label(top, text="Nazwa:").pack()
        name_entry = tk.Entry(top)
        name_entry.pack()

        tk.Label(top, text="Składniki (format: mleko:200:ml;cukier:50:g):").pack()
        ingredients_text = tk.Text(top, height=5)
        ingredients_text.pack()

        tk.Label(top, text="Sposób przygotowania:").pack()
        instructions_text = tk.Text(top, height=5)
        instructions_text.pack()

        tk.Label(top, text="Ścieżka do zdjęcia:").pack()
        image_entry = tk.Entry(top)
        image_entry.pack()
        tk.Button(top, text="Przeglądaj...", command=browse_image).pack()

        tk.Button(top, text="Dodaj przepis", command=confirm_add).pack(pady=5)


    def remove_recipe(self):
        top = tk.Toplevel(self.master)
        top.title("Usuń przepis")

        conn = sqlite3.connect("recipes.db")
        c = conn.cursor()
        c.execute("SELECT id, name FROM recipes ORDER BY name ASC")
        items = c.fetchall()
        conn.close()

        vars_list = []
        for row in items:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(top, text=row[1], variable=var)
            cb.pack(anchor="w")
            vars_list.append((var, row[0]))

        def confirm_delete():
            ids_to_delete = [recipe_id for var, recipe_id in vars_list if var.get()]
            if ids_to_delete:
                conn = sqlite3.connect("recipes.db")
                c = conn.cursor()
                c.executemany("DELETE FROM recipes WHERE id=?", [(id,) for id in ids_to_delete])
                conn.commit()
                conn.close()
                top.destroy()
                self.refresh_recipe_list()

        tk.Button(top, text="Usuń zaznaczone", bg="red", fg="white", command=confirm_delete).pack(pady=5)


    def edit_recipe(self):
        top = tk.Toplevel(self.master)
        top.title("Edytuj przepis")

        conn = sqlite3.connect("recipes.db")
        c = conn.cursor()
        c.execute("SELECT id, name FROM recipes ORDER BY name ASC")
        recipes = c.fetchall()
        conn.close()

        selected = tk.StringVar(top)
        if recipes:
            selected.set(recipes[0][1])
        names_to_ids = {name: rid for rid, name in recipes}

        tk.Label(top, text="Wybierz przepis:").pack()
        tk.OptionMenu(top, selected, *names_to_ids.keys()).pack()
        
        def load_recipe():
            rid = names_to_ids[selected.get()]
            conn = sqlite3.connect("recipes.db")
            c = conn.cursor()
            c.execute("SELECT name, instructions, image_path FROM recipes WHERE id=?", (rid,))
            name, instructions, image_path = c.fetchone()

            c.execute("SELECT ingredient_name, amount, unit FROM recipe_ingredients WHERE recipe_id=?", (rid,))
            ingredients_rows = c.fetchall()
            conn.close()

            ingredients = ";".join([f"{n}:{a}:{u}" for n, a, u in ingredients_rows])

            edit_win = tk.Toplevel(top)
            edit_win.title(f"Edytuj: {name}")

            tk.Label(edit_win, text="Nazwa:").pack()
            name_entry = tk.Entry(edit_win)
            name_entry.insert(0, name)
            name_entry.pack()

            tk.Label(edit_win, text="Składniki:").pack()
            ingredients_text = tk.Text(edit_win, height=5)
            ingredients_text.insert("1.0", ingredients)
            ingredients_text.pack()

            tk.Label(edit_win, text="Instrukcje:").pack()
            instructions_text = tk.Text(edit_win, height=5)
            instructions_text.insert("1.0", instructions)
            instructions_text.pack()

            tk.Label(edit_win, text="Obraz:").pack()
            image_entry = tk.Entry(edit_win)
            image_entry.insert(0, image_path)
            image_entry.pack()

            def update():
                new_name = name_entry.get().strip()
                new_ingredients_text = ingredients_text.get("1.0", tk.END).strip()
                new_instructions = instructions_text.get("1.0", tk.END).strip()
                new_image_path = image_entry.get().strip()

                conn = sqlite3.connect("recipes.db")
                c = conn.cursor()
                c.execute("""UPDATE recipes SET name=?, instructions=?, image_path=? WHERE id=?""",
                    (new_name, new_instructions, new_image_path, rid))

                c.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?", (rid,))

        
                if new_ingredients_text:
                    for part in new_ingredients_text.split(";"):
                        try:
                            ing_name, ing_amount, ing_unit = part.strip().split(":")
                            c.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_name, amount, unit) VALUES (?, ?, ?, ?)",
                                  (rid, ing_name, int(ing_amount), ing_unit))
                        except ValueError:
                            continue

                conn.commit()
                conn.close()
                edit_win.destroy()
                top.destroy()
                self.refresh_recipe_list()

            tk.Button(edit_win, text="Zapisz zmiany", command=update).pack(pady=5)
        tk.Button(top, text="Załaduj przepis", command=load_recipe).pack(pady=5)

    def refresh_recipe_list(self):
        conn = sqlite3.connect("recipes.db")
        c = conn.cursor()
        c.execute("SELECT name FROM recipes ORDER BY name ASC")
        rows = c.fetchall()
        conn.close()

        self.recipe_listbox.config(state="normal")
        self.recipe_listbox.delete(0, tk.END)
        for row in rows:
            self.recipe_listbox.insert(tk.END, row[0])
        self.recipe_listbox.config(state="disabled")

