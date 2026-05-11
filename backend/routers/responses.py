from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import openai_client


router = APIRouter()


class VariationPayload(BaseModel):
    label: str
    technique: str
    text: str


class ResponsesRequest(BaseModel):
    variations: list[VariationPayload]


@router.post("/get-responses")
async def get_responses(payload: ResponsesRequest):
    responses = []
    token_usage = 0

    try:
        for variation in payload.variations:
            response_text, tokens_used = await openai_client.get_completion(variation.text)
            responses.append(
                {
                    "label": variation.label,
                    "response": response_text,
                    "cached": False,
                }
            )
            token_usage += tokens_used
    except openai_client.OpenAIClientError:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API is unreachable. Please try again.",
        )

    return {"responses": responses, "token_usage": token_usage}
