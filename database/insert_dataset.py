import sqlite3
import os

# paths to database and SQL file
db_path = os.path.join("database", "data_source.db")
sql_path = os.path.join("database", "dataset99.sql")

print("Opening database...")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Reading SQL file...")
with open(sql_path, "r") as f:
    sql_script = f.read()

print("Executing SQL commands...")
cur.executescript(sql_script)

conn.commit()
print("All 99 rows inserted successfully!")

# verify first 5 rows
print("First 5 rows in userinformation2:")
cur.execute("SELECT * FROM userinformation2 LIMIT 5;")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.close()
print("Database connection closed.")
