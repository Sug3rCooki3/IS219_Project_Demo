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