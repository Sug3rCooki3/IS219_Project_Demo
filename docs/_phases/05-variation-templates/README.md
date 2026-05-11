# Phase 05 — Variation Templates

> Source spec: [../../_specs/05-variation-templates.md](../../_specs/05-variation-templates.md)

Use this phase to implement the exact prompt-variation logic and scoring rubric prompt.

## Focus
- Variation A: role-based
- Variation B: few-shot
- Variation C: instruction rewording
- Variation D: output formatting
- `build_variations(base_prompt)`
- Auto-score rubric construction
- `max_tokens` settings

## Required Variations
- [x] Variation A: `"You are an expert mathematics tutor. " + base_prompt`
- [x] Variation B uses 2 fixed hardcoded math Q&A examples, then opens a new Q for the LLM. Exact text:
  ```
  "Q: What is a derivative?\nA: A derivative measures the rate of change of a function at a given point.\n\nQ: What is an integral?\nA: An integral calculates the area under a curve over an interval.\n\nQ: " + base_prompt + "\nA:"
  ```
- [x] Variation C: `base_prompt + " Explain step by step, using simple language."`
- [x] Variation D: `base_prompt + " Respond using bullet points and a final summary sentence."`
- [x] Do not invent additional variation logic
- [x] Do not change the two hardcoded few-shot examples

## `build_variations()` Contract
- [x] Function signature: `build_variations(base_prompt: str) -> list[dict]`
- [x] Return 4 dicts only
- [x] Each dict contains `label`, `technique`, `text`
- [x] Labels are `A`, `B`, `C`, `D`
- [x] Techniques are `role-based`, `few-shot`, `instruction-rewording`, `output-formatting`

**Exact implementation (`backend/variations.py`):**
```python
def build_variations(base_prompt: str) -> list[dict]:
    return [
        {
            "label": "A",
            "technique": "role-based",
            "text": f"You are an expert mathematics tutor. {base_prompt}",
        },
        {
            "label": "B",
            "technique": "few-shot",
            "text": (
                "Q: What is a derivative?\n"
                "A: A derivative measures the rate of change of a function at a given point.\n\n"
                "Q: What is an integral?\n"
                "A: An integral calculates the area under a curve over an interval.\n\n"
                f"Q: {base_prompt}\nA:"
            ),
        },
        {
            "label": "C",
            "technique": "instruction-rewording",
            "text": f"{base_prompt} Explain step by step, using simple language.",
        },
        {
            "label": "D",
            "technique": "output-formatting",
            "text": f"{base_prompt} Respond using bullet points and a final summary sentence.",
        },
    ]
```

## Auto-score Rubric Rules
- [x] Build the rubric prompt from plain strings — exact wording implemented in `routers/scoring.py`
- [x] Do not make the whole block one f-string
- [x] Only append `response_text` at the end with string concatenation (`+`)
- [x] Response format demanded from the model is exact JSON with `clarity`, `relevance`, `completeness`

## Token Limits
- [x] Use `max_tokens=300` for normal variation responses
- [x] Use `max_tokens=100` for auto-score calls

## Tests for this Phase

`test_generate.py` (created in Phase 04) validates all variation text, labels, and techniques. Re-run it after implementing `variations.py` to confirm correctness.

**Run command:**
```bash
pytest tests/test_generate.py -v
```

> **Status:** ✅ 9/9 tests passing

Expected: 9 tests passing. Key assertions:
- Variation A text starts with `"You are an expert mathematics tutor. "`
- Variation B ends with `"Q: <prompt>\nA:"`  and contains both hardcoded Q&A examples
- Variation C ends with `" Explain step by step, using simple language."`
- Variation D ends with `" Respond using bullet points and a final summary sentence."`

The source spec is authoritative.
