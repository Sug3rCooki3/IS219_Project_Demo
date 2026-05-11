# Variation Templates

These are the exact 4 template functions that live in `backend/variations.py`. No other variation logic exists — this is the complete implementation spec for that file.

---

## Template Definitions

### Variation A — Role-based
Prepend a mathematician tutor persona.

```
"You are an expert mathematics tutor. " + base_prompt
```

**Example:**
- Input: `"What is the chain rule?"`
- Output: `"You are an expert mathematics tutor. What is the chain rule?"`

---

### Variation B — Few-shot
Wrap the base prompt with 2 fixed math Q&A examples, then open a new Q for the LLM to complete.

```
"Q: What is a derivative?\nA: A derivative measures the rate of change of a function at a given point.\n\nQ: What is an integral?\nA: An integral calculates the area under a curve over an interval.\n\nQ: " + base_prompt + "\nA:"
```

**Example:**
- Input: `"What is the chain rule?"`
- Output:
  ```
  Q: What is a derivative?
  A: A derivative measures the rate of change of a function at a given point.

  Q: What is an integral?
  A: An integral calculates the area under a curve over an interval.

  Q: What is the chain rule?
  A:
  ```

---

### Variation C — Instruction rewording
Append a step-by-step instruction to the base prompt.

```
base_prompt + " Explain step by step, using simple language."
```

**Example:**
- Input: `"What is the chain rule?"`
- Output: `"What is the chain rule? Explain step by step, using simple language."`

---

### Variation D — Output formatting
Append a bullet-point formatting constraint.

```
base_prompt + " Respond using bullet points and a final summary sentence."
```

**Example:**
- Input: `"What is the chain rule?"`
- Output: `"What is the chain rule? Respond using bullet points and a final summary sentence."`

---

## Python Implementation

```python
# backend/variations.py

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

---

## Auto-score Rubric Prompt

Used in `POST /auto-score`. Build this string by concatenating plain strings with the `response_text` variable at the end. Do **not** make the entire block an f-string — only the final line needs interpolation.

Recommended Python construction:
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

`response_text` is the function parameter passed into the scoring handler. Use plain string concatenation (`+`) for the final line — no f-string needed anywhere in this block.

Set `max_tokens=100` for auto-score calls (60 is too tight — some models add whitespace before the JSON). Set `max_tokens=300` for variation response calls.
