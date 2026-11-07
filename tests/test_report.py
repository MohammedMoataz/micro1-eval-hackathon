from evalkit.report import render, summarize

TASKS = [{"id": "a", "metadata": {"trap": "units"}}, {"id": "b", "metadata": {"trap": "units"}},
         {"id": "c", "metadata": {"trap": "steps"}}]
META = {"model": "m", "date": "2026-11-07T00:00", "temperature": 0.7, "trials": 2}


def row(i, trial, ok, error=None):
    return {"id": i, "trial": trial, "output": "", "error": error, "passed": ok, "seconds": 1.0}


def test_metrics_known_values():
    rows = [row("a", 0, True), row("a", 1, True),    # always right
            row("b", 0, True), row("b", 1, False),   # sometimes right
            row("c", 0, False), row("c", 1, False)]  # never right
    s = summarize(META, rows, TASKS)
    assert s["pass_rate"] == 0.5
    assert abs(s["pass_at_k"] - 2 / 3) < 1e-9 and abs(s["pass_hat_k"] - 1 / 3) < 1e-9
    assert s["by_trap"] == {"steps": 0.0, "units": 0.75}
    assert s["ci"][0] <= 0.5 <= s["ci"][1]
    assert "| m | 0.0% | 75.0% |" in render([s])


def test_api_errors_are_not_counted_as_wrong():
    rows = [row("a", 0, True), row("a", 1, False, error="timeout")]
    s = summarize(META, rows, TASKS)
    assert s["pass_rate"] == 1.0 and s["errors"] == 1 and s["attempts"] == 1
