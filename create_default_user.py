import sqlite3

import bcrypt

username = "admin"

password = "123456"

hashed = bcrypt.hashpw(

    password.encode("utf-8"),

    bcrypt.gensalt()

).decode("utf-8")

conn = sqlite3.connect("users.db")

cursor = conn.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE,

    password TEXT

)

""")

try:

    cursor.execute(

        "INSERT INTO users (username, password) VALUES (?, ?)",

        (username, hashed)

    )

    conn.commit()

    print("Default user created")

except:

    print("User already exists")

conn.close()