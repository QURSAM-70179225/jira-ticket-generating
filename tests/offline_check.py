"""Offline tests for the Python stages (0, 4, 5). No API key or internet needed.

Run from the task1 folder:   python tests/offline_check.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pipeline  # noqa: E402
from pipeline import (number_sentences, clean_question, find_uncovered,  # noqa: E402
                      normalise_facts, normalise_questions, normalise_plan, run_pipeline)
from tickets import build_tickets, NOT_SPECIFIED  # noqa: E402
from verify import check_quote, verify  # noqa: E402

failures = 0


def check(name, condition):
    global failures
    print(("PASS " if condition else "FAIL ") + name)
    if not condition:
        failures += 1


vague = (ROOT / "briefs" / "vague_brief.txt").read_text(encoding="utf-8")
clear = (ROOT / "briefs" / "clear_brief.txt").read_text(encoding="utf-8")
vs = number_sentences(vague)
cs = number_sentences(clear)
vtext = " ".join(s["text"] for s in vs)

# ---- Stage 0
check("Stage 0: vague brief has 12 sentences", len(vs) == 12)
check("Stage 0: clear brief has 14 sentences", len(cs) == 14)
check("Stage 0: two sentences on one line are split",
      [s["text"] for s in number_sentences("A is X. B is Y!")] == ["A is X.", "B is Y!"])
check("Stage 0: empty brief gives no sentences", number_sentences("  \n ") == [])

# ---- Stage 2 clean-up
q, changed = clean_question("What metrics (e.g., load time, response time) define fast?")
check("Stage 2: '(e.g. ...)' removed from question", q == "What metrics define fast?" and changed)
check("Stage 2: question without examples unchanged", clean_question("Which methods?") == ("Which methods?", False))

# ---- Stage 5 quote checks: real errors seen in earlier runs
check("Verify: exact quote passes",
      check_quote("We want to launch soon.", "S12", vs, vtext)["status"] == "exact")
check("Verify: wrong capital letter is caught ('We want a modern...' vs '...and we want')",
      check_quote("We want a modern fitness app for our members.", "S1", vs, vtext)["status"] == "not_found")
check("Verify: missing word is caught ('be web-only product' without 'a')",
      check_quote("this should be web-only product", "S10", vs, vtext)["status"] == "not_found")
check("Verify: non-breaking hyphen is accepted as typography only",
      check_quote("this should be a web‑only product", "S10", vs, vtext)["status"] == "normalised")
check("Verify: right quote with wrong ref is caught",
      check_quote("It should be secure.", "S2", vs, vtext)["status"] == "ref_mismatch")
check("Verify: ref that does not exist is caught",
      check_quote("It should be secure.", "S99", vs, vtext)["status"] == "ref_mismatch")
check("Verify: contradiction quote across two refs passes",
      check_quote("We need this as a mobile app for iPhone and Android.", ["S4", "S10"], vs, vtext)["status"] == "exact")

# ---- Stage 3 coverage check
plan = {"epics": [{"tasks": [{"covers": ["F1"]}]}]}
items = [{"id": "F1", "text": "a"}, {"id": "F2", "text": "b"}]
check("Stage 3: uncovered feature F2 is found", [m["id"] for m in find_uncovered(plan, items)] == ["F2"])

# ---- Stage 4 + 5 on a small hand-made plan
facts = {"features": [{"text": "Book classes", "quote": "book classes", "ref": "S3"},
                      {"text": "Leaderboard", "quote": "leaderboard", "ref": "S9"}],
         "quality_requirements": []}
questions = [
    {"id": "Q-001", "category": "contradiction", "question": "Mobile app or web only?",
     "quotes": ["We need this as a mobile app for iPhone and Android.",
                "To keep costs low, this should be a web-only product, no app store apps."],
     "refs": ["S4", "S10"], "affects": ["GENERAL"]},
    {"id": "Q-002", "category": "scope_gap", "question": "What are the booking rules?",
     "quotes": ["book classes"], "refs": ["S3"], "affects": ["Book classes"]},
    {"id": "Q-003", "category": "scope_gap", "question": "Who sees the leaderboard?",
     "quotes": ["leaderboard"], "refs": ["S9"], "affects": ["Not a real feature"]},
]
plan = {
    "work_items": [{"id": "F1", "text": "Book classes"}, {"id": "F2", "text": "Leaderboard"}],
    "coverage": {"uncovered": []},
    "epics": [{
        "title": "Members", "description": "Member features",
        "source": {"quote": "Members should be able to book classes", "ref": "S3"},
        "tasks": [
            {"key": "T1", "title": "Book a class", "type": "Story", "covers": ["F1"],
             "description": "Members should be able to book classes.",
             "acceptance_criteria": [], "source": {"quote": "book classes", "ref": "S3"},
             "depends_on": ["T9"], "question_ids": [], "priority": None, "deadline": None},
            {"key": "T2", "title": "Leaderboard", "type": "Story", "covers": ["F2"],
             "description": "A leaderboard.",
             "acceptance_criteria": [{"criterion": "Shows top 10", "quote": "top 10 members", "ref": "S9"}],
             "source": {"quote": "leaderboard to keep people motivated", "ref": "S9"},
             "depends_on": [{"key": "T1", "quote": "leaderboard to keep people motivated", "ref": "S9"}],
             "question_ids": ["Q-999"],
             "priority": {"value": "High", "quote": "invented priority", "ref": "S9"}, "deadline": None},
        ],
    }],
}
tickets, questions = build_tickets(plan, questions, facts)
by_title = {t["title"]: t for t in tickets}
report = verify(vs, facts, questions, plan, tickets)
kinds = [i["status"] for i in report["issues"]]

check("Stage 4: IDs are TASK-001.. in order", [t["ticket_id"] for t in tickets] == ["TASK-001", "TASK-002", "TASK-003"])
check("Stage 4: missing priority/deadline/estimate say 'Not specified'",
      by_title["Book a class"]["priority"] == NOT_SPECIFIED and by_title["Book a class"]["estimate"] == NOT_SPECIFIED)
check("Stage 4: 'affects' links Q-002 to the booking task", "Q-002" in by_title["Book a class"]["open_questions"])
check("Stage 4: GENERAL question Q-001 blocks the epic AND every task",
      all("Q-001" in t["open_questions"] for t in tickets))
check("Stage 4: question whose 'affects' matches nothing falls back to the task built from its sentence (S9)",
      "Q-003" in by_title["Leaderboard"]["open_questions"])
check("Stage 4: ticket with open questions = Needs clarification",
      by_title["Book a class"]["status"] == "Needs clarification")
check("Stage 4: unknown dependency T9 dropped with a warning",
      by_title["Book a class"]["dependencies"] == [] and any("T9" in w for w in by_title["Book a class"]["warnings"]))
check("Stage 4: dependency with a quote from the brief mapped to TASK-002",
      by_title["Leaderboard"]["dependencies"] == ["TASK-002"])
check("Stage 4: unknown question id Q-999 dropped with a warning",
      any("Q-999" in w for w in by_title["Leaderboard"]["warnings"]))
check("Verify: invented acceptance-criterion quote flagged", any("acceptance criterion" in i["where"] for i in report["issues"]))
check("Stage 4/Verify: invented priority never reaches the ticket",
      by_title["Leaderboard"]["priority"] == NOT_SPECIFIED
      and any(n.startswith("Rejected AI priority") for n in by_title["Leaderboard"]["notes"]))
check("Verify: unknown 'affects' feature flagged", "unknown_feature" in kinds)
check("Verify: flagged ticket carries an UNVERIFIED warning",
      any(w.startswith("UNVERIFIED") for w in by_title["Leaderboard"]["warnings"]))

# ---- malformed AI answers must not crash (bug seen in run_demo: 'str' object has no attribute 'get')
f = normalise_facts({"features": ["Book classes", {"text": "Pay", "quote": "pay online", "ref": "S6"}],
                     "integrations": "MBS system", "users": None})
check("Normalise: plain-string facts become items with empty quote",
      f["features"][0] == {"text": "Book classes", "quote": "", "ref": ""} and f["integrations"][0]["text"] == "MBS system")
check("Normalise: every fact category exists", all(isinstance(f[k], list) for k in pipeline.FACT_KEYS))
nq = normalise_questions(["What is MBS?", {"question": "Q?", "affects": "Book classes", "quotes": "x"}, 5, {}])
check("Normalise: string question kept, bad entries dropped, string fields become lists",
      len(nq) == 2 and nq[1]["affects"] == ["Book classes"] and nq[1]["quotes"] == ["x"])
np_ = normalise_plan({"epics": ["oops", {"title": "E", "tasks": ["bad", {"key": "T1", "title": "x",
                       "covers": "F1", "acceptance_criteria": ["Shows menu"], "source": "menu",
                       "priority": "High"}]}]})
t0 = np_["epics"][0]["tasks"][0]
check("Normalise: string epics/tasks dropped, string covers -> list",
      len(np_["epics"]) == 1 and len(np_["epics"][0]["tasks"]) == 1 and t0["covers"] == ["F1"])
check("Normalise: priority without a source quote is not trusted", t0["priority"] is None)

# ---- full pipeline with a fake AI: messy answers + a missed feature that needs repair
answers = iter([
    {"features": [{"text": "Book classes", "quote": "book classes", "ref": "S3"},
                  "Leaderboard"],  # one malformed item
     "integrations": [{"text": "MBS sync", "quote": "sync with our MBS system", "ref": "S7"}]},
    {"questions": [{"category": "vague", "question": "What does fast mean (e.g. 2s)?",
                    "quotes": ["fast"], "refs": ["S2"], "affects": ["GENERAL"]}]},
    {"epics": [{"title": "Members", "source": {"quote": "book classes", "ref": "S3"},
                "tasks": [{"key": "T1", "title": "Book a class", "covers": ["F1"],
                           "source": {"quote": "book classes", "ref": "S3"}}]}]},
    {"epics": [{"title": "Members", "tasks": [
        {"key": "T1", "title": "Leaderboard", "covers": ["F2"], "source": {"quote": "leaderboard", "ref": "S9"}},
        {"key": "T2", "title": "Sync MBS", "covers": ["I1"],
         "source": {"quote": "sync with our MBS system", "ref": "S7"}}]}]},
])
real_call = pipeline.call_llm
pipeline.call_llm = lambda *a, **k: next(answers)
res = run_pipeline(vague)
pipeline.call_llm = real_call
cov = res["plan"]["coverage"]
check("Fake run: first try missed F2 and I1, repair was asked", cov["uncovered_first_try"] == ["F2", "I1"] and cov["repair_attempted"])
check("Fake run: after repair nothing is uncovered", cov["uncovered"] == [])
check("Fake run: repaired task with clashing key T1 got a new key",
      len({t["key"] for e in res["plan"]["epics"] for t in e["tasks"]}) == 3)
check("Fake run: example removed from question", res["questions"][0]["question"] == "What does fast mean?")
check("Fake run: malformed fact flagged by verification (no quote)",
      any(i["where"].startswith("fact features[1]") for i in res["verification"]["issues"]))

# ---- Stage 4 rejects AI values that are not stated, and keeps criteria in the brief's words
facts2 = {"features": [{"text": "Book classes", "quote": "book classes", "ref": "S3"}],
          "constraints": [{"text": "keep costs low", "quote": "To keep costs low", "ref": "S10"}],
          "deadlines": [{"text": "launch soon", "quote": "We want to launch soon.", "ref": "S12"}],
          "priorities": [], "estimates": [], "quality_requirements": []}
plan2 = {"work_items": [{"id": "F1", "text": "Book classes"}], "coverage": {"uncovered": []},
         "epics": [{"title": "E", "source": {"quote": "book classes", "ref": "S3"}, "tasks": [{
             "key": "T1", "title": "Book", "type": "Story", "covers": ["F1"], "description": "x",
             "source": {"quote": "book classes", "ref": "S3"}, "depends_on": [], "question_ids": [],
             "acceptance_criteria": [
                 {"criterion": "Members can select a class and confirm the booking",
                  "quote": "Members should be able to book classes", "ref": "S3"},
                 {"criterion": "Members should be able to book classes",
                  "quote": "Members should be able to book classes", "ref": "S3"}],
             "priority": {"value": "keep costs low", "quote": "To keep costs low", "ref": "S10"},
             "deadline": {"value": "launch soon", "quote": "We want to launch soon.", "ref": "S12"}}]}]}
tk, _ = build_tickets(plan2, [], facts2, vs)
task = tk[1]
check("Stage 4: constraint 'keep costs low' rejected as a priority", task["priority"] == NOT_SPECIFIED)
check("Stage 4: 'launch soon' rejected as a deadline", task["deadline"] == NOT_SPECIFIED)
check("Stage 4: reworded criterion ('confirm the booking') replaced by the brief's words, duplicate removed",
      [c["criterion"] for c in task["acceptance_criteria"]] == ["Members should be able to book classes"])
check("Stage 4: every correction is recorded in notes", len(task["notes"]) == 3)
facts3 = dict(facts2, deadlines=[{"text": "go live", "quote": "must go live by 15 December 2026", "ref": "S14"}],
              priorities=[{"text": "menu", "quote": "menu pages are the highest priority", "ref": "S13"}])
plan3 = json.loads(json.dumps(plan2))
plan3["epics"][0]["tasks"][0]["priority"] = {"value": "Highest", "quote": "highest priority", "ref": "S13"}
plan3["epics"][0]["tasks"][0]["deadline"] = {"value": "15 December 2026", "quote": "15 December 2026", "ref": "S14"}
tk3, _ = build_tickets(plan3, [], facts3)
check("Stage 4: a stated priority and a real date are kept",
      tk3[1]["priority"].startswith("Highest") and tk3[1]["deadline"].startswith("15 December 2026"))

# ---- dependencies the brief does not state become open questions; unused constraints and sentences
plan4 = json.loads(json.dumps(plan2))
plan4["epics"][0]["tasks"].append({
    "key": "T2", "title": "Pay", "type": "Story", "covers": [], "description": "pay",
    "source": {"quote": "Members should be able to pay online for memberships.", "ref": "S6"},
    "depends_on": [{"key": "T1", "quote": "", "ref": ""}], "question_ids": [],
    "acceptance_criteria": [{"criterion": "Members should be able to pay online for memberships.",
                             "quote": "Members should be able to pay online for memberships.", "ref": "S6"}],
    "priority": None, "deadline": None})
facts4 = dict(facts2, constraints=[{"text": "web only", "ref": "S10",
                                    "quote": "To keep costs low, this should be a web-only product, no app store apps."}])
qs4 = []
tk4, qs4 = build_tickets(plan4, qs4, facts4, vs)
pay = next(t for t in tk4 if t["title"] == "Pay")
check("Stage 4: dependency without evidence is NOT added", pay["dependencies"] == [])
check("Stage 4: ...it becomes an open question linked to the ticket",
      len(qs4) == 1 and qs4[0]["category"] == "dependency" and qs4[0]["id"] in pay["open_questions"]
      and pay["status"] == "Needs clarification")
check("Stage 4: constraint used by no task is added to the epic as a project constraint",
      any(c.get("project_constraint") and c["ref"] == "S10" for c in tk4[0]["acceptance_criteria"]))
rep4 = verify(vs, facts4, qs4, plan4, tk4)
unused = rep4["summary"]["unused_sentences"]
check("Verify: brief sentences that reach no ticket are reported (e.g. S2, S4), used ones are not",
      "S2" in unused and "S4" in unused and "S3" not in unused and "S6" not in unused and "S10" not in unused)

# ---- smaller model behaviour seen in run 4: "(S8)" inside quotes, everything GENERAL, missed items
nq2 = normalise_questions([{"question": "Q?", "quotes": ["It should be secure. (S8)", "x [S2, S3]"]}])
check("Normalise: '(S8)' ref markers removed from quotes", nq2[0]["quotes"] == ["It should be secure.", "x"])
qs5 = [{"id": "Q-001", "category": "missing", "question": "Booking rules?", "quotes": ["book classes"],
        "refs": ["S3"], "affects": ["GENERAL"]},
       {"id": "Q-002", "category": "missing", "question": "Launch date?", "quotes": ["We want to launch soon."],
        "refs": ["S12"], "affects": ["GENERAL"]}]
plan5 = json.loads(json.dumps(plan4))
tk5, qs5 = build_tickets(plan5, qs5, facts4, vs)
book = next(t for t in tk5 if t["title"] == "Book")
pay5 = next(t for t in tk5 if t["title"] == "Pay")
check("Stage 4: GENERAL question about S3 scoped to the S3 task only",
      "Q-001" in book["open_questions"] and "Q-001" not in pay5["open_questions"] and qs5[0].get("scope_note"))
check("Stage 4: GENERAL question with no matching sentence still blocks every ticket",
      all("Q-002" in t["open_questions"] for t in tk5))
sent_rep = verify(vs, {"users": [{"text": "Admins", "quote": "Admins should get reports.", "ref": "S11"}],
                       "goals": [{"text": "app", "quote": "x", "ref": "S1"}]}, [], {"coverage": {}}, [])
check("Verify: 'Admins should get reports.' is a requirement, so being a user fact is not enough",
      "S11" in sent_rep["summary"]["unused_sentences"] and "S1" not in sent_rep["summary"]["unused_sentences"])
answers2 = iter([
    {"features": [{"text": "Book classes", "quote": "book classes", "ref": "S3"}],
     "quality_requirements": [{"text": "secure", "quote": "It should be secure.", "ref": "S8"}]},
    {"questions": []},
    {"epics": [{"title": "M", "source": {"quote": "book classes", "ref": "S3"}, "tasks": []}]},
    {"epics": []},
])
pipeline.call_llm = lambda *a, **k: next(answers2)
res2 = run_pipeline(vague)
pipeline.call_llm = real_call
cov2 = res2["plan"]["coverage"]
check("Fake run 2: items still missing after repair get a Python-made task, nothing uncovered",
      cov2["created_by_python"] == ["F1", "R1"] and cov2["uncovered"] == [])
sec = next(t for t in res2["tickets"] if "R1" in t["covers"])
check("Fake run 2: Python-made task uses only the brief's words and says so",
      sec["description"] == "It should be secure." and sec["acceptance_criteria"] == []
      and any("Created by Python" in n for n in sec["notes"]))

# ---- Stage 4 + 5 on the real saved outputs (if they exist)
for name in ("clear_brief", "vague_brief"):
    folder = ROOT / "outputs" / name
    full = folder / "result_full.json"
    if full.exists():
        r = json.loads(full.read_text(encoding="utf-8"))
        t2, q2 = build_tickets(r["plan"], r["questions"], r["facts"], r["sentences"])
        rep = verify(r["sentences"], r["facts"], q2, r["plan"], t2)
        print(f"INFO {name}: {len(t2)} tickets, verification {rep['summary']}")

print(f"\n{failures} failure(s)")
sys.exit(1 if failures else 0)
