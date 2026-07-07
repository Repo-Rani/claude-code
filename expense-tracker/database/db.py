import os
import sqlite3
from werkzeug.security import generate_password_hash

def get_db():
    """Return a SQLite connection with row_factory and foreign keys enabled."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(base_dir, 'spendly.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """Create tables if they do not exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    conn.commit()
    conn.close()

def seed_db():
    """Insert demo data if the database is empty (idempotent)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] > 0:
        conn.close()
        return

    password_hash = generate_password_hash('demo123')
    cur.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', password_hash)
    )
    user_id = cur.lastrowid

    sample_expenses = [
        (user_id, 23.45, 'Food', '2026-07-01', 'Lunch at cafe'),
        (user_id, 15.00, 'Transport', '2026-07-02', 'Bus ticket'),
        (user_id, 75.99, 'Bills', '2026-07-03', 'Internet bill'),
        (user_id, 12.50, 'Health', '2026-07-04', 'Pharmacy'),
        (user_id, 45.00, 'Entertainment', '2026-07-05', 'Movie night'),
        (user_id, 120.00, 'Shopping', '2026-07-06', 'Clothes'),
        (user_id, 9.99, 'Other', '2026-07-07', 'Coffee beans'),
        (user_id, 30.00, 'Food', '2026-07-08', 'Groceries')
    ]

    cur.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        sample_expenses
    )
    conn.commit()
    conn.close()
