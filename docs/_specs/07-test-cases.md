# Test Cases

Complete test code for every file in `tests/`. Run all tests from the project root with:
```bash
pytest tests/ -v
```

Phase 1 test files (`test_scoring.py`, `test_export.py`) are included but marked — do not run them until Phase 1 is built.

---

## `tests/conftest.py`

Sets up the test app, a temporary in-memory database, and mocks the OpenAI client so no real API calls are made during tests.

```python
import sys
import os
import pytest
import pytest_asyncio
import httpx
from unittest.mock import AsyncMock, patch

# Add backend/ to the import path so tests can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
import database

# --- Test database setup ---

@pytest.fixture(autouse=True)
def use_test_db(tmp_path, monkeypatch):
    """
    Replace the real database with a temp file for every test.
    Automatically applied to every test (autouse=True).
    """
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.init_db()
    yield

# --- Shared async HTTP client ---

@pytest_asyncio.fixture
async def client():
    """
    Async HTTP client that talks directly to the FastAPI app (no real network).
    """
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c

# --- Mock OpenAI response ---

MOCK_RESPONSE_TEXT = "The chain rule states that d/dx[f(g(x))] = f'(g(x)) * g'(x)."
MOCK_TOKEN_USAGE = 42

@pytest.fixture
def mock_openai():
    """
    Patches openai_client.get_completion to return a fixed response without calling the API.
    Use this fixture in any test that triggers a /get-responses call.

    IMPORTANT: This patch only works if the router imports the module, not the function.
    Routers must use:
        import openai_client
        result = await openai_client.get_completion(prompt)
    NOT:
        from openai_client import get_completion  # patch won't intercept this
    """
    with patch(
        "openai_client.get_completion",
        new=AsyncMock(return_value=(MOCK_RESPONSE_TEXT, MOCK_TOKEN_USAGE))
    ) as mock:
        yield mock
```

---

## `tests/test_generate.py`

Tests for `POST /generate-variations`.

```python
import pytest

@pytest.mark.asyncio
async def test_returns_four_variations(client):
    res = await client.post("/generate-variations", json={"base_prompt": "What is the chain rule?"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["variations"]) == 4

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
    assert res.status_code == 422  # FastAPI validation error
```

---

## `tests/test_responses.py`

Tests for `POST /get-responses`.

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
    # token_usage = MOCK_TOKEN_USAGE (42) * 4 calls = 168
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

---

## `tests/test_results.py`

Tests for `POST /save-results`.

```python
import pytest

SAMPLE_SESSION = {
    "base_prompt": "What is the chain rule?",
    "token_usage": 168,
    "variations": [
        {
            "label": "A", "technique": "role-based",
            "variation_text": "You are an expert mathematics tutor. What is the chain rule?",
            "response_text": "The chain rule states that...",
            "response_cached": False,
            "manual_score": 4,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
        {
            "label": "B", "technique": "few-shot",
            "variation_text": "Q: ...\nA:", "response_text": "...",
            "response_cached": False, "manual_score": 3,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
        {
            "label": "C", "technique": "instruction-rewording",
            "variation_text": "...", "response_text": "...",
            "response_cached": False, "manual_score": None,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
        {
            "label": "D", "technique": "output-formatting",
            "variation_text": "...", "response_text": "...",
            "response_cached": False, "manual_score": 5,
            "auto_clarity": None, "auto_relevance": None, "auto_completeness": None,
        },
    ],
}

@pytest.mark.asyncio
async def test_save_returns_201_and_session_id(client):
    res = await client.post("/save-results", json=SAMPLE_SESSION)
    assert res.status_code == 201
    assert "session_id" in res.json()
    assert isinstance(res.json()["session_id"], int)

@pytest.mark.asyncio
async def test_save_persists_to_database(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    history_res = await client.get("/history")
    assert len(history_res.json()["sessions"]) == 1

@pytest.mark.asyncio
async def test_manual_score_null_is_accepted(client):
    # Variation C has manual_score: None — should not fail
    res = await client.post("/save-results", json=SAMPLE_SESSION)
    assert res.status_code == 201

@pytest.mark.asyncio
async def test_wrong_number_of_variations_returns_400(client):
    bad_session = {**SAMPLE_SESSION, "variations": SAMPLE_SESSION["variations"][:2]}
    res = await client.post("/save-results", json=bad_session)
    assert res.status_code == 400
    assert "4" in res.json()["detail"]

@pytest.mark.asyncio
async def test_session_ids_are_unique(client):
    res1 = await client.post("/save-results", json=SAMPLE_SESSION)
    res2 = await client.post("/save-results", json=SAMPLE_SESSION)
    assert res1.json()["session_id"] != res2.json()["session_id"]
```

