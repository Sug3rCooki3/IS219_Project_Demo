# Data Schema

SQLite database at `/data/app.db`. Tables are created automatically by `database.init_db()` on app startup.

---

## Table: `sessions`

Represents one prompt run (user submits one base prompt = one session).

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,  -- ISO 8601 UTC, e.g. "2026-04-27T14:32:00Z"
                                   -- Python: from datetime import datetime, timezone
                                   --         datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    base_prompt TEXT    NOT NULL,
    token_usage INTEGER             -- populated in Phase 0 via /save-results; displayed in UI in Phase 1
);
```

---

## Table: `variations`

One row per variation per session (4 rows per session).

```sql
CREATE TABLE IF NOT EXISTS variations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL REFERENCES sessions(id),
    label           TEXT    NOT NULL CHECK(label IN ('A', 'B', 'C', 'D')),
    technique       TEXT    NOT NULL,  -- e.g. "role-based"
    variation_text  TEXT    NOT NULL,  -- the full prompt text sent to the LLM
    response_text   TEXT    NOT NULL,  -- the LLM's response
    response_cached INTEGER NOT NULL DEFAULT 0,  -- 1 if served from cache (Phase 1)
    manual_score    INTEGER             CHECK(manual_score BETWEEN 1 AND 5),  -- NULL until user rates
    auto_clarity    INTEGER             CHECK(auto_clarity BETWEEN 1 AND 5),  -- NULL in Phase 0
    auto_relevance  INTEGER             CHECK(auto_relevance BETWEEN 1 AND 5),
    auto_completeness INTEGER           CHECK(auto_completeness BETWEEN 1 AND 5)
);
```

---

## Table: `prompt_cache` (Phase 1 only)

Stores past LLM responses keyed by a hash of the exact variation text. Prevents duplicate API calls.

```sql
CREATE TABLE IF NOT EXISTS prompt_cache (
    prompt_hash     TEXT NOT NULL,
    variation_label TEXT NOT NULL CHECK(variation_label IN ('A', 'B', 'C', 'D')),
    response_text   TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    PRIMARY KEY (prompt_hash, variation_label)
);
```

**Hash method:** SHA-256 of the full `variation_text` string, hex-encoded. Use Python's `hashlib.sha256(text.encode()).hexdigest()`.

---

## Relationships

```
sessions 1 ──< variations (session_id)
prompt_cache is standalone (keyed by hash, not session_id)
```

---

## Notes for the AI Coder

- In Phase 0, create `sessions` and `variations` tables only. Skip `prompt_cache`.
- `auto_clarity`, `auto_relevance`, `auto_completeness` columns must still be created in Phase 0 (as nullable), so Phase 1 doesn't require a schema migration.
- `manual_score` starts as `NULL` if the user hasn't rated yet. When the user rates all 4 variations, the frontend sends scores in the `POST /save-results` payload and they are set during the initial `INSERT` — there is no separate `UPDATE` query.
- Never use an ORM. All queries are raw SQL strings passed to `sqlite3.execute()`.
- **SQLite does not enforce foreign keys by default.** Add `PRAGMA foreign_keys = ON;` inside `get_connection()` immediately after opening each connection, before any query runs.
- Use `RETURNING id` (SQLite 3.35+) when inserting sessions to get the new row's ID back. To check your SQLite version: `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`. If below 3.35, use `cursor.lastrowid` instead.
