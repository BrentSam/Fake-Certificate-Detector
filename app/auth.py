import os
import sqlite3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id: int, username: str, email: str, password_hash: str, created_at: str):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    def get_id(self) -> str:
        return str(self.id)


def get_db_connection(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def create_user(db_path: str, username: str, email: str, password: str) -> User | None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Check if duplicate exists
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        return None
        
    pw_hash = generate_password_hash(password)
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, pw_hash, created_at)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row['id'], row['username'], row['email'], row['password_hash'], row['created_at'])
    except sqlite3.IntegrityError:
        pass
        
    conn.close()
    return None


def authenticate_user(db_path: str, username_or_email: str, password: str) -> User | None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
    row = cursor.fetchone()
    conn.close()
    if row and check_password_hash(row['password_hash'], password):
        return User(row['id'], row['username'], row['email'], row['password_hash'], row['created_at'])
    return None


def get_user_by_id(db_path: str, user_id: int | str) -> User | None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (int(user_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(row['id'], row['username'], row['email'], row['password_hash'], row['created_at'])
    return None
