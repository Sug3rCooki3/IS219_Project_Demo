import os
import sys
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import pytest_asyncio


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import database
from main import app


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
        base_url="http://test",
    ) as c:
        yield c


MOCK_RESPONSE_TEXT = "The chain rule states that d/dx[f(g(x))] = f'(g(x)) * g'(x)."
MOCK_TOKEN_USAGE = 42


@pytest.fixture
def mock_openai():
    with patch(
        "openai_client.get_completion",
        new=AsyncMock(return_value=(MOCK_RESPONSE_TEXT, MOCK_TOKEN_USAGE)),
    ) as mock:
        yield mock
