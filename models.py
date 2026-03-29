import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'notes.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()

def create_user(username, password):
    hashed = generate_password_hash(password)
    with get_db() as conn:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
        conn.commit()

def get_user_by_username(username):
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return user

def get_user_by_id(user_id):
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return user

def add_note(user_id, text):
    with get_db() as conn:
        conn.execute('INSERT INTO notes (user_id, text) VALUES (?, ?)', (user_id, text))
        conn.commit()

def get_notes_by_user(user_id):
    with get_db() as conn:
        notes = conn.execute('SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    return notes

def get_note_by_id(note_id):
    with get_db() as conn:
        note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    return note

def update_note(note_id, new_text):
    with get_db() as conn:
        conn.execute('UPDATE notes SET text = ? WHERE id = ?', (new_text, note_id))
        conn.commit()

def delete_note(note_id, user_id):
    with get_db() as conn:
        conn.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
        conn.commit()
        return conn.total_changes > 0