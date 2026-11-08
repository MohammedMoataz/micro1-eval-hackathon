# Egyptian national-ID lookup eval (English + Arabic)

Entry for the micro1 Eval Hackathon. A small, reproducible eval that checks whether a model can **recall an arbitrary local lookup table** or just guesses fluently, asked in English and in Arabic.

## Short description

An English + Arabic eval of whether a model recalls the arbitrary province-code table inside the 14-digit Egyptian national ID or only guesses fluently: 10 tasks (20 rows), a deterministic grader with 37 offline tests, run on two free-tier models. `nvidia/nemotron-3-ultra-550b-a55b:free` named the right governorate in 4 of 23 graded attempts while passing all 16 control attempts, and once cited an "official CAPMAS/Ministry of Interior coding" for a wrong answer; `gemini-3.5-flash` passed 20 of 20. This is a capability gradient between two models, not a frontier-model failure, and the tasks were kept after probing (selection effect).

## Video walkthrough

VIDEO LINK: (add before submitting)

## Domain and expertise

AUTHOR EXPERTISE: (add before submitting: why you can judge Egyptian ID codes and Arabic governorate names)

## The eval

- **What it tests:** the 14-digit Egyptian national ID has a 2-digit province code (digits 8-9) that maps to a governorate (13 = Sharqia, 25 = Asyut, 32 = New Valley, ...). The table has no rule to derive it. Each of 10 tasks is written in English and in Arabic (20 rows).
  - 6 tasks: given an invented ID, name the governorate of birth.
  - 4 controls: reverse lookup (governorate to code), counting IDs from three governorates, code 88 (born abroad), a landline area code.
- **Who it is for:** people building or choosing models for Arabic-language or Egypt-facing products (ID checks, KYC, forms) who need to know whether a model can be trusted to decode local identifiers.
- **Why it matters:** a model that confidently names the wrong governorate from an ID digit pair passes for a model that knows. The failure is silent. MultiLoKo (Meta, MIT licence) motivates asking local-knowledge questions in the local language and in English; no MultiLoKo data is used.
- **Grading:** deterministic. The last `ANSWER: ...` line must equal an accepted spelling (`answer_set`) or be one number (`numeric`). Hedged answers ("Ismailia, not Sharqia") fail. `tests/test_grader.py` shows what is accepted and rejected.

## Results (what we actually have)

All runs 2026-11-08, temperature 0, free tiers (cost $0).

| Model ID | Run | ID-to-governorate | Controls | Raw outputs |
|---|---|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter) | 2 trials, 39 of 40 graded (1 timeout), 1804 s | **4 / 23** (English 1/11, Arabic 3/12) | 16 / 16 | `results/nemotron-3-ultra__2026-11-08/` |
| `gemini-3.5-flash` (Google free key) | 1 trial, 20 of 20 graded, 179 s | **12 / 12** | 8 / 8 | `results/gemini-3.5-flash__2026-11-08/` |

Full metrics (bootstrap CI, pass@k, pass^k, task-by-model grid): `results/REPORT.md`.

Read `docs/failure_analysis.md` before quoting any number. In short:

- Nemotron's 19 gov failures are all real wrong governorates (no grader misses); several are stable (code 25 answered Matrouh 4 of 4).
- It decodes common codes (Cairo 01 and Giza 21 in the counting control) and recalls Qena = 27, but fails six less common codes. No code was tested in both directions, so this is not evidence of a one-way memory.
- 4 of 6 gov tasks passed in one temperature-0 trial and failed in the other.
- Gemini 3.5 Flash passed every row (one trial), so the eval shows a **capability gradient** between two models, not a failure of the stronger one.
- **Honest limits:** this separates a weaker free model from a stronger one; it does **not** show that frontier models fail. The 6 gov tasks were kept because Nemotron failed them in exploration (selection effect), so the pass rate is not general Egyptian-knowledge accuracy. The answer key comes from secondary sources (English Wikipedia, matches django-localflavor), not an official table. The Arabic-versus-English difference is within noise; we claim no language gap.

### Representative transcripts

Nemotron, `eg-gov-02-en` (ID `27304172558692`, code 25, correct answer Asyut), trial 1, final lines verbatim:

> The governorate code **25** corresponds to **Matrouh** (also spelled Matruh) according to the official CAPMAS/Ministry of Interior coding used in national IDs.
>
> ANSWER: Matrouh

Gemini 3.5 Flash passed every row; its full outputs are in `results/gemini-3.5-flash__2026-11-08/raw.jsonl`.

### Hot take

Asked for a table it does not hold, the model does not hedge. For code 25 it gave the same wrong governorate in all 4 attempts (Matrouh), and in one transcript it cites an "official" source for that answer. It lays out the whole ID digit by digit before the wrong lookup, so the layout knowledge makes the guess look trustworthy.

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

- MultiLoKo (Meta, MIT): multilingual local-knowledge benchmark. Idea borrowed (local question in local language and in English); no data or questions copied. Paper: Hupkes and Bogoychev, "MultiLoKo: a multilingual local knowledge benchmark for LLMs spanning 31 languages", https://arxiv.org/abs/2504.10356. Code: https://github.com/facebookresearch/multiloko
- ID layout and province codes: English Wikipedia "Egyptian National Identity Card" (CC BY-SA 4.0), revision used: https://en.wikipedia.org/w/index.php?title=Egyptian_National_Identity_Card&oldid=1377865466. Cross-check: django-localflavor Egypt national-ID validator, https://github.com/django/django-localflavor/blob/master/localflavor/eg/forms.py. All ID numbers in the tasks are invented.
- Landline area code (Damanhur = 45): English Wikipedia "Telephone numbers in Egypt", https://en.wikipedia.org/wiki/Telephone_numbers_in_Egypt.
## AI use

Built with Claude Code assistance (task generator, grader, runner, report, docs). HUMAN REVIEW: (add before submitting: what you checked yourself, e.g. every task, answer-key entry and grading rule, and the 19 failure transcripts)
