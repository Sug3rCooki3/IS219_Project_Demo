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
- [ ] Variation A: `"You are an expert mathematics tutor. " + base_prompt`
- [ ] Variation B uses 2 fixed hardcoded math Q&A examples, then opens a new Q for the LLM. Exact text:
  ```
  "Q: What is a derivative?\nA: A derivative measures the rate of change of a function at a given point.\n\nQ: What is an integral?\nA: An integral calculates the area under a curve over an interval.\n\nQ: " + base_prompt + "\nA:"
  ```
- [ ] Variation C: `base_prompt + " Explain step by step, using simple language."`
- [ ] Variation D: `base_prompt + " Respond using bullet points and a final summary sentence."`
- [ ] Do not invent additional variation logic
- [ ] Do not change the two hardcoded few-shot examples

## `build_variations()` Contract
- [ ] Function signature: `build_variations(base_prompt: str) -> list[dict]`
- [ ] Return 4 dicts only
- [ ] Each dict contains `label`, `technique`, `text`
- [ ] Labels are `A`, `B`, `C`, `D`
- [ ] Techniques are `role-based`, `few-shot`, `instruction-rewording`, `output-formatting`

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
- [ ] Build the rubric prompt from plain strings — exact wording:
  ```python
  rubric = (
      "Rate the following response on three criteria, each from 1 to 5:\n"
      "1. Clarity – Is it easy to understand?\n"
      "2. Relevance – Does it directly answer the question?\n"
      "3. Completeness – Is the answer thorough?\n\n"
      "Respond in this exact JSON format:\n"
      '{"clarity": <1-5>, "relevance": <1-5>, "completeness": <1-5>}\n\n'
      "Response to evaluate:\n"
      '"' + response_text + '"'
  )
  ```
- [ ] Do not make the whole block one f-string
- [ ] Only append `response_text` at the end with string concatenation (`+`)
- [ ] Response format demanded from the model is exact JSON with `clarity`, `relevance`, `completeness`

## Token Limits
- [ ] Use `max_tokens=300` for normal variation responses
- [ ] Use `max_tokens=100` for auto-score calls

## Tests for this Phase

`test_generate.py` (created in Phase 04) validates all variation text, labels, and techniques. Re-run it after implementing `variations.py` to confirm correctness.

**Run command:**
```bash
pytest tests/test_generate.py -v
```

Expected: 9 tests passing. Key assertions:
- Variation A text starts with `"You are an expert mathematics tutor. "`
- Variation B ends with `"Q: <prompt>\nA:"`  and contains both hardcoded Q&A examples
- Variation C ends with `" Explain step by step, using simple language."`
- Variation D ends with `" Respond using bullet points and a final summary sentence."`

The source spec is authoritative.
