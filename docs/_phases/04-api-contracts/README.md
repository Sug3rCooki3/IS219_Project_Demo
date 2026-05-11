# Phase 04 — API Contracts

> Source spec: [../../_specs/04-api-contracts.md](../../_specs/04-api-contracts.md)

Use this phase to implement the request/response behavior for every endpoint.

## Focus
- `POST /generate-variations`
- `POST /get-responses`
- `POST /auto-score` (Phase 1)
- `POST /save-results`
- `GET /history`
- `GET /export-best` (Phase 1)
- CORS configuration

## Global Rules
- [ ] Base URL is `http://localhost:8000`
- [ ] All requests/responses use JSON
- [ ] All errors return `{ "detail": "message" }`

## Phase 0 Endpoints

### `POST /generate-variations`
- [ ] Accepts `{ "base_prompt": "..." }`
- [ ] Returns exactly 4 variations with labels `A-D`
- [ ] Each variation has fields: `label`, `technique`, `text`
- [ ] No LLM call in this endpoint — pure string transformation
- [ ] Empty prompt returns `400` with `{ "detail": "base_prompt cannot be empty." }`

**Request:**
```json
{ "base_prompt": "What is the chain rule?" }
```

**Response `200`:**
```json
{
  "variations": [
    { "label": "A", "technique": "role-based",            "text": "You are an expert mathematics tutor. What is the chain rule?" },
    { "label": "B", "technique": "few-shot",              "text": "Q: What is a derivative?\nA: A derivative measures the rate of change of a function at a given point.\n\nQ: What is an integral?\nA: An integral calculates the area under a curve over an interval.\n\nQ: What is the chain rule?\nA:" },
    { "label": "C", "technique": "instruction-rewording", "text": "What is the chain rule? Explain step by step, using simple language." },
    { "label": "D", "technique": "output-formatting",     "text": "What is the chain rule? Respond using bullet points and a final summary sentence." }
  ]
}
```

### `POST /get-responses`
- [ ] Accepts `{ "variations": [...] }`
- [ ] Returns `responses` array plus `token_usage`
- [ ] Each item in `responses` has fields: `label`, `response`, `cached`
- [ ] `token_usage` is the total tokens across all 4 API calls combined
- [ ] `cached` is always `false` in Phase 0
- [ ] OpenAI failure returns `503` with `{ "detail": "OpenAI API is unreachable. Please try again." }`

**Response `200`:**
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

### `POST /save-results`
- [ ] Accepts `base_prompt`, `token_usage`, and all 4 variations
- [ ] Each variation in the array includes: `label`, `technique`, `variation_text`, `response_text`, `response_cached`, `manual_score`, `auto_clarity`, `auto_relevance`, `auto_completeness`
- [ ] `manual_score` may be `null`
- [ ] `auto_*` fields are `null` in Phase 0
- [ ] Returns `201` with `{ "session_id": <int> }`
- [ ] If variations array length is not 4, return `400` with `{ "detail": "variations array must contain exactly 4 items." }`

**Request:**
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
*(Send all 4 variations in the array.)*

**Response `201`:**
```json
{ "session_id": 7 }
```

### `GET /history`
- [ ] Returns all sessions newest first
- [ ] Each session includes: `id`, `created_at`, `base_prompt`, `token_usage`, and a nested `variations` array
- [ ] Each variation in the array includes: `label`, `technique`, `variation_text`, `response_text`, `response_cached`, `manual_score`, `auto_clarity`, `auto_relevance`, `auto_completeness`
- [ ] `response_cached` is returned as a boolean in the JSON response (even though it is stored as `INTEGER` in SQLite)
- [ ] Empty history returns `200` with `{ "sessions": [] }`
- [ ] Never return `404` for empty history

**Response `200`:**
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

## Phase 1 Endpoints

### `POST /auto-score`
- [ ] Accepts `label` and `response_text`
- [ ] Returns `label`, `clarity`, `relevance`, `completeness`
- [ ] If the LLM returns malformed JSON, still return `200` with null subscores and `error: "Score unavailable"`
- [ ] Never return `4xx`/`5xx` for a parse failure

### `GET /export-best`
- [ ] Accepts `?session_id=7`
- [ ] Returns `{ "session_id": <int>, "best_variation": { ... } }`
- [ ] `best_variation` includes: `label`, `technique`, `variation_text`, `response_text`, `manual_score`, `auto_clarity`, `auto_relevance`, `auto_completeness`, `combined_score`
- [ ] `combined_score` is `(auto_clarity + auto_relevance + auto_completeness) / 3`, rounded to 1 decimal place
- [ ] If all variations tie, return Variation A
- [ ] If all auto-scores are null, fall back to `manual_score` for ranking
- [ ] Invalid session returns `404` with `{ "detail": "Session not found." }`

