# MVP Scope

## What This Document Is
A phased breakdown of what to build first (Phase 0 – MVP) vs. what comes after (Phase 1 – Full Spec). An AI coder should implement Phase 0 completely before touching Phase 1.

---

## Phase 0 – MVP (Build This First)

**Goal:** A working app that takes a math prompt, sends 4 variations to OpenAI, shows the responses side-by-side, and lets the user rate them manually. Sessions are saved and browsable.

### Backend (Phase 0)
| Endpoint | Status |
|---|---|
| `POST /generate-variations` | ✅ MVP |
| `POST /get-responses` | ✅ MVP (no caching yet) |
| `POST /save-results` | ✅ MVP |
| `GET /history` | ✅ MVP |
| `POST /auto-score` | ❌ Phase 1 |
| `GET /export-best` | ❌ Phase 1 |

### Frontend (Phase 0)
| Feature | Status |
|---|---|
| Prompt input field + submit button | ✅ MVP |
| 4 response cards with label + technique name | ✅ MVP |
| Manual rating buttons (1–5) per card | ✅ MVP |
| History sidebar (list previous prompts, click to reload) | ✅ MVP |
| Auto-score display (clarity / relevance / completeness) | ❌ Phase 1 |
| Export Best Prompt button + explanation | ❌ Phase 1 |
| Token usage counter | ❌ Phase 1 — Note: the backend collects and stores `token_usage` in Phase 0 (the `/get-responses` response includes it and it is saved via `/save-results`), but it is not displayed in the UI until Phase 1 |

### Database (Phase 0)
| Table | Status |
|---|---|
| `sessions` | ✅ MVP |
| `variations` (all columns including `auto_clarity`, `auto_relevance`, `auto_completeness` — created as nullable so Phase 1 requires no schema migration) | ✅ MVP |
| `prompt_cache` | ❌ Phase 1 |

### Error Handling (Phase 0)
| Case | Status |
|---|---|
| Empty prompt validation | ✅ MVP |
| OpenAI API failure → user-facing error | ✅ MVP |
| Malformed auto-score JSON | ❌ Phase 1 |
| Tiebreaker on export | ❌ Phase 1 |

---

## Phase 1 – Full Spec (Build After Phase 0 is Working)

1. Add `POST /auto-score` endpoint — sends rubric prompt to LLM, returns `{clarity, relevance, completeness}`
2. Populate `auto_clarity`, `auto_relevance`, `auto_completeness` columns in the `variations` table (columns already exist as nullable from Phase 0)
3. Call `/auto-score` for each of the 4 variations immediately after `/get-responses` returns
4. Display sub-scores on each response card
5. Add `GET /export-best` endpoint — returns highest-scoring variation from a session
6. Add Export Best Prompt button to frontend with computed explanation string
7. Add `prompt_cache` table and cache lookup in `/get-responses`
8. Add token usage tracking and display
9. Handle malformed auto-score JSON (store `null`, display "Score unavailable")
10. Handle all-tie tiebreaker (Variation A wins)

---

## What Is Explicitly Out of Scope (Do Not Build)
- User authentication or accounts
- Multiple users or multi-tenancy
- LLM-generated prompt variations (all templates are hardcoded strings)
- Any AI pipeline beyond single OpenAI API calls
- Deployment or hosting — local dev only
- Do not change the 2 hardcoded few-shot examples in Variation B to non-math domains (the examples are fixed)
