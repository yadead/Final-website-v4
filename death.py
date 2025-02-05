import sqlite3

# Connect to the database
conn = sqlite3.connect("databaseFiles\database.db")
cursor = conn.cursor()

# Execute the DROP TABLE command
cursor.execute("DROP TABLE IF EXISTS user_table")
cursor.execute("DROP TABLE IF EXISTS diary_entry")
# Commit changes and close the connection
conn.commit()
conn.close()

print("Table 'diary_entry' deleted (if it existed).")