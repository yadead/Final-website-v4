import sqlite3 as sql
import bcrypt
import os

database_name = "databaseFiles/database.db"
table_nameu = "user_table"
table_name = "diary_entry"
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
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        Developer TEXT,
        Project TEXT,
        Start_Time TEXT,
        End_Time TEXT,
        Diary_Entry TEXT,
        Time_Worked TEXT,
        Repo TEXT,
        Developer_Notes TEXT
    );
    """)
    connection.commit()
    cursor.close()
    connection.close()

initialize_db()

def signup(username, password):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = f"INSERT INTO {table_nameu} (username, password) VALUES (?, ?)"
    cursor.execute(query, (username, hashed_password))
    connection.commit()
    cursor.close()
    connection.close()

def signin(username, password):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"SELECT password FROM {table_nameu} WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return True
    return False

def diary_entry(Developer, Project, Start_Time, End_Time, Diary_Entry, Time_Worked, Repo, Developer_Notes):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"""
        INSERT INTO {table_name} (Developer, Project, Start_Time, End_Time, Diary_Entry, Time_Worked, Repo, Developer_Notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
    cursor.execute(query, (Developer, Project, Start_Time, End_Time, Diary_Entry, Time_Worked, Repo, Developer_Notes))
    connection.commit()
    cursor.close()
    connection.close()

def all_entries():
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"SELECT rowid, * FROM {table_name}"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def search_entries(query):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"%{query}%"
    sql_query = f"""
        SELECT rowid, * FROM {table_name}
        WHERE Developer LIKE ? OR Project LIKE ? OR Start_Time LIKE ? OR End_Time LIKE ? OR Diary_Entry LIKE ? OR Time_Worked LIKE ? OR Repo LIKE ? OR Developer_Notes LIKE ?
    """
    cursor.execute(sql_query, (query, query, query, query, query, query, query, query))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def delete_entry(entry_id, username):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"DELETE FROM {table_name} WHERE rowid = ? AND Developer = ?"
    cursor.execute(query, (entry_id, username))
    connection.commit()
    cursor.close()
    connection.close()

def get_entry(entry_id):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"SELECT rowid, * FROM {table_name} WHERE rowid = ?"
    cursor.execute(query, (entry_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result

def username_exists(username):
    connection = sql.connect(database_name)
    cursor = connection.cursor()
    query = f"SELECT 1 FROM user_table WHERE username = ?"  # Ensure 'users' is the correct table name
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result is not None