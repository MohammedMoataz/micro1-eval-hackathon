# Failure analysis

Run analysed: `results/nemotron-3-ultra__2026-11-08` (Nemotron 3 Ultra, free tier, temperature 0, 2 trials, 40 requests; 39 graded, 1 timeout).
Second run: `results/gemini-3.5-flash__2026-11-08` (Gemini 3.5 Flash, free key, temperature 0, 1 trial, 20 requests). **20 / 20 passed, 0 errors**: 12/12 on the ID-to-governorate rows (English and Arabic) and 8/8 on controls. A first attempt the same day returned HTTP 429 on all 20 rows (daily free quota used up by the exploration probe); it was discarded as invalid, not counted as a result, and rerun after the quota reset.

## Result

| Slice | Passed / graded | Reading |
|---|---|---|
| 4 control tasks x 2 languages x 2 trials | 16 / 16 | Model follows the format, counts, and recalls an area code and a code-to-governorate fact |
| 6 ID-to-governorate tasks x 2 languages x 2 trials | 4 / 23 (English 1/11, Arabic 3/12) | Fails the lookup |

## Classification of every failure (19 of 19 gov failures read by hand)

| Class | Count | Evidence |
|---|---|---|
| REAL (wrong governorate) | 19 | Each ANSWER line names a different governorate than the code in the ID implies |
| GRADER (right answer rejected) | 0 | No failed row contains the reference answer on its ANSWER line |
| TASK (ambiguous prompt) | 0 | Prompts name the digits-to-province layout implicitly and ask for one governorate |
| INFRA (not a model failure) | 1 | gov-01-en trial 1: `The read operation timed out`; excluded from scoring |

Typical wrong answers (code in the ID -> model answer):

- 25 (Asyut) -> Matrouh, 4 times out of 4 (English and Arabic, both trials). A stable wrong belief, not noise.
- 32 (New Valley) -> Matrouh x3, North Sinai x1.
- 18 (Beheira) -> Asyut (3 of 4), correct once in Arabic.
- 34 (North Sinai) -> South Sinai x2 in English; one Arabic answer was "غرب قنا" ("West Qena"), which is not a governorate.
- 13 (Sharqia) -> Ismailia in 2 of 3 graded attempts; 22 (Beni Suef) -> Fayoum 3 of 4.

## Why it fails (hypothesis, partly supported)

The 2-digit province code is an arbitrary lookup table with no rule to derive it. Models know the ID layout, so they answer fluently, but they do not reliably hold the table. Evidence for guessing rather than recall:

1. Four of six tasks give a different result across two temperature-0 trials of the same prompt (gov-01, 04, 05 and 06 each pass once, fail once, in some language).
2. Several wrong answers are neighbouring or similar-sounding governorates (Sharqia/Ismailia, North/South Sinai, Beni Suef/Fayoum).
3. The controls that need the table passed: reverse lookup Qena = 27 (`eg-code-01`, 4 of 4) and forward decoding of Cairo 01 and Giza 21 (`eg-count-01`, 4 of 4). So the model holds common codes but not the six less common ones tested. No code was tested in both directions, so this does not show a one-way memory.

This is a hypothesis. We did not inspect reasoning traces or run an ablation, so "guessing" is the simplest explanation, not a proven mechanism.

## Arabic versus English

English 9 of 19 graded, Arabic 11 of 20 (all tasks). On the gov tasks alone, 1/11 against 3/12. With one model, two trials and 6 tasks this difference is within noise. We make **no claim** about a language gap.

## What we do not know

- **Frontier models are not shown to fail.** Gemini 3.5 Flash passed every row in the final run and in the exploration probes (`results/_exploration/`). The eval therefore separates a weaker free model from a stronger one (4/23 against 12/12 on the gov rows); it does not show a limit of frontier models. We also did not test any other strong model, so "Gemini knows the table" is one data point with one trial.
- **Selection effect.** The six gov tasks were kept because Nemotron failed them in exploration. The pass rate on this set is not an estimate of general Egyptian-knowledge accuracy. Controls were all solved by both models.
- **Answer key is secondary-sourced.** Province codes come from English Wikipedia (matches the django-localflavor list), not an official Civil Status Authority table; area codes from secondary pages. A wrong key entry would turn real passes into false fails. Gov rows where the model answered consistently and wrongly (e.g. 25 -> Matrouh) fit the key, so the key looks right for those, but this is not independent verification.
- **Small and uneven.** 6 gov tasks; Nemotron 2 trials, Gemini 1 trial (its free tier allows 20 requests per day). Gemini's 100% interval is degenerate (all passed), not a guarantee.
- **Wide intervals.** Nemotron overall 51.3% with 95% CI 32.4% to 70.0%.
