import sqlite3 as sql
import bcrypt
import os

database_name = "databaseFiles/database.db"
table_nameu = "user_table"
print("Database path:", os.path.abspath(database_name))

# Create a table if it doesn't exist yet
def initialize_db():
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_nameu} (
            username TEXT,
            password TEXT
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

initialize_db()

def signup(username, password):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"INSERT INTO {table_nameu} (username, password) VALUES (?, ?)"
    cursor.execute(query, (username, password))
    connection.commit()
    cursor.close()
    connection.close()

def signin(username, password):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"SELECT * FROM {table_nameu} WHERE username = ? AND password = ?;"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    return result is not None