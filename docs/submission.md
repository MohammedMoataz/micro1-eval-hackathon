# Submission text (draft)

## Short description (paste into HackerRank)

An English + Arabic eval of whether a model can recall an arbitrary local lookup table or only guesses fluently. The 14-digit Egyptian national ID hides a 2-digit province code (13 = Sharqia, 25 = Asyut, 32 = New Valley ...) that has no rule behind it. 10 tasks, each written in English and Arabic (20 rows): 6 "which governorate was this invented ID issued in" tasks plus 4 controls (reverse lookup, counting, code 88, an area code). Deterministic grader: the last `ANSWER:` line must match an accepted spelling or one number; hedged answers fail; 37 offline tests. Result: Nemotron 3 Ultra (free) passes 4 of 23 graded governorate attempts and all 16 control attempts, with wrong answers that are often stable (code 25 answered Matrouh 4 of 4) or flip between identical temperature-0 trials; Gemini 3.5 Flash passes 20 of 20. So it shows a capability gradient between two models, not a failure of a frontier model. Limits we state: tasks were kept after probing (selection effect), the answer key is secondary-sourced (Wikipedia), 1 to 2 trials, no claim of an Arabic-versus-English gap. Idea of asking local knowledge in the local language and English is borrowed from MultiLoKo (Meta); no data copied.

## Video script (about 4 minutes)

1. (0:00-0:30) Problem. "Models answer fluently even when they don't know. An Egyptian national ID has a province code at digits 8-9. It is an arbitrary table. Can a model recall it?" Show one task in English and the same in Arabic.
2. (0:30-1:15) The tasks. Show `data/tasks.jsonl`: 10 tasks x 2 languages, 6 lookup tasks and 4 controls. All IDs invented. Explain controls prove the model can follow the format and is fine elsewhere.
3. (1:15-2:00) Grader. Show `evalkit/grader.py` `answer_set`: last ANSWER line must equal an accepted variant; "Ismailia, not Sharqia" fails. Show `tests/test_grader.py` and 37 tests passing.
4. (2:00-3:00) Results. Show `results/REPORT.md` and the task-by-model grid. Nemotron 4/23 on lookup, 16/16 on controls; Gemini 20/20. Point at the code-25-answered-Matrouh rows and the pass-then-fail flips at temperature 0.
5. (3:00-4:00) Honest limits. Capability gradient, not a frontier failure; selection effect; secondary-source key; small trials; no language-gap claim. Show `docs/failure_analysis.md` "What we do not know". Close with run commands from the README.
