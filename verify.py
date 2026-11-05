"""Stage 5: check the AI output against the brief. Pure Python, no AI.

Checks
1. Every quote appears in the brief (exact, or exact after normalising
   typography such as non-breaking hyphens and curly quotes).
2. Every ref (S1, S2, ...) exists and the quote is in that sentence.
3. Every question 'affects' entry names a real feature (or GENERAL).
4. Every question is linked to at least one ticket.
5. Every feature / quality requirement is covered by a task.
6. Dependencies point to tickets that exist.
Anything that fails is reported as UNVERIFIED and added to the ticket's warnings.
"""
import re
import unicodedata

_TYPO = str.maketrans({
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    " ": " ", " ": " ", " ": " ", " ": " ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
})


def _clean(text: str) -> str:
    """Normalise typography and spacing only. Case and words are NOT changed."""
    text = unicodedata.normalize("NFKC", str(text or "")).translate(_TYPO)
    return re.sub(r"\s+", " ", text).strip()


def _split_refs(text: str) -> list[str]:
    return [r.strip() for r in str(text).split(",") if r.strip()]


def _strip_end(text: str) -> str:
    return text.rstrip(" .!?;,")


def check_quote(quote: str, ref, sentences: list[dict], full_text: str) -> dict:
    """Return {'status': exact|normalised|ref_mismatch|not_found|missing, ...}."""
    if not quote or not str(quote).strip():
        return {"status": "missing", "detail": "no quote given"}
    q_raw = str(quote).strip()
    q = _strip_end(_clean(q_raw))
    refs = ref if isinstance(ref, list) else ([ref] if ref else [])
    ref_texts = {s["ref"]: s["text"] for s in sentences}
    bad_refs = [r for r in refs if r not in ref_texts]

    if _strip_end(q_raw) in full_text:
        status = "exact"
    elif q in _clean(full_text):
        status = "normalised"
    else:
        return {"status": "not_found", "detail": f'"{q_raw}" is not in the brief'}

    if bad_refs:
        return {"status": "ref_mismatch", "detail": f"ref(s) {bad_refs} do not exist"}
    # a quote may span several referenced sentences (e.g. contradictions)
    if refs:
        joined = _clean(" ".join(ref_texts[r] for r in refs))
        if q not in joined and not any(q in _clean(ref_texts[r]) for r in refs):
            return {"status": "ref_mismatch", "detail": f'quote is in the brief but not in {refs}'}
    return {"status": status, "detail": ""}


