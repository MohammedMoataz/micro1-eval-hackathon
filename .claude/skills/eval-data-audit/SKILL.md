---
name: eval-data-audit
description: Use when tasks.jsonl is created or edited, after any model run lands in results/, before writing failure analysis, or before submitting an eval - and whenever someone asks "are the tasks ok", "summarize the results", or "which tasks do models fail".
---

# Eval Data Audit

Adapted from csv-data-summarizer: inspect the data first, report everything in one pass, ask nothing. Here the data is the eval itself: `data/tasks.jsonl` and `results/*/raw.jsonl`.

## Run it, don't offer it

```bash
python .claude/skills/eval-data-audit/audit.py            # report, exit 1 on blockers
python .claude/skills/eval-data-audit/audit.py --selftest # proves the checks still bite
```

Run it immediately, then paste the report. Do not list options or ask what to check.

## What it reports

| Section | Checks |
|---|---|
| Blockers (exit 1) | missing fields, unknown grader, duplicate id or prompt, `TODO` left in a task, **grader rejects its own reference answer** |
| Warnings | answer appears verbatim in prompt (leak), no metadata, task count outside 5-10, API errors counted as fails, run ids out of sync with tasks.jsonl |
| Stats | grader mix, domain / difficulty / source spread |
| Results | per-run pass rate table, tasks every run passes (too easy), tasks every run fails (suspect task or grader first) |

## Reading the result

- **Any blocker = not shippable.** Fix and rerun before any model run.
- **Passed by every run**: no signal. Harden or drop the task.
- **Failed by every run**: the best signal, but also the classic sign of a broken task. Hand to `eval-failure-analysis` before claiming it.
- **API errors**: rerun those tasks; an error is not a model failure.

## Common mistakes

- Trusting `pytest` alone: `test_grader.py` only checks the cases you wrote. The audit checks every task's own answer.
- Regex tasks skip the self-check (the answer is a pattern). Add a known-good string for them in `tests/test_grader.py`.
- Files saved from PowerShell 5.1 or Notepad carry a BOM. The audit reads them fine, but `evalkit.run.load_tasks` uses plain `utf-8` and will fail. Save as UTF-8 without BOM.
