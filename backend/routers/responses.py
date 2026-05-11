import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import openai_client


router = APIRouter()


class VariationPayload(BaseModel):
    label: str
    technique: str
    text: str


class ResponsesRequest(BaseModel):
    variations: list[VariationPayload]


class SingleVariationPayload(BaseModel):
    label: str
    text: str


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


@router.post("/stream-response")
async def stream_response(payload: SingleVariationPayload):
    async def event_gen():
        try:
            async for chunk in openai_client.get_completion_stream(payload.text):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except openai_client.OpenAIClientError as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
