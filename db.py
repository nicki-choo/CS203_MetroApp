import sqlite3

conn = sqlite3.connect('users.sqlite')
cursor = conn.cursor()
sql_query = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        "password" TEXT NOT NULL
)
"""

cursor.execute(sql_query)