"""python -m evalkit.report results/<run> [...] [--out results/REPORT.md]

Markdown metrics per model: pass rate with bootstrap CI, pass@k, pass^k, errors, runtime,
accuracy per trap type, and a task x model grid. Failed API calls are never counted as wrong answers.
"""
import argparse
import json
import pathlib
import random
from collections import defaultdict

from .run import load_tasks


def load_run(d):
    d = pathlib.Path(d)
    lines = (d / "raw.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(l) for l in lines if l.strip()]
    return json.loads((d / "meta.json").read_text(encoding="utf-8")), rows


def by_task(rows):
    """task id -> list of pass flags, graded attempts only (errored calls dropped)."""
    g = defaultdict(list)
    for r in rows:
        if not r.get("error"):
            g[r["id"]].append(bool(r["passed"]))
    return g


def rate(g, ids=None):
    flags = [f for i, fs in g.items() if ids is None or i in ids for f in fs]
    return sum(flags) / len(flags) if flags else None


def bootstrap_ci(g, n=2000, seed=0):
    # Resample TASKS, not attempts: trials of one task are not independent.
    # ponytail: percentile bootstrap, fixed seed; with <10 tasks the interval is wide on purpose.
    ids, rng, vals = list(g), random.Random(seed), []
    for _ in range(n):
        flags = [f for i in (rng.choice(ids) for _ in ids) for f in g[i]]
        vals.append(sum(flags) / len(flags))
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.975 * n) - 1]


def summarize(meta, rows, tasks):
    g = by_task(rows)
    trap = {t["id"]: t.get("metadata", {}).get("trap", "untagged") for t in tasks}
    traps = defaultdict(set)
    for i in g:
        traps[trap.get(i, "untagged")].add(i)
    return {
        "model": meta["model"], "date": meta["date"][:10], "trials": meta.get("trials", 1),
        "temperature": meta["temperature"], "tasks": len(g), "attempts": sum(map(len, g.values())),
        "errors": sum(1 for r in rows if r.get("error")),
        "seconds": round(sum(r.get("seconds", 0) for r in rows), 1),
        "pass_rate": rate(g),
        "pass_at_k": sum(any(f) for f in g.values()) / len(g) if g else None,
        "pass_hat_k": sum(all(f) for f in g.values()) / len(g) if g else None,
        "ci": bootstrap_ci(g) if g else None,
        "by_trap": {k: rate(g, v) for k, v in sorted(traps.items())},
        "by_task": {i: (sum(fs), len(fs)) for i, fs in g.items()},
    }


def pct(x):
    return "n/a" if x is None else f"{100 * x:.1f}%"


def render(summaries):
    md = []
    for s in summaries:
        k = s["trials"]
        lo, hi = s["ci"] or (None, None)
        md += [f"## {s['model']} ({s['date']}, {k} trials, temperature {s['temperature']})", "",
               "| metric | value |", "|---|---|",
               f"| pass rate | {pct(s['pass_rate'])} (95% CI {pct(lo)} to {pct(hi)}, bootstrap over tasks) |",
               f"| pass@{k} (any trial right) | {pct(s['pass_at_k'])} |",
               f"| pass^{k} (all trials right) | {pct(s['pass_hat_k'])} |",
               f"| API errors (not graded) | {s['errors']} |",
               f"| graded attempts | {s['attempts']} over {s['tasks']} tasks |",
               f"| runtime | {s['seconds']} s |", ""]
    traps = sorted({t for s in summaries for t in s["by_trap"]})
    md += ["## Accuracy by trap type (model x trap)", "",
           "| model | " + " | ".join(traps) + " |", "|---|" + "---|" * len(traps)]
    md += [f"| {s['model']} | " + " | ".join(pct(s["by_trap"].get(t)) for t in traps) + " |" for s in summaries]
    ids = sorted({i for s in summaries for i in s["by_task"]})
    md += ["", "## Passes per task (task x model)", "",
           "| task | " + " | ".join(s["model"] for s in summaries) + " |", "|---|" + "---|" * len(summaries)]
    for i in ids:
        cells = [f"{s['by_task'][i][0]}/{s['by_task'][i][1]}" if i in s["by_task"] else "-" for s in summaries]
        md.append(f"| {i} | " + " | ".join(cells) + " |")
    return "\n".join(md) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--tasks", default="data/tasks.jsonl")
    ap.add_argument("--out")
    a = ap.parse_args()
    tasks = load_tasks(a.tasks)
    text = render([summarize(*load_run(d), tasks) for d in a.runs])
    print(text)
    if a.out:
        pathlib.Path(a.out).write_text(text, encoding="utf-8")
