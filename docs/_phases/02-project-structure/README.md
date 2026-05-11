# Phase 02 — Project Structure

> Source spec: [../../_specs/02-project-structure.md](../../_specs/02-project-structure.md)

Use this phase to create the exact file and folder layout.

## Focus
- Root file tree
- Backend and router files
- Frontend component files
- Tests layout
- `data/` directory creation
- File responsibilities

## Required Root Files
- [x] `.gitignore` includes at minimum `.env`, `backend/.env`, `data/app.db`, `.venv/`, `__pycache__/`, `*.pyc`
- [x] `pytest.ini` exists at project root with the following content:
  ```ini
  [pytest]
  asyncio_mode = auto
  ```
- [x] `README.md` exists
- [x] `data/` directory exists before first run
- [x] Do not create `data/app.db` manually

## Required Backend Files
- [x] `backend/__init__.py`
- [x] `backend/main.py`
- [x] `backend/database.py`
- [x] `backend/variations.py`
- [x] `backend/openai_client.py`
- [x] `backend/requirements.txt`
- [x] `backend/.env`
- [x] `backend/.env.example` with empty key values, e.g. `OPENAI_API_KEY=`

### Required Routers
- [x] `backend/routers/__init__.py`
- [x] `backend/routers/generate.py`
- [x] `backend/routers/responses.py`
- [x] `backend/routers/results.py`
- [x] `backend/routers/history.py`
- [ ] `backend/routers/scoring.py` (Phase 1)
- [ ] `backend/routers/export.py` (Phase 1)

## Required Frontend Files
- [x] `frontend/index.html`
- [x] `frontend/vite.config.js`
- [x] `frontend/package.json`
- [x] `frontend/src/main.jsx`
- [x] `frontend/src/App.jsx`
- [x] `frontend/src/api.js`
- [x] `frontend/src/styles.css`

### Required Components
- [x] `frontend/src/components/PromptInput.jsx`
- [x] `frontend/src/components/ResponseCard.jsx`
- [x] `frontend/src/components/ResponseGrid.jsx`
- [x] `frontend/src/components/HistoryPanel.jsx`
- [ ] `frontend/src/components/ScoreDisplay.jsx` (Phase 1)
- [ ] `frontend/src/components/ExportButton.jsx` (Phase 1)

## Required Test Files
- [x] `tests/conftest.py` — created; exact code is in Phase 07 README
- [x] `tests/test_results.py` — created in Phase 03
- [x] `tests/test_history.py` — created in Phase 03
- [x] `tests/test_generate.py` — created in Phase 04
- [x] `tests/test_responses.py` — created in Phase 04
- [ ] `tests/test_scoring.py` (Phase 1)
- [ ] `tests/test_export.py` (Phase 1)

## Critical Responsibilities
- [x] `main.py` creates the FastAPI app, mounts all routers, adds CORS, and calls `database.init_db()` on startup
- [x] `database.py` owns connection setup, table creation, inserts, history lookup, and Phase 1 cache queries:
  - Phase 0: `init_db()`, `save_session()`, `get_all_sessions()`, `get_session_by_id()`
  - Phase 1: `get_cached_response(prompt_hash, label)`, `save_cached_response(prompt_hash, label, response)`
- [x] `variations.py` exposes `build_variations(base_prompt: str) -> list[dict]`
- [x] `openai_client.py` exposes `get_completion(prompt: str) -> tuple[str, int]`; raises `OpenAIClientError` on failure (router catches and returns 503)
- [x] Routers must import `openai_client` as a module, not `from openai_client import get_completion`
- [x] `api.js` exports one function per endpoint:
  - Phase 0: `generateVariations(basePrompt)`, `getResponses(variations)`, `saveResults(sessionData)`, `getHistory()`
  - Phase 1 stubs (defined but not wired): `autoScore(label, responseText)`, `exportBest(sessionId)`
- [x] `App.jsx` owns all app state: `basePrompt`, `variations`, `responses`, `tokenUsage`, `ratings`, `autoScores`, `history`, `currentSessionId`, `loading`, `error`
- [x] `App.jsx` defines all event handlers (`handleSubmit`, `handleRatingChange`, `handleSave`, `handleHistorySelect`) and a `useEffect` that calls `getHistory()` on mount
- [x] No frontend component calls `fetch` directly except through `api.js`

The source spec is authoritative.
