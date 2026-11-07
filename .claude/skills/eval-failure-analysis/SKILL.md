---
name: eval-failure-analysis
description: Use when model runs in results/ show failed tasks, before claiming a model limitation, when filling docs/failure_analysis.md, or when a result looks too good or too bad to be true.
---

# Eval Failure Analysis

A failure counts only after you have tried to prove it is your own bug. Adapted from recursive-research's rule "never self-confirm; gaps are part of the deliverable".

## Step 1: Audit first

```bash
python .claude/skills/eval-data-audit/audit.py
```

If there are blockers or API-error warnings, fix them and rerun the model before analysing anything.

## Step 2: Classify every failed (run, task) pair

Open the raw output in `results/<run>/raw.jsonl` and assign exactly one class:

| Class | Test | Action |
|---|---|---|
| **REAL** | Output reasoning is wrong in the way the `why_hard` hypothesis predicted, or wrong in another explainable way | Keep. This is evidence. |
| **GRADER** | The answer is right but formatted differently, or right in substance | Fix the grader and add the output as a known-good test. Rerun grading. |
| **TASK** | The prompt is ambiguous, or another answer is also defensible | Fix the prompt or drop the task. Rerun the model. |
| **INFRA** | Empty output, truncation, refusal, API error | Rerun. Never count it. |

Do the same for **passes**: a pass with wrong reasoning is a false pass, and it means the grader is too loose.

## Step 3: Adversarial check

For each REAL failure, ask a fresh-context `verifier` agent to refute it. Give it the task, the reference answer, the raw output, and the instruction "argue the model was right or the task is unfair". A failure that does not survive is not a REAL failure.

## Step 4: Write docs/failure_analysis.md

```markdown
## Headline
<model>: X/N passed. <one-sentence limitation>.

## Per task
### <id>, <REAL|GRADER fixed|TASK fixed>
- Expected: ... (how derived)
- Model said: "<shortest quote that shows the error>"
- Why: <mechanism, tied to why_hard>

## What we do not know
- Sample size, single seed, models not tried, providers whose temperature 0 is not deterministic.
```

The "What we do not know" section is required. Judges trust stated limits more than overclaims.

## Red flags

- Any failure class left as "probably REAL".
- 0% or 100% pass rate with no task-level reading.
- Quoting the whole output instead of the decisive line.
