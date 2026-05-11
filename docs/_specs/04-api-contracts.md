# API Contracts

Base URL: `http://localhost:8000`

All requests and responses use `Content-Type: application/json`. All endpoints return errors as `{ "detail": "message" }`.

---

## POST `/generate-variations`

**Phase:** 0 (MVP)

Accepts a base prompt string and returns 4 filled variation strings. No LLM call — pure string transformation.

### Request
```json
{
  "base_prompt": "What is the chain rule?"
}
```

### Response `200`
```json
{
  "variations": [
    { "label": "A", "technique": "role-based",             "text": "You are an expert mathematics tutor. What is the chain rule?" },
    { "label": "B", "technique": "few-shot",               "text": "Q: What is a derivative?\nA: A derivative measures the rate of change of a function at a given point.\n\nQ: What is an integral?\nA: An integral calculates the area under a curve over an interval.\n\nQ: What is the chain rule?\nA:" },
    { "label": "C", "technique": "instruction-rewording",  "text": "What is the chain rule? Explain step by step, using simple language." },
    { "label": "D", "technique": "output-formatting",      "text": "What is the chain rule? Respond using bullet points and a final summary sentence." }
  ]
}
```

### Error `400`
```json
{ "detail": "base_prompt cannot be empty." }
```

---

## POST `/get-responses`

**Phase:** 0 (MVP) — no caching. Phase 1 adds cache lookup.

Sends each variation to the OpenAI API and returns responses.

### Request
```json
{
  "variations": [
    { "label": "A", "technique": "role-based",            "text": "You are an expert mathematics tutor. What is the chain rule?" },
    { "label": "B", "technique": "few-shot",              "text": "..." },
    { "label": "C", "technique": "instruction-rewording", "text": "..." },
    { "label": "D", "technique": "output-formatting",     "text": "..." }
  ]
}
```

### Response `200`
```json
{
  "responses": [
    { "label": "A", "response": "The chain rule states that...", "cached": false },
    { "label": "B", "response": "...", "cached": false },
    { "label": "C", "response": "...", "cached": false },
    { "label": "D", "response": "...", "cached": false }
  ],
  "token_usage": 1140
}
```
- `cached` is always `false` in Phase 0. Phase 1 sets it to `true` when served from cache.
- `token_usage` is the total tokens used across all 4 calls combined.

### Error `503`
```json
{ "detail": "OpenAI API is unreachable. Please try again." }
```

---

## POST `/auto-score` (Phase 1)

Sends one response to the LLM using the rubric prompt. Returns parsed sub-scores.

### Request
```json
{
  "label": "A",
  "response_text": "The chain rule states that..."
}
```

### Response `200` — success
```json
{
  "label": "A",
  "clarity": 4,
  "relevance": 5,
  "completeness": 3
}
```

### Response `200` — LLM returned malformed JSON
```json
{
  "label": "A",
  "clarity": null,
  "relevance": null,
  "completeness": null,
  "error": "Score unavailable"
}
```
Never return a 4xx/5xx for a parse failure — always return 200 with nulls so the frontend can display gracefully.

---

## POST `/save-results`

**Phase:** 0 (MVP)

Persists a complete session. Called after the user has finished rating.

### Request
```json
{
  "base_prompt": "What is the chain rule?",
  "token_usage": 1140,
  "variations": [
    {
      "label": "A",
      "technique": "role-based",
      "variation_text": "You are an expert mathematics tutor. What is the chain rule?",
      "response_text": "The chain rule states that...",
      "response_cached": false,
      "manual_score": 4,
      "auto_clarity": null,
      "auto_relevance": null,
      "auto_completeness": null
    }
  ]
}
```
- Send all 4 variations in the array.
- `manual_score` may be `null` if the user didn't rate that variation.
- `auto_*` fields are `null` in Phase 0.

### Response `201`
```json
{ "session_id": 7 }
```

### Error `400`
```json
{ "detail": "variations array must contain exactly 4 items." }
```

---

## GET `/history`

**Phase:** 0 (MVP)

Returns all past sessions, newest first. Returns an empty array if no sessions exist — never returns `404`.

### Response `200`
```json
{
  "sessions": [
    {
      "id": 7,
      "created_at": "2026-04-27T14:32:00Z",
      "base_prompt": "What is the chain rule?",
      "token_usage": 1140,
      "variations": [
        {
          "label": "A",
          "technique": "role-based",
          "variation_text": "...",
          "response_text": "...",
          "response_cached": false,
          "manual_score": 4,
          "auto_clarity": null,
          "auto_relevance": null,
          "auto_completeness": null
        }
      ]
    }
  ]
}
```

---

## GET `/export-best` (Phase 1)

Returns the highest-scoring variation from a given session. Score = average of the three auto-score sub-scores.

### Query params
`?session_id=7`

### Response `200`
```json
{
  "session_id": 7,
  "best_variation": {
    "label": "A",
    "technique": "role-based",
    "variation_text": "...",
    "response_text": "The chain rule states that...",
    "manual_score": 4,
    "auto_clarity": 5,
    "auto_relevance": 4,
    "auto_completeness": 3,
    "combined_score": 4.0
  }
}
```
- `combined_score` = `(auto_clarity + auto_relevance + auto_completeness) / 3`, rounded to 1 decimal place.
- If all variations are tied, return Variation A.
- If no auto-scores exist (all null), fall back to `manual_score` for ranking.

### Error `404`
```json
{ "detail": "Session not found." }
```

---

## CORS Configuration

Add the following CORS middleware in `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],  # allows Content-Type and any other headers the browser sends
)
```
