"""
EduPath AI - Authentication Module (src/auth.py)
Supports:
- Username / Password authentication
- Email-based login
- Google Account configuration / single sign-on
- Forgot Password & secure password reset
- Passwords securely hashed with bcrypt
"""
import os
import sqlite3
from datetime import datetime, timezone
import bcrypt

from src import config

DB_PATH = os.path.join(config.BASE_DIR, "careercompass.db")


def init_users_table():
    """Creates or updates the users table with email and auth_provider columns."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            email TEXT,
            auth_provider TEXT DEFAULT 'local',
            created_at TEXT
        )
    """)
    # Automatic schema migration for existing databases
    cur.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cur.fetchall()]
    if "email" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "auth_provider" not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'local'")
    conn.commit()
    conn.close()


def create_user(username: str, password: str, email: str = "") -> tuple[bool, str]:
    """Creates a new user with optional email. Returns (success, message)."""
    username = username.strip()
    email = email.strip().lower()

    if not username:
        return False, "Username cannot be empty."
    if not password:
        return False, "Password cannot be empty."

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check username uniqueness
    cur.execute("SELECT username FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    if cur.fetchone() is not None:
        conn.close()
        return False, "Username is already taken. Please choose another."

    # Check email uniqueness if email provided
    if email:
        cur.execute("SELECT username FROM users WHERE LOWER(email) = LOWER(?)", (email,))
        if cur.fetchone() is not None:
            conn.close()
            return False, "An account with this email address already exists."

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cur.execute(
        "INSERT INTO users (username, password_hash, email, auth_provider, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, email if email else None, "local", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return True, "Account created successfully! Please sign in."


def verify_user(identifier: str, password: str) -> bool:
    """Verifies credentials by either username or email address."""
    identifier = identifier.strip()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT password_hash FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (identifier, identifier),
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), row[0].encode("utf-8"))


def get_actual_username(identifier: str) -> str:
    """Resolves email or username identifier to the official username stored in the database."""
    identifier = identifier.strip()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT username FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (identifier, identifier),
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else identifier


def reset_password(identifier: str, new_password: str) -> tuple[bool, str]:
    """Resets password for an existing account matching username or email."""
    identifier = identifier.strip()
    if not identifier:
        return False, "Please enter your username or registered email."
    if not new_password or len(new_password) < 4:
        return False, "New password must be at least 4 characters long."

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT username FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (identifier, identifier),
    )
    row = cur.fetchone()
    if row is None:
        conn.close()
        return False, "No registered account found with that username or email."

    username = row[0]
    password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cur.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
    conn.commit()
    conn.close()
    return True, f"Password successfully reset for account '{username}'. You can now sign in."


def login_or_create_google_user(email: str, display_name: str = "") -> tuple[bool, str]:
    """Authenticates or auto-registers a user via Google Account email."""
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Please enter a valid Google email address."

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    row = cur.fetchone()

    if row is not None:
        username = row[0]
        conn.close()
        return True, username

    # Create new account derived from Google profile
    clean_name = display_name.strip().replace(" ", "_").lower() if display_name.strip() else email.split("@")[0]
    base_username = "".join(c for c in clean_name if c.isalnum() or c == "_") or "student"
    username = base_username
    counter = 1

    while True:
        cur.execute("SELECT username FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        if cur.fetchone() is None:
            break
        username = f"{base_username}_{counter}"
        counter += 1

    dummy_secret = os.urandom(24).hex()
    password_hash = bcrypt.hashpw(dummy_secret.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cur.execute(
        "INSERT INTO users (username, password_hash, email, auth_provider, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, email, "google", datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return True, username


if __name__ == "__main__":
    init_users_table()
    print("Users table ready.")