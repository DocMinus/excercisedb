import sqlite3

conn = sqlite3.connect("exercise_log.db")

c = conn.cursor()

# Delete an entry for a specific user on a specific date
c.execute(
    """DELETE FROM exercises WHERE user_id=? AND date_last_done=?""",
    (user_id, date_last_done),
)

# Commit the changes and close the connection
conn.commit()
conn.close()
