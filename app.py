"""Streamlit UI: paste or upload a brief -> marked-up brief, ticket board, client questions, downloads.

Run:  streamlit run app.py
No login: anyone who opens the page can use it.

Design idea: the brief is the hero. Every sentence is marked with a highlighter
showing what it became (a ticket, a question for the client, a project
constraint, or nothing), so the "never assume" rule is visible at a glance.
"""
import html
import json
import re
from pathlib import Path

import streamlit as st

from export import questions_csv, report_markdown, tickets_csv, tickets_json
from pipeline import MODEL, run_pipeline

st.set_page_config(page_title="Brief to tickets", page_icon="🖍️", layout="wide")

E = html.escape


def show(markup: str):
    """Render HTML. Lines are stripped so Markdown never turns indented HTML into a code block."""
    st.markdown("\n".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


# ---------------------------------------------------------------- style
show("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Instrument+Sans:wght@400;500;600&display=swap');
:root{
--paper:#F6F7F9; --sheet:#FFFFFF; --ink:#1E2A3B; --ink-soft:#56657A; --rule:#D9DEE5;
--hl-ticket:#FFE766; --hl-question:#FFB3C8; --hl-constraint:#CFC4FF; --hl-ready:#A8EBD3;
--alert:#B42318;
}
html, body, [data-testid="stAppViewContainer"], .stApp{background:var(--paper); color:var(--ink);}
html, body, .stApp, .stMarkdown, button, input, textarea, select{font-family:'Instrument Sans', system-ui, sans-serif;}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem; max-width:1320px;}
h1,h2,h3,h4{font-family:'Bricolage Grotesque', 'Instrument Sans', sans-serif !important; color:var(--ink); letter-spacing:-0.01em;}
.mast{display:flex; align-items:flex-end; justify-content:space-between; gap:2rem; flex-wrap:wrap;
border-bottom:2px solid var(--ink); padding-bottom:1rem; margin-bottom:1.6rem;}
.mast h1{font-size:2.6rem; line-height:1.05; margin:0; font-weight:700; padding:0;}
.mast h1 .arrow{display:inline-block; padding:0 .3em; background:linear-gradient(104deg,transparent 2%,var(--hl-ticket) 5%,var(--hl-ticket) 94%,transparent 97%); border-radius:2px;}
.mast p{max-width:46ch; margin:0; color:var(--ink-soft); font-size:1.02rem; line-height:1.5;}
.sheet{background:var(--sheet); border:1px solid var(--rule); border-radius:4px; padding:1.6rem 1.7rem 1.3rem;
box-shadow:0 1px 0 var(--rule), 0 12px 28px -18px rgba(30,42,59,.35);}
.sheet h2{font-size:1.25rem; margin:0 0 .9rem; font-weight:700; padding:0;}
.sent{display:grid; grid-template-columns:2.4rem 1fr; gap:0 .6rem; margin:.15rem 0; line-height:1.75; font-size:1.02rem;}
.sent .ref{color:var(--ink-soft); font-variant-numeric:tabular-nums; font-size:.85rem; padding-top:.2rem; text-align:right;}
.mark{padding:.08em .25em; border-radius:3px; -webkit-box-decoration-break:clone; box-decoration-break:clone;}
.mark.ticket{background:linear-gradient(100deg,transparent .3em,var(--hl-ticket) .4em,var(--hl-ticket) calc(100% - .3em),transparent calc(100% - .2em));}
.mark.question{background:linear-gradient(100deg,transparent .3em,var(--hl-question) .4em,var(--hl-question) calc(100% - .3em),transparent calc(100% - .2em));}
.mark.constraint{background:linear-gradient(100deg,transparent .3em,var(--hl-constraint) .4em,var(--hl-constraint) calc(100% - .3em),transparent calc(100% - .2em));}
.mark.background{color:var(--ink-soft);}
.mark.unused{text-decoration:underline wavy var(--alert); text-underline-offset:4px;}
.sent .uses{grid-column:2; font-size:.8rem; color:var(--ink-soft); margin:-.15rem 0 .35rem;}
.legend{display:flex; flex-wrap:wrap; gap:.4rem 1rem; margin-top:1rem; padding-top:.8rem; border-top:1px dashed var(--rule); font-size:.85rem; color:var(--ink-soft);}
.legend span{display:inline-flex; align-items:center; gap:.4rem;}
.sw{display:inline-block; width:1.4rem; height:.8rem; border-radius:2px;}
.summary{font-size:1.15rem; line-height:1.55; margin:.2rem 0 1.1rem; max-width:62ch;}
.summary b{font-family:'Bricolage Grotesque', sans-serif; font-weight:700;}
.summary .bad{color:var(--alert);}
.col-head{display:flex; align-items:center; gap:.55rem; font-family:'Bricolage Grotesque', sans-serif; font-weight:700; font-size:1.05rem; margin:.2rem 0 .6rem;}
.col-head .count{font-family:'Instrument Sans', sans-serif; font-weight:500; color:var(--ink-soft); font-size:.9rem;}
.tk{background:var(--sheet); border:1px solid var(--rule); border-left:5px solid var(--hl-question); border-radius:3px; padding:.7rem .85rem .75rem; margin-bottom:.6rem;}
.tk.ready{border-left-color:#3BB98B;}
.tk-top{display:flex; justify-content:space-between; align-items:baseline; gap:.5rem; font-size:.8rem; color:var(--ink-soft);}
.tk-id{font-variant-numeric:tabular-nums; font-weight:600; color:var(--ink);}
.tk-title{font-weight:600; font-size:.98rem; margin:.25rem 0 .35rem; line-height:1.3;}
.tk-meta{display:flex; flex-wrap:wrap; gap:.35rem; font-size:.78rem;}
.pill{display:inline-block; padding:.05rem .45rem; border-radius:999px; border:1px solid var(--rule); color:var(--ink-soft); background:var(--paper); margin:0;}
.pill.q{background:#FFE5EC; border-color:#FFC2D3; color:#7A1F3D;}
.pill.warn{background:#FDECEA; border-color:#F5B5AE; color:var(--alert);}
.pill.fix{background:#EEEAFE; border-color:#D5CCFF; color:#3E2E8C;}
.detail{background:var(--sheet); border:1px solid var(--rule); border-radius:4px; padding:1.2rem 1.4rem;}
.detail h3{margin:.1rem 0 .2rem; font-size:1.4rem; padding:0;}
.detail .sub{color:var(--ink-soft); font-size:.9rem; margin-bottom:.9rem;}
.fields{display:grid; grid-template-columns:9.5rem 1fr; gap:.35rem 1rem; font-size:.93rem; margin:.4rem 0 1rem;}
.fields dt{color:var(--ink-soft); font-weight:400;} .fields dd{margin:0;}
.ns{color:var(--ink-soft); font-style:italic;}
.quote{border-left:3px solid var(--hl-ticket); padding:.15rem 0 .15rem .75rem; margin:.35rem 0 .55rem; line-height:1.5;}
.quote .r{color:var(--ink-soft); font-size:.8rem; margin-left:.4rem;}
.detail h4{font-size:1rem; margin:1rem 0 .3rem; padding:0;}
.qcard{background:var(--sheet); border:1px solid var(--rule); border-radius:3px; padding:.85rem 1rem; margin-bottom:.65rem;}
.qtop{display:flex; flex-wrap:wrap; gap:.6rem; align-items:baseline; font-size:.82rem; color:var(--ink-soft);}
.qid{font-weight:600; color:var(--ink); font-variant-numeric:tabular-nums;}
.qtext{font-size:1.02rem; font-weight:500; margin:.3rem 0 .4rem; line-height:1.4;}
.qcard .quote{border-left-color:var(--hl-question);}
.qcard .uses{font-size:.8rem; color:var(--ink-soft);}
.qcat{display:inline-block; padding:.02rem .45rem; border-radius:2px; color:var(--ink);}
.cat-missing{background:#FFE5EC;} .cat-vague{background:#FFF3B0;} .cat-contradiction{background:#FFD0C2;}
.cat-undefined_term{background:#DCEBFF;} .cat-scope_gap{background:#E4F7EE;} .cat-dependency{background:#EEEAFE;}
.check{display:grid; grid-template-columns:1.6rem 1fr; gap:.5rem; padding:.55rem 0; border-bottom:1px solid var(--rule);}
.check .ok{color:#2E9C73; font-weight:700;} .check .no{color:var(--alert); font-weight:700;}
.check small{color:var(--ink-soft);}
.stTabs [data-baseweb="tab-list"]{gap:1.4rem; border-bottom:1px solid var(--rule);}
.stTabs [data-baseweb="tab"]{font-family:'Bricolage Grotesque', sans-serif; font-weight:600; font-size:1rem; padding:.4rem 0;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--ink); height:3px;}
.stButton > button, .stDownloadButton > button{border-radius:3px; font-weight:600;}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"]{background:var(--ink); border-color:var(--ink); color:#fff;}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover{background:#2D3E55; border-color:#2D3E55; color:#fff;}
textarea{font-size:1rem !important; line-height:1.6 !important;}
button:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible{outline:3px solid #3B6FD8 !important; outline-offset:2px;}
@media (max-width: 800px){ .mast h1{font-size:2rem;} .fields{grid-template-columns:1fr;} .sent{grid-template-columns:2rem 1fr;} }
</style>
""")

# ---------------------------------------------------------------- masthead
show("""
<div class="mast">
<h1>Client brief <span class="arrow">to</span> dev tickets</h1>
<p>Paste a brief. Every ticket points back to the sentence it came from, and anything
the brief doesn't say becomes a question for the client, never a guess.</p>
</div>
""")

# ---------------------------------------------------------------- saved results (no AI call)
saved = {p.parent.name: p for p in sorted(Path("outputs").glob("*/result_full.json"))}
with st.sidebar:
    st.markdown("### Saved runs")
    st.caption("Open an earlier result without calling the AI.")
    if saved:
        pick = st.selectbox("Saved run", ["—"] + list(saved), label_visibility="collapsed")
        if st.button("Open saved run", disabled=pick == "—"):
            st.session_state["result"] = json.loads(saved[pick].read_text(encoding="utf-8"))
            st.session_state["source"] = f"saved run outputs/{pick}"
    else:
        st.caption("No saved runs yet. Run `python run_demo.py` to create some.")
    if st.session_state.get("result") and st.button("Start a new brief"):
        st.session_state.pop("result", None)
        st.rerun()

result = st.session_state.get("result")


# ---------------------------------------------------------------- helpers
def refs_of(v) -> list[str]:
    if isinstance(v, list):
        return [str(x) for x in v]
    return [x.strip() for x in str(v or "").split(",") if x.strip()]


def source_ref(t) -> str:
    m = re.match(r'(\S.*?): "', t["source_reference"])
    return m.group(1) if m else ""


def sentence_roles(r: dict) -> dict:
    """What each sentence became: ticket / constraint / question / background / unused."""
    roles = {s["ref"]: {"tickets": [], "questions": [], "constraint": False} for s in r["sentences"]}
    for t in r["tickets"]:
        found = refs_of(source_ref(t))
        for c in t["acceptance_criteria"]:
            if c.get("project_constraint"):
                for ref in refs_of(c.get("ref")):
                    if ref in roles:
                        roles[ref]["constraint"] = True
            else:
                found += refs_of(c.get("ref"))
        if t["type"] != "Epic":
            for ref in set(found):
                if ref in roles:
                    roles[ref]["tickets"].append(t["ticket_id"])
    for q in r["questions"]:
        for ref in refs_of(q.get("refs")):
            if ref in roles:
                roles[ref]["questions"].append(q["id"])
    unused = set(r["verification"]["summary"].get("unused_sentences") or [])
    for ref, info in roles.items():
        if ref in unused:
            info["kind"] = "unused"
        elif info["tickets"]:
            info["kind"] = "ticket"
        elif info["constraint"]:
            info["kind"] = "constraint"
        elif info["questions"]:
            info["kind"] = "question"
        else:
            info["kind"] = "background"
    return roles


def brief_sheet(r: dict):
    roles = sentence_roles(r)
    rows = ['<div class="sheet"><h2>The brief, marked up</h2>']
    for s in r["sentences"]:
        info = roles[s["ref"]]
        uses = []
        if info["tickets"]:
            uses.append("on " + ", ".join(dict.fromkeys(info["tickets"])))
        if info["constraint"]:
            uses.append("project constraint on every epic")
        if info["questions"]:
            uses.append("asked in " + ", ".join(dict.fromkeys(info["questions"])))
        if info["kind"] == "unused":
            uses.insert(0, "not on any ticket, check by hand")
        rows.append(f'<div class="sent"><span class="ref">{E(s["ref"])}</span>'
                    f'<span><span class="mark {info["kind"]}">{E(s["text"])}</span></span>'
                    + (f'<div class="uses">{E("; ".join(uses))}</div>' if uses else "") + "</div>")
    rows.append('<div class="legend">'
                '<span><i class="sw" style="background:var(--hl-ticket)"></i>became a ticket</span>'
                '<span><i class="sw" style="background:var(--hl-question)"></i>only asked about</span>'
                '<span><i class="sw" style="background:var(--hl-constraint)"></i>project constraint</span>'
                '<span><i class="sw" style="border-bottom:2px solid var(--alert);height:.5rem"></i>not used, check</span>'
                '</div></div>')
    show("".join(rows))


def cell(value: str) -> str:
    return f'<span class="ns">{E(value)}</span>' if value == "Not specified" else E(value)


def ref_text(ref) -> str:
    return ", ".join(refs_of(ref))


# ---------------------------------------------------------------- input view
if not result:
    examples = {p.stem.replace("_", " ").capitalize(): p for p in sorted(Path("briefs").glob("*_brief.txt"))}
    left, right = st.columns([7, 4], gap="large")
    with right:
        st.markdown("#### Start from a file")
        choice = st.radio("Example brief", ["None"] + list(examples), index=0)
        upload = st.file_uploader("Upload a .txt brief", type=["txt"])
        st.caption(f"Model: {MODEL}. The AI reads the brief in three steps, then Python builds "
                   "the tickets and checks every quote against the brief.")
    default_text = ""
    if upload is not None:
        default_text = upload.read().decode("utf-8", errors="replace")
    elif choice != "None":
        default_text = examples[choice].read_text(encoding="utf-8")
    with left:
        brief = st.text_area("Client brief", value=default_text, height=330,
                             placeholder="Paste the client's brief here, exactly as they sent it.")
        go = st.button("Turn into tickets", type="primary", disabled=not brief.strip())
    if go:
        try:
            with st.status("Reading the brief…", expanded=True) as status:
                result = run_pipeline(brief, progress=lambda name: st.write(name))
                status.update(label="Tickets ready", state="complete", expanded=False)
            st.session_state["result"] = result
            st.session_state["source"] = "this run"
            st.rerun()
        except Exception as e:
            st.error(f"Stopped: {e}")
            st.caption("A timeout usually means a slow connection, so try again. If the daily limit is "
                       "used up, open a saved run from the sidebar instead.")
    st.stop()

# ---------------------------------------------------------------- result view
v = result["verification"]["summary"]
cov = result["plan"].get("coverage", {})
tickets = result["tickets"]
questions = result["questions"]
q_by_id = {q["id"]: q for q in questions}
tasks = [t for t in tickets if t["type"] != "Epic"]
ready = [t for t in tasks if t["status"].startswith("Ready")]
waiting = [t for t in tasks if not t["status"].startswith("Ready")]
problems = v["issues"]

left, right = st.columns([5, 7], gap="large")
with left:
    brief_sheet(result)
    st.caption(f"Showing {st.session_state.get('source', 'this run')}, model {result['meta']['model']}.")

with right:
    problem_text = (f'<span class="bad"><b>{problems}</b> need a look</span>' if problems else "<b>none</b>")
    n_epics = len(tickets) - len(tasks)
    show(f'<p class="summary"><b>{len(tasks)}</b> tickets in <b>{n_epics}</b> epic{"s" if n_epics != 1 else ""}, '
         f'<b>{len(ready)}</b> ready to build. <b>{len(questions)}</b> questions for the client. '
         f'<b>{v["quotes_checked"]}</b> quotes checked against the brief; problems found: {problem_text}.</p>')

    tab_board, tab_q, tab_checks, tab_export = st.tabs(
        ["Ticket board", f"Questions for the client ({len(questions)})", "Checks", "Export"])

    # ---- board
    with tab_board:
        epic_title = {t["ticket_id"]: t["title"] for t in tickets if t["type"] == "Epic"}

        def card(t):
            n_q = len(t["open_questions"])
            pills = [f'<span class="pill">{E(t["type"])}</span>']
            if source_ref(t):
                pills.append(f'<span class="pill">{E(source_ref(t))}</span>')
            if n_q:
                pills.append(f'<span class="pill q">{n_q} question{"s" if n_q != 1 else ""}</span>')
            if t["warnings"]:
                pills.append(f'<span class="pill warn">{len(t["warnings"])} warning{"s" if len(t["warnings"]) != 1 else ""}</span>')
            if t.get("notes"):
                pills.append(f'<span class="pill fix">{len(t["notes"])} Python fix{"es" if len(t["notes"]) != 1 else ""}</span>')
            cls = "ready" if t["status"].startswith("Ready") else ""
            return (f'<div class="tk {cls}"><div class="tk-top"><span class="tk-id">{E(t["ticket_id"])}</span>'
                    f'<span>{E(epic_title.get(t["parent"], ""))}</span></div>'
                    f'<div class="tk-title">{E(t["title"])}</div><div class="tk-meta">{"".join(pills)}</div></div>')

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            show(f'<div class="col-head"><span class="sw" style="background:var(--hl-question)"></span>'
                 f'Waiting on the client <span class="count">{len(waiting)}</span></div>'
                 + ("".join(card(t) for t in waiting) or '<p class="ns">Nothing is waiting.</p>'))
        with c2:
            show(f'<div class="col-head"><span class="sw" style="background:var(--hl-ready)"></span>'
                 f'Ready to build <span class="count">{len(ready)}</span></div>'
                 + ("".join(card(t) for t in ready) or
                    '<p class="ns">Nothing yet. Every ticket has an open question or no testable criteria.</p>'))

        st.markdown("#### Open a ticket")
        labels = {f'{t["ticket_id"]}  {t["title"]}': t for t in tickets}
        sel = labels[st.selectbox("Ticket", list(labels), label_visibility="collapsed")]

        crit_html = "".join(
            f'<div class="quote">{"Project constraint: " if c.get("project_constraint") else ""}{E(c["criterion"])}'
            f'<span class="r">{E(ref_text(c.get("ref")))}</span></div>' for c in sel["acceptance_criteria"])
        if sel["type"] == "Epic":
            crit_html = f'<p>Child tickets: {E(", ".join(sel.get("children", [])))}</p>' + crit_html
        elif not sel["acceptance_criteria"]:
            crit_html = ('<p class="ns">Not specified. The brief gives no testable condition, '
                         'so this waits on the questions below.</p>')
        q_html = "".join(f'<div class="quote" style="border-left-color:var(--hl-question)"><b>{E(qid)}</b> '
                         f'{E(q_by_id[qid]["question"])}</div>' for qid in sel["open_questions"] if qid in q_by_id)
        q_html = q_html or "<p>None. This ticket can be built as written.</p>"
        extra = ""
        if sel["warnings"]:
            extra += "<h4>Warnings from the checks</h4>" + "".join(
                f'<div class="quote" style="border-left-color:var(--alert)">{E(w)}</div>' for w in sel["warnings"])
        if sel.get("notes"):
            extra += "<h4>Corrected by Python</h4>" + "".join(
                f'<div class="quote" style="border-left-color:var(--hl-constraint)">{E(n)}</div>' for n in sel["notes"])
        part = f', part of {E(sel["parent"])}' if sel["parent"] else ""
        deps = E(", ".join(sel["dependencies"])) or '<span class="ns">Nothing stated in the brief</span>'
        show(f"""
<div class="detail">
<h3>{E(sel["title"])}</h3>
<div class="sub">{E(sel["ticket_id"])}, {E(sel["type"])}{part}. {E(sel["status"])}: {E(sel["status_reason"])}.</div>
<dl class="fields">
<dt>Description</dt><dd>{E(sel["description"])}</dd>
<dt>From the brief</dt><dd>{E(sel["source_reference"])}</dd>
<dt>Depends on</dt><dd>{deps}</dd>
<dt>Priority</dt><dd>{cell(sel["priority"])}</dd>
<dt>Estimate</dt><dd>{cell(sel["estimate"])}</dd>
<dt>Deadline</dt><dd>{cell(sel["deadline"])}</dd>
</dl>
<h4>Acceptance criteria, in the brief's words</h4>{crit_html}
<h4>Open questions</h4>{q_html}
{extra}
</div>""")

    # ---- questions
    with tab_q:
        names = {"missing": "Missing", "vague": "Vague", "contradiction": "Contradiction",
                 "undefined_term": "Undefined term", "scope_gap": "Scope gap", "dependency": "Dependency"}
        if not questions:
            st.info("No open questions. The brief answers everything the tickets need.")
        else:
            present = sorted({q.get("category", "missing") for q in questions},
                             key=lambda c: list(names).index(c) if c in names else 99)
            pick_cat = st.radio("Show", ["All"] + present, horizontal=True, label_visibility="collapsed",
                                format_func=lambda c: c if c == "All" else names.get(c, c))
            out = []
            for q in questions:
                cat = q.get("category", "missing")
                if pick_cat != "All" and cat != pick_cat:
                    continue
                quotes = "".join(f'<div class="quote">{E(x)}<span class="r">{E(", ".join(q.get("refs", [])))}</span></div>'
                                 for x in q.get("quotes", []))
                scope = f'<div class="uses">{E(q["scope_note"])}</div>' if q.get("scope_note") else ""
                out.append(f'<div class="qcard"><div class="qtop"><span class="qid">{E(q["id"])}</span>'
                           f'<span class="qcat cat-{E(cat)}">{E(names.get(cat, cat))}</span>'
                           f'<span>blocks {E(", ".join(q.get("blocks", [])) or "no ticket")}</span></div>'
                           f'<div class="qtext">{E(q.get("question", ""))}</div>{quotes}{scope}</div>')
            show("".join(out))
            st.download_button("Download questions for the client (CSV)", questions_csv(result).encode("utf-8-sig"),
                               "open_questions.csv", "text/csv")

    # ---- checks
    with tab_checks:
        def row(ok, title, detail):
            mark = '<span class="ok">✓</span>' if ok else '<span class="no">✕</span>'
            return f'<div class="check">{mark}<div>{E(title)}<br><small>{E(detail)}</small></div></div>'

        issues = result["verification"]["issues"]
        kinds = {i["status"] for i in issues}
        show("".join([
            row(not kinds & {"not_found", "ref_mismatch", "missing"},
                "Every quote is in the brief, in the sentence it cites",
                f'{v["quotes_checked"]} quotes checked word for word, case-sensitive.'),
            row(not cov.get("uncovered"), "Every feature and requirement has a ticket",
                f'{cov.get("work_items", 0)} items. Missed in the first AI answer: '
                f'{", ".join(cov.get("uncovered_first_try") or []) or "none"}. Made by Python after the repair: '
                f'{", ".join(cov.get("created_by_python") or []) or "none"}.'),
            row(not v.get("unused_sentences"), "Every sentence of the brief reaches a ticket",
                f'Not on any ticket: {", ".join(v.get("unused_sentences") or []) or "none"}.'),
            row("unlinked" not in kinds and "unknown_feature" not in kinds,
                "Every question is linked to the tickets it blocks", f"{len(questions)} questions."),
            row(True, "Unstated priorities, deadlines and estimates are refused",
                f'{v.get("ai_values_rejected", 0)} AI values rejected and left as "Not specified".'),
            row(True, "Acceptance criteria use the brief's words",
                f'{v.get("criteria_replaced_with_brief_words", 0)} reworded criteria replaced by the exact quote.'),
        ]))
        if issues:
            st.markdown("#### Everything the checks flagged")
            show("".join(f'<div class="check"><span class="no">!</span><div>{E(i["where"])}'
                         f'<br><small>{E(i.get("detail", ""))}</small></div></div>' for i in issues))

    # ---- export
    with tab_export:
        st.markdown("The CSV imports into Jira: map *Title* to *Summary* and *Type* to *Issue Type*.")
        d1, d2 = st.columns(2)
        d1.download_button("Tickets for Jira (CSV)", tickets_csv(result).encode("utf-8-sig"), "tickets.csv",
                           "text/csv", type="primary")
        d2.download_button("Tickets (JSON)", tickets_json(result), "tickets.json", "application/json")
        d3, d4 = st.columns(2)
        d3.download_button("Questions for the client (CSV)", questions_csv(result).encode("utf-8-sig"),
                           "open_questions.csv", "text/csv", key="q_export")
        d4.download_button("Full report (Markdown)", report_markdown(result), "report.md", "text/markdown")
        with st.expander("Every stage's raw output (JSON)"):
            st.json(result, expanded=False)
