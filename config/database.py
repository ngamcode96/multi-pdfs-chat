import sqlite3
from datetime import datetime

def connect_db():
    return sqlite3.connect('chats.db')



#if table doesn't exist:
# Create a cursor object to interact with the database

def init_database():   
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY,
            title TEXT,
            number_docs_uploaded INTEGER DEFAULT 0,
            created_at TIMESTAMP
        )
    ''')

    db.commit()
    db.close()


def get_all_chats():
    conn = connect_db()
    cursor = conn.cursor()

    rows = []

    try:
        cursor.execute('SELECT * FROM chats ORDER BY created_at DESC')
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(e)
        return []
    finally:
        conn.close()
    return rows

def get_chat_by_id(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row




def get_last_chat():
    conn = connect_db()
    cursor = conn.cursor()
    row = None
    try:
        cursor.execute('SELECT * FROM chats WHERE number_docs_uploaded = 0 ORDER BY created_at DESC LIMIT 1')
        rows = cursor.fetchall()
        if len(rows) > 0:
            row = rows[0]

    except sqlite3.Error as e:
        print(e)
        return None
    finally:
        conn.close()
    return row


def new_chat():
    conn = connect_db()
    cursor = conn.cursor()

    current_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO chats (title, created_at) VALUES (?, ?)', ('New chat', current_timestamp))
    conn.commit()
    last_inserted_id = cursor.lastrowid
    conn.close()

    chat = get_chat_by_id(last_inserted_id)
    return chat


def update_column_value(column_name, column_value, chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = f"UPDATE chats SET {column_name} = '{column_value}' WHERE id = {chat_id}"
    cursor.execute(query)
    conn.commit()
    cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
    updated_row = cursor.fetchone()
    conn.close()

    return updated_row



def delete_chat(chat_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
        conn.commit()
        print(f"Chat with ID {chat_id} deleted successfully.")
    except sqlite3.Error as e:
        print("SQLite error:", e)
        conn.rollback() 
    finally:
        conn.close()


