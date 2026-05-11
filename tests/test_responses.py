import pytest
from conftest import MOCK_RESPONSE_TEXT, MOCK_TOKEN_USAGE


SAMPLE_VARIATIONS = [
    {"label": "A", "technique": "role-based", "text": "You are an expert mathematics tutor. What is the chain rule?"},
    {"label": "B", "technique": "few-shot", "text": "Q: What is a derivative?\nA: ...\n\nQ: What is the chain rule?\nA:"},
    {"label": "C", "technique": "instruction-rewording", "text": "What is the chain rule? Explain step by step, using simple language."},
    {"label": "D", "technique": "output-formatting", "text": "What is the chain rule? Respond using bullet points and a final summary sentence."},
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
    for response in res.json()["responses"]:
        assert response["response"] == MOCK_RESPONSE_TEXT


@pytest.mark.asyncio
async def test_cached_is_false_in_phase_0(client, mock_openai):
    res = await client.post("/get-responses", json={"variations": SAMPLE_VARIATIONS})
    for response in res.json()["responses"]:
        assert response["cached"] is False


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
