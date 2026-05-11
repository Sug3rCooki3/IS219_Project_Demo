# Phase 00 — MVP Scope

> **Source spec:** [`../../_specs/00-mvp-scope.md`](../../_specs/00-mvp-scope.md)
> Build everything in this phase before touching Phase 01.

---

## Goal

A working app that takes a math prompt, sends 4 variations to OpenAI, shows the responses side-by-side, and lets the user rate them manually. Sessions are saved and browsable.

---

## Build Checklist

### Backend
- [ ] `POST /generate-variations` — pure string transform, no LLM call
- [ ] `POST /get-responses` — sends 4 variations to OpenAI, returns responses + token_usage
- [ ] `POST /save-results` — persists session + 4 variations to SQLite, returns `{ session_id }`
- [ ] `GET /history` — returns all sessions newest-first, always 200 with `{ "sessions": [] }` when empty
- [ ] Do not build `POST /auto-score` in Phase 00
- [ ] Do not build `GET /export-best` in Phase 00

### Frontend
- [ ] `PromptInput.jsx` — text area + submit button, disabled while loading
- [ ] `ResponseGrid.jsx` — 2×2 grid of 4 `ResponseCard` components
- [ ] `ResponseCard.jsx` — label, technique, response text, 1–5 rating buttons
- [ ] `HistoryPanel.jsx` — collapsible sidebar, lists past sessions, click to reload
- [ ] `api.js` — `generateVariations`, `getResponses`, `saveResults`, `getHistory`
- [ ] Do not display auto-scores in Phase 00
- [ ] Do not add Export Best Prompt UI in Phase 00
- [ ] Collect and save `token_usage` in Phase 00, but do not display it in the UI until Phase 01

### Database
- [ ] `sessions` table — `id`, `created_at`, `base_prompt`, `token_usage`
- [ ] `variations` table — all columns including `auto_clarity`, `auto_relevance`, `auto_completeness` as **nullable** (no migration needed in Phase 1)
- [ ] Do not create `prompt_cache` until Phase 01

### Error Handling
- [ ] Empty prompt → `400`
- [ ] OpenAI API failure → `503`
- [ ] Wrong variation count in `/save-results` → `400`
- [ ] Do not implement malformed auto-score JSON handling in Phase 00
- [ ] Do not implement export tiebreaker logic in Phase 00

### Config
- [ ] `pytest.ini` at project root (`asyncio_mode = auto`)
- [ ] `.env` in `backend/` with `OPENAI_API_KEY` (never committed)
- [ ] `data/` directory created manually (SQLite won't create it)
- [ ] CORS middleware in `main.py` allowing `http://localhost:5173`

---

## Relevant Specs

| Spec | Purpose |
|---|---|
| [`01-tech-stack.md`](../../_specs/01-tech-stack.md) | All package choices, `requirements.txt`, `pytest.ini` |
| [`02-project-structure.md`](../../_specs/02-project-structure.md) | Full file tree and file responsibilities |
| [`03-data-schema.md`](../../_specs/03-data-schema.md) | `CREATE TABLE` statements |
| [`04-api-contracts.md`](../../_specs/04-api-contracts.md) | Request/response contracts for all 4 Phase 0 endpoints |
| [`05-variation-templates.md`](../../_specs/05-variation-templates.md) | Exact `build_variations()` implementation |
| [`06-frontend-components.md`](../../_specs/06-frontend-components.md) | All component props, state, and behavior |
| [`07-test-cases.md`](../../_specs/07-test-cases.md) | Complete test code — Phase 0 tests only |

---

## Phase 0 Test Command

```bash
pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v
```

All tests must pass before moving to Phase 01.