def verify(sentences, facts, questions, plan, tickets) -> dict:
    full_text = " ".join(s["text"] for s in sentences)
    issues = []
    checked = 0
    by_id = {t["ticket_id"]: t for t in tickets}

    def record(where, quote, ref, ticket_id=None):
        nonlocal checked
        checked += 1
        res = check_quote(quote, ref, sentences, full_text)
        if res["status"] not in ("exact", "normalised"):
            issue = {"where": where, "quote": quote, "ref": ref, **res}
            issues.append(issue)
            if ticket_id and ticket_id in by_id:
                by_id[ticket_id]["warnings"].append(f"UNVERIFIED {where}: {res['detail']}")
        return res["status"]

    # 1-2. quotes in facts
    for cat, items in facts.items():
        if isinstance(items, list):
            for i, it in enumerate(items):
                if isinstance(it, dict):
                    record(f"fact {cat}[{i}]", it.get("quote"), it.get("ref"))

    # 1-2. quotes in questions
    for q in questions:
        quotes = q.get("quotes") or []
        if not quotes:
            issues.append({"where": f"question {q['id']}", "status": "missing", "detail": "no quote"})
        for qt in quotes:
            st = record(f"question {q['id']}", qt, q.get("refs"))
            if st not in ("exact", "normalised"):
                q.setdefault("warnings", []).append(f'UNVERIFIED quote "{qt}"')

    # 1-2. quotes in tickets (source, criteria, stated priority/deadline/estimate)
    task_by_ticket = {}
    for epic in plan.get("epics", []):
        for t in epic.get("tasks", []):
            task_by_ticket[t.get("key")] = t
    for t in tickets:
        src = t["source_reference"]
        m = re.match(r'(\S.*?): "(.*)"$', src, re.S)
        if m:
            record(f"{t['ticket_id']} source", m.group(2), _split_refs(m.group(1)), t["ticket_id"])
        else:
            issues.append({"where": f"{t['ticket_id']} source", "status": "missing", "detail": "no source quote"})
            t["warnings"].append("UNVERIFIED source: no source quote")
        for c in t["acceptance_criteria"]:
            record(f"{t['ticket_id']} acceptance criterion", c.get("quote"), c.get("ref"), t["ticket_id"])
        for field in ("priority", "deadline", "estimate"):
            m = re.match(r'.*? \(([^()]*?): "(.*)"\)$', t[field], re.S)
            if m:
                record(f"{t['ticket_id']} {field}", m.group(2), _split_refs(m.group(1)), t["ticket_id"])

    # 3. 'affects' must name real features
    feature_texts = {str(f.get("text", "")).strip().lower() for f in facts.get("features", [])}
    for cat in ("quality_requirements", "integrations"):
        feature_texts |= {str(r.get("text", "")).strip().lower() for r in facts.get(cat, [])}
    for q in questions:
        for a in q.get("affects") or []:
            if a.strip().lower() != "general" and a.strip().lower() not in feature_texts:
                issues.append({"where": f"question {q['id']} affects", "status": "unknown_feature",
                               "detail": f'"{a}" is not an extracted feature'})

    # 4. every question blocks at least one ticket
    for q in questions:
        if not q.get("blocks"):
            issues.append({"where": f"question {q['id']}", "status": "unlinked",
                           "detail": "not linked to any ticket"})

    # 5. coverage
    uncovered = plan.get("coverage", {}).get("uncovered", [])
    for item_id in uncovered:
        issues.append({"where": f"work item {item_id}", "status": "uncovered",
                       "detail": "no task covers this feature/requirement"})

    # 6. dependencies
    for t in tickets:
        for d in t["dependencies"]:
            if d not in by_id:
                issues.append({"where": f"{t['ticket_id']} dependency", "status": "bad_dependency",
                               "detail": f"{d} does not exist"})

    # 7. every sentence of the brief must reach a ticket (or be background: goals, users, names).
    #    A sentence only mentioned in a question is NOT enough: the developer would not see the rule.
    used = set()

    def add_refs(ref):
        if isinstance(ref, list):
            used.update(str(r) for r in ref)
        elif ref:
            used.update(_split_refs(str(ref)))

    background = set()
    for cat in ("goals", "users", "terms_used"):
        for it in facts.get(cat, []):
            if isinstance(it, dict):
                r = it.get("ref")
                background.update(r if isinstance(r, list) else _split_refs(str(r or "")))
    for t in tickets:
        m = re.match(r'(\S.*?): "', t["source_reference"])
        if m:
            add_refs(m.group(1))
        for c in t["acceptance_criteria"]:
            add_refs(c.get("ref"))
        for field in ("priority", "deadline", "estimate"):
            m = re.match(r'.*? \(([^()]*?): "', t[field])
            if m:
                add_refs(m.group(1))
    # background (goals, users, names) only counts for sentences that state no requirement:
    # "Admins should get reports." names a user AND asks for a feature, so it must reach a ticket
    req = re.compile(r"\b(must|should|need|needs|able to|can)\b", re.IGNORECASE)
    for s in sentences:
        if s["ref"] in background and not req.search(s["text"]):
            used.add(s["ref"])
    unused = [s["ref"] for s in sentences if s["ref"] not in used]
    for ref in unused:
        text = next(s["text"] for s in sentences if s["ref"] == ref)
        issues.append({"where": f"brief sentence {ref}", "status": "sentence_unused",
                       "detail": f'"{text}" does not appear on any ticket - review by hand'})

    # duplicated questions (same text)
    seen = {}
    for q in questions:
        key = _clean(q.get("question", "")).lower()
        if key in seen:
            issues.append({"where": f"question {q['id']}", "status": "duplicate",
                           "detail": f"same text as {seen[key]}"})
        else:
            seen[key] = q["id"]

    notes = [n for t in tickets for n in t.get("notes", [])]
    summary = {
        "quotes_checked": checked,
        "ai_values_rejected": sum(1 for n in notes if n.startswith("Rejected")),
        "criteria_replaced_with_brief_words": sum(1 for n in notes if n.startswith("Criterion")),
        "issues": len(issues),
        "tickets_ready": sum(1 for t in tickets if t["status"].startswith("Ready")),
        "tickets_need_clarification": sum(1 for t in tickets if not t["status"].startswith("Ready")),
        "uncovered_work_items": uncovered,
        "unused_sentences": unused,
        "passed": not issues,
    }
    return {"summary": summary, "issues": issues}
