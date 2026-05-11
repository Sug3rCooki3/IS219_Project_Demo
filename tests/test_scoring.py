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
