"""Stage 4: build Jira-style tickets from the Stage 3 plan. Pure Python, no AI.

Python, not the AI, decides IDs, links, "Not specified" values and
Ready / Needs clarification status, so none of these can be hallucinated.
"""
import re

from verify import _clean

MONTHS = ("january february march april may june july august september october november "
          "december jan feb mar apr jun jul aug sep sept oct nov dec").split()
NOT_SPECIFIED = "Not specified"
READY = "Ready for development"
NEEDS = "Needs clarification"


def _norm(text) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def _stated(field) -> str:
    """Priority/estimate/deadline: only filled if the brief states it (with its source)."""
    if isinstance(field, dict) and field.get("value"):
        ref = _ref_text(field.get("ref"))
        quote = field.get("quote", "")
        return f'{field["value"]} ({ref}: "{quote}")'
    return NOT_SPECIFIED


def _ref_text(ref) -> str:
    if isinstance(ref, list):
        return ", ".join(str(r) for r in ref) or "?"
    return str(ref or "?")


def _source(src) -> str:
    if isinstance(src, dict) and src.get("quote"):
        return f'{_ref_text(src.get("ref"))}: "{src["quote"]}"'
    return NOT_SPECIFIED


def _refs(value) -> set:
    if isinstance(value, list):
        return {str(v) for v in value}
    return {str(value)} if value else set()


def _fact_refs(facts: dict, category: str) -> set:
    refs = set()
    for item in facts.get(category, []):
        if isinstance(item, dict):
            refs |= _refs(item.get("ref"))
    return refs


def _is_real_date(text: str) -> bool:
    """A deadline must name a date (digits or a month). "soon" / "later" are not deadlines."""
    words = re.findall(r"[a-z]+", text.lower())
    return bool(re.search(r"\d", text)) or any(w in MONTHS for w in words)


def _check_stated(field, kind: str, facts: dict, notes: list):
    """Keep an AI-filled priority/deadline/estimate only if Stage 1 extracted it as that kind
    of fact from the same sentence. Otherwise reject it (-> 'Not specified') and say why."""
    if not (isinstance(field, dict) and field.get("value")):
        return None
    category = {"priority": "priorities", "deadline": "deadlines", "estimate": "estimates"}[kind]
    if not (_refs(field.get("ref")) & _fact_refs(facts, category)):
        notes.append(f'Rejected AI {kind} "{field["value"]}": sentence {field.get("ref")} is not one of '
                     f'the {category} extracted from the brief')
        return None
    if kind == "deadline" and not _is_real_date(f'{field["value"]} {field.get("quote", "")}'):
        notes.append(f'Rejected AI deadline "{field["value"]}": vague timing is not a date '
                     f'(kept as an open question instead)')
        return None
    return field


