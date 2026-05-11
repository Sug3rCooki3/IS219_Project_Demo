# Tech Stack

All choices below are final. Do not substitute alternatives unless a package is unavailable.

---

## Backend

| Concern | Choice | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Web framework | FastAPI | latest |
| ASGI server | Uvicorn | latest |
| OpenAI client | `openai` Python SDK | latest (v1.x) |
| Database driver | `sqlite3` | stdlib (no install needed) |
| Env vars | `python-dotenv` | latest |
| Testing | `pytest` | latest |
| Async test support | `pytest-asyncio` | latest |
| HTTP testing | `httpx` | latest (used directly as `httpx.AsyncClient` in tests — do NOT use FastAPI's `TestClient`, which uses `requests`) |

### Install command
```bash
pip install fastapi uvicorn openai python-dotenv httpx pytest pytest-asyncio
```

### `backend/requirements.txt` contents
```
fastapi
uvicorn
openai
python-dotenv
httpx
pytest
pytest-asyncio
```
Create this file manually — do not use `pip freeze` (it adds noise).

### `pytest.ini` (create at project root)
Required so `pytest-asyncio` automatically handles `@pytest.mark.asyncio` without warnings:
```ini
[pytest]
asyncio_mode = auto
```

---

## Frontend

| Concern | Choice | Notes |
|---|---|---|
| Language | JavaScript (not TypeScript) | Keep it simple |
| Framework | React 18 | via Vite scaffold |
| Build tool | Vite | `npm create vite@latest` |
| HTTP client | `fetch` (native) | No axios |
| Styling | Plain CSS (no framework) | One flat CSS file |
| State management | React `useState` / `useEffect` only | No Redux, no Zustand |
| Node.js | 18+ required | Vite 5 will not run on Node < 18 |

### Scaffold command
```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install
```

---

## Database

| Concern | Choice |
|---|---|
| Engine | SQLite |
| File location | `/data/app.db` |
| Access method | Python `sqlite3` stdlib directly (no ORM, no SQLAlchemy) |

---

## Environment Variables

File: `/backend/.env` (never committed)
File: `/backend/.env.example` (committed, shows keys with empty values)

```
OPENAI_API_KEY=
```

---

## Dev Server Ports

| Service | Port | Start command |
|---|---|---|
| Backend (Uvicorn) | `8000` | `cd backend && uvicorn main:app --reload --port 8000` |
| Frontend (Vite) | `5173` | `cd frontend && npm run dev` |

Frontend calls backend at `http://localhost:8000`. Run both servers simultaneously in separate terminals.

---

## Python + SQLite Note for FastAPI
FastAPI is async. Do **not** create a single shared SQLite connection with `check_same_thread=False` — that is a threading pattern and does not apply here. Instead, open a new connection per request and close it when done:

```python
# correct pattern in database.py
import sqlite3

# Path is relative to where uvicorn is launched (backend/).
# Must be run as: cd backend && uvicorn main:app --reload --port 8000
DB_PATH = "../data/app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # required — SQLite disables FK checks by default
    return conn

# in each function that needs the DB — open, use, close explicitly.
# NOTE: `with conn:` only handles commit/rollback, NOT closing.
# Always call conn.close() when done.
def save_session(data):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO sessions ...", ...)
        conn.commit()
    finally:
        conn.close()
```

Never store the connection as a module-level global.
