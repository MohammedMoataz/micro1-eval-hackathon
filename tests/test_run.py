from evalkit.run import load_tasks, run


def test_pipeline_offline(tmp_path):
    tasks = load_tasks("data/tasks.jsonl")
    answers = {t["prompt"]: t["answer"] for t in tasks}
    rows = run("fake", tasks, tmp_path, trials=3, complete=lambda m, p, temp: "ANSWER: " + answers[p])
    assert len(rows) == 3 * len(tasks) and all(r["passed"] for r in rows)
    assert (tmp_path / "raw.jsonl").exists() and (tmp_path / "meta.json").exists()


def test_errors_are_recorded_not_graded(tmp_path):
    def boom(m, p, temp):
        raise RuntimeError("api down")
    rows = run("fake", load_tasks("data/tasks.jsonl"), tmp_path, trials=1, complete=boom)
    assert all(r["error"] and not r["passed"] for r in rows)
