# Data

`tasks.jsonl`: 20 rows = **10 tasks, each written in English and in Arabic** (`id` ends in `-en` / `-ar`; both rows share `metadata.pair` and have the same answer). Do not edit it by hand: `python scripts/make_tasks.py` regenerates it, and `tests/test_tasks.py` fails if the file and the generator disagree.

| field | meaning |
|-------|---------|
| id | `eg-<family>-<nn>-<lang>` |
| prompt | the question plus the answer-line format (`ANSWER: <answer>`) |
| answer | reference answer. For `answer_set`: accepted variants joined by `\|` (spellings, with or without "Governorate"/"محافظة") |
| grader | `answer_set` (names) or `numeric` (numbers); see `evalkit/grader.py` |
| metadata | `lang`, `pair`, `trap` (`id-code` or `area-code`), `reference` (the derivation), `slip` (the plausible wrong answer; the grader must reject it), `source`, `why_hard` |

## What the tasks ask

All IDs are **invented**; a real person's ID is never used.

| Family | Tasks | Question |
|---|---|---|
| ID to governorate | 6 | "Which governorate was the holder of this fictional national ID born in?" (province codes 13, 25, 32, 18, 34, 22) |
| Code lookup | 1 | Which 2-digit code marks Qena in the national ID? (control) |
| Counting | 1 | How many of 5 IDs were born in Cairo, Giza or Alexandria? (control) |
| Born abroad | 1 | ID with code 88; answer a governorate name or "outside Egypt" (control; the prompt names the option) |
| Area code | 1 | Landline area code of Damanhur (control) |

## Where the facts come from

- **Provincial codes** of the 14-digit Egyptian national ID: English Wikipedia, "Egyptian National Identity Card" (revision oldid=1377865466, CC BY-SA 4.0). It lists 27 governorate codes plus 88 for "outside the republic"; the code list matches the django-localflavor `eg` validator. This is a **secondary source**, not an official Civil Status Authority table. Arabic governorate names are the standard names.
- **Area codes**: Wikipedia "Telephone numbers in Egypt" mirror and the dubai-online country-code page (secondary sources).
- **ID layout** (century digit 2 = 1900s, 3 = 2000s; six digits date of birth; two digits province): same Wikipedia article.
- Nothing is copied from MultiLoKo (Meta, MIT licence). Its idea of asking local-knowledge questions in the local language and in English, and of reporting the difference, is borrowed; its questions and data are not used.

## How the tasks were chosen (selection effect)

15 candidate tasks were first probed on two models (Nemotron Ultra and Gemini 3.5 Flash, 1 trial each; raw outputs in `results/_exploration/`). The final 10 keep all 6 ID-to-governorate tasks (the family where the models differed) and one task from each other family as a control (all solved). So the **pass rate on this set is not an estimate of general Egyptian-knowledge accuracy**; it measures the ID-code decoding weakness, with controls to show the models are otherwise fine.

## Output format and grading

Prompts ask the model to end with `ANSWER: <answer>`. Only the last such line is graded. `answer_set` passes only if the whole line equals an accepted variant after folding case, Arabic diacritics, alef variants, teh marbuta and punctuation. "Ismailia, not Sharqia" and hedged answers fail. `numeric` accepts exactly one number on the line. `tests/test_grader.py` shows what is accepted and rejected.
