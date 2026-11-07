from evalkit.grader import GRADERS
from evalkit.run import load_tasks

TASKS = load_tasks("data/tasks.jsonl")


def test_schema():
    for t in TASKS:
        assert {"id", "prompt", "answer", "grader"} <= t.keys()
        assert t["grader"] in GRADERS


def test_unique():
    assert len({t["id"] for t in TASKS}) == len(TASKS)
    assert len({t["prompt"] for t in TASKS}) == len(TASKS)
