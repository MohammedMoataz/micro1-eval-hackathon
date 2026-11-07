"""python scripts/select_candidates.py [--per-trap 5] -> data/raw/candidates.md

Shortlists FinQA (dev + test) questions worth turning into tasks. Heuristics only; a human picks the final 8.
Drops questions whose program uses constants the report never explains (const_5 and similar).
"""
import argparse
import json
import pathlib
import random
import re

RAW = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"
OK_CONSTS = {"const_100", "const_1000", "const_1000000", "const_1", "const_2", "const_m1"}
SCALE_CONSTS = {"const_1000", "const_1000000"}


def ops(program):
    return re.findall(r"([a-z_]+)\(", program)


def consts(program):
    return set(re.findall(r"const_\w+", program))


def traps(r):
    qa, q, prog = r["qa"], r["qa"]["question"].lower(), r["qa"]["program"]
    n, t = len(ops(prog)), []
    if consts(prog) & SCALE_CONSTS or re.search(r"in (thousands|millions)", " ".join(r["pre_text"]).lower() + str(r["table"]).lower()) and "million" in q:
        t.append("units")
    if "percentage point" in q or (re.search(r"percent", q) and re.search(r"difference|compared|greater|gap", q)):
        t.append("pct-vs-points")
    if qa["ann_text_rows"] and qa["ann_table_rows"]:
        t.append("lookup")
    if n >= 4:
        t.append("multi-step")
    return t


def answer_matches_program(qa):
    """Gold answer text must agree with the executed program (FinQA has some that do not)."""
    m = re.search(r"-?\d[\d,]*\.?\d*", str(qa["answer"]).replace("$", ""))
    if not m:
        return False
    text = m.group().replace(",", "")
    a, e = float(text), float(qa["exe_ans"])
    tol = 0.5 * 10 ** -(len(text.split(".")[1]) if "." in text else 0) + 1e-9  # the answer's own rounding
    pct = "%" in str(qa["answer"])
    return any(abs(a - c) <= tol for c in ((e * 100, e) if pct else (e,)))


def size_ok(r):
    return len(r["table"]) <= 12 and len(" ".join(r["pre_text"] + r["post_text"])) <= 6000


def load():
    for name in ("dev", "test"):
        for r in json.loads((RAW / f"{name}.json").read_text(encoding="utf-8")):
            r["_split"] = name
            yield r


def keep(r):
    qa = r["qa"]
    return (qa.get("program") and qa.get("exe_ans") not in (None, "") and len(ops(qa["program"])) >= 3
            and consts(qa["program"]) <= OK_CONSTS and size_ok(r) and answer_matches_program(qa))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-trap", type=int, default=5)
    a = ap.parse_args()
    pool = {}
    total = kept = 0
    for r in load():
        total += 1
        if keep(r):
            kept += 1
            for t in traps(r):
                pool.setdefault(t, []).append(r)
    rng = random.Random(0)
    lines = [f"# FinQA candidates ({kept} of {total} pass the filters)", ""]
    for t, rs in sorted(pool.items()):
        lines += [f"## {t} ({len(rs)} eligible, showing {min(a.per_trap, len(rs))})", ""]
        for r in rng.sample(rs, min(a.per_trap, len(rs))):
            qa = r["qa"]
            lines += [f"- `{r['id']}` ({r['_split']}) steps={len(ops(qa['program']))}",
                      f"  - Q: {qa['question']}",
                      f"  - program: `{qa['program']}`  answer: `{qa['answer']}` (exe {qa['exe_ans']})",
                      f"  - tags: {', '.join(traps(r))}"]
        lines.append("")
    out = RAW / "candidates.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{kept}/{total} pass filters; " + ", ".join(f"{t}={len(v)}" for t, v in sorted(pool.items())) + f" -> {out}")
