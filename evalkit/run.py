"""python -m evalkit.run --model <id> --out results/<name> [--trials 3] [--temperature 0.0]"""
import argparse
import json
import os
import pathlib
import time
from datetime import datetime, timezone

from . import models
from .grader import grade


def load_env(path=".env"):
    p = pathlib.Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_tasks(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    return [json.loads(l) for l in text.splitlines() if l.strip()]


def run(model, tasks, out, trials=3, temperature=0.0, complete=models.complete):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for t in tasks:
        for i in range(trials):
            start = time.time()
            try:
                output = complete(model, t["prompt"], temperature)
                error = None
            except Exception as e:  # keep going; record the failure instead of losing the run
                output, error = "", str(e)
            rows.append({"id": t["id"], "trial": i, "output": output, "error": error,
                         "passed": error is None and grade(t, output),
                         "seconds": round(time.time() - start, 2)})
    meta = {"model": model, "date": datetime.now(timezone.utc).isoformat(),
            "temperature": temperature, "trials": trials}
    (out / "raw.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", default="data/tasks.jsonl")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.0)
    a = ap.parse_args()
    load_env()
    rows = run(a.model, load_tasks(a.tasks), a.out, a.trials, a.temperature)
    print(f"{sum(r['passed'] for r in rows)}/{len(rows)} attempts passed -> {a.out}")
