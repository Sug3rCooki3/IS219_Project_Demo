# AI Prompt Engineering Tool

Phase 0 MVP for comparing hardcoded prompt variations against OpenAI responses.

## Run

Backend:

```bash
cd backend && uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd frontend && npm install && npm run dev
```

Tests:

```bash
pytest tests/test_generate.py tests/test_responses.py tests/test_results.py tests/test_history.py -v
```
