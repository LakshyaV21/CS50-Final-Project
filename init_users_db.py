import sqlite3
import os

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

# Connect to users.db in the data folder
conn = sqlite3.connect("data/users.db")
c = conn.cursor()

# Create the users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    allergens TEXT
)
""")

conn.commit()
conn.close()

print("users.db initialized successfully!")