---

## `tests/test_history.py`

Tests for `GET /history`.

```python
import pytest
from test_results import SAMPLE_SESSION

@pytest.mark.asyncio
async def test_empty_history_returns_empty_list(client):
    res = await client.get("/history")
    assert res.status_code == 200
    assert res.json() == {"sessions": []}

@pytest.mark.asyncio
async def test_history_returns_saved_session(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    res = await client.get("/history")
    sessions = res.json()["sessions"]
    assert len(sessions) == 1
    assert sessions[0]["base_prompt"] == "What is the chain rule?"

@pytest.mark.asyncio
async def test_history_returns_newest_first(client):
    session_a = {**SAMPLE_SESSION, "base_prompt": "First prompt"}
    session_b = {**SAMPLE_SESSION, "base_prompt": "Second prompt"}
    await client.post("/save-results", json=session_a)
    await client.post("/save-results", json=session_b)
    res = await client.get("/history")
    sessions = res.json()["sessions"]
    assert sessions[0]["base_prompt"] == "Second prompt"
    assert sessions[1]["base_prompt"] == "First prompt"

@pytest.mark.asyncio
async def test_history_session_includes_variations(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    res = await client.get("/history")
    session = res.json()["sessions"][0]
    assert "variations" in session
    assert len(session["variations"]) == 4

@pytest.mark.asyncio
async def test_history_session_includes_token_usage(client):
    await client.post("/save-results", json=SAMPLE_SESSION)
    res = await client.get("/history")
    session = res.json()["sessions"][0]
    assert session["token_usage"] == 168
```

---

## `tests/test_scoring.py` (Phase 1)

Tests for `POST /auto-score`. Do not run until Phase 1 is implemented.

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_auto_score_returns_three_subscores(client):
    mock_json = '{"clarity": 4, "relevance": 5, "completeness": 3}'
    with patch("openai_client.get_completion", new=AsyncMock(return_value=(mock_json, 10))):
        res = await client.post("/auto-score", json={
            "label": "A",
            "response_text": "The chain rule states that..."
        })
    assert res.status_code == 200
    data = res.json()
    assert data["clarity"] == 4
    assert data["relevance"] == 5
    assert data["completeness"] == 3
    assert data["label"] == "A"

@pytest.mark.asyncio
async def test_auto_score_malformed_json_returns_nulls(client):
    with patch("openai_client.get_completion", new=AsyncMock(return_value=("not valid json", 10))):
        res = await client.post("/auto-score", json={
            "label": "B",
            "response_text": "Some response"
        })
    assert res.status_code == 200
    data = res.json()
    assert data["clarity"] is None
    assert data["relevance"] is None
    assert data["completeness"] is None
    assert data["error"] == "Score unavailable"

@pytest.mark.asyncio
async def test_auto_score_scores_within_valid_range(client):
    mock_json = '{"clarity": 5, "relevance": 5, "completeness": 5}'
    with patch("openai_client.get_completion", new=AsyncMock(return_value=(mock_json, 10))):
        res = await client.post("/auto-score", json={"label": "C", "response_text": "..."})
    data = res.json()
    for key in ("clarity", "relevance", "completeness"):
        assert 1 <= data[key] <= 5
