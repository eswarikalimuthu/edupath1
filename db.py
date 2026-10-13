"""
Module 4 - SQLite session storage.

Stores each advisory session (student input + profile + recommendation +
pathway + optional schedule) tagged to the logged-in user, so history
persists across visits and stays private per student.
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

from src import config

DB_PATH = os.path.join(config.BASE_DIR, "careercompass.db")


def init_db():
    """Creates the sessions table if it doesn't exist, and migrates older
    databases (from before auth/schedule were added) by adding any missing
    columns instead of requiring a fresh database file."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            username TEXT,
            created_at TEXT,
            student_text TEXT,
            profile TEXT,
            recommendation TEXT,
            pathway TEXT,
            schedule TEXT,
            milestones_json TEXT,
            schedule_json TEXT
        )
    """)

    existing_cols = [row[1] for row in cur.execute("PRAGMA table_info(sessions)").fetchall()]
    if "username" not in existing_cols:
        cur.execute("ALTER TABLE sessions ADD COLUMN username TEXT")
    if "schedule" not in existing_cols:
        cur.execute("ALTER TABLE sessions ADD COLUMN schedule TEXT")
    if "milestones_json" not in existing_cols:
        cur.execute("ALTER TABLE sessions ADD COLUMN milestones_json TEXT")
    if "schedule_json" not in existing_cols:
        cur.execute("ALTER TABLE sessions ADD COLUMN schedule_json TEXT")
    if "scholarships_json" not in existing_cols:
        cur.execute("ALTER TABLE sessions ADD COLUMN scholarships_json TEXT")
    if "practice_json" not in existing_cols:
        cur.execute("ALTER TABLE sessions ADD COLUMN practice_json TEXT")

    # Performance optimization: WAL mode and composite index for quick history loading
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_time ON sessions(username, created_at DESC);")

    conn.commit()
    conn.close()


def save_session(
    username: str,
    student_text: str,
    profile: dict,
    recommendation: str,
    pathway: str,
    milestones_json: str = None,
    scholarships_json: str = None,
    practice_json: str = None,
) -> str:
    """Saves a completed advisory session for a specific user and returns its generated ID."""
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (id, username, created_at, student_text, profile, recommendation, pathway, schedule, milestones_json, schedule_json, scholarships_json, practice_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            session_id,
            username,
            datetime.now(timezone.utc).isoformat(),
            student_text,
            json.dumps(profile),
            recommendation,
            pathway,
            None,
            milestones_json,
            None,
            scholarships_json,
            practice_json,
        ),
    )
    conn.commit()
    conn.close()
    return session_id


def update_session_schedule(session_id: str, schedule: str):
    """Attaches a generated schedule to an existing session."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE sessions SET schedule = ? WHERE id = ?", (schedule, session_id))
    conn.commit()
    conn.close()


def update_session_milestones(session_id: str, milestones_json: str):
    """Updates the milestones progress JSON for a session."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE sessions SET milestones_json = ? WHERE id = ?", (milestones_json, session_id))
    conn.commit()
    conn.close()


def update_session_schedule_json(session_id: str, schedule_json: str):
    """Updates the schedule progress JSON for a session."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE sessions SET schedule_json = ? WHERE id = ?", (schedule_json, session_id))
    conn.commit()
    conn.close()


def get_all_sessions(username: str) -> list[dict]:
    """Returns a lightweight list of a specific user's past sessions for the sidebar history list."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, created_at, student_text FROM sessions WHERE username = ? ORDER BY created_at DESC",
        (username,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_session(session_id: str) -> dict | None:
    """Returns the full saved session (profile parsed back into a dict) for a given ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    result = dict(row)
    result["profile"] = json.loads(result["profile"]) if result.get("profile") else {}
    if result.get("scholarships_json"):
        try:
            result["scholarships"] = json.loads(result["scholarships_json"])
        except Exception:
            result["scholarships"] = []
    else:
        result["scholarships"] = []

    if result.get("practice_json"):
        try:
            result["practice_plan"] = json.loads(result["practice_json"])
        except Exception:
            result["practice_plan"] = {}
    else:
        result["practice_plan"] = {}

    return result


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")