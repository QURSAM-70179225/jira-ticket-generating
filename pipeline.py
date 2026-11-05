"""Client brief -> dev tasks pipeline.

Stage 0  Prepare     (Python) number the sentences S1, S2, ...
Stage 1  Extract     (AI)     facts the brief states, each with quote + ref
Stage 2  Gaps        (AI)     open questions; Python assigns IDs, removes "e.g." lists
Stage 3  Break down  (AI)     epics -> tasks; Python checks coverage and asks for missing tasks once
Stage 4  Tickets     (Python) see tickets.py
Stage 5  Verify      (Python) see verify.py

Every AI answer is passed through a normalise_* function first, so a wrongly
shaped answer (e.g. a plain string where an object was expected) can never
crash a later stage.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from prompts import EXTRACT_PROMPT, GAPS_PROMPT, BREAKDOWN_PROMPT
from tickets import build_tickets
from verify import verify

# .env lives in the hackathon-2026 folder (one level up)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
# Groq free tier: 8,000 tokens per minute for this model (input + reserved output).
TOKENS_PER_MINUTE = int(os.getenv("GROQ_TPM_LIMIT", "8000"))
MAX_OUTPUT_TOKENS = 4000
_client = None


def get_client():
    global _client
    if _client is None:
        from groq import Groq  # imported here so offline tests don't need the package

        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set. Add it to the .env file.")
        _client = Groq(api_key=key, timeout=90, max_retries=2)
    return _client


def compact(data) -> str:
    """JSON without spaces: same content, far fewer tokens."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


# ---------- Stage 0: prepare (no AI) ----------
def number_sentences(brief: str) -> list[dict]:
    """Split the brief into sentences and give each an id S1, S2, ..."""
    text = brief.replace("\r", "")
    parts = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts.extend(p.strip() for p in re.split(r"(?<=[.!?])\s+", line) if p.strip())
    return [{"ref": f"S{i}", "text": s} for i, s in enumerate(parts, start=1)]


def format_numbered(sentences: list[dict]) -> str:
    return "\n".join(f"[{s['ref']}] {s['text']}" for s in sentences)


# ---------- LLM helper ----------
class DailyLimitError(RuntimeError):
    """Raised when the provider's daily token limit is reached."""


def _estimate_tokens(text: str) -> int:
    return len(text) // 3 + 50  # rough, deliberately on the high side


def _retry_after(err, default=20.0) -> float:
    try:
        return min(float(err.response.headers.get("retry-after", default)), 65.0)
    except Exception:
        return default


def call_llm(system_prompt: str, user_content: str, retries: int = 1,
             max_output: int = MAX_OUTPUT_TOKENS) -> dict:
    """Call Groq in JSON mode and return a parsed dict.

    - keeps each request under the free-tier token limit (clear error if impossible)
    - waits and retries when the per-minute limit is hit (429)
    - retries once on invalid JSON, and reports if the answer was cut off
    """
    import groq

    est_in = _estimate_tokens(system_prompt + user_content)
    max_out = min(max_output, TOKENS_PER_MINUTE - est_in - 200)
    if max_out < 1000:
        raise ValueError(
            f"This request is too large for the Groq free tier (~{est_in} input tokens, "
            f"limit {TOKENS_PER_MINUTE}/min). Use a shorter brief or a higher tier.")

    kwargs = dict(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        max_completion_tokens=max_out,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    if "gpt-oss" in MODEL:
        kwargs["extra_body"] = {"reasoning_effort": "low"}  # fewer hidden reasoning tokens

    last_error = None
    attempt = 0
    rate_waits = 0
    while attempt <= retries:
        try:
            resp = get_client().chat.completions.create(**kwargs)
        except groq.RateLimitError as e:  # 429
            message = str(e)
            if "per day" in message or "TPD" in message or "RPD" in message:
                # a DAILY limit: waiting a minute cannot help, so stop with a clear message
                wait_text = re.search(r"try again in ([0-9hms.]+)", message)
                raise DailyLimitError(
                    "Groq's daily token limit for this model is used up"
                    + (f" (try again in about {wait_text.group(1).rstrip('.')})" if wait_text else "")
                    + ". Wait, or set GROQ_MODEL in .env to another model "
                      "(e.g. openai/gpt-oss-20b) for this run.") from e
            # per-minute budget used up -> wait, then retry
            if rate_waits >= 4:
                raise
            rate_waits += 1
            wait = _retry_after(e)
            print(f"    (rate limit reached, waiting {wait:.0f}s and retrying)")
            time.sleep(wait)
            continue
        except groq.APIStatusError as e:
            if e.status_code == 413:
                raise ValueError(
                    "Request too large for the Groq free-tier token limit. "
                    "Use a shorter brief, or set GROQ_MODEL to a model with a higher limit.") from e
            raise
        choice = resp.choices[0]
        raw = choice.message.content
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
            last_error = TypeError("top-level JSON is not an object")
        except (json.JSONDecodeError, TypeError) as e:
            last_error = e
            if choice.finish_reason == "length":
                last_error = ValueError("the answer was cut off (output token limit reached)")
        attempt += 1
    raise ValueError(f"LLM did not return valid JSON: {last_error}")


# ---------- normalising AI output (Python, never trusts the shape) ----------
def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_ref(value):
    if isinstance(value, list):
        return [str(v) for v in value]
    return str(value) if value is not None else ""


def _as_item(value) -> dict | None:
    """A fact item must be {'text','quote','ref'}. A plain string becomes text with no quote
    (so Stage 5 will flag it as unverified instead of crashing)."""
    if isinstance(value, dict):
        return {"text": str(value.get("text") or value.get("quote") or ""),
                "quote": str(value.get("quote") or ""),
                "ref": _as_ref(value.get("ref"))}
    if isinstance(value, str) and value.strip():
        return {"text": value.strip(), "quote": "", "ref": ""}
    return None


FACT_KEYS = ["goals", "users", "features", "constraints", "quality_requirements",
             "integrations", "deadlines", "priorities", "estimates", "terms_used"]


def normalise_facts(facts: dict) -> dict:
    out = {}
    for k in FACT_KEYS:
        out[k] = [i for i in (_as_item(v) for v in _as_list(facts.get(k))) if i]
    return out


REF_MARKER = re.compile(r"\s*[\(\[]\s*S\d+(?:\s*[,;]\s*S\d+)*\s*[\)\]]\s*$")


def _strip_ref_marker(text) -> str:
    """'...order number. (S8)' -> '...order number.'  (format only; the words are not changed)"""
    return REF_MARKER.sub("", str(text)).strip()


def normalise_questions(raw: list) -> list[dict]:
    questions = []
    for q in _as_list(raw):
        if isinstance(q, str):
            q = {"question": q}
        if not isinstance(q, dict) or not str(q.get("question", "")).strip():
            continue
        questions.append({
            "category": str(q.get("category") or "missing"),
            "issue": str(q.get("issue") or ""),
            "quotes": [_strip_ref_marker(x) for x in _as_list(q.get("quotes"))],
            "refs": [str(x) for x in _as_list(q.get("refs"))],
            "question": str(q["question"]),
            "affects": [str(x) for x in _as_list(q.get("affects"))] or ["GENERAL"],
        })
    return questions


def _as_source(value) -> dict:
    if isinstance(value, dict):
        return {"quote": str(value.get("quote") or ""), "ref": _as_ref(value.get("ref"))}
    if isinstance(value, str):
        return {"quote": value, "ref": ""}
    return {"quote": "", "ref": ""}


def _as_stated(value):
    if isinstance(value, dict) and value.get("value"):
        return {"value": str(value["value"]), "quote": str(value.get("quote") or ""),
                "ref": _as_ref(value.get("ref"))}
    return None  # a bare string has no source quote, so it is not trusted


def _as_dependency(value) -> dict:
    """A dependency is {'key','quote','ref'}. A bare key has no quote, so Stage 4 will
    turn it into an open question instead of trusting it."""
    if isinstance(value, dict):
        return {"key": str(value.get("key") or ""), "quote": str(value.get("quote") or ""),
                "ref": _as_ref(value.get("ref"))}
    return {"key": str(value), "quote": "", "ref": ""}


def normalise_plan(plan: dict) -> dict:
    epics = []
    for e in _as_list(plan.get("epics")):
        if not isinstance(e, dict):
            continue
        tasks = []
        for t in _as_list(e.get("tasks")):
            if not isinstance(t, dict):
                continue
            criteria = []
            for c in _as_list(t.get("acceptance_criteria")):
                if isinstance(c, dict):
                    criteria.append({"criterion": str(c.get("criterion") or ""),
                                     "quote": str(c.get("quote") or ""), "ref": _as_ref(c.get("ref"))})
                elif isinstance(c, str) and c.strip():
                    criteria.append({"criterion": c, "quote": "", "ref": ""})  # will be flagged
            tasks.append({
                "key": str(t.get("key") or ""),
                "title": str(t.get("title") or ""),
                "type": str(t.get("type") or "Task"),
                "covers": [str(x) for x in _as_list(t.get("covers"))],
                "description": str(t.get("description") or ""),
                "acceptance_criteria": criteria,
                "source": _as_source(t.get("source")),
                "depends_on": [_as_dependency(d) for d in _as_list(t.get("depends_on")) if d],
                "question_ids": [str(x) for x in _as_list(t.get("question_ids"))],
                "priority": _as_stated(t.get("priority")),
                "deadline": _as_stated(t.get("deadline")),
                "estimate": _as_stated(t.get("estimate")),
            })
        epics.append({"title": str(e.get("title") or ""), "description": str(e.get("description") or ""),
                      "source": _as_source(e.get("source")), "tasks": tasks})
    return {"epics": epics}


# ---------- Stage 1: extract (AI) ----------
def extract(sentences: list[dict]) -> dict:
    return normalise_facts(call_llm(EXTRACT_PROMPT, "CLIENT BRIEF:\n" + format_numbered(sentences),
                                    max_output=2500))


# ---------- Stage 2: detect gaps (AI + Python clean-up) ----------
EXAMPLE_PATTERN = re.compile(r"\s*\((?:e\.g\.|eg\.|for example|such as)[^)]*\)", re.IGNORECASE)


def clean_question(text: str) -> tuple[str, bool]:
    """Remove '(e.g. ...)' example lists from a question. Returns (text, changed)."""
    cleaned = EXAMPLE_PATTERN.sub("", text).strip()
    return cleaned, cleaned != text


def detect_gaps(sentences: list[dict], facts: dict) -> list[dict]:
    user_content = (
        "CLIENT BRIEF:\n" + format_numbered(sentences)
        + "\n\nEXTRACTED FACTS:\n" + compact(facts)
    )
    result = call_llm(GAPS_PROMPT, user_content, max_output=3000)
    questions = normalise_questions(result.get("questions"))
    # IDs and clean-up are done by Python, not by the AI
    for i, q in enumerate(questions, start=1):
        q["id"] = f"Q-{i:03d}"
        q["question"], q["examples_removed"] = clean_question(q["question"])
    return questions


# ---------- Stage 3: break down (AI) + coverage check & repair (Python) ----------
def build_work_items(facts: dict) -> list[dict]:
    """Number every feature (F1..), integration (I1..) and quality requirement (R1..)
    so Python can check that each one is covered by a task."""
    items = []
    feature_refs = set()
    for i, f in enumerate(facts.get("features", []), start=1):
        items.append({"id": f"F{i}", "text": f.get("text"), "quote": f.get("quote"), "ref": f.get("ref")})
        feature_refs.add(str(f.get("ref")))
    # integrations are work too, unless the same sentence is already a feature
    n = 0
    for g in facts.get("integrations", []):
        if str(g.get("ref")) in feature_refs:
            continue
        n += 1
        items.append({"id": f"I{n}", "text": g.get("text"), "quote": g.get("quote"), "ref": g.get("ref")})
    for i, r in enumerate(facts.get("quality_requirements", []), start=1):
        items.append({"id": f"R{i}", "text": r.get("text"), "quote": r.get("quote"), "ref": r.get("ref")})
    return items


def find_uncovered(plan: dict, items: list[dict]) -> list[dict]:
    covered = set()
    for epic in plan.get("epics", []):
        for t in epic.get("tasks", []):
            covered.update(t.get("covers", []) or [])
    return [it for it in items if it["id"] not in covered]


def _stage3_context(sentences, facts, questions) -> str:
    """Only what Stage 3 needs, in compact JSON, to stay under the token limit."""
    needed = {k: facts.get(k, []) for k in
              ("users", "features", "constraints", "quality_requirements", "integrations",
               "deadlines", "priorities", "estimates")}
    short_q = [{"id": q["id"], "category": q["category"], "question": q["question"],
                "affects": q["affects"]} for q in questions]
    return ("CLIENT BRIEF:\n" + format_numbered(sentences)
            + "\n\nEXTRACTED FACTS:\n" + compact(needed)
            + "\n\nOPEN QUESTIONS:\n" + compact(short_q))


def _merge_new_tasks(plan: dict, extra: dict):
    """Add tasks returned by the repair call; join epics with the same title."""
    by_title = {e["title"].strip().lower(): e for e in plan["epics"]}
    used_keys = {t["key"] for e in plan["epics"] for t in e["tasks"]}
    for e in extra.get("epics", []):
        target = by_title.get(e["title"].strip().lower())
        if target is None:
            target = {**e, "tasks": []}
            plan["epics"].append(target)
            by_title[e["title"].strip().lower()] = target
        for t in e["tasks"]:
            if not t["key"] or t["key"] in used_keys:
                n = len(used_keys) + 1
                while f"T{n}" in used_keys:
                    n += 1
                t["key"] = f"T{n}"
            used_keys.add(t["key"])
            target["tasks"].append(t)


def breakdown(sentences: list[dict], facts: dict, questions: list[dict]) -> dict:
    items = build_work_items(facts)
    context = _stage3_context(sentences, facts, questions)
    short_items = [{"id": i["id"], "text": i["text"], "ref": i["ref"]} for i in items]
    plan = normalise_plan(call_llm(BREAKDOWN_PROMPT, context + "\n\nWORK ITEM LIST:\n" + compact(short_items)))

    # Python checks coverage; if items are missing, ask ONLY for the missing tasks (small request)
    first_missing = find_uncovered(plan, items)
    missing = first_missing
    repaired = False
    if missing:
        existing = [{"epic": e["title"], "key": t["key"], "title": t["title"]}
                    for e in plan["epics"] for t in e["tasks"]]
        missing_items = [{"id": m["id"], "text": m["text"], "ref": m["ref"]} for m in missing]
        repair = (
            context
            + "\n\nWORK ITEM LIST (ONLY THESE ARE STILL MISSING):\n" + compact(missing_items)
            + "\n\nTASKS THAT ALREADY EXIST (do not repeat them):\n" + compact(existing)
            + "\n\nERROR IN YOUR PREVIOUS ANSWER: the work items above were not covered by any task. "
              "Return JSON in the same format containing ONLY the NEW tasks that cover them. "
              "Reuse an existing epic title if it fits. Keep all other rules."
        )
        _merge_new_tasks(plan, normalise_plan(call_llm(BREAKDOWN_PROMPT, repair, max_output=3000)))
        repaired = True
        missing = find_uncovered(plan, items)

    # Still missing after the repair: Python adds a minimal task made only of the brief's words
    created = []
    if missing:
        used_keys = {t["key"] for e in plan["epics"] for t in e["tasks"]}
        for m in missing:
            is_quality = m["id"].startswith("R")
            epic_title = "Quality requirements" if is_quality else "Other requirements from the brief"
            epic = next((e for e in plan["epics"] if e["title"].strip().lower() == epic_title.lower()), None)
            if epic is None:
                epic = {"title": epic_title, "description": "Items the AI did not break down; created by Python "
                        "from the brief's own words.", "source": {"quote": m["quote"], "ref": m["ref"]}, "tasks": []}
                plan["epics"].append(epic)
            n = len(used_keys) + 1
            while f"T{n}" in used_keys:
                n += 1
            used_keys.add(f"T{n}")
            text = str(m["text"] or m["quote"])
            epic["tasks"].append({
                "key": f"T{n}", "title": (text[:1].upper() + text[1:])[:70], "type": "Task" if is_quality else "Story",
                "covers": [m["id"]], "description": m["quote"] or text,
                "acceptance_criteria": [] if is_quality or not m["quote"] else
                [{"criterion": m["quote"], "quote": m["quote"], "ref": m["ref"]}],
                "source": {"quote": m["quote"], "ref": m["ref"]}, "depends_on": [], "question_ids": [],
                "priority": None, "deadline": None, "estimate": None, "created_by": "python",
            })
            created.append(m["id"])
        missing = find_uncovered(plan, items)

    # Remove empty epics (Python, not AI)
    plan["epics"] = [e for e in plan["epics"] if e["tasks"]]
    plan["work_items"] = items
    plan["coverage"] = {
        "work_items": len(items),
        "uncovered_first_try": [m["id"] for m in first_missing],
        "repair_attempted": repaired,
        "created_by_python": created,
        "uncovered": [m["id"] for m in missing],
    }
    return plan


# ---------- full pipeline ----------
def run_pipeline(brief: str, progress=None) -> dict:
    """Run all stages. `progress(stage_name)` is an optional callback for the UI."""
    def step(name):
        if progress:
            progress(name)

    if not brief or not brief.strip():
        raise ValueError("The brief is empty. Paste a client brief first.")

    step("Stage 0: numbering sentences")
    sentences = number_sentences(brief)

    step("Stage 1: extracting facts (AI)")
    facts = extract(sentences)

    step("Stage 2: detecting gaps (AI)")
    questions = detect_gaps(sentences, facts)

    step("Stage 3: breaking down into epics and tasks (AI)")
    plan = breakdown(sentences, facts, questions)

    step("Stage 4: building tickets (Python)")
    tickets, questions = build_tickets(plan, questions, facts, sentences)

    step("Stage 5: verifying against the brief (Python)")
    report = verify(sentences, facts, questions, plan, tickets)

    return {
        "meta": {
            "model": MODEL,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "brief": brief,
        "sentences": sentences,
        "facts": facts,
        "questions": questions,
        "plan": plan,
        "tickets": tickets,
        "verification": report,
    }


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "briefs/clear_brief.txt")
    result = run_pipeline(path.read_text(encoding="utf-8"), progress=print)
    from export import save_all

    folder = save_all(result, Path("outputs") / path.stem)
    v = result["verification"]["summary"]
    print(f"\n{len(result['tickets'])} tickets, {len(result['questions'])} open questions")
    print(f"Verification: {v}")
    print(f"Saved to {folder}")
