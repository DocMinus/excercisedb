import sqlite3

conn = sqlite3.connect("exercise_log.db")

c = conn.cursor()

c.execute("INSERT INTO users (username) VALUES (?)", ("Alexander",))
user_id = c.lastrowid

c.execute(
    "INSERT INTO exercises (user_id, exercise_type, date_last_done, number_of_reps, highest_weight, notes) VALUES (?, ?, ?, ?, ?, ?)",
    (user_id, "bench", "2023-05-01", 5, 100, "Felt good today"),
)
c.execute(
    "INSERT INTO exercises (user_id, exercise_type, date_last_done, number_of_reps, highest_weight, notes) VALUES (?, ?, ?, ?, ?, ?)",
    (user_id, "squat", "2023-05-02", 3, 150, None),
)

conn.commit()
conn.close()


import sqlite3

conn = sqlite3.connect("exercise_log.db")

c = conn.cursor()

# Check if the username already exists
c.execute("""SELECT * FROM users WHERE username=?""", (username,))
user_exists = c.fetchone()

if user_exists:
    print("Username already exists!")
else:
    # Insert the new user into the users table
    c.execute("""INSERT INTO users (username) VALUES (?)""", (username,))
    user_id = c.lastrowid
    print("New user created with ID:", user_id)

# Commit the changes and close the connection
conn.commit()
conn.close()
