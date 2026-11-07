"""Audit an eval's tasks and results. Stdlib only.

python .claude/skills/eval-data-audit/audit.py [--tasks data/tasks.jsonl] [--results results]
python .claude/skills/eval-data-audit/audit.py --selftest

Prints a markdown report. Exit 1 if any BLOCKER is found (duplicate, leak, grader
rejects its own answer, missing field, TODO left in a task).
"""
import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from evalkit.grader import GRADERS, grade  # noqa: E402

REQUIRED = {"id", "prompt", "answer", "grader"}


def norm(s):
    return " ".join(str(s).lower().split())


def read_jsonl(path):
    text = pathlib.Path(path).read_text(encoding="utf-8-sig")  # tolerate BOM from PS 5.1 / Notepad
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def audit_tasks(tasks):
    """Return (blockers, warnings, stats-lines)."""
    blockers, warnings, stats = [], [], []
    ids = collections.Counter(t.get("id") for t in tasks)
    prompts = collections.Counter(norm(t.get("prompt", "")) for t in tasks)
    for t in tasks:
        tid = t.get("id", "?")
        missing = REQUIRED - t.keys()
        if missing:
            blockers.append(f"{tid}: missing fields {sorted(missing)}")
            continue
        if t["grader"] not in GRADERS:
            blockers.append(f"{tid}: unknown grader '{t['grader']}'")
            continue
        if ids[tid] > 1:
            blockers.append(f"{tid}: duplicate id")
        if prompts[norm(t["prompt"])] > 1:
            blockers.append(f"{tid}: duplicate prompt")
        if "TODO" in json.dumps(t):
            blockers.append(f"{tid}: TODO still in task")
        # Known-good check: the grader must accept the reference answer itself.
        ref = str(t["answer"])
        if t["grader"] != "regex" and not (grade(t, ref) or grade(t, f"ANSWER: {ref}")):
            blockers.append(f"{tid}: grader rejects its own reference answer")
        # Leak check: a short answer sitting verbatim in the prompt is a giveaway.
        a = norm(t["answer"])
        if t["grader"] != "regex" and a and re.search(rf"\b{re.escape(a)}\b", norm(t["prompt"])):
            warnings.append(f"{tid}: reference answer appears in prompt (leak?)")
        if not t.get("metadata"):
            warnings.append(f"{tid}: no metadata (domain/difficulty/source)")
    n = len(tasks)
    stats.append(f"- tasks: {n} (judges want 5-10)")
    if not 5 <= n <= 10:
        warnings.append(f"task count {n} outside 5-10")
    stats.append("- graders: " + ", ".join(f"{k}={v}" for k, v in collections.Counter(t.get("grader") for t in tasks).items()))
    for key in ("domain", "difficulty", "source"):
        c = collections.Counter(str((t.get("metadata") or {}).get(key, "-")) for t in tasks)
        stats.append(f"- {key}: " + ", ".join(f"{k}={v}" for k, v in c.most_common()))
    return blockers, warnings, stats


def audit_results(results_dir, tasks):
    """Per-model pass rate, plus tasks every model passes or every model fails."""
    lines, warnings = [], []
    runs = sorted(p.parent for p in pathlib.Path(results_dir).glob("*/raw.jsonl"))
    if not runs:
        return ["- no runs yet under " + str(results_dir)], warnings
    by_id = {t["id"]: t for t in tasks}
    passes = collections.defaultdict(list)  # task id -> [bool per run]
    lines.append("| run | model | passed | errors | empty |")
    lines.append("|---|---|---|---|---|")
    for d in runs:
        rows = read_jsonl(d / "raw.jsonl")
        meta_p = d / "meta.json"
        model = json.loads(meta_p.read_text(encoding="utf-8-sig")).get("model", "?") if meta_p.exists() else "? (no meta.json)"
        errors = sum(1 for r in rows if r.get("error"))
        empty = sum(1 for r in rows if not r.get("error") and not str(r.get("output", "")).strip())
        ok = sum(1 for r in rows if r.get("passed"))
        lines.append(f"| {d.name} | {model} | {ok}/{len(rows)} | {errors} | {empty} |")
        if errors:
            warnings.append(f"{d.name}: {errors} API errors counted as fails; rerun before claiming")
        stale = {r["id"] for r in rows} ^ set(by_id)
        if stale:
            warnings.append(f"{d.name}: task ids differ from tasks.jsonl ({len(stale)}); stale run?")
        for r in rows:
            passes[r["id"]].append(bool(r.get("passed")))
    all_pass = [i for i, v in passes.items() if all(v)]
    all_fail = [i for i, v in passes.items() if not any(v)]
    lines.append(f"\n- passed by every run (too easy?): {', '.join(all_pass) or '-'}")
    lines.append(f"- failed by every run (check task + grader first): {', '.join(all_fail) or '-'}")
    return lines, warnings


def report(tasks_path, results_dir):
    tasks = read_jsonl(tasks_path)
    blockers, warnings, stats = audit_tasks(tasks)
    res_lines, res_warn = audit_results(results_dir, tasks)
    out = ["# Eval audit", "", "## Tasks", *stats, "", "## Results", *res_lines, ""]
    out += ["## Blockers", *(f"- {b}" for b in blockers or ["none"]), ""]
    out += ["## Warnings", *(f"- {w}" for w in (warnings + res_warn) or ["none"])]
    return "\n".join(out), bool(blockers)


def selftest():
    good = {"id": "a", "prompt": "What is 6*7? Reply with the number.", "answer": "42", "grader": "numeric", "metadata": {"domain": "x"}}
    leak = {"id": "b", "prompt": "The answer is paris. Capital of France?", "answer": "paris", "grader": "exact", "metadata": {"domain": "x"}}
    broken = {"id": "c", "prompt": "Pick one", "answer": "not a number", "grader": "numeric"}
    b, w, _ = audit_tasks([good, leak, broken, dict(good)])
    assert any("c: grader rejects" in x for x in b), b
    assert any("a: duplicate id" in x for x in b), b
    assert any("b: reference answer appears" in x for x in w), w
    assert not any(x.startswith("b:") for x in b), b
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default=str(ROOT / "data" / "tasks.jsonl"))
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    text, bad = report(a.tasks, a.results)
    print(text)
    sys.exit(1 if bad else 0)
