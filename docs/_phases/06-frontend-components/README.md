# Phase 06 — Frontend Components

> Source spec: [../../_specs/06-frontend-components.md](../../_specs/06-frontend-components.md)

Use this phase to build the React UI and client API layer.

## Focus
- `App.jsx` state and handlers
- `PromptInput.jsx`
- `ResponseGrid.jsx`
- `ResponseCard.jsx`
- `HistoryPanel.jsx`
- `ScoreDisplay.jsx` (Phase 1)
- `ExportButton.jsx` (Phase 1)
- `api.js`

## App-Level Rules
- [x] All API calls go through `frontend/src/api.js`
- [x] No component calls `fetch` directly
- [x] `App.jsx` owns all state and passes handlers via props

## `App.jsx` State
- [x] `basePrompt` — `useState('')`
- [x] `variations` — `useState([])` — `[{label, technique, text}, ...]`
- [x] `responses` — `useState([])` — `[{label, response, cached}, ...]`
- [x] `tokenUsage` — `useState(null)`
- [x] `ratings` — `useState({})` — `{ A: 3, B: null, ... }`
- [x] `autoScores` — `useState({})` — `{ A: {clarity, relevance, completeness}, ... }` (Phase 1)
- [x] `history` — `useState([])`
- [x] `currentSessionId` — `useState(null)`
- [x] `loading` — `useState(false)`
- [x] `error` — `useState(null)`

## `App.jsx` Handlers
- [x] `handleSubmit(prompt)` — calls `generateVariations(prompt)` then `getResponses(variations)`; sets `variations`, `responses`, `tokenUsage`; then auto-scores each response (Phase 1)
- [x] `handleRatingChange(label, score)` — updates `ratings` state; if all 4 variations now have a non-null rating, automatically calls `handleSave()`
- [x] `handleSave()` — calls `saveResults(...)` with current session data; sets `currentSessionId` from the response
- [x] `handleHistorySelect(session)` — loads a past session into `App` state

## On Mount
- [x] `App.jsx` fetches history once on mount:
  ```js
  useEffect(() => {
    getHistory().then(data => setHistory(data.sessions));
  }, []);
  ```

## Required Behaviors

### `PromptInput.jsx`
**Props:** `onSubmit` (function), `loading` (boolean)
- [x] Has a textarea and submit button
- [x] Button is disabled while `loading === true`
- [x] Button is disabled when textarea is empty
- [x] Does not clear the input after submit

```html
<div class="prompt-input">
  <textarea placeholder="Enter a math prompt, e.g. What is the chain rule?" />
  <button>Generate Variations</button>
</div>
```

### `ResponseGrid.jsx`
**Props:** `responses`, `variations`, `ratings`, `autoScores`, `onRatingChange`
- [x] Renders nothing if `responses` is empty
- [x] Renders 4 `ResponseCard` items in a 2×2 grid — CSS: `display: grid; grid-template-columns: 1fr 1fr;`

### `ResponseCard.jsx`
**Props:** `label`, `technique`, `responseText`, `cached`, `rating`, `autoScore`, `onRatingChange`
- [x] Shows label, technique, response text, and 1-5 rating buttons
- [x] Selected rating button is visually distinct (e.g. `background-color: #333`)
- [x] Can display cached badge when `cached === true` (Phase 1)
- [x] Can display `ScoreDisplay` in Phase 1

```html
<div class="response-card">
  <div class="card-header">
    <span class="label">Variation A</span>
    <span class="technique">role-based</span>
  </div>
  <div class="response-text">...</div>
  <div class="rating-controls">
    <button>1</button><button>2</button><button>3</button><button>4</button><button>5</button>
  </div>
  <!-- ScoreDisplay here in Phase 1 -->
</div>
```

### `HistoryPanel.jsx`
**Props:** `history`, `onSelect`
- [x] Has internal `isOpen` state — defaults to `true` (open by default)
- [x] Toggle button shows `▶ History` when closed, `▼ History` when open
- [x] When closed, the list is hidden with `display: none`; the header remains visible
- [x] Shows `base_prompt` (truncated to 60 chars) and `created_at` for each session
- [x] Clicking a session calls `onSelect(session)`
- [x] Shows `No history yet.` when `history` is empty

### `ScoreDisplay.jsx` (Phase 1)
**Props:** `autoScore` (object or null)
- [x] Shows `Score unavailable` when `autoScore` is null
- [x] Shows `Clarity: X / 5`, `Relevance: X / 5`, `Completeness: X / 5`, and `Avg: X.X`
- [x] Avg computed with `(Math.round(avg * 10) / 10).toFixed(1)`

### `ExportButton.jsx` (Phase 1)
**Props:** `sessionId` (number or null), `onExport` (function)
- [x] Disabled if `sessionId` is null
- [x] After click, displays: `"Variation X scored highest — strongest in [sub-score name]."`
- [x] Explanation is computed in the frontend from `best_variation` data — no extra LLM call
- [x] To find the strongest sub-score: compare `auto_clarity`, `auto_relevance`, `auto_completeness`; tiebreak order is clarity → relevance → completeness

## `api.js` Functions
- [x] `BASE = 'http://localhost:8000'` at the top of the file
- [x] On non-ok response, throw `new Error((await res.json()).detail)`
- [x] `generateVariations(basePrompt)` — `POST /generate-variations`, body `{ base_prompt: basePrompt }`
- [x] `getResponses(variations)` — `POST /get-responses`, body `{ variations }`
- [x] `saveResults(sessionData)` — `POST /save-results`, body `sessionData`
- [x] `getHistory()` — `GET /history`
- [x] `autoScore(label, responseText)` (Phase 1) — `POST /auto-score`, body `{ label, response_text: responseText }`
- [x] `exportBest(sessionId)` (Phase 1) — `GET /export-best?session_id=<id>`

**Exact implementation (`frontend/src/api.js`):**
```js
const BASE = 'http://localhost:8000';

export async function generateVariations(basePrompt) {
  const res = await fetch(`${BASE}/generate-variations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ base_prompt: basePrompt }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function getResponses(variations) {
  const res = await fetch(`${BASE}/get-responses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ variations }),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function autoScore(label, responseText) { /* Phase 1 */ }

export async function saveResults(sessionData) {
  const res = await fetch(`${BASE}/save-results`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(sessionData),
  });
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function getHistory() {
  const res = await fetch(`${BASE}/history`);
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
}

export async function exportBest(sessionId) { /* Phase 1 */ }
```

The source spec is authoritative.
