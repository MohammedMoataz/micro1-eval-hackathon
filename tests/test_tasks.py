import runpy

from evalkit.grader import GRADERS, grade
from evalkit.run import load_tasks

TASKS = load_tasks("data/tasks.jsonl")
TRAPS = {"pct-vs-points", "lookup", "multi-step", "units"}


def test_schema():
    for t in TASKS:
        assert {"id", "prompt", "answer", "grader", "metadata"} <= t.keys()
        assert t["grader"] in GRADERS
        assert t["metadata"]["trap"] in TRAPS and t["metadata"]["reference"] and t["metadata"]["slip"]


def test_unique():
    assert len({t["id"] for t in TASKS}) == len(TASKS)
    assert len({t["prompt"] for t in TASKS}) == len(TASKS)


def test_two_tasks_per_trap():
    assert sorted(t["metadata"]["trap"] for t in TASKS) == sorted(list(TRAPS) * 2)


def test_tasks_file_matches_generator():
    built = runpy.run_path("scripts/make_tasks.py")["build"]()
    assert built == TASKS


def test_grader_accepts_reference_rejects_slip_and_no_answer_line():
    for t in TASKS:
        assert grade(t, f"reasoning\nANSWER: {t['answer']}"), t["id"]
        assert not grade(t, f"reasoning\nANSWER: {t['metadata']['slip']}"), t["id"]
        assert not grade(t, f"the result is {t['answer']}"), t["id"]
        assert t["answer"] not in t["prompt"], t["id"]  # reference answer must not leak into the prompt
