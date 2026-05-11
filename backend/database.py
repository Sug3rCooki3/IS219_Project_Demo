import sqlite3
from datetime import datetime, timezone


DB_PATH = "../data/app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                base_prompt TEXT NOT NULL,
                token_usage INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS variations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES sessions(id),
                label TEXT NOT NULL CHECK(label IN ('A', 'B', 'C', 'D')),
                technique TEXT NOT NULL,
                variation_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                response_cached INTEGER NOT NULL DEFAULT 0,
                manual_score INTEGER CHECK(manual_score BETWEEN 1 AND 5),
                auto_clarity INTEGER CHECK(auto_clarity BETWEEN 1 AND 5),
                auto_relevance INTEGER CHECK(auto_relevance BETWEEN 1 AND 5),
                auto_completeness INTEGER CHECK(auto_completeness BETWEEN 1 AND 5)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_session(session_data: dict) -> int:
    conn = get_connection()
    try:
        created_at = _utc_timestamp()
        try:
            cursor = conn.execute(
                "INSERT INTO sessions (created_at, base_prompt, token_usage) VALUES (?, ?, ?) RETURNING id",
                (created_at, session_data["base_prompt"], session_data.get("token_usage")),
            )
            session_id = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            cursor = conn.execute(
                "INSERT INTO sessions (created_at, base_prompt, token_usage) VALUES (?, ?, ?)",
                (created_at, session_data["base_prompt"], session_data.get("token_usage")),
            )
            session_id = cursor.lastrowid

        for variation in session_data["variations"]:
            conn.execute(
                """
                INSERT INTO variations (
                    session_id,
                    label,
                    technique,
                    variation_text,
                    response_text,
                    response_cached,
                    manual_score,
                    auto_clarity,
                    auto_relevance,
                    auto_completeness
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    variation["label"],
                    variation["technique"],
                    variation["variation_text"],
                    variation["response_text"],
                    int(bool(variation.get("response_cached", False))),
                    variation.get("manual_score"),
                    variation.get("auto_clarity"),
                    variation.get("auto_relevance"),
                    variation.get("auto_completeness"),
                ),
            )

        conn.commit()
        return session_id
    finally:
        conn.close()


def get_all_sessions() -> list[dict]:
    conn = get_connection()
    try:
        session_rows = conn.execute(
            "SELECT id, created_at, base_prompt, token_usage FROM sessions ORDER BY id DESC"
        ).fetchall()

        sessions = []
        for row in session_rows:
            variation_rows = conn.execute(
                """
                SELECT label, technique, variation_text, response_text, response_cached,
                       manual_score, auto_clarity, auto_relevance, auto_completeness
                FROM variations
                WHERE session_id = ?
                ORDER BY label ASC
                """,
                (row["id"],),
            ).fetchall()
            sessions.append(
                {
                    "id": row["id"],
                    "created_at": row["created_at"],
                    "base_prompt": row["base_prompt"],
                    "token_usage": row["token_usage"],
                    "variations": [
                        {
                            "label": variation["label"],
                            "technique": variation["technique"],
                            "variation_text": variation["variation_text"],
                            "response_text": variation["response_text"],
                            "response_cached": bool(variation["response_cached"]),
                            "manual_score": variation["manual_score"],
                            "auto_clarity": variation["auto_clarity"],
                            "auto_relevance": variation["auto_relevance"],
                            "auto_completeness": variation["auto_completeness"],
                        }
                        for variation in variation_rows
                    ],
                }
            )
        return sessions
    finally:
        conn.close()
