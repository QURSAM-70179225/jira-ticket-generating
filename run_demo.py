"""Run the full pipeline on both demo briefs and save all deliverables.

Run:  python run_demo.py            (both briefs)
      python run_demo.py vague      (only briefs whose name contains "vague")
Output: outputs/clear_brief/ and outputs/vague_brief/, each with
        report.md, tickets.json, tickets.csv, open_questions.csv, result_full.json
"""
import sys
import traceback
from pathlib import Path

from export import save_all
from pipeline import DailyLimitError, run_pipeline

BRIEFS = ["briefs/clear_brief.txt", "briefs/vague_brief.txt"]
if len(sys.argv) > 1:
    BRIEFS = [b for b in BRIEFS if any(a in b for a in sys.argv[1:])]

for brief_path in BRIEFS:
    path = Path(brief_path)
    print(f"\n===== {path.name} =====")
    try:
        result = run_pipeline(path.read_text(encoding="utf-8"), progress=lambda s: print("  " + s))
    except DailyLimitError as e:
        print(f"  STOPPED: {e}")
        break
    except Exception as e:
        print(f"  FAILED: {e}")
        print("  --- details (paste these if you need help) ---")
        traceback.print_exc()
        continue
    folder = save_all(result, Path("outputs") / path.stem)
    v = result["verification"]["summary"]
    cov = result["plan"]["coverage"]
    print(f"  {len(result['tickets'])} tickets, {len(result['questions'])} open questions")
    print(f"  ready: {v['tickets_ready']}, need clarification: {v['tickets_need_clarification']}")
    print(f"  coverage: missed first try {cov['uncovered_first_try'] or 'none'}, "
          f"repair asked: {cov['repair_attempted']}, still uncovered: {cov['uncovered'] or 'none'}")
    print(f"  verification: {v['quotes_checked']} quotes checked, {v['issues']} issue(s)")
    for i in result["verification"]["issues"]:
        print(f"    - {i['status']} at {i['where']}: {i.get('detail', '')}")
    print(f"  saved to {folder}")
