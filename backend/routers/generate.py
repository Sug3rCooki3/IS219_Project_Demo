from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from variations import build_variations


router = APIRouter()


class GenerateRequest(BaseModel):
    base_prompt: str


@router.post("/generate-variations")
async def generate_variations(payload: GenerateRequest):
    if not payload.base_prompt.strip():
        raise HTTPException(status_code=400, detail="base_prompt cannot be empty.")
    return {"variations": build_variations(payload.base_prompt)}