```

---

## `tests/test_export.py` (Phase 1)

Tests for `GET /export-best`. Do not run until Phase 1 is implemented.

```python
import pytest
from test_results import SAMPLE_SESSION

SCORED_SESSION = {
    **SAMPLE_SESSION,
    "variations": [
        {**SAMPLE_SESSION["variations"][0], "auto_clarity": 5, "auto_relevance": 4, "auto_completeness": 3},
        {**SAMPLE_SESSION["variations"][1], "auto_clarity": 3, "auto_relevance": 3, "auto_completeness": 3},
        {**SAMPLE_SESSION["variations"][2], "auto_clarity": 4, "auto_relevance": 4, "auto_completeness": 4},
        {**SAMPLE_SESSION["variations"][3], "auto_clarity": 2, "auto_relevance": 2, "auto_completeness": 2},
    ]
}

@pytest.mark.asyncio
async def test_export_best_returns_highest_scoring_variation(client):
    save_res = await client.post("/save-results", json=SCORED_SESSION)
    session_id = save_res.json()["session_id"]
    res = await client.get(f"/export-best?session_id={session_id}")
    assert res.status_code == 200
    # Variation A: (5+4+3)/3 = 4.0, Variation C: (4+4+4)/3 = 4.0 — exact tie, tiebreaker = A
    assert res.json()["best_variation"]["label"] == "A"

@pytest.mark.asyncio
async def test_export_best_combined_score_is_correct(client):
    save_res = await client.post("/save-results", json=SCORED_SESSION)
    session_id = save_res.json()["session_id"]
    res = await client.get(f"/export-best?session_id={session_id}")
    best = res.json()["best_variation"]
    expected = round((best["auto_clarity"] + best["auto_relevance"] + best["auto_completeness"]) / 3, 1)
    assert best["combined_score"] == expected

@pytest.mark.asyncio
async def test_export_best_invalid_session_returns_404(client):
    res = await client.get("/export-best?session_id=9999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

@pytest.mark.asyncio
async def test_export_best_tie_returns_variation_a(client):
    tied_session = {
        **SAMPLE_SESSION,
        "variations": [
            {**SAMPLE_SESSION["variations"][0], "auto_clarity": 4, "auto_relevance": 4, "auto_completeness": 4},
            {**SAMPLE_SESSION["variations"][1], "auto_clarity": 4, "auto_relevance": 4, "auto_completeness": 4},
            {**SAMPLE_SESSION["variations"][2], "auto_clarity": 4, "auto_relevance": 4, "auto_completeness": 4},
            {**SAMPLE_SESSION["variations"][3], "auto_clarity": 4, "auto_relevance": 4, "auto_completeness": 4},
        ]
    }
    save_res = await client.post("/save-results", json=tied_session)
    session_id = save_res.json()["session_id"]
    res = await client.get(f"/export-best?session_id={session_id}")
    assert res.json()["best_variation"]["label"] == "A"
```

---

## Notes for the AI Coder

- Run only Phase 0 tests during Phase 0: `pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v`
- `mock_openai` fixture must be passed to any test that triggers a real LLM call via `/get-responses`
- `autouse=True` on `use_test_db` means every test automatically gets a clean isolated database — do not share state between tests
- If a test imports from another test file (e.g. `test_history.py` imports `SAMPLE_SESSION` from `test_results.py`), that is intentional to avoid duplication
- `pytest-asyncio` is already in `requirements.txt` (see `01-tech-stack.md`). Install with `pip install -r backend/requirements.txt`
- `@pytest.mark.asyncio` decorators on each test are technically redundant because `pytest.ini` sets `asyncio_mode = auto` (which auto-handles all `async def test_*` functions). They are kept for readability but can be omitted.
