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
- [ ] `.gitignore` includes at minimum `.env`, `backend/.env`, `data/app.db`, `.venv/`, `__pycache__/`, `*.pyc`
- [ ] `pytest.ini` exists at project root with the following content:
  ```ini
  [pytest]
  asyncio_mode = auto
  ```
- [ ] `README.md` exists
- [ ] `data/` directory exists before first run
- [ ] Do not create `data/app.db` manually

## Required Backend Files
- [ ] `backend/__init__.py`
- [ ] `backend/main.py`
- [ ] `backend/database.py`
- [ ] `backend/variations.py`
- [ ] `backend/openai_client.py`
- [ ] `backend/requirements.txt`
- [ ] `backend/.env`
- [ ] `backend/.env.example` with empty key values, e.g. `OPENAI_API_KEY=`

### Required Routers
- [ ] `backend/routers/__init__.py`
- [ ] `backend/routers/generate.py`
- [ ] `backend/routers/responses.py`
- [ ] `backend/routers/results.py`
- [ ] `backend/routers/history.py`
- [ ] `backend/routers/scoring.py` (Phase 1)
- [ ] `backend/routers/export.py` (Phase 1)

## Required Frontend Files
- [ ] `frontend/index.html`
- [ ] `frontend/vite.config.js`
- [ ] `frontend/package.json`
- [ ] `frontend/src/main.jsx`
- [ ] `frontend/src/App.jsx`
- [ ] `frontend/src/api.js`
- [ ] `frontend/src/styles.css`

### Required Components
- [ ] `frontend/src/components/PromptInput.jsx`
- [ ] `frontend/src/components/ResponseCard.jsx`
- [ ] `frontend/src/components/ResponseGrid.jsx`
- [ ] `frontend/src/components/HistoryPanel.jsx`
- [ ] `frontend/src/components/ScoreDisplay.jsx` (Phase 1)
- [ ] `frontend/src/components/ExportButton.jsx` (Phase 1)

## Required Test Files
- [ ] `tests/conftest.py` — create now; exact code is in Phase 07 README
- [ ] `tests/test_results.py` — create in Phase 03
- [ ] `tests/test_history.py` — create in Phase 03
- [ ] `tests/test_generate.py` — create in Phase 04
- [ ] `tests/test_responses.py` — create in Phase 04
- [ ] `tests/test_scoring.py` (Phase 1)
- [ ] `tests/test_export.py` (Phase 1)

## Critical Responsibilities
- [ ] `main.py` creates the FastAPI app, mounts all routers, adds CORS, and calls `database.init_db()` on startup
- [ ] `database.py` owns connection setup, table creation, inserts, history lookup, and Phase 1 cache queries:
  - Phase 0: `init_db()`, `save_session()`, `get_all_sessions()`, `get_session_by_id()`
  - Phase 1: `get_cached_response(prompt_hash, label)`, `save_cached_response(prompt_hash, label, response)`
- [ ] `variations.py` exposes `build_variations(base_prompt: str) -> list[dict]`
- [ ] `openai_client.py` exposes `get_completion(prompt: str) -> tuple[str, int]`; raises `OpenAIClientError` on failure (router catches and returns 503)
- [ ] Routers must import `openai_client` as a module, not `from openai_client import get_completion`
- [ ] `api.js` exports one function per endpoint:
  - Phase 0: `generateVariations(basePrompt)`, `getResponses(variations)`, `saveResults(sessionData)`, `getHistory()`
  - Phase 1 stubs (defined but not wired): `autoScore(label, responseText)`, `exportBest(sessionId)`
- [ ] `App.jsx` owns all app state: `basePrompt`, `variations`, `responses`, `tokenUsage`, `ratings`, `autoScores`, `history`, `currentSessionId`, `loading`, `error`
- [ ] `App.jsx` defines all event handlers (`handleSubmit`, `handleRatingChange`, `handleSave`, `handleHistorySelect`) and a `useEffect` that calls `getHistory()` on mount
- [ ] No frontend component calls `fetch` directly except through `api.js`

The source spec is authoritative.
