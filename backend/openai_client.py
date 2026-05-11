import os

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()


class OpenAIClientError(Exception):
    pass


async def get_completion(prompt: str, max_tokens: int = 1500) -> tuple[str, int]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIClientError("Missing OPENAI_API_KEY")

    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=max_tokens,
        )
    except Exception as exc:
        raise OpenAIClientError(str(exc)) from exc

    text = getattr(response, "output_text", "") or ""
    usage = getattr(response, "usage", None)
    total_tokens = getattr(usage, "total_tokens", 0) if usage else 0
    return text, total_tokens


async def get_completion_stream(prompt: str, max_tokens: int = 1500):
    """Async generator that yields text chunks from OpenAI streaming."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIClientError("Missing OPENAI_API_KEY")

    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=max_tokens,
            stream=True,
        )
        async for event in response:
            if event.type == "response.output_text.delta":
                yield event.delta
    except Exception as exc:
        raise OpenAIClientError(str(exc)) from exc
