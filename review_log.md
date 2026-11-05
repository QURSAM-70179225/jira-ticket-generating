# Review log — testing and fixes, step by step

Each stage was run on both briefs, compared line by line with the brief, and
fixed before moving on. The vague brief was scored against
`briefs/vague_brief_planted_issues.txt` (15 planted issues).

## Stage 1 — Extract

| Run | Problem found | Fix |
|---|---|---|
| 1 | Clear brief failed with an SSL handshake timeout (network, not code) | Groq client now uses `timeout=60, max_retries=3` |
| 1 | "fast", "user-friendly", "secure" were listed as *features* (would become "build fast" tickets) | New category `quality_requirements` (prompt rules 6–7) |
| 1 | Leaderboard listed as a *goal*, so it would get no ticket | Rule 6: every requested capability is a feature, even "later" ones |
| 1 | "iPhone", "Android" in `terms_used` (would trigger "what is Android?") | Rule 5: only client-specific names / acronyms |
| 2 | Clear brief: `users` had customers but not "bakery staff" (S9–S11) | Rule 8: every role that uses or operates the system |
| 2 | Same brief, two runs: "Sync with MBS" moved between `integrations` and `features` | Noted as LLM variation → Stage 3 counts integrations as work items too |

## Stage 2 — Detect gaps (vague brief vs answer key)

| Test | Found | Partial | Missed | Invented |
|---|---|---|---|---|
| 1 | 11 | 2 | 2 (booking rules, user roles/login) | 0 |
| 2 | 14 | 0 | 1 (user roles/login) | 0 |
| 3 | **15** | 0 | 0 | 0 |

Problems found and fixed:

- Questions contained suggestions such as "(e.g., REST API, SOAP)" or
  "(e.g., PDF, CSV)", which put ideas in the client's mouth. The prompt rule
  alone did not stop it (test 2 still had 7), so **Python now removes
  `(e.g. …)` lists** (`clean_question`) and records `examples_removed`.
- Payment and report questions were labelled `missing` instead of
  `scope_gap` → clearer category definitions.
- No systematic coverage → rule 6: check each feature, each role
  (must ask about access/login), each integration (data, direction,
  frequency), each "later" feature (in scope now?).
- Clear brief went from 4/8 sensible questions to 14 including developer
  decisions (hosting, email service, photo formats, cart timeout) → rule 7:
  ask only what the client must decide. Result: 8 client questions.
