import pytest


SAMPLE_SESSION = {
    "base_prompt": "What is the chain rule?",
    "token_usage": 168,
    "variations": [
        {
            "label": "A",
            "technique": "role-based",
            "variation_text": "You are an expert mathematics tutor. What is the chain rule?",
            "response_text": "The chain rule states that...",
            "response_cached": False,
            "manual_score": 4,
            "auto_clarity": None,
            "auto_relevance": None,
            "auto_completeness": None,
        },
        {
            "label": "B",
            "technique": "few-shot",
            "variation_text": "Q: ...\nA:",
            "response_text": "...",
            "response_cached": False,
            "manual_score": 3,
            "auto_clarity": None,
            "auto_relevance": None,
            "auto_completeness": None,
        },
        {
            "label": "C",
            "technique": "instruction-rewording",
            "variation_text": "...",
            "response_text": "...",
            "response_cached": False,
            "manual_score": None,
            "auto_clarity": None,
            "auto_relevance": None,
            "auto_completeness": None,
        },
        {
            "label": "D",
            "technique": "output-formatting",
            "variation_text": "...",
            "response_text": "...",
            "response_cached": False,
            "manual_score": 5,
            "auto_clarity": None,
            "auto_relevance": None,
            "auto_completeness": None,
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
