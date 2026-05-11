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
