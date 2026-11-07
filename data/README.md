# Data

`tasks.jsonl`: one task per line.

| field | meaning |
|-------|---------|
| id | unique string |
| prompt | text sent to the model |
| answer | expected answer (string, or regex pattern for `regex`) |
| grader | `exact`, `numeric` or `regex` (see `evalkit/grader.py`) |
| metadata | `trap` (required: the pitfall this task tests, used for the by-trap report), plus free-form domain, difficulty, source |

TODO: where the tasks came from, licence, and how any synthetic data was generated.