def build_tickets(plan: dict, questions: list[dict], facts: dict, sentences: list[dict] | None = None):
    """Return (tickets, questions). Each question gets a 'blocks' list of ticket IDs.

    If `sentences` are given, acceptance criteria must use the brief's own words:
    a criterion the AI reworded (and possibly extended) is replaced by its exact quote.
    """
    brief_clean = _clean(" ".join(s["text"] for s in sentences)) if sentences else None
    q_by_id = {q["id"]: q for q in questions}
    work_items = plan.get("work_items", [])
    item_by_text = {_norm(it.get("text")): it["id"] for it in work_items}

    tickets: list[dict] = []
    key_to_id: dict[str, str] = {}
    epic_ids: list[str] = []
    counter = 0

    def next_id():
        nonlocal counter
        counter += 1
        return f"TASK-{counter:03d}"

    # pass 1: create tickets and assign IDs
    raw_tasks = []  # (ticket, task_json)
    for epic in plan.get("epics", []):
        epic_ticket = {
            "ticket_id": next_id(),
            "title": epic.get("title") or "Untitled epic",
            "type": "Epic",
            "parent": "",
            "description": epic.get("description") or NOT_SPECIFIED,
            "acceptance_criteria": [],
            "source_reference": _source(epic.get("source")),
            "dependencies": [],
            "open_questions": [],
            "priority": NOT_SPECIFIED,
            "estimate": NOT_SPECIFIED,
            "deadline": NOT_SPECIFIED,
            "covers": [],
            "warnings": [],
            "notes": [],
        }
        tickets.append(epic_ticket)
        epic_ids.append(epic_ticket["ticket_id"])
        children = []
        for t in epic.get("tasks", []):
            ttype = t.get("type") if t.get("type") in ("Story", "Task") else "Task"
            notes: list[str] = []
            criteria = []
            for c in (t.get("acceptance_criteria") or []):
                if not isinstance(c, dict):
                    continue
                crit = {"criterion": c.get("criterion", ""), "quote": c.get("quote", ""), "ref": c.get("ref", "")}
                if brief_clean is not None and crit["criterion"]:
                    in_brief = _clean(crit["criterion"]).rstrip(" .") in brief_clean
                    quote_ok = crit["quote"] and _clean(crit["quote"]).rstrip(" .") in brief_clean
                    if not in_brief and quote_ok:
                        notes.append(f'Criterion reworded by the AI was replaced by the brief\'s words: '
                                     f'"{crit["criterion"]}" -> "{crit["quote"]}"')
                        crit["criterion"] = crit["quote"]
                criteria.append(crit)
            ticket = {
                "ticket_id": next_id(),
                "title": t.get("title") or "Untitled task",
                "type": ttype,
                "parent": epic_ticket["ticket_id"],
                "description": t.get("description") or NOT_SPECIFIED,
                "acceptance_criteria": criteria,
                "source_reference": _source(t.get("source")),
                "dependencies": [],
                "open_questions": [],
                "priority": _stated(_check_stated(t.get("priority"), "priority", facts, notes)),
                "estimate": _stated(_check_stated(t.get("estimate"), "estimate", facts, notes)),
                "deadline": _stated(_check_stated(t.get("deadline"), "deadline", facts, notes)),
                "covers": list(t.get("covers") or []),
                "warnings": [],
                "notes": notes,
            }
            if t.get("created_by") == "python":
                notes.append("Created by Python from the brief's words: the AI did not produce a task "
                             "for this item, even after a repair request")
            if t.get("key"):
                key_to_id[t["key"]] = ticket["ticket_id"]
            tickets.append(ticket)
            children.append(ticket["ticket_id"])
            raw_tasks.append((ticket, t))
        epic_ticket["children"] = children

    # two reworded criteria can end up as the same quote: keep one
    for tk in tickets:
        seen, unique = set(), []
        for c in tk["acceptance_criteria"]:
            k = _clean(c["criterion"]).lower()
            if k not in seen:
                seen.add(k)
                unique.append(c)
        tk["acceptance_criteria"] = unique

    by_id = {t["ticket_id"]: t for t in tickets}

    def link(qid: str, ticket_id: str):
        t = by_id[ticket_id]
        if qid not in t["open_questions"]:
            t["open_questions"].append(qid)

    # pass 2: dependencies and questions chosen by the AI (only if they exist)
    next_q = len(questions) + 1
    for ticket, t in raw_tasks:
        for dep in t.get("depends_on") or []:
            if isinstance(dep, str):  # old format: a bare key with no evidence
                dep = {"key": dep, "quote": "", "ref": ""}
            key = dep.get("key", "")
            if key not in key_to_id or key_to_id[key] == ticket["ticket_id"]:
                ticket["warnings"].append(f"Dropped unknown dependency '{key}'")
                continue
            other = by_id[key_to_id[key]]
            quote = dep.get("quote", "")
            stated = bool(quote) and (brief_clean is None or _clean(quote).rstrip(" .") in brief_clean)
            if stated:
                ticket["dependencies"].append(other["ticket_id"])
                continue
            # the brief does not state this link -> do not add it; ask the client instead
            src = t.get("source") or {}
            qid = f"Q-{next_q:03d}"
            next_q += 1
            q = {
                "id": qid, "category": "dependency",
                "issue": "The AI suggested a dependency that the brief does not state",
                "quotes": [src.get("quote", "")] if src.get("quote") else [],
                "refs": [str(r) for r in _refs(src.get("ref"))],
                "question": (f'Does "{ticket["title"]}" ({ticket["ticket_id"]}) depend on '
                             f'"{other["title"]}" ({other["ticket_id"]})? The brief does not say.'),
                "affects": [], "generated_by": "python",
            }
            questions.append(q)
            q_by_id[qid] = q
            ticket["open_questions"].append(qid)
            ticket["notes"].append(f"Dependency on {other['ticket_id']} not stated in the brief: "
                                   f"turned into open question {qid}")
        for qid in t.get("question_ids") or []:
            if qid in q_by_id:
                link(qid, ticket["ticket_id"])
            else:
                ticket["warnings"].append(f"Dropped unknown question id '{qid}'")

    def task_refs(tk) -> set:
        refs = set()
        m = re.match(r'(\S.*?): "', tk["source_reference"])
        if m:
            refs |= {r.strip() for r in m.group(1).split(",")}
        for c in tk["acceptance_criteria"]:
            refs |= _refs(c.get("ref"))
        return refs

    # pass 3: link each question to the tickets it blocks, using its 'affects' list and its refs
    for q in questions:
        if q.get("generated_by") == "python":
            q["link_type"] = "task"
            q["blocks"] = [t["ticket_id"] for t in tickets if q["id"] in t["open_questions"]]
            continue
        affects = q.get("affects") or ["GENERAL"]
        general = any(_norm(a) == "general" for a in affects)
        for a in affects:
            item_id = item_by_text.get(_norm(a))
            if item_id:
                for ticket, _ in raw_tasks:
                    if item_id in ticket["covers"]:
                        link(q["id"], ticket["ticket_id"])
        by_affects = [tk["ticket_id"] for tk in tickets if q["id"] in tk["open_questions"]]
        # tasks built from the same brief sentence(s) the question quotes
        q_refs = set(str(r) for r in (q.get("refs") or []))
        ref_tasks = [tk["ticket_id"] for tk, _ in raw_tasks if q_refs & task_refs(tk)]
        if general and ref_tasks and len(ref_tasks) < len(raw_tasks):
            # the AI said "whole project", but the question is about specific sentences:
            # scope it to the tasks built from those sentences instead of blocking everything
            general = False
            q["scope_note"] = (f"AI labelled this GENERAL; Python scoped it to the tasks built from "
                               f"{', '.join(sorted(q_refs))}")
        if not general and not by_affects:
            # 'affects' matched nothing: fall back to the tasks built from the quoted sentences
            for tid in ref_tasks:
                link(q["id"], tid)
        already = [t["ticket_id"] for t in tickets if q["id"] in t["open_questions"]]
        if general:
            # project-wide: the answer changes every feature, so it blocks EVERY ticket
            for tk in tickets:
                link(q["id"], tk["ticket_id"])
            q["link_type"] = "project-wide"
        elif not already:
            # not matched to any task: never lose it, attach it to every epic
            for eid in epic_ids:
                link(q["id"], eid)
            q["link_type"] = "fallback (no matching task)"
        else:
            q["link_type"] = "task"
        q["blocks"] = [t["ticket_id"] for t in tickets if q["id"] in t["open_questions"]]

    # pass 3b: constraints that no task uses become project constraints on every epic
    used_refs = set()
    for tk in tickets:
        for c in tk["acceptance_criteria"]:
            used_refs |= _refs(c.get("ref"))
    for c in facts.get("constraints", []):
        if not isinstance(c, dict) or not c.get("quote"):
            continue
        if _refs(c.get("ref")) & used_refs:
            continue
        for eid in epic_ids:
            by_id[eid]["acceptance_criteria"].append(
                {"criterion": c["quote"], "quote": c["quote"], "ref": c.get("ref", ""), "project_constraint": True})
            by_id[eid]["notes"].append(f'Constraint {c.get("ref")} was on no task: added as a project '
                                       f'constraint ("{c["quote"]}")')

    # pass 4: status
    for t in tickets:
        reasons = []
        if t["open_questions"]:
            reasons.append(f"{len(t['open_questions'])} open question(s)")
        if t["type"] != "Epic" and not t["acceptance_criteria"]:
            reasons.append("no testable acceptance criteria in the brief")
        t["status"] = NEEDS if reasons else READY
        t["status_reason"] = "; ".join(reasons) if reasons else "All fields come from the brief"

    return tickets, questions
