# Task 1 — AI-Powered Client Brief → Dev-Ready Tasks / Jira Tickets

A small tool that turns a raw client brief into:

1. a structured task breakdown (Epics → Stories/Tasks),
2. Jira-style developer tickets (on screen + JSON/CSV export),
3. a list of open questions for the client.

**Golden rule: the tool never assumes.** If the brief does not say something,
the field says `Not specified` and the gap becomes an open question.

## Libraries used

| Library | Why |
|---|---|
| Python 3 | language |
| `groq` | calls the LLM (model `openai/gpt-oss-120b`, JSON mode, temperature 0) |
| `python-dotenv` | loads the API key from `.env` |
| `streamlit` | web UI (paste box, tabs, download buttons) |
| `pandas` | tables in the UI |
| standard library (`re`, `json`, `csv`, `unicodedata`) | Stages 0, 4, 5 and exports |

No login or user accounts.

## How to run

```powershell
cd hackathon-2026\task1-brief-to-tickets
..\backend\venv\Scripts\Activate.ps1          # or your own venv
pip install groq python-dotenv streamlit pandas
```

Put the key in `hackathon-2026\.env` (never in code or chats):

```
GROQ_API_KEY=your_key_here
```

| Command | What it does |
|---|---|
| `streamlit run app.py` | opens the web tool in the browser |
| `python run_demo.py` | runs both demo briefs and saves all outputs |
| `python run_demo.py vague` | runs only the vague brief |
| `python pipeline.py briefs\vague_brief.txt` | runs one brief from the command line |
| `python tests\offline_check.py` | tests the Python stages without an API key |

## How it works

| Stage | Done by | Input → Output |
|---|---|---|
| 0 Prepare | Python | brief → numbered sentences `S1, S2, …` |
| 1 Extract | AI | numbered brief → goals, users, features, constraints, quality requirements, integrations, deadlines, priorities, estimates, terms — each with an exact `quote` and `ref` |
| 2 Detect gaps | AI + Python | brief + facts → open questions (missing, vague, contradiction, undefined term, scope gap). Python gives IDs `Q-001…` and removes any `(e.g. …)` suggestions |
| 3 Break down | AI + Python | facts + questions + numbered work-item list (`F1…`, `I1…`, `R1…`) → epics and tasks. Python checks every work item is covered; if not, it sends the missed items back to the AI once for repair |
| 4 Build tickets | Python | plan → tickets `TASK-001…` with all required fields, dependencies, linked questions, status |
| 5 Verify | Python | checks everything against the brief (below) |
| 6 Output | Streamlit | breakdown, tickets, questions on screen + JSON / CSV / Markdown downloads |

Each AI stage has its own prompt in `prompts.py` with a role, only the context
that stage needs, its rules and an exact JSON output format.

## How it avoids assumptions

- **Prompt rules (Stages 1–3):** extract only what is written, quote it word
  for word, write nothing for silent categories, never choose a side in a
  contradiction, never suggest providers, numbers or options in questions,
  never invent acceptance criteria (empty list instead).
- **Python owns everything that must not be invented (Stage 4):** ticket IDs,
  links, `Not specified` for priority / estimate / deadline unless the brief
  states them (with their quote), and the status:
  - **Ready for development** = no open questions and at least one testable
    acceptance criterion from the brief;
  - **Needs clarification** = otherwise (the reason is shown).
- **Python rejects unstated values (Stage 4):** a priority, deadline or
  estimate from the AI is kept only if Stage 1 extracted it as that kind of
  fact from the same sentence; a deadline must also name a real date
  ("soon" is rejected). Acceptance criteria must be in the brief's own words:
  a reworded criterion is replaced by its exact quote. Every correction is
  listed on the ticket under *Python corrections*.
- **Python verification (Stage 5)** — the AI is checked, not trusted:
  - every quote must appear in the brief (case-sensitive; only typography such
    as non-breaking hyphens is normalised) and in the sentence it cites;
  - every question must name real features and block at least one ticket;
    project-wide questions (`GENERAL`) block every ticket;
  - every feature, integration and quality requirement must be covered by a task;
  - a dependency is kept only if the AI quotes the sentence that states it and
    the quote is in the brief; otherwise it becomes an open question
    ("Does X depend on Y? The brief does not say.");
  - every sentence of the brief must reach a ticket (or be background such as
    goals or users); sentences that do not are reported for review;
  - constraints used by no task are added to every epic as project constraints;
  - a feature or quality requirement still missing after the repair request
    gets a minimal task built only from the brief's words, marked as created by Python;
  - a question the AI labels GENERAL but that quotes specific task sentences is
    scoped to those tasks (with a note);
  - duplicate questions are reported.
  Failures are shown as **UNVERIFIED** warnings on the ticket and in the
  Verification tab. Nothing is silently corrected.

## Ticket format

`Ticket ID, Title, Type (Epic/Story/Task), Parent, Status, Description,
Acceptance Criteria, Source Reference, Dependencies, Open Questions, Priority,
Estimate, Deadline, Warnings, Python Corrections`

`tickets.csv` can be imported into Jira (map *Title → Summary*, *Type → Issue
Type*, *Description → Description*); `tickets.json` holds the same data.

## Demo evidence

| Brief | Purpose | Output folder |
|---|---|---|
| `briefs/clear_brief.txt` | reasonably clear brief (bakery ordering site) | `outputs/clear_brief/` |
| `briefs/vague_brief.txt` | deliberately vague and contradictory brief (fitness app) | `outputs/vague_brief/` |
| `briefs/vague_brief_planted_issues.txt` | answer key: the problems planted in the vague brief | — |

Each output folder has `report.md` (breakdown + tickets + questions +
verification), `tickets.json`, `tickets.csv`, `open_questions.csv` and
`result_full.json` (every stage's output).

See `review_log.md` for the tests, the errors found and how each was fixed.

## Groq free-tier limits

The free tier allows about 8,000 tokens per minute. The tool keeps every
request under that (compact JSON, capped output) and waits automatically when
the per-minute limit is reached, so a full run can take 1–3 minutes. Very long
briefs give a clear "too large" message. The free tier also has a daily
limit (about 200,000 tokens for `gpt-oss-120b`); when it is reached the run
stops with a clear message. Saved results can be opened in the app (sidebar)
without using tokens. Set `GROQ_MODEL` in `.env` to use a
different model.

## Known limitations

- LLM output varies slightly between runs, even at temperature 0 (e.g. how
  many questions Stage 2 asks). Verification runs on every result for this reason.
- Python checks that a dependency quote is real, not that the quoted sentence
  really implies the link; the quote is shown so a reviewer can judge.
- Duplicate detection only catches identical question text, not reworded duplicates.
- The sentence splitter is simple (splits on `. ! ?`), so abbreviations such as
  "e.g." inside a brief can split a sentence.
