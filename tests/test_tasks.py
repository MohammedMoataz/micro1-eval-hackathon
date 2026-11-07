import runpy
from collections import defaultdict

from evalkit.grader import GRADERS, grade
from evalkit.run import load_tasks

TASKS = load_tasks("data/tasks.jsonl")
TRAPS = {"id-code", "area-code"}


def test_schema():
    for t in TASKS:
        assert {"id", "prompt", "answer", "grader", "metadata"} <= t.keys()
        assert t["grader"] in GRADERS
        m = t["metadata"]
        assert m["trap"] in TRAPS and m["lang"] in ("en", "ar") and m["pair"] and m["reference"] and m["slip"]


def test_unique():
    assert len({t["id"] for t in TASKS}) == len(TASKS)
    assert len({t["prompt"] for t in TASKS}) == len(TASKS)


def test_every_task_exists_in_both_languages():
    pairs = defaultdict(list)
    for t in TASKS:
        pairs[t["metadata"]["pair"]].append(t)
    for pid, rows in pairs.items():
        assert sorted(r["metadata"]["lang"] for r in rows) == ["ar", "en"], pid
        assert all(r["id"] == f"{pid}-{r['metadata']['lang']}" for r in rows), pid


def test_arabic_prompts_are_arabic():
    for t in TASKS:
        has_ar = any("؀" <= c <= "ۿ" for c in t["prompt"].split("ANSWER")[0])
        assert has_ar == (t["metadata"]["lang"] == "ar"), t["id"]


def test_tasks_file_matches_generator():
    built = runpy.run_path("scripts/make_tasks.py")["build"]()
    assert built == TASKS


def test_grader_accepts_reference_rejects_slip_and_no_answer_line():
    for t in TASKS:
        variants = t["answer"].split("|")
        for v in variants:
            assert grade(t, f"reasoning\nANSWER: {v}"), (t["id"], v)
        assert not grade(t, f"reasoning\nANSWER: {t['metadata']['slip']}"), t["id"]
        assert not grade(t, f"the result is {variants[0]}"), t["id"]  # no ANSWER line
