import sqlite3
import os

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

# Connect to foods.db
conn = sqlite3.connect("data/foods.db")
c = conn.cursor()

# Table for dishes
c.execute("""
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    name TEXT NOT NULL,
    ingredients TEXT,
    notes TEXT
)
""")

# Table for translations of common allergy phrases
c.execute("""
CREATE TABLE IF NOT EXISTS translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language TEXT NOT NULL,
    phrase_en TEXT NOT NULL,
    phrase_translated TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print(" foods.db initialized successfully!")
