---
name: eval-task-design
description: Use when writing or revising eval tasks in data/tasks.jsonl, choosing or changing a grader in evalkit/grader.py, adding grader tests, or when a task's correct answer could be disputed or graded wrongly (false pass / false fail).
---

# Eval Task and Grader Design

Judges score: a real limitation, 5-10 clear tasks, one defensible answer each, and a grader with no false passes and no false fails. Every task is a contract between three parts: the prompt, the answer, and the grader.

## Task recipe (one line in tasks.jsonl)

```json
{"id": "dom-001", "prompt": "<self-contained question>. Reply with only the final number.", "answer": "17", "grader": "numeric", "metadata": {"domain": "...", "difficulty": "hard", "source": "synthetic: <how made>", "why_hard": "<failure hypothesis>"}}
```

- The **prompt fixes the output format** ("Reply with only ..."), so a format slip is never mistaken for a reasoning fail.
- The **answer is derivable**: write how it was derived in `metadata.source`, or generate it with a script kept in `scripts/`.
- **`why_hard`** names the expected failure. `docs/failure_analysis.md` later checks it against what happened.
- Make **variants, not copies**: change numbers or entities across tasks so one memorized fact cannot pass several tasks.

## Choosing a grader

| Answer shape | Grader | Trap |
|---|---|---|
| Single number | `numeric` (uses the **last** number in the output) | "17 steps, not 20" grades as 20. Demand number-only output. |
| Short fixed string | `exact` (lowercase, collapses whitespace, strips edge dots) | Synonyms fail. List accepted forms with `regex` instead. |
| Several accepted forms | `regex` (case-insensitive, search) | Unanchored `5` also matches "25". Anchor it: `^\s*5\s*$`. |
| Free text | Avoid. If unavoidable, use an LLM judge with a rubric, tested like any other grader. | Judge bias. Costs per run. |

To add a new kind, add one function to `GRADERS`. Do not branch inside `grade()`.

## Grader tests (required)

For every task, `tests/test_grader.py` needs:
- the **known-good** answer and one realistic paraphrase passing, and
- at least two **known-bad** answers failing: the likely wrong answer (the `why_hard` mistake) and a right-number-wrong-place output.

Then run `pytest` and `python .claude/skills/eval-data-audit/audit.py`. Both must be clean.

## Common mistakes

| Mistake | Fix |
|---|---|
| Answer depends on an unstated assumption | Put the assumption in the prompt. |
| Two answers are defensible | Rewrite the prompt or drop the task. Do not argue it in the README. |
| Model fails on formatting only | Tighten the output instruction. That is a grader bug, not a finding. |
| 10 shaky tasks | 5 solid tasks beat 10 shaky ones. |
