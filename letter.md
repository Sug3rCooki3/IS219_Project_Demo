# AI Prompt Engineering Tool – Development Instructions

## Objective

Design and implement a lightweight **AI Prompt Testing and Optimization Tool**. The purpose of this system is to demonstrate practical prompt engineering skills, including prompt design, evaluation, and iteration. The demo domain for all example prompts should be **mathematics** (e.g., explaining calculus concepts, solving algebra problems, describing proof techniques), tying the project directly to the IS219 Mathematics course context. The final product should be suitable for inclusion in a professional portfolio targeting entry-level AI or prompt engineering roles.

---

## System Overview

The application should allow a user to:

* Input a base prompt
* Automatically generate multiple prompt variations
* Send each variation to an LLM (e.g., OpenAI API)
* Display and compare responses
* Rate or score outputs based on quality
* Save the best-performing prompt

The system should emphasize **prompt experimentation and evaluation**, not complex backend engineering.

---

## Core Requirements

### 1. LLM Integration

* Use OpenAI API (or equivalent)
* Send multiple prompt variations per request
* Ensure consistent formatting of responses

---

### 2. Prompt Variation Engine

Generate variations using **hardcoded template wrappers** applied to the user's base prompt. Each template transforms the base prompt in a well-defined way:

| Variation | Technique | How it works |
|---|---|---|
| A | Role-based | Prepends `"You are an expert mathematics tutor. "` to the base prompt |
| B | Few-shot | Wraps the base prompt with 2 hardcoded math Q&A examples before asking the question. Use these fixed examples: **Q: "What is a derivative?" A: "A derivative measures the rate of change of a function at a given point."** and **Q: "What is an integral?" A: "An integral calculates the area under a curve over an interval."** |
| C | Instruction rewording | Appends `"Explain step by step, using simple language."` to the base prompt |
| D | Output formatting | Appends `"Respond using bullet points and a final summary sentence."` to the base prompt |

Templates are stored as static strings in the backend. No LLM is used to generate the variations themselves — only to respond to them. Each variation must display its technique label in the UI.

---

### 3. Response Comparison Interface

Display outputs side-by-side:

* Prompt A (Role-based) → Response
* Prompt B (Few-shot) → Response
* Prompt C (Instruction rewording) → Response
* Prompt D (Output formatting) → Response

Ensure readability and clear separation between responses. Each card must show the variation label and technique name.

---

### 4. Evaluation System

Implement a two-layer scoring system:

**Manual scoring:**
* User rates each response on a 1–5 scale
* Rating is stored alongside the prompt, variation type, and response text

**Auto-scoring:**
Send each response to the LLM with the following rubric prompt:

```
Rate the following response on three criteria, each from 1 to 5:
1. Clarity – Is it easy to understand?
2. Relevance – Does it directly answer the question?
3. Completeness – Is the answer thorough?

Respond in this exact JSON format:
{"clarity": <1-5>, "relevance": <1-5>, "completeness": <1-5>}

Response to evaluate:
"<insert response here>"
```

Parse the JSON and store the three sub-scores. Display the average auto-score next to the manual score for each variation. Auto-scoring is triggered automatically after responses are received.

---

### 5. Data Storage

* Store:

  * prompts
  * variations (label + technique name)
  * responses
  * manual scores (1–5 integer per variation)
  * auto-scores (three integers: clarity, relevance, completeness — stored separately, not as an average)
  * token usage count per session
* Use a simple database (SQLite or JSON file)

---

### 6. Basic Frontend

* Simple UI (React or basic HTML/JS)
* Features:

  * input field for prompt
  * button to generate variations
  * response display section with variation label shown for each response
  * manual rating controls (1–5 stars or buttons) per response
  * auto-score display (clarity / relevance / completeness) per response
  * **Prompt History panel** – a sidebar or collapsible section listing all previous prompts; clicking one reloads its variations, responses, and scores
  * **Export Best Prompt button** – highlights the variation with the highest combined score. The explanation is **computed in the frontend** (no extra LLM call): find which of clarity, relevance, or completeness had the highest sub-score for the winning variation and display: `"Variation X scored highest — strongest in [sub-score name]."`
  * estimated token usage counter displayed after each run

---

### 7. Backend (Lightweight)

* Node.js or Python
* Minimal API endpoints:

  * `/generate-variations` – accepts a base prompt string, returns the 4 filled variation strings
  * `/get-responses` – accepts the 4 variation strings, calls the LLM for each, returns responses + token usage; checks cache first before calling the API
  * `/auto-score` – accepts a response string, sends the rubric prompt to the LLM, returns parsed `{clarity, relevance, completeness}`; called once per variation after `/get-responses`
  * `/save-results` – accepts a full session object (prompt, variations, responses, manual scores, auto-scores, token usage) and persists it
  * `/history` – returns all past prompt sessions
  * `/export-best` – returns the highest-scoring prompt and response from the most recent session

**API Key Security:**
* The OpenAI API key must be stored in a `.env` file and loaded via `dotenv` (or equivalent)
* The `.env` file must be listed in `.gitignore` — it must never be committed to the repository
* The frontend must never receive or display the API key
* All LLM calls are made server-side only

**Cost Control:**
* Limit variations to a maximum of 4 per request
* Set `max_tokens` to 300 per LLM call to cap response length
* Cache responses by prompt hash in the local database — if the same prompt+variation has been run before, return the stored response instead of making a new API call
* Display an estimated token usage count in the UI after each run

---

### 8. Testing

#### Functional Tests:

* Prompt variations generate correctly for all 4 templates (A–D)
* Responses return from API for each variation
* Auto-scoring returns valid `{clarity, relevance, completeness}` JSON for each response
* Manual ratings are saved correctly
* Cache returns stored response on repeated identical prompt+variation
* `/history` returns all past sessions in correct format
* `/export-best` returns the variation with the highest combined auto-score

#### Edge Cases:

* Empty prompt input — return a validation error before calling the API
* API failure (LLM unreachable) — return a user-facing error message, do not crash
* Duplicate prompts — serve response from cache, do not make a new API call
* Auto-scorer returns malformed or non-JSON output — catch the parse error, store `null` for sub-scores, and display "Score unavailable" in the UI
* All variations tie on score — `/export-best` returns the first one (Variation A) as the tiebreaker

---

### 9. Project Structure

* `/frontend` – UI components
* `/backend` – API + logic
* `/data` – stored results (SQLite file or JSON)
* `/tests` – all functional and edge-case tests
* `/docs` – brief documentation

---

### 10. Documentation

The README is fully specified in the **Deliverables** section below. Do not duplicate content here — follow the Deliverables README spec exactly.

---

## Success Criteria

The project must demonstrate:

* Ability to design effective prompts
* Understanding of prompt variation techniques (role-based, few-shot, rewording, formatting)
* Experience evaluating AI-generated outputs using both manual and automated rubric scoring
* Basic integration with an LLM API
* Responsible API key handling and basic cost awareness
* A domain-specific use case (mathematics) that gives the project a concrete identity

---

## Constraints

* Keep the system simple and clean
* Do NOT overcomplicate with advanced AI pipelines
* Focus on usability and clarity

---

## Deliverables

1. Functional application
2. GitHub repository (with `.env` in `.gitignore` and a `.env.example` file showing required variables)
3. README with:
   * Project description and math domain context
   * Features list
   * Tech stack
   * Setup instructions including how to configure the API key
   * Screenshots of the comparison view, scoring, and history panel
   * At least two example math prompt tests with their variation outputs and scores

---

End of Instructions
