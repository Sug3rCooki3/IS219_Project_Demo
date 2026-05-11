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
> **Status: COMPLETE — 25/25 tests passing**

- [x] `POST /generate-variations` — implemented in `backend/routers/generate.py`
- [x] `POST /get-responses` — implemented in `backend/routers/responses.py`
- [x] `POST /save-results` — implemented in `backend/routers/results.py`
- [x] `GET /history` — implemented in `backend/routers/history.py`
- [x] `token_usage` collected and stored; not yet displayed in UI (Phase 1)
- [x] Phase 0 tests all pass:

```bash
pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v
# 25 passed in 1.10s
```

## Required Stack

### Backend
- [x] Python `3.11+` — running Python 3.12.3
- [x] FastAPI
- [x] Uvicorn
- [x] `openai` Python SDK `v1.x` — installed v2.32.0 (v2.x is backwards-compatible)
- [x] `sqlite3` stdlib directly, with raw SQL only
- [x] `python-dotenv`
- [x] `pytest`
- [x] `pytest-asyncio`
- [x] `httpx.AsyncClient` for HTTP testing, not FastAPI `TestClient`

### Frontend
- [x] JavaScript only, not TypeScript
- [x] React 18 via Vite — React `^18.3.1`, Vite `^5.4.19`
- [x] Native `fetch`, not axios
- [x] Plain CSS in one flat CSS file (`frontend/src/styles.css`)
- [x] React `useState` / `useEffect` only; no Redux, no Zustand
- [x] Node `18+` — running Node v24.13.0

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
- [x] Created manually
- [x] Does not use `pip freeze`

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
- [x] Backend: `cd backend && uvicorn main:app --reload --port 8000`
- [x] Frontend: `cd frontend && npm run dev`
- [x] Frontend must call backend at `http://localhost:8000`

## Database Rules
- [x] SQLite file is `/data/app.db` — `DB_PATH = "../data/app.db"` in `database.py`
- [x] Open a new SQLite connection per request
- [x] Never use one shared module-level connection
- [x] Do not use `check_same_thread=False` as a shared-connection workaround
- [x] In `get_connection()`, set `conn.row_factory = sqlite3.Row`
- [x] In `get_connection()`, run `PRAGMA foreign_keys = ON`
- [x] Close every connection explicitly with `conn.close()`

## Environment Files
- [x] `/backend/.env` contains `OPENAI_API_KEY`
- [x] `/backend/.env` is never committed (in `.gitignore`)
- [x] `/backend/.env.example` is committed and shows keys with empty values, e.g. `OPENAI_API_KEY=`

## Non-Negotiable Notes
- [x] Start the backend from `backend/` with `uvicorn main:app --reload --port 8000`
- [x] `DB_PATH = "../data/app.db"` is relative to that `backend/` launch directory
- [x] Run frontend and backend in separate terminals

The source spec is authoritative.
