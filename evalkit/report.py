"""python -m evalkit.report results/<name> [...]: pass rate plus the failed task ids."""
import json
import pathlib
import sys


def summarize(run_dir):
    d = pathlib.Path(run_dir)
    lines = (d / "raw.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(l) for l in lines if l.strip()]
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    failed = [r["id"] for r in rows if not r["passed"]]
    return f"{meta['model']}: {len(rows) - len(failed)}/{len(rows)} passed; failed: {', '.join(failed) or '-'}"


if __name__ == "__main__":
    for d in sys.argv[1:]:
        print(summarize(d))
