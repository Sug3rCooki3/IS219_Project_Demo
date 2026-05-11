# Frontend Components

All components live in `frontend/src/components/`. All API calls go through `frontend/src/api.js` — no component calls `fetch` directly.

---

## Component Tree

```
App.jsx  (owns all state)
├── PromptInput.jsx
├── ResponseGrid.jsx
│   └── ResponseCard.jsx  (×4)
│       └── ScoreDisplay.jsx  (Phase 1)
├── ExportButton.jsx  (Phase 1)
└── HistoryPanel.jsx
```

---

## App.jsx — Root Component

Owns all state. Passes data and handlers as props. Contains the page layout.

### State
```js
const [basePrompt, setBasePrompt] = useState('');
const [variations, setVariations] = useState([]);      // [{label, technique, text}, ...]
const [responses, setResponses] = useState([]);         // [{label, response, cached}, ...]
const [tokenUsage, setTokenUsage] = useState(null);    // integer or null
const [ratings, setRatings] = useState({});            // { A: 3, B: null, C: 5, D: null }
const [autoScores, setAutoScores] = useState({});      // { A: {clarity,relevance,completeness}, ... }
const [history, setHistory] = useState([]);             // array of past sessions
const [currentSessionId, setCurrentSessionId] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
```

### Handlers (defined in App.jsx, passed as props)
- `handleSubmit(prompt)` — calls `/generate-variations` then `/get-responses`, triggers auto-score after (Phase 1)
- `handleRatingChange(label, score)` — updates `ratings` state; after updating, automatically calls `handleSave()` if all 4 variations have been rated
- `handleSave()` — calls `/save-results` with current session data; sets `currentSessionId` from the response; also called automatically once all 4 ratings are submitted
- `handleHistorySelect(session)` — loads a past session into state
- `handleExportBest()` — Phase 1

### On mount (App.jsx)
```js
useEffect(() => {
  getHistory().then(data => setHistory(data.sessions));
}, []);
```
Runs once on mount to populate the history panel. No other component fetches history.

---

## PromptInput.jsx

**Phase:** 0

A text area for the user to type their math prompt, with a submit button.

### Props
| Prop | Type | Description |
|---|---|---|
| `onSubmit` | `function(prompt: string)` | Called when user clicks submit |
| `loading` | `boolean` | Disables the button during API calls |

### Behavior
- Submit button is disabled while `loading === true`
- Submit button is disabled if the text area is empty
- Does not clear the input after submit (user may want to edit and resubmit)

### DOM structure (approximate)
```html
<div class="prompt-input">
  <textarea placeholder="Enter a math prompt, e.g. What is the chain rule?" />
  <button>Generate Variations</button>
</div>
```

---

## ResponseGrid.jsx

**Phase:** 0

Renders 4 `ResponseCard` components in a 2×2 grid layout.

### Props
| Prop | Type | Description |
|---|---|---|
| `responses` | `array` | `[{label, response, cached}, ...]` |
| `variations` | `array` | `[{label, technique, text}, ...]` |
| `ratings` | `object` | `{ A: 3, ... }` |
| `autoScores` | `object` | `{ A: {clarity, relevance, completeness}, ... }` (Phase 1) |
| `onRatingChange` | `function(label, score)` | Passed down to each card |

### Behavior
- Renders nothing if `responses` is empty
- CSS: `display: grid; grid-template-columns: 1fr 1fr;`

---

## ResponseCard.jsx

**Phase:** 0

Displays one variation's label, technique, response text, and manual rating controls.

### Props
| Prop | Type | Description |
|---|---|---|
| `label` | `string` | "A", "B", "C", or "D" |
| `technique` | `string` | e.g. "role-based" |
| `responseText` | `string` | The LLM's response |
| `cached` | `boolean` | Shows a "Cached" badge if true (Phase 1) |
| `rating` | `number or null` | Current manual score |
| `autoScore` | `object or null` | `{clarity, relevance, completeness}` (Phase 1) |
| `onRatingChange` | `function(label, score)` | Called when user clicks a rating button |

### DOM structure (approximate)
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

The currently selected rating button should have a visually distinct style (e.g., `background-color: #333`).

---

## HistoryPanel.jsx

**Phase:** 0

A sidebar listing all past prompt sessions. Collapsible via a toggle button inside the panel header.

### Props
| Prop | Type | Description |
|---|---|---|
| `history` | `array` | Array of session objects from `/history` |
| `onSelect` | `function(session)` | Called when user clicks a past session |

### Behavior
- Has its own internal `isOpen` state (`useState(true)` — open by default)
- A toggle button in the panel header shows "▶ History" when closed, "▼ History" when open
- When closed, only the header is visible; the list is hidden (`display: none`)
- Displays `base_prompt` and `created_at` for each session (truncate prompt to 60 chars)
- Clicking a session calls `onSelect(session)`, which loads it into `App` state
- Shows "No history yet." if `history` is empty
- Fetches history on mount (`useEffect` with empty deps in `App.jsx`)

---

## ScoreDisplay.jsx (Phase 1)

Shows the three auto-score sub-scores for one variation card.

### Props
| Prop | Type | Description |
|---|---|---|
| `autoScore` | `object or null` | `{clarity, relevance, completeness}` or null |

### Behavior
- If `autoScore` is null, display "Score unavailable"
- If `autoScore` has values, display:
  ```
  Clarity: 4 / 5   Relevance: 5 / 5   Completeness: 3 / 5
  Avg: 4.0
  ```
- `Avg` = `(clarity + relevance + completeness) / 3`, rounded to 1 decimal place using `(Math.round(avg * 10) / 10).toFixed(1)`

---

## ExportButton.jsx (Phase 1)

A button that calls `/export-best` and displays the winner and explanation.

### Props
| Prop | Type | Description |
|---|---|---|
| `sessionId` | `number or null` | Current session's DB id |
| `onExport` | `function(result)` | Called with the API response |

### Behavior
- Button is disabled if `sessionId` is null (session not yet saved)
- After click, displays the winning variation label and the computed explanation string:
  `"Variation X scored highest — strongest in [sub-score name]."`
- Explanation is computed in the frontend from the `best_variation` data in the API response — no extra LLM call
- To find the strongest sub-score: compare `auto_clarity`, `auto_relevance`, `auto_completeness` and pick the highest. If two or more tie for highest, prefer in this order: clarity → relevance → completeness

---

## api.js — All Fetch Functions

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
