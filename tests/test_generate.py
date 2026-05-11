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
    assert res.status_code == 422