## CORS Rules
- [ ] Allow origin `http://localhost:5173`
- [ ] Allow methods `GET` and `POST`
- [ ] Use `allow_headers=["*"]`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Tests for this Phase

Create these files after implementing all Phase 0 routers and `variations.py` (Phase 05). Then run all 4 Phase 0 test files together.

**Phase 0 full run command:**
```bash
pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v
```

### `tests/test_generate.py`
```python
import pytest

@pytest.mark.asyncio
async def test_returns_four_variations(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is the chain rule?"})
    assert res.status_code == 200
    assert len(res.json()["variations"]) == 4

@pytest.mark.asyncio
async def test_variation_labels(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is the chain rule?"})
    labels = [v["label"] for v in res.json()["variations"]]
    assert labels == ["A", "B", "C", "D"]

@pytest.mark.asyncio
async def test_variation_techniques(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is the chain rule?"})
    techniques = [v["technique"] for v in res.json()["variations"]]
    assert techniques == ["role-based", "few-shot", "instruction-rewording", "output-formatting"]

@pytest.mark.asyncio
async def test_variation_a_text(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is integration?"})
    text = res.json()["variations"][0]["text"]
    assert text == "You are an expert mathematics tutor. What is integration?"

@pytest.mark.asyncio
async def test_variation_b_contains_few_shot_examples(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is integration?"})
    text = res.json()["variations"][1]["text"]
    assert "Q: What is a derivative?" in text
    assert "Q: What is an integral?" in text
    assert text.endswith("Q: What is integration?\nA:")

@pytest.mark.asyncio
async def test_variation_c_text(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is integration?"})
    text = res.json()["variations"][2]["text"]
    assert text == "What is integration? Explain step by step, using simple language."

@pytest.mark.asyncio
async def test_variation_d_text(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is integration?"})
    text = res.json()["variations"][3]["text"]
    assert text == "What is integration? Respond using bullet points and a final summary sentence."

@pytest.mark.asyncio
async def test_empty_prompt_returns_400(client):
    res = await client.post("/generate-variations", json={"base_prompt": ""})
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_missing_base_prompt_field_returns_422(client):
    res = await client.post("/generate-variations", json={})
    assert res.status_code == 422
```

### `tests/test_responses.py`
```python
import pytest
from conftest import MOCK_RESPONSE_TEXT, MOCK_TOKEN_USAGE

SAMPLE_VARIATIONS = [
    {"label": "A", "technique": "role-based",            "text": "You are an expert mathematics tutor. What is the chain rule?"},
    {"label": "B", "technique": "few-shot",              "text": "Q: What is a derivative?\nA: ...\n\nQ: What is the chain rule?\nA:"},
    {"label": "C", "technique": "instruction-rewording", "text": "What is the chain rule? Explain step by step, using simple language."},
    {"label": "D", "technique": "output-formatting",     "text": "What is the chain rule? Respond using bullet points and a final summary sentence."},
]

@pytest.mark.asyncio
async def test_returns_four_responses(client, mock_openai):
    res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    assert res.status_code == 200
    assert len(res.json()["responses"]) == 4

@pytest.mark.asyncio
async def test_response_labels_match_input(client, mock_openai):
    res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    labels = [r["label"] for r in res.json()["responses"]]
    assert labels == ["A", "B", "C", "D"]

@pytest.mark.asyncio
async def test_response_text_is_populated(client, mock_openai):
    res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    for r in res.json()["responses"]:
        assert r["response"] == MOCK_RESPONSE_TEXT

@pytest.mark.asyncio
async def test_cached_is_false_in_phase_0(client, mock_openai):
    res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    for r in res.json()["responses"]:
        assert r["cached"] is False

@pytest.mark.asyncio
async def test_token_usage_is_returned(client, mock_openai):
    res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    assert res.json()["token_usage"] == MOCK_TOKEN_USAGE * 4

@pytest.mark.asyncio
async def test_openai_failure_returns_503(client):
    from unittest.mock import AsyncMock, patch
    from openai_client import OpenAIClientError
    with patch("openai_client.get_completion", new=AsyncMock(side_effect=OpenAIClientError("API down"))):
        res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    assert res.status_code == 503
    assert "unreachable" in res.json()["detail"].lower()
```

The source spec is authoritative.
