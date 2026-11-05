"""Stage 6 helpers: turn the pipeline result into JSON, CSV and Markdown."""
import csv
import io
import json
from pathlib import Path

CSV_COLUMNS = [
    "Ticket ID", "Title", "Type", "Parent", "Status", "Description",
    "Acceptance Criteria", "Source Reference", "Dependencies", "Open Questions",
    "Priority", "Estimate", "Deadline", "Warnings", "Python Corrections",
]


def _criteria_lines(t) -> list[str]:
    if t["type"] == "Epic":
        kids = ", ".join(t.get("children", [])) or "none"
        lines = [f"Epic: see child tickets {kids}"]
        lines += [f'Project constraint: {c["criterion"]} [{c["ref"]}]' for c in t["acceptance_criteria"]]
        return lines
    if not t["acceptance_criteria"]:
        return ["Not specified (the brief gives no testable condition; see open questions)"]
    return [f'{c["criterion"]} [{c["ref"]}: "{c["quote"]}"]' for c in t["acceptance_criteria"]]


def _question_lines(t, q_by_id) -> list[str]:
    return [f'{qid}: {q_by_id[qid]["question"]}' for qid in t["open_questions"] if qid in q_by_id]


def tickets_json(result: dict) -> str:
    q_by_id = {q["id"]: q for q in result["questions"]}
    out = []
    for t in result["tickets"]:
        out.append({
            "ticket_id": t["ticket_id"],
            "title": t["title"],
            "type": t["type"],
            "parent": t["parent"] or None,
            "status": t["status"],
            "status_reason": t["status_reason"],
            "description": t["description"],
            "acceptance_criteria": _criteria_lines(t),
            "source_reference": t["source_reference"],
            "dependencies": t["dependencies"],
            "open_questions": _question_lines(t, q_by_id),
            "priority": t["priority"],
            "estimate": t["estimate"],
            "deadline": t["deadline"],
            "warnings": t["warnings"],
            "python_corrections": t.get("notes", []),
        })
    return json.dumps({"tickets": out, "open_questions": result["questions"]}, indent=2, ensure_ascii=False)


def tickets_csv(result: dict) -> str:
    q_by_id = {q["id"]: q for q in result["questions"]}
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(CSV_COLUMNS)
    for t in result["tickets"]:
        w.writerow([
            t["ticket_id"], t["title"], t["type"], t["parent"], t["status"], t["description"],
            "\n".join(_criteria_lines(t)), t["source_reference"], ", ".join(t["dependencies"]),
            "\n".join(_question_lines(t, q_by_id)), t["priority"], t["estimate"], t["deadline"],
            "\n".join(t["warnings"]), "\n".join(t.get("notes", [])),
        ])
    return buf.getvalue()


def questions_csv(result: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Question ID", "Category", "Question", "Issue", "Quotes", "Refs", "Blocks tickets"])
    for q in result["questions"]:
        w.writerow([q["id"], q.get("category", ""), q.get("question", ""), q.get("issue", ""),
                    " | ".join(q.get("quotes", [])), ", ".join(q.get("refs", [])),
                    ", ".join(q.get("blocks", []))])
    return buf.getvalue()


def report_markdown(result: dict) -> str:
    q_by_id = {q["id"]: q for q in result["questions"]}
    v = result["verification"]["summary"]
    lines = ["# Brief → Dev Tasks report", "",
             f"Generated {result['meta']['generated_at']} with model `{result['meta']['model']}`.", "",
             "## Client brief (numbered)", ""]
    lines += [f"- **{s['ref']}** {s['text']}" for s in result["sentences"]]

    lines += ["", "## Open questions for the client", ""]
    if not result["questions"]:
        lines.append("_None found._")
    for q in result["questions"]:
        quotes = "; ".join(f'"{x}"' for x in q.get("quotes", []))
        lines.append(f"- **{q['id']}** [{q.get('category')}] {q.get('question')}  ")
        lines.append(f"  Source: {', '.join(q.get('refs', []))} {quotes} · Blocks: {', '.join(q.get('blocks', [])) or 'none'}")
        if q.get("scope_note"):
            lines.append(f"  _Python: {q['scope_note']}_")

    lines += ["", "## Task breakdown", ""]
    for t in result["tickets"]:
        if t["type"] == "Epic":
            lines.append("")
            lines.append(f"### {t['ticket_id']} · Epic: {t['title']}")
            lines.append(f"{t['description']}  ")
            lines.append(f"Source: {t['source_reference']}")
            lines.append("")
        else:
            lines.append(f"- **{t['ticket_id']}** [{t['type']}] {t['title']} — _{t['status']}_")

    lines += ["", "## Tickets", ""]
    for t in result["tickets"]:
        lines += [
            f"### {t['ticket_id']} — {t['title']}",
            "",
            "| Field | Value |", "|---|---|",
            f"| Type | {t['type']} |",
            f"| Parent | {t['parent'] or '—'} |",
            f"| Status | {t['status']} ({t['status_reason']}) |",
            f"| Description | {t['description']} |",
            f"| Source reference | {t['source_reference']} |",
            f"| Dependencies | {', '.join(t['dependencies']) or 'None stated in the brief'} |",
            f"| Priority | {t['priority']} |",
            f"| Estimate | {t['estimate']} |",
            f"| Deadline | {t['deadline']} |",
            "",
            "**Acceptance criteria**", "",
        ]
        lines += [f"- {c}" for c in _criteria_lines(t)]
        lines += ["", "**Open questions**", ""]
        qs = _question_lines(t, q_by_id)
        lines += [f"- {x}" for x in qs] if qs else ["- None — ready for development"]
        if t["warnings"]:
            lines += ["", "**⚠ Verification warnings**", ""] + [f"- {w}" for w in t["warnings"]]
        if t.get("notes"):
            lines += ["", "**Python corrections (AI output not trusted)**", ""] + [f"- {n}" for n in t["notes"]]
        lines.append("")

    lines += ["## Verification (Python checks against the brief)", "",
              f"- Quotes checked: {v['quotes_checked']}",
              f"- Issues found: {v['issues']}",
              f"- AI priorities/deadlines/estimates rejected: {v.get('ai_values_rejected', 0)}",
              f"- Reworded acceptance criteria replaced with the brief's words: {v.get('criteria_replaced_with_brief_words', 0)}",
              f"- Tickets ready: {v['tickets_ready']} · needing clarification: {v['tickets_need_clarification']}",
              f"- Uncovered features: {v['uncovered_work_items'] or 'none'}",
              f"- Brief sentences not used anywhere: {v.get('unused_sentences') or 'none'}",
              f"- Coverage repair needed: {result['plan'].get('coverage', {}).get('repair_attempted')}",
              f"- Tasks created by Python for items the AI missed: {result['plan'].get('coverage', {}).get('created_by_python') or 'none'}", ""]
    for i in result["verification"]["issues"]:
        lines.append(f"- ⚠ **{i['status']}** at {i['where']}: {i.get('detail', '')}")
    return "\n".join(lines) + "\n"


def save_all(result: dict, folder: Path) -> Path:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result_full.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (folder / "tickets.json").write_text(tickets_json(result), encoding="utf-8")
    # utf-8-sig so Excel opens it with the right characters
    (folder / "tickets.csv").write_text(tickets_csv(result), encoding="utf-8-sig", newline="")
    (folder / "open_questions.csv").write_text(questions_csv(result), encoding="utf-8-sig", newline="")
    (folder / "report.md").write_text(report_markdown(result), encoding="utf-8")
    return folder
