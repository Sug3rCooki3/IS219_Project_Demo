# Phase 01 — Tech Stack

> Source spec: [../../_specs/01-tech-stack.md](../../_specs/01-tech-stack.md)

Use this phase to lock the implementation stack before coding.
Do not substitute alternatives unless a package is unavailable.
Phase 00 scope is still in force while using this stack: build only the Phase 0 endpoints, components, and tables until Phase 0 tests pass.

## Focus
- Backend dependencies and versions
- Frontend scaffold and Node requirement
- `backend/requirements.txt`
- `pytest.ini`
- Dev server ports and startup commands
- FastAPI + SQLite connection pattern

## Phase 00 Alignment
- [ ] Use this stack for Phase 0 only: `POST /generate-variations`, `POST /get-responses`, `POST /save-results`, `GET /history`
- [ ] Do not use this phase to justify building `POST /auto-score` or `GET /export-best` yet
- [ ] Keep `token_usage` collection/storage in Phase 0, but do not display it in the UI until Phase 1
- [ ] Phase 0 test command must pass before moving past the MVP scope:

```bash
pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v
```

## Required Stack

### Backend
- [ ] Python `3.11+`
- [ ] FastAPI
- [ ] Uvicorn
- [ ] `openai` Python SDK `v1.x`
- [ ] `sqlite3` stdlib directly, with raw SQL only
- [ ] `python-dotenv`
- [ ] `pytest`
- [ ] `pytest-asyncio`
- [ ] `httpx.AsyncClient` for HTTP testing, not FastAPI `TestClient`

### Frontend
- [ ] JavaScript only, not TypeScript
- [ ] React 18 via Vite
- [ ] Native `fetch`, not axios
- [ ] Plain CSS in one flat CSS file
- [ ] React `useState` / `useEffect` only; no Redux, no Zustand
- [ ] Node `18+`

## Required Files

### `backend/requirements.txt`
```txt
fastapi
uvicorn
openai
python-dotenv
httpx
pytest
pytest-asyncio
```
- [ ] Create manually
- [ ] Do not use `pip freeze`

### `pytest.ini`
Create at the project root:

```ini
[pytest]
asyncio_mode = auto
```

## Scaffold / Run Commands

### Install
```bash
pip install fastapi uvicorn openai python-dotenv httpx pytest pytest-asyncio
```

### Frontend scaffold
```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install
```

### Dev servers
- [ ] Backend: `cd backend && uvicorn main:app --reload --port 8000`
- [ ] Frontend: `cd frontend && npm run dev`
- [ ] Frontend must call backend at `http://localhost:8000`

## Database Rules
- [ ] SQLite file is `/data/app.db`
- [ ] Open a new SQLite connection per request
- [ ] Never use one shared module-level connection
- [ ] Do not use `check_same_thread=False` as a shared-connection workaround
- [ ] In `get_connection()`, set `conn.row_factory = sqlite3.Row`
- [ ] In `get_connection()`, run `PRAGMA foreign_keys = ON`
- [ ] Close every connection explicitly with `conn.close()`

## Environment Files
- [ ] `/backend/.env` contains `OPENAI_API_KEY`
- [ ] `/backend/.env` is never committed
- [ ] `/backend/.env.example` is committed and shows keys with empty values, e.g. `OPENAI_API_KEY=`

## Non-Negotiable Notes
- [ ] Start the backend from `backend/` with `uvicorn main:app --reload --port 8000`
- [ ] `DB_PATH = "../data/app.db"` is relative to that `backend/` launch directory
- [ ] Run frontend and backend in separate terminals

The source spec is authoritative.
