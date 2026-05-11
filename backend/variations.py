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
