from evalkit.run import load_tasks, run


def test_pipeline_offline(tmp_path):
    tasks = load_tasks("data/tasks.jsonl")
    answers = {t["prompt"]: t["answer"] for t in tasks}
    rows = run("fake", tasks, tmp_path, complete=lambda m, p: answers[p])
    assert all(r["passed"] for r in rows)
    assert (tmp_path / "raw.jsonl").exists() and (tmp_path / "meta.json").exists()
