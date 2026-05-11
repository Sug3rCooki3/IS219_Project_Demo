from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

import database


router = APIRouter()


class VariationResult(BaseModel):
    label: str
    technique: str
    variation_text: str
    response_text: str
    response_cached: bool
    manual_score: int | None
    auto_clarity: int | None
    auto_relevance: int | None
    auto_completeness: int | None


class SaveResultsRequest(BaseModel):
    base_prompt: str
    token_usage: int | None
    variations: list[VariationResult]


@router.post("/save-results", status_code=201)
async def save_results(payload: SaveResultsRequest, response: Response):
    if len(payload.variations) != 4:
        raise HTTPException(status_code=400, detail="variations array must contain exactly 4 items.")

    session_id = database.save_session(payload.model_dump())
    response.status_code = 201
    return {"session_id": session_id}
