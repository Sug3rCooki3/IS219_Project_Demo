# Project Structure

Exact folder and file layout. Create every file listed here, **except `data/app.db`** which is auto-created on first run. **Do create the empty `data/` directory** — SQLite cannot create `app.db` if the folder doesn't exist. Files marked `(Phase 1)` are created in Phase 1 only.

```
/
├── .gitignore                      ← must contain at minimum: `.env` and `data/app.db`
├── pytest.ini                      ← required: sets asyncio_mode = auto for pytest-asyncio
├── README.md
├── backend/
│   ├── .env                        ← API key (never committed)
│   ├── .env.example                ← committed, shows key names with empty values
│   ├── __init__.py                 ← empty file, makes backend a Python package
│   ├── main.py                     ← FastAPI app entry point, mounts all routers
│   ├── database.py                 ← SQLite connection, table creation, all DB queries
│   ├── variations.py               ← The 4 hardcoded template functions
│   ├── openai_client.py            ← Thin wrapper around the OpenAI SDK
│   ├── routers/
│   │   ├── __init__.py             ← empty file, makes routers a Python package
│   │   ├── generate.py             ← POST /generate-variations
│   │   ├── responses.py            ← POST /get-responses
│   │   ├── scoring.py              ← POST /auto-score (Phase 1)
│   │   ├── results.py              ← POST /save-results
│   │   ├── history.py              ← GET /history
│   │   └── export.py               ← GET /export-best (Phase 1)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx                ← React entry point
│       ├── App.jsx                 ← Root component, owns all state
│       ├── api.js                  ← All fetch calls to backend (one function per endpoint)
│       ├── styles.css              ← All styling (one file)
│       └── components/
│           ├── PromptInput.jsx     ← Text area + submit button
│           ├── ResponseCard.jsx    ← One card per variation (label, response, rating)
│           ├── ResponseGrid.jsx    ← Renders 4 ResponseCards side-by-side
│           ├── HistoryPanel.jsx    ← Sidebar with list of past prompts
│           ├── ScoreDisplay.jsx    ← Shows clarity/relevance/completeness (Phase 1)
│           └── ExportButton.jsx    ← Export Best Prompt button + explanation (Phase 1)
├── data/
│   └── app.db                      ← SQLite database file (auto-created on first run)
├── tests/
│   ├── conftest.py                 ← adds backend/ to sys.path so imports work; run pytest from root
│   ├── test_generate.py            ← Tests for /generate-variations
│   ├── test_responses.py           ← Tests for /get-responses
│   ├── test_scoring.py             ← Tests for /auto-score (Phase 1)
│   ├── test_results.py             ← Tests for /save-results
│   ├── test_history.py             ← Tests for /history
│   └── test_export.py              ← Tests for /export-best (Phase 1)
                                    ← See 07-test-cases.md for complete test code
└── docs/
    └── project_management/
        └── _specs/                 ← You are here
```

---

## File Responsibilities (Key Files)

### `backend/main.py`
- Creates the FastAPI app instance
- Includes all routers from `backend/routers/`
- Adds CORS middleware allowing `http://localhost:5173`
- Calls `database.init_db()` on startup to ensure tables exist

### `backend/database.py`
- `init_db()` — creates all tables if they don't exist
- `save_session(session_data)` — inserts a session + its variations
- `get_all_sessions()` — returns all sessions with their variations
- `get_session_by_id(session_id)` — returns one session with variations
- `get_cached_response(prompt_hash, label)` — Phase 1
- `save_cached_response(prompt_hash, label, response)` — Phase 1

### `backend/variations.py`
- `build_variations(base_prompt: str) -> list[dict]`
- Returns a list of 4 dicts, each with `label`, `technique`, `text`
- Uses the 4 hardcoded templates (see `05-variation-templates.md`)

### `backend/openai_client.py`
- `get_completion(prompt: str) -> tuple[str, int]`
- Returns `(response_text, tokens_used)`
- Uses `max_tokens=300`
- On API failure, raises `OpenAIClientError` (a custom exception defined in this file). The router catches `OpenAIClientError` and returns a `503` response.
- **Routers must import this as a module** (`import openai_client`) and call `openai_client.get_completion(...)` — do NOT use `from openai_client import get_completion`. The module-level import is required for the test mocks to intercept calls correctly.

### `frontend/src/api.js`
- `generateVariations(basePrompt)` — POST /generate-variations
- `getResponses(variations)` — POST /get-responses
- `autoScore(label, responseText)` — POST /auto-score (Phase 1)
- `saveResults(sessionData)` — POST /save-results
- `getHistory()` — GET /history
- `exportBest(sessionId)` — GET /export-best (Phase 1)

### `frontend/src/App.jsx`
- Owns all application state: `basePrompt`, `variations`, `responses`, `tokenUsage`, `ratings`, `autoScores`, `history`, `currentSessionId`, `loading`, `error`
- Passes state and handlers down to child components as props
- No child component fetches data directly — all API calls go through `api.js` and are triggered from `App.jsx`
