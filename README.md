# Egyptian national-ID lookup eval (English + Arabic)

Entry for the micro1 Eval Hackathon. A small, reproducible eval that checks whether a model can **recall an arbitrary local lookup table** or just guesses fluently, asked in English and in Arabic.

## The eval

- **What it tests:** the 14-digit Egyptian national ID has a 2-digit province code (digits 8-9) that maps to a governorate (13 = Sharqia, 25 = Asyut, 32 = New Valley, ...). The table has no rule to derive it. Each of 10 tasks is written in English and in Arabic (20 rows).
  - 6 tasks: given an invented ID, name the governorate of birth.
  - 4 controls: reverse lookup (governorate to code), counting IDs from three governorates, code 88 (born abroad), a landline area code.
- **Who it is for:** people building or choosing models for Arabic-language or Egypt-facing products (ID checks, KYC, forms) who need to know whether a model can be trusted to decode local identifiers.
- **Why it matters:** a model that confidently names the wrong governorate from an ID digit pair passes for a model that knows. The failure is silent. MultiLoKo (Meta, MIT licence) motivates asking local-knowledge questions in the local language and in English; no MultiLoKo data is used.
- **Grading:** deterministic. The last `ANSWER: ...` line must equal an accepted spelling (`answer_set`) or be one number (`numeric`). Hedged answers ("Ismailia, not Sharqia") fail. `tests/test_grader.py` shows what is accepted and rejected.

## Results (what we actually have)

| Model | Run | ID-to-governorate | Controls |
|---|---|---|---|
| Nemotron 3 Ultra (free) | 2 trials, temp 0, 39 graded | **4 / 23** (English 1/11, Arabic 3/12) | 16 / 16 |
| Gemini 3.5 Flash (free key) | final run pending (free quota exhausted); exploration probe, 1 trial | passed all in the probe | passed |

Read `docs/failure_analysis.md` before quoting any number. In short:

- Nemotron's 19 gov failures are all real wrong governorates (no grader misses); several are stable (code 25 answered Matrouh 4 of 4).
- It passes the reverse lookup, so it holds the table in one direction only.
- **Honest limits:** this separates a weaker free model from a stronger one; it does **not** show that frontier models fail. The 6 gov tasks were kept because Nemotron failed them in exploration (selection effect), so the pass rate is not general Egyptian-knowledge accuracy. The answer key comes from secondary sources (English Wikipedia, matches django-localflavor), not an official table. The Arabic-versus-English difference is within noise; we claim no language gap.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # add OPENROUTER_API_KEY (and/or GEMINI_API_KEY for gemini-* ids)
python -m evalkit.run --model nvidia/nemotron-3-ultra-550b-a55b:free --out results/nemotron --trials 2 --temperature 0
python -m evalkit.report results/nemotron --out results/REPORT.md
python -m pytest -q                                   # grader and task-file tests, offline
```

- Python 3.11, standard library only for the eval itself; `pytest` for tests.
- `gemini-*` ids go to Google's endpoint with `GEMINI_API_KEY`; everything else goes to OpenRouter.
- Cost: free tiers only. Runtime: about 30 minutes for 40 requests on the free Nemotron endpoint.
- Free quotas are small: OpenRouter free models allow 50 requests a day, and Gemini's free key allows 20 a day, which is one trial of this set. Requests that fail with 429 or a timeout are recorded as errors and excluded from scores, never counted as wrong.
- `scripts/make_tasks.py` regenerates `data/tasks.jsonl` (fixed seeds); a test fails if they disagree.
- Raw outputs for the runs behind the claims are in `results/`; `results/_exploration/` holds the 15-candidate probes used to pick tasks.

### Metrics reported

Pass rate with a 95% bootstrap CI over tasks, pass@k, pass^k, accuracy by trap type, a task-by-model grid, API errors and runtime.

## Layout

```
data/tasks.jsonl        20 rows (10 tasks x en/ar); data/README.md has sources and the selection effect
evalkit/                run.py, models.py, grader.py, report.py
scripts/make_tasks.py   task generator; scripts/make_zip.py builds the submission ZIP
tests/                  grader, runner, report, task-file tests
docs/failure_analysis.md  failure classification and what we do not know
results/                runs and REPORT.md
```

## Prior art and disclosure

- MultiLoKo (Meta, MIT): multilingual local-knowledge benchmark. Idea borrowed (local question in local language and in English); no data or questions copied.
- ID layout and province codes: English Wikipedia "Egyptian National Identity Card" (CC BY-SA 4.0). All ID numbers in the tasks are invented.
- Tooling: built with Claude Code assistance.
