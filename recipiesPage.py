import tkinter as tk
from PIL import Image, ImageTk
from recipe_db import initialize_recipe_database
import sqlite3
from tkinter import messagebox

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

        
        self.show_button = tk.Button(self.canvas, text="Wyświetl\ndostępne przepisy", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.show_available_recipes)
        self.add_button = tk.Button(self.canvas, text="Dodaj przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.add_recipe)
        self.remove_button = tk.Button(self.canvas, text="Usuń przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.remove_recipe)
        self.edit_button = tk.Button(self.canvas, text="Edytuj przepis", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.edit_recipe)
        self.refresh_button = tk.Button(self.canvas, text="Odśwież\nprzepisy", font=("Arial", 14), bg="#333", fg="white", relief="flat", command=self.refresh_recipe_list)
        self.home_button = tk.Button(self.canvas, text="Homepage", font=("Arial", 14), bg="#555", fg="white", relief="flat", command=self.go_to_home_callback)
        self.fridge_button = tk.Button(self.canvas, text="Fridge", font=("Arial", 14), bg="#555", fg="white", relief="flat", command=self.go_to_fridge_callback)
        

        
        self.listbox_window = self.canvas.create_window(0, 0, window=self.recipe_listbox, anchor="nw")
        self.buttons = [
            self.show_button,
            self.add_button,
            self.remove_button,
            self.edit_button,
            self.refresh_button,
            self.fridge_button,
            self.home_button
  
        ]
        for btn in self.buttons:
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#555"))  
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#333" if b in self.buttons[:5] else "#444"))  
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


    def show_available_recipes(self):
        self.recipe_listbox.config(state="normal")
        self.recipe_listbox.delete(0, tk.END)

        conn_fridge = sqlite3.connect("fridge.db")
        c_fridge = conn_fridge.cursor()
        c_fridge.execute("SELECT name, amount, unit FROM ingredients")
        fridge_ingredients = c_fridge.fetchall()
        conn_fridge.close()

        fridge_dict = {(name.lower(), unit): amount for name, amount, unit in fridge_ingredients}

        conn = sqlite3.connect("recipes.db")
        c = conn.cursor()
        c.execute("SELECT id, name FROM recipes ORDER BY name")
        recipes = c.fetchall()

        for recipe_id, recipe_name in recipes:
            c.execute("SELECT ingredient_name, amount, unit FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
            ingredients = c.fetchall()

            can_make = True
            for ing_name, ing_amount, ing_unit in ingredients:
                key = (ing_name.lower(), ing_unit)
                if key not in fridge_dict or fridge_dict[key] < ing_amount:
                    can_make = False
                    break

            if can_make:
                self.recipe_listbox.insert(tk.END, recipe_name)

        conn.close()
        
        if self.recipe_listbox.size() == 0:
            self.recipe_listbox.insert(tk.END, "Brak dostępnych przepisów.")
        self.recipe_listbox.config(state="disabled")


    def add_recipe(self):
        top = tk.Toplevel(self.master)
        top.title("Dodaj przepis")

        tk.Label(top, text="Nazwa przepisu:").pack()
        name_entry = tk.Entry(top)
        name_entry.pack()

        ingredient_frame = tk.Frame(top)
        ingredient_frame.pack(pady=10)

        ingredient_list = []

        def add_ingredient_popup():
            popup = tk.Toplevel(top)
            popup.title("Dodaj składnik")

            tk.Label(popup, text="Nazwa:").pack()
            name_field = tk.Entry(popup)
            name_field.pack()

            tk.Label(popup, text="Ilość:").pack()
            amount_field = tk.Entry(popup)
            amount_field.pack()

            tk.Label(popup, text="Jednostka:").pack()
            unit_var = tk.StringVar(popup)
            unit_var.set("g")
            unit_menu = tk.OptionMenu(popup, unit_var, "szt.", "ml", "g", "kg", "l", "opak.")
            unit_menu.pack()

            def confirm_ingredient():
                name = name_field.get().strip()
                try:
                    amount = float(amount_field.get())
                except ValueError:
                    return
                unit = unit_var.get()
                if name:
                    ingredient_list.append((name, amount, unit))
                    ingredient_label = tk.Label(ingredient_frame, text=f"{name} - {amount} {unit}")
                    ingredient_label.pack(anchor="w")
                popup.destroy()

            tk.Button(popup, text="Dodaj", command=confirm_ingredient).pack(pady=5)

        tk.Button(top, text="Dodaj składnik", command=add_ingredient_popup).pack()

        tk.Label(top, text="Sposób przygotowania:").pack()
        instructions_text = tk.Text(top, height=5)
        instructions_text.pack()

        tk.Label(top, text="Ścieżka do zdjęcia:").pack()
        image_entry = tk.Entry(top)
        image_entry.pack()

        def browse_image():
            from tkinter import filedialog
            path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg *.png *.jpeg")])
            if path:
                image_entry.delete(0, tk.END)
                image_entry.insert(0, path)

        tk.Button(top, text="Przeglądaj...", command=browse_image).pack()

        def confirm_add():
            name = name_entry.get().strip()
            instructions = instructions_text.get("1.0", tk.END).strip()
            image_path = image_entry.get().strip()

            if not name or not ingredient_list:
                return

            conn = sqlite3.connect("recipes.db")
            c = conn.cursor()
            c.execute("INSERT INTO recipes (name, instructions, image_path) VALUES (?, ?, ?)", (name, instructions, image_path))
            recipe_id = c.lastrowid

            for ing_name, ing_amount, ing_unit in ingredient_list:
                c.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_name, amount, unit) VALUES (?, ?, ?, ?)",
                          (recipe_id, ing_name, ing_amount, ing_unit))

            conn.commit()
            conn.close()
            top.destroy()
            self.refresh_recipe_list()

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
        def open_editor_for(recipe_name):
            conn = sqlite3.connect("recipes.db")
            c = conn.cursor()
            c.execute("SELECT id, instructions, image_path FROM recipes WHERE name=?", (recipe_name,))
            result = c.fetchone()
            if not result:
                conn.close()
                return

            recipe_id, instructions, image_path = result
            c.execute("SELECT ingredient_name, amount, unit FROM recipe_ingredients WHERE recipe_id=?", (recipe_id,))
            ingredients = c.fetchall()
            conn.close()

            top = tk.Toplevel(self.master)
            top.title("Edytuj przepis")

            tk.Label(top, text="Nazwa przepisu:").pack()
            name_entry = tk.Entry(top)
            name_entry.insert(0, recipe_name)
            name_entry.pack()

            ingredient_frame = tk.Frame(top)
            ingredient_frame.pack(pady=10)

            ingredient_list = list(ingredients)

            def refresh_ingredient_display():
                for widget in ingredient_frame.winfo_children():
                    widget.destroy()
                for name, amount, unit in ingredient_list:
                    tk.Label(ingredient_frame, text=f"{name} - {amount} {unit}").pack(anchor="w")

            def add_ingredient_popup():
                popup = tk.Toplevel(top)
                popup.title("Dodaj składnik")

                tk.Label(popup, text="Nazwa:").pack()
                name_field = tk.Entry(popup)
                name_field.pack()

                tk.Label(popup, text="Ilość:").pack()
                amount_field = tk.Entry(popup)
                amount_field.pack()

                tk.Label(popup, text="Jednostka:").pack()
                unit_var = tk.StringVar(popup)
                unit_var.set("g")
                unit_menu = tk.OptionMenu(popup, unit_var, "szt.", "ml", "g", "kg", "l", "opak.")
                unit_menu.pack()

                def confirm_ingredient():
                    name = name_field.get().strip()
                    try:
                        amount = float(amount_field.get().replace(",", "."))
                    except ValueError:
                        messagebox.showwarning("Błąd", "Podaj poprawną liczbę jako ilość.")
                        return
                    unit = unit_var.get()
                    if name:
                        ingredient_list.append((name, amount, unit))
                        refresh_ingredient_display()
                    popup.destroy()

                tk.Button(popup, text="Dodaj", command=confirm_ingredient).pack(pady=5)

            tk.Button(top, text="Dodaj składnik", command=add_ingredient_popup).pack()
            refresh_ingredient_display()

            tk.Label(top, text="Sposób przygotowania:").pack()
            instructions_text = tk.Text(top, height=5)
            instructions_text.insert("1.0", instructions)
            instructions_text.pack()

            tk.Label(top, text="Ścieżka do zdjęcia:").pack()
            image_entry = tk.Entry(top)
            image_entry.insert(0, image_path)
            image_entry.pack()

            def browse_image():
                from tkinter import filedialog
                path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg *.png *.jpeg")])
                if path:
                    image_entry.delete(0, tk.END)
                    image_entry.insert(0, path)

            tk.Button(top, text="Przeglądaj...", command=browse_image).pack()

            def confirm_edit():
                new_name = name_entry.get().strip()
                new_instructions = instructions_text.get("1.0", tk.END).strip()
                new_image_path = image_entry.get().strip()

                if not new_name or not ingredient_list:
                    messagebox.showwarning("Błąd", "Wprowadź nazwę przepisu i przynajmniej jeden składnik.")
                    return

                conn = sqlite3.connect("recipes.db")
                c = conn.cursor()

                c.execute("UPDATE recipes SET name=?, instructions=?, image_path=? WHERE id=?",
                        (new_name, new_instructions, new_image_path, recipe_id))

                c.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?", (recipe_id,))
                for ing_name, ing_amount, ing_unit in ingredient_list:
                    c.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_name, amount, unit) VALUES (?, ?, ?, ?)",
                            (recipe_id, ing_name, ing_amount, ing_unit))

                conn.commit()
                conn.close()
                top.destroy()
                self.refresh_recipe_list()

            tk.Button(top, text="Zapisz zmiany", command=confirm_edit).pack(pady=5)

        choose_window = tk.Toplevel(self.master)
        choose_window.title("Wybierz przepis do edycji")

        tk.Label(choose_window, text="Wybierz przepis do edycji:").pack(pady=5)

        recipe_listbox = tk.Listbox(choose_window, height=10, width=40)
        recipe_listbox.pack(padx=10, pady=5)

        conn = sqlite3.connect("recipes.db")
        c = conn.cursor()
        c.execute("SELECT name FROM recipes ORDER BY name")
        recipes = [row[0] for row in c.fetchall()]
        conn.close()

        for recipe in recipes:
            recipe_listbox.insert(tk.END, recipe)

        def confirm_selection():
            selection = recipe_listbox.curselection()
            if not selection:
                messagebox.showinfo("Brak wyboru", "Wybierz przepis z listy.")
                return
            recipe_name = recipe_listbox.get(selection[0])
            choose_window.destroy()
            open_editor_for(recipe_name)

        tk.Button(choose_window, text="Dalej", command=confirm_selection).pack(pady=5)



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

