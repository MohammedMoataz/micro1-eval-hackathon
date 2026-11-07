# Data

`tasks.jsonl`: one task per line. Do not edit it by hand: `python scripts/make_tasks.py` regenerates it and `tests/test_tasks.py` fails if the file and the generator disagree.

| field | meaning |
|-------|---------|
| id | unique string |
| prompt | text sent to the model: a report excerpt with a table, a question, and the answer-line format |
| answer | reference answer as a string; its number of decimals sets the grading tolerance |
| grader | `numeric` (reads the last `ANSWER: <number>` line), `exact` or `regex` (see `evalkit/grader.py`) |
| metadata | `trap` (the pitfall tested: `pct-vs-points`, `lookup`, `multi-step`, `units`), `reference` (the calculation), `slip` (the wrong answer the trap produces; the grader must reject it), `source`, `why_hard` |

## Where the tasks come from

- **Structure**: six tasks keep the table shape of a FinQA record (`fin-ms-002` adds an original fiscal-year shift); two (`fin-un-001` EPS, `fin-un-002` FX translation) use original structures. FinQA source: (Chen et al., "FinQA: A Dataset of Numerical Reasoning over Financial Data", EMNLP 2021, https://arxiv.org/abs/2109.00122). Code and data: https://github.com/czyssrs/FinQA, MIT licence, copy in `data/FinQA_LICENSE.txt`. The FinQA files were downloaded at commit `0f16e28` into `data/raw/` (not shipped).
- **Numbers and companies are invented.** Each task is generated with a fixed seed, so no FinQA text or figure appears and answers cannot be recalled from the original.
- **Answers come from our own reference solution** in `scripts/make_tasks.py`, never from FinQA's labels. Reading the reports behind the first shortlist showed three FinQA gold answers that were wrong (for example, one multiplies shares by the fair value of a different row, and another treats a $411M increase as the base year), so FinQA labels are not trusted here.
- `scripts/select_candidates.py` produced the shortlist of source records (at least 3 steps, only explained constants, gold answer matches its own program). A human then read every source report and rejected the unsound ones.

## Output format

Prompts ask the model to end with `ANSWER: <number>` and give the rounding. A reply without that line, or with two numbers on it, fails. This keeps formatting slips out of the reasoning score, and `tests/test_grader.py` shows what is accepted and rejected.
