import sqlite3
from pathlib import Path

conn = sqlite3.connect("database/exercise_log.db")

c = conn.cursor()

def read_sql_query(sql_path: Path) -> str:
    """Read sql library from file"""
    return Path(sql_path).read_text()

raw_sql = read_sql_query("sql/create.sql")

# Create the tables
c.executescript(raw_sql)

# Commit the changes and close the connection
conn.commit()
conn.close()
