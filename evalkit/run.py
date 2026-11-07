"""python -m evalkit.run --model <id> --out results/<name>"""
import argparse
import json
import os
import pathlib
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


def run(model, tasks, out, complete=models.complete):
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for t in tasks:
        try:
            output = complete(model, t["prompt"])
            error = None
        except Exception as e:  # keep going; record the failure instead of losing the run
            output, error = "", str(e)
        rows.append({"id": t["id"], "output": output, "error": error,
                     "passed": error is None and grade(t, output)})
    meta = {"model": model, "date": datetime.now(timezone.utc).isoformat(), "temperature": 0.0}
    (out / "raw.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", default="data/tasks.jsonl")
    a = ap.parse_args()
    load_env()
    rows = run(a.model, load_tasks(a.tasks), a.out)
    print(f"{sum(r['passed'] for r in rows)}/{len(rows)} passed -> {a.out}")
