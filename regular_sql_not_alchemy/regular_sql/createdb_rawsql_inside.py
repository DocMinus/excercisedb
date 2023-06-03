import sqlite3

conn = sqlite3.connect("database/exercise_log.db")

c = conn.cursor()

# table structures
sql_raw_users = """
CREATE TABLE users (
   id INTEGER PRIMARY KEY,
   username TEXT NOT NULL,
   password TEXT
)
"""

sql_raw_excercises =  """
CREATE TABLE exercises (
   id INTEGER PRIMARY KEY,
   user_id INTEGER NOT NULL,
   exercise_type TEXT NOT NULL,
   date_last_done DATE,
   number_of_reps INTEGER,
   highest_weight INTEGER,
   notes TEXT,
   FOREIGN KEY (user_id) REFERENCES users(id)
)
"""

# Create the tables
c.execute(sql_raw_users)
c.execute(sql_raw_excercises)

# Commit the changes and close the connection
conn.commit()
conn.close()