- Two quotes were not word for word: "We want a modern fitness app…" (brief:
  "…and **we** want…") and "this should be web-only product" (brief: "be **a**
  web-only product"). Kept as test cases for the Stage 5 verifier
  (`tests/offline_check.py` checks both are caught).

Known limitation: reworded duplicates remain (e.g. "target launch date" and
"exact launch deadline").

## Stage 3 — Break down

Run 1 problems (checked against the brief):

- Clear brief: **no tasks for S10 (mark Ready/Collected) or S11
  (add/edit/remove products)** — two features silently dropped.
- Clear brief: S13 priority and S14 go-live date ignored (all `null`).
- Clear brief: "Display cash-on-pickup payment option" stretched S7 into a screen.
- Vague brief: "Future enhancements" epic with **no tasks** (leaderboard lost);
  no "Quality requirements" epic; a task "Resolve platform delivery approach"
  turned the contradiction into a ticket.

Root cause: in a big step the model drops items. Asking more politely is not
reliable, so the fix is in code:

- Python numbers every feature / integration / quality requirement
  (`F1…`, `I1…`, `R1…`); each task must list what it `covers`.
- Python finds uncovered items and sends them back to the AI **once** with an
  error message ("these work items are not covered: …"). The result records
  `uncovered_first_try`, `repair_attempted` and `uncovered`.
- Python removes empty epics.
- Prompt: constraints become acceptance criteria, not tasks; never create a
  task to "resolve" a contradiction; priority applies to every task for the
  named work; a project go-live date applies to every task; "soon"/"later"
  are not deadlines.

## Stages 4–5 — Tickets and verification (Python)

`python tests/offline_check.py` — 51 checks, all passing, including:
wrong capital letter caught, missing word caught, wrong ref caught, invented
acceptance criterion and invented priority quotes flagged, unknown dependency
and unknown question id dropped with a warning, GENERAL and unmatched
questions always linked to a ticket, status = Needs clarification when there
are open questions.

## First full run (`run_demo.py`) — two failures, both fixed

| Brief | Error | Cause | Fix |
|---|---|---|---|
| clear | `413 Request too large … Limit 8000, Requested 8982` | Groq free tier allows 8,000 tokens/min; Stage 3 sent pretty-printed JSON of all facts and questions, and the repair step re-sent the whole first answer | Compact JSON; Stage 3 gets only the facts and question fields it needs; output capped per stage (2,500 / 3,000 / 4,000) with `reasoning_effort=low`; repair asks only for the missing tasks and Python merges them; clear error if a request can never fit |
| both | (would follow) per-minute limit reached between stages | three calls within one minute | `429` → wait for `retry-after`, then retry (up to 4 times) |
| vague | `'str' object has no attribute 'get'` | the AI returned a plain string where an object was expected; the code trusted the shape | every AI answer goes through `normalise_facts / normalise_questions / normalise_plan`; a string becomes an item with no quote, so Stage 5 flags it instead of crashing; `run_demo.py` now prints the full traceback |

New offline checks cover both: malformed answers, and a fake run where the
first breakdown misses two items and the repair call fills them.

## Second full run — runs end to end; manual review against the brief

The pipeline finished on both briefs (clear: 9 tickets, 4 questions, 1 quote
error caught by Stage 5; vague: 13 tickets, 17 questions, all 15 planted
issues covered). Reading the tickets line by line still found assumptions that
the quote check cannot see, because the quotes were real but used for the
wrong meaning:

| Problem (vague brief) | Fix |
|---|---|
| Every task had priority "keep costs low" (S10). Stage 1 had classed a budget constraint as a priority | Extraction rule 10: priorities only rank work. Stage 4 keeps a priority only if Stage 1 extracted it as a priority from the same sentence |
| Tasks had deadline "launch soon" (S12), even though the prompt said vague timing is not a deadline | Stage 4 keeps a deadline only if it is an extracted deadline AND names a real date (digits or a month) |
| Acceptance criteria added details: "…and vice-versa" (assumes two-way MBS sync), "view and export reports", "select a class and confirm the booking" | Prompt: criteria in the brief's own words. Stage 4: if the criterion text is not in the brief, it is replaced by its exact quote and the change is recorded |
| Clear brief: TASK-008 depends on TASK-007 although the brief does not state it | Not fixable by a text check; listed as a known limitation |
| Clear brief: one criterion mixed S5 and S6 but quoted only S5, so the S6 slot rule is lost after replacement | AI error made visible by the replacement note; prompt asks for one criterion per quote |

Re-applying Stage 4 to the saved results of this run: vague brief → 9
deadlines rejected, 7 reworded criteria replaced; clear brief → 7 reworded
criteria replaced, S13 priority and S14 date kept. (The "keep costs low"
priority still passed here because Stage 1 of that run had extracted it as a
priority; the new extraction rule addresses that on the next run.)

## Third full run — daily token limit

Clear brief finished: 9 tickets, 5 open questions, 2 ready / 7 need
clarification, every work item covered first try, 47 quotes checked, 0 issues.

Vague brief stopped at Stage 3 with `429 … tokens per day (TPD): Limit 200000,
Used 197790`. All of today's test runs had used up Groq's daily free quota.
The tool kept waiting 65 s and retrying, which cannot help with a daily limit.

Fixes: a daily-limit error now stops the run at once with a clear message
(when to try again, or which setting changes the model); `python run_demo.py
vague` re-runs only one brief so finished results are not paid for twice; the
app can open a saved result from `outputs/` without calling the AI.

## Manual review of the clear-brief report (third run)

Read line by line against the brief. Verification said 0 issues, but four
gaps were found by hand, so new Python checks were added:

| Found by hand | Fix |
|---|---|
| **S6 (slot rule "every 30 minutes between 10:00 AM and 8:00 PM") appears on no ticket.** Stage 1 dropped it this run; only a question mentioned it | New check: every sentence must reach a ticket (source, criterion, priority/deadline field) or be background (goals, users, names). Unused sentences are reported for review |
| S7 (cash only) and S12 (English only) were extracted as constraints but put on no ticket | Constraints used by no task are added to every epic as *Project constraint* criteria, with their quote |
| Q-001 (customer login) was labelled GENERAL, so it was attached to the epics only (including the admin epic) while customer tasks showed "Ready" | A GENERAL question now blocks every ticket (consistent). Prompt: GENERAL only if the answer changes every feature; a role's access question affects that role's features |
| 5 dependencies (e.g. TASK-008 → TASK-007) are not stated in the brief | Prompt: each dependency must quote the sentence that states it. Python keeps it only if the quote is in the brief; otherwise it is NOT added and becomes an open question ("Does X depend on Y? The brief does not say."), as the handbook requires |

Re-applying Stages 4–5 to the saved clear-brief result: S6 reported as not on
any ticket; S7 and S12 added to both epics; 5 unstated dependencies turned
into questions Q-006–Q-010; 0 tickets ready because Q-001 was labelled GENERAL
in that run.

## Fourth full run — with the smaller model `openai/gpt-oss-20b`

Run while the daily limit of `gpt-oss-120b` was used up. Both briefs finished.
The Python checks caught the smaller model's weaker output instead of letting it through:

| Brief | What went wrong (caught by Python or by hand) | Fix |
|---|---|---|
| clear | Every question quoted the brief with " (S8)" appended → 7 `not_found` flags (correctly caught) | Quotes are cleaned of trailing ref markers like `(S8)` before checking (format only, words unchanged) |
| clear | **All 7 questions labelled GENERAL**, so every question blocked all 11 tickets (pickup-date rules blocking the admin page) | If a GENERAL question quotes sentences that specific tasks are built from, Python scopes it to those tasks and notes it; truly project-wide questions still block everything |
| clear | Coverage missed F1–F6 on the first try; the repair call fixed it | (repair worked as designed) |
| vague | Quality requirements R1–R3 not covered even after repair; S2 and S8 reported as on no ticket (correctly caught) | Items still missing after the repair get a minimal task made by Python from the brief's own words (quality items: no criteria, so "Needs clarification") |
| vague | **"Admins should get reports" (S11) was not extracted as a feature, so no ticket exists**, yet no check failed: S11 counted as background because it named the "admins" user | Background (goals/users/names) now only excuses sentences without requirement words (*must, should, need, can, able to*); S11 is now reported |
| clear | Q-005 asks which email *service* to use (a developer decision, against prompt rule 7) | Not fixed in code — noted as a model-quality limitation |

Re-applying the new Stages 4–5 to the saved results: clear brief → 0 issues,
5 questions scoped to their tasks, 2 still project-wide (customer login, S13
priority); vague brief → S11 now reported. Conclusion: use `gpt-oss-120b`
for the final demo; the checks make weaker output visible but cannot make it good.

## Final demo run

_Fill in after `python run_demo.py`: number of tickets, questions,
first-try coverage misses and repairs, verification issues for each brief,
and what you checked by hand._
