import sqlite3

conn = sqlite3.connect("exercise_log.db")

c = conn.cursor()

# Update an entry for a specific user on a specific date
c.execute(
    """UPDATE exercises SET exercise_type=?, number_of_reps=?, highest_weight=?, notes=?
             WHERE user_id=? AND date_last_done=?""",
    (
        new_exercise_type,
        new_number_of_reps,
        new_highest_weight,
        new_notes,
        user_id,
        date_last_done,
    ),
)

# Commit the changes and close the connection
conn.commit()
conn.close()
