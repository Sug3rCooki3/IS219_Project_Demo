# Phase 07 — Test Cases

> Source spec: [../../_specs/07-test-cases.md](../../_specs/07-test-cases.md)

Use this phase to add the test suite and fixtures.

## Focus
- `tests/conftest.py`
- `test_generate.py`
- `test_responses.py`
- `test_results.py`
- `test_history.py`
- `test_scoring.py` (Phase 1)
- `test_export.py` (Phase 1)

## Test Run Rules
- [ ] Run all tests from the project root
- [ ] Phase 0 command: `pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v`
- [ ] Full suite (Phase 1+): `pytest tests/ -v`
- [ ] Do not run `test_scoring.py` or `test_export.py` until Phase 1 exists

## Required Fixtures

### `tests/conftest.py`
- [ ] Adds `backend/` to `sys.path` at the top (before any backend imports)
- [ ] Uses an autouse temp SQLite DB per test — `monkeypatch.setattr(database, "DB_PATH", ...)` then `database.init_db()`
- [ ] Provides async `httpx.AsyncClient` with `ASGITransport` as a `@pytest_asyncio.fixture`
- [ ] Provides `mock_openai` fixture returning fixed `(response_text, token_usage)` via `AsyncMock`
- [ ] Exports module-level constants `MOCK_RESPONSE_TEXT` and `MOCK_TOKEN_USAGE` — `test_responses.py` imports these from `conftest`
- [ ] Routers must `import openai_client` as a module (not `from openai_client import get_completion`) so `patch("openai_client.get_completion", ...)` intercepts correctly

**Exact implementation (`tests/conftest.py`):**
```python
import sys
import os
import pytest
import pytest_asyncio
import httpx
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
import database

@pytest.fixture(autouse=True)
def use_test_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(database, "DB_PATH", test_db)
    database.init_db()
    yield

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as c:
        yield c

MOCK_RESPONSE_TEXT = "The chain rule states that d/dx[f(g(x))] = f'(g(x)) * g'(x)."
MOCK_TOKEN_USAGE = 42

@pytest.fixture
def mock_openai():
    with patch(
        "openai_client.get_completion",
        new=AsyncMock(return_value=(MOCK_RESPONSE_TEXT, MOCK_TOKEN_USAGE))
    ) as mock:
        yield mock
```

## Required Test Files
- [ ] `test_generate.py` covers 4 generated variations, correct labels/techniques/text, empty prompt `400`, missing field `422`
- [ ] `test_responses.py` covers 4 responses, labels preserved, response text populated, `cached=false`, token usage total, OpenAI failure `503`
  - Imports `MOCK_RESPONSE_TEXT` and `MOCK_TOKEN_USAGE` from `conftest`
  - OpenAI failure test uses `OpenAIClientError` — `openai_client.py` must define this custom exception class
- [ ] `test_results.py` covers `201`, DB persistence, null manual score allowed, wrong variation count `400`, unique session IDs
  - Defines and exports `SAMPLE_SESSION` at module level — imported by `test_history.py` and `test_export.py`
- [ ] `test_history.py` covers empty history, saved history, newest-first ordering, variations included, token usage included
  - Imports `SAMPLE_SESSION` from `test_results`
- [ ] `test_scoring.py` (Phase 1) covers valid scores, malformed JSON -> nulls, and score range 1-5
- [ ] `test_export.py` (Phase 1) covers highest scorer, combined score math, invalid session `404`, tie -> Variation A
  - Imports `SAMPLE_SESSION` from `test_results`

## Async Test Rules
- [ ] `pytest-asyncio` is required
- [ ] `pytest.ini` uses `asyncio_mode = auto`
- [ ] `@pytest.mark.asyncio` decorators may remain for readability but are technically redundant

The source spec is authoritative.
