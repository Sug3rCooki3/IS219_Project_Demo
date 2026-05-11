import json

import openai_client
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from openai_client import OpenAIClientError
from pydantic import BaseModel

router = APIRouter()


class ScoreRequest(BaseModel):
    label: str
    response_text: str


@router.post("/auto-score")
async def auto_score(body: ScoreRequest):
    rubric = (
        "Rate the following response on three criteria, each from 1 to 5:\n"
        "1. Clarity – Is it easy to understand?\n"
        "2. Relevance – Does it directly answer the question?\n"
        "3. Completeness – Is the answer thorough?\n\n"
        "Respond in this exact JSON format:\n"
        '{"clarity": <1-5>, "relevance": <1-5>, "completeness": <1-5>}\n\n'
        "Response to evaluate:\n"
        '"' + body.response_text + '"'
    )

    try:
        text, _ = await openai_client.get_completion(rubric, max_tokens=100)
    except OpenAIClientError:
        return JSONResponse(
            status_code=503,
            content={"detail": "OpenAI API is unreachable. Please try again."},
        )

    try:
        parsed = json.loads(text)
        return {
            "label": body.label,
            "clarity": parsed["clarity"],
            "relevance": parsed["relevance"],
            "completeness": parsed["completeness"],
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "label": body.label,
            "clarity": None,
            "relevance": None,
            "completeness": None,
            "error": "Score unavailable",
        }
