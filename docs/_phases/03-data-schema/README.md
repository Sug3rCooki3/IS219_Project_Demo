# Phase 03 — Data Schema

> Source spec: [../../_specs/03-data-schema.md](../../_specs/03-data-schema.md)

Use this phase to implement the SQLite schema and DB rules.

SQLite database path is `/data/app.db`. Tables are created automatically by `database.init_db()` on app startup.

## Focus
- `sessions` table
- `variations` table
- `prompt_cache` table (Phase 1)
- Foreign key enforcement
- Insert ID retrieval
- Timestamp format

## Required Tables

### `sessions`

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL,
    base_prompt TEXT    NOT NULL,
    token_usage INTEGER
);
```

- [ ] `token_usage` is populated in Phase 0 via `/save-results` and displayed in the UI in Phase 1

### `variations`

```sql
CREATE TABLE IF NOT EXISTS variations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id        INTEGER NOT NULL REFERENCES sessions(id),
    label             TEXT    NOT NULL CHECK(label IN ('A', 'B', 'C', 'D')),
    technique         TEXT    NOT NULL,
    variation_text    TEXT    NOT NULL,
    response_text     TEXT    NOT NULL,
    response_cached   INTEGER NOT NULL DEFAULT 0,
    manual_score      INTEGER CHECK(manual_score BETWEEN 1 AND 5),
    auto_clarity      INTEGER CHECK(auto_clarity BETWEEN 1 AND 5),
    auto_relevance    INTEGER CHECK(auto_relevance BETWEEN 1 AND 5),
    auto_completeness INTEGER CHECK(auto_completeness BETWEEN 1 AND 5)
);
```

### `prompt_cache` (Phase 1)

```sql
CREATE TABLE IF NOT EXISTS prompt_cache (
    prompt_hash     TEXT NOT NULL,
    variation_label TEXT NOT NULL CHECK(variation_label IN ('A', 'B', 'C', 'D')),
    response_text   TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    PRIMARY KEY (prompt_hash, variation_label)
);
```

## Required Rules
- [ ] In Phase 0, create only `sessions` and `variations`
- [ ] Still create `auto_*` columns in Phase 0 as nullable
- [ ] Do not create `prompt_cache` until Phase 1
- [ ] Never use an ORM
- [ ] Use raw SQL with `sqlite3.execute()`
- [ ] In `get_connection()`, set `conn.row_factory = sqlite3.Row` so query results are accessible as dicts
- [ ] In `get_connection()`, run `PRAGMA foreign_keys = ON`
- [ ] `manual_score` may start as `NULL`; when present, it is inserted from the `/save-results` payload and does not require a separate `UPDATE`
- [ ] `prompt_hash` is the SHA-256 hex digest of the full `variation_text`: `hashlib.sha256(text.encode()).hexdigest()`

## Relationships
- [ ] `sessions` has a one-to-many relationship with `variations` via `session_id`
- [ ] `prompt_cache` is standalone and keyed by hash, not `session_id`

## Insert / Timestamp Rules
- [ ] `created_at` format is ISO 8601 UTC like `2026-04-27T14:32:00Z`
- [ ] Generate timestamps with `datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")`
- [ ] Prefer `RETURNING id` for session inserts on SQLite 3.35+
- [ ] Fall back to `cursor.lastrowid` on older SQLite versions

## Tests for this Phase

Create these files now. They can only be run after Phase 04 routers (`/save-results`, `/history`) are also implemented.

**Run command:**
```bash
pytest tests/test_results.py tests/test_history.py -v
```

### `tests/test_results.py`
```python
import pytest

SAMPLE_SESSION = {
    "base_prompt": "What is the chain rule?",
    "token_usage": 168,
    "variations": [
        {
            "label": "A", "technique": "role-based",
            "variation_text": "You are an expert mathematics tutor. What is the chain rule?",
            "response_text": "The chain rule states that...",
            "response_cached": False,
            "manual_score": 4,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
        {
            "label": "B", "technique": "few-shot",
            "variation_text": "Q: ...\nA:", "response_text": "...",
            "response_cached": False, "manual_score": 3,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
        {
            "label": "C", "technique": "instruction-rewording",
            "variation_text": "...", "response_text": "...",
            "response_cached": False, "manual_score": None,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
        {
            "label": "D", "technique": "output-formatting",
            "variation_text": "...", "response_text": "...",
            "response_cached": False, "manual_score": 5,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
    ],
}

@pytest.mark.asyncio
async def test_save_returns_201_and_session_id(client):
    res = await client.post("/save-results", json=SAMPLE_SESSION)
    assert res.status_code == 201
    assert "session_id" in res.json()
    assert isinstance(res.json()["session_id"], int)

@pytest.mark.asyncio
async def test_save_persists_to_database(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    history_res = await client.get("/history")
    assert len(history_res.json()["sessions"]) == 1

@pytest.mark.asyncio
async def test_manual_score_null_is_accepted(client):
    res = await client.post("/save-results", json=SAMPLE_SESSION)
    assert res.status_code == 201

@pytest.mark.asyncio
async def test_wrong_number_of_variations_returns_400(client):
    bad_session = {**SAMPLE_SESSION, "variations": SAMPLE_SESSION["variations"][:2]}
    res = await client.post("/save-results", json=bad_session)
    assert res.status_code == 400
    assert "4" in res.json()["detail"]

@pytest.mark.asyncio
async def test_session_ids_are_unique(client):
    res1 = await client.post("/save-results", json=SAMPLE_SESSION)
    res2 = await client.post("/save-results", json=SAMPLE_SESSION)
    assert res1.json()["session_id"] != res2.json()["session_id"]
```

### `tests/test_history.py`
```python
import pytest
from test_results import SAMPLE_SESSION

@pytest.mark.asyncio
async def test_empty_history_returns_empty_list(client):
    res = await client.get("/history")
    assert res.status_code == 200
    assert res.json() == {"sessions": []}

@pytest.mark.asyncio
async def test_history_returns_saved_session(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    res = await client.get("/history")
    sessions = res.json()["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["base_prompt"] == "What is the chain rule?"

@pytest.mark.asyncio
async def test_history_returns_newest_first(client):
    session_a = {**SAMPLE_SESSION, "base_prompt": "First prompt"}
    session_b = {**SAMPLE_SESSION, "base_prompt": "Second prompt"}
    await client.post("/save-results", json=session_a)
    await client.post("/save-results", json=session_b)
    res = await client.get("/history")
    sessions = res.json()["sessions"]
    assert sessions[0]["base_prompt"] == "Second prompt"
    assert sessions[1]["base_prompt"] == "First prompt"

@pytest.mark.asyncio
async def test_history_session_includes_variations(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    res = await client.get("/history")
    session = res.json()["sessions"][0]
    assert "variations" in session
    assert len(session["variations"]) == 4

@pytest.mark.asyncio
async def test_history_session_includes_token_usage(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    res = await client.get("/history")
    session = res.json()["sessions"][0]
    assert session["token_usage"] == 168
```

The source spec is authoritative.
