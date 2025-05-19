import sqlite3

def initialize_database():
    conn = sqlite3.connect("fridge.db")  # Tworzy plik jeśli nie istnieje
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()