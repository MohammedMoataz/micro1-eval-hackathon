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

## Task overview

Each task exists in English (`-en`) and Arabic (`-ar`) with the same answer. Every prompt states the output format (`ANSWER: <answer>`, and digits only where a number is asked).

| Task | Question | Reference answer | Plausible wrong answer (grader must reject) | Why it is hard |
|---|---|---|---|---|
| `eg-gov-01` | Governorate of birth for an invented ID with code 13 | Sharqia | Ismailia | The code table is arbitrary; neighbouring governorates are easy to confuse |
| `eg-gov-02` | Same, code 25 | Asyut | Sohag | Same; Upper Egypt governorates look alike to a guesser |
| `eg-gov-03` | Same, code 32 | New Valley | Matruh | Same; both are large desert governorates |
| `eg-gov-04` | Same, code 18 | Beheira | Gharbia | Same; both are Delta governorates |
| `eg-gov-05` | Same, code 34 | North Sinai | South Sinai | Same; North and South Sinai differ by one word |
| `eg-gov-06` | Same, code 22 | Beni Suef | Fayoum | Same; adjacent governorates |
| `eg-code-01` | Which code marks Qena? (control) | 27 | 26 | Reverse lookup of the same table; shows the model knows part of it |
| `eg-count-01` | How many of 5 IDs are from Cairo, Giza or Alexandria? (control) | 2 | 3 | Needs only the well-known codes 01, 21, 02 |
| `eg-abroad-01` | ID with code 88; prompt offers "outside Egypt" as an option (control) | outside Egypt | Cairo | 88 is the one non-governorate code; the option is named in the prompt |
| `eg-area-01` | Landline area code of Damanhur (control) | 45 | 40 | Different arbitrary table, used to show local recall works elsewhere |

The derivation of every answer is in `metadata.reference` in `data/tasks.jsonl`; sources are listed under Provenance below.

**How the grader was validated:** `tests/test_tasks.py` runs every row's reference answer through the grader (must pass), its plausible wrong answer (must fail) and a reply with no ANSWER line (must fail). `tests/test_grader.py` adds spelling, Arabic-normalisation and hedging cases. All 19 failed model answers were also read by hand: none was a correct answer rejected by the grader (`docs/failure_analysis.md`).

## Results (what we actually have)

All runs 2026-11-08, temperature 0, same 20 rows and same grader for both models. Free tiers, so cost per full run is $0.

| Model (version, settings) | Trials per task | Pass rate (95% CI) | pass^k | ID-to-governorate | Controls | Cost per full run | Runtime | Raw outputs |
|---|---|---|---|---|---|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter), temp 0 | 2 (39 of 40 graded, 1 timeout excluded) | 51.3% (32.4-70.0%) | pass^2 = 40.0% | **4 / 23** (English 1/11, Arabic 3/12) | 16 / 16 | $0 | 1804 s | `results/nemotron-3-ultra__2026-11-08/raw.jsonl` |
| `gemini-3.5-flash` (Google free key), temp 0 | 1 (20 of 20 graded) | 100% | pass^1 = 100% | **12 / 12** | 8 / 8 | $0 | 179 s | `results/gemini-3.5-flash__2026-11-08/raw.jsonl` |

Full metrics (bootstrap CI, pass@k, pass^k, task-by-model grid): `results/REPORT.md`. Gemini has one trial only (its free key allows 20 requests a day), so its pass^k equals its pass rate and says nothing about consistency.

### Per-task notes

Answers below are the final `ANSWER:` line of each Nemotron trial, verbatim (English row t0, t1 / Arabic row t0, t1). "line N" is the line in `results/nemotron-3-ultra__2026-11-08/raw.jsonl` that holds the full transcript. Gemini 3.5 Flash answered every row correctly (`results/gemini-3.5-flash__2026-11-08/raw.jsonl`, lines 1-20 in task order).

| Task | Nemotron answers | Reading |
|---|---|---|
| `eg-gov-01` (13, Sharqia) | EN: timeout, Ismailia / AR: الإسماعيلية, **الشرقية** (lines 1-4) | **Came close:** right once in Arabic; otherwise the neighbouring governorate |
| `eg-gov-02` (25, Asyut) | EN: Matrouh, Matrouh / AR: مطروح, مطروح (lines 5-8) | Stable wrong answer, 4 of 4; line 6 cites an "official" source |
| `eg-gov-03` (32, New Valley) | EN: Matrouh, Matrouh / AR: مطروح, شمال سيناء (lines 9-12) | Wrong every time; Matrouh again |
| `eg-gov-04` (18, Beheira) | EN: Asyut, Asyut / AR: أسيوط, **البحيرة** (lines 13-16) | **Came close:** right once in Arabic; otherwise Asyut |
| `eg-gov-05` (34, North Sinai) | EN: South Sinai, South Sinai / AR: **شمال سيناء**, غرب قنا (lines 17-20) | **Came close:** right once; "غرب قنا" (West Qena) is not a governorate |
| `eg-gov-06` (22, Beni Suef) | EN: **Beni Suef**, Fayoum / AR: الفيوم, الفيوم (lines 21-24) | **Came close:** right once in English; otherwise the adjacent Fayoum |
| `eg-code-01` (Qena = 27) | 27 in all 4 (lines 25-28) | Control passed |
| `eg-count-01` (2) | 2 in all 4 (lines 29-32) | Control passed |
| `eg-abroad-01` (outside Egypt) | outside Egypt / خارج مصر in all 4 (lines 33-36) | Control passed |
| `eg-area-01` (45) | 45 in all 4 (lines 37-40) | Control passed |

Read `docs/failure_analysis.md` before quoting any number. In short:

- Nemotron's 19 gov failures are all real wrong governorates (no grader misses); several are stable (code 25 answered Matrouh 4 of 4).
- It decodes common codes (Cairo 01 and Giza 21 in the counting control) and recalls Qena = 27, but fails six less common codes. No code was tested in both directions, so this is not evidence of a one-way memory.
- 4 of 6 gov tasks passed in one temperature-0 trial and failed in the other.
- Gemini 3.5 Flash passed every row (one trial), so the eval shows a **capability gradient** between two models, not a failure of the stronger one.
- **Honest limits:** this separates a weaker free model from a stronger one; it does **not** show that frontier models fail. The 6 gov tasks were kept because Nemotron failed them in exploration (selection effect), so the pass rate is not general Egyptian-knowledge accuracy. The answer key comes from secondary sources (English Wikipedia, matches django-localflavor), not an official table. The Arabic-versus-English difference is within noise; we claim no language gap.

### Representative transcripts

Same task for both models: `eg-gov-02-en` (ID `27304172558692`, code 25, correct answer Asyut). Final lines verbatim.

Nemotron 3 Ultra, trial 1 (raw.jsonl line 6), **fail**:

> The governorate code **25** corresponds to **Matrouh** (also spelled Matruh) according to the official CAPMAS/Ministry of Interior coding used in national IDs.
>
> ANSWER: Matrouh

Gemini 3.5 Flash, trial 0 (raw.jsonl line 3), **pass**:

> Code **25** corresponds to the **Asyut** Governorate (Assiut).
>
> ANSWER: Asyut

The full transcript of every trial (prompt id, full output, verdict, timing) is in the `raw.jsonl` files; the per-task notes above give the line for each failure.

### Main failure mode

Nemotron knows the ID layout (it explains century, birth date and the position of the province code correctly) but does not hold the code table. It fills the gap with a plausible governorate: often a neighbour of the right one (Sharqia/Ismailia, North/South Sinai, Beni Suef/Fayoum), sometimes the same wrong answer every time (code 25 and code 32 both become Matrouh). Four of six tasks give a different verdict across two temperature-0 trials of the same prompt, which fits guessing better than recall. This is a hypothesis from reading the transcripts; we did not run an ablation.

### Hot take

Asked for a table it does not hold, the model does not hedge. For code 25 it gave the same wrong governorate in all 4 attempts (Matrouh), and in one transcript it cites an "official" source for that answer. It lays out the whole ID digit by digit before the wrong lookup, so the layout knowledge makes the guess look trustworthy.

What it would take to close the gap: the table is small (27 governorates plus 88) and public, so giving the model the table or a lookup tool is the obvious fix. We did not test that here; it is the natural next experiment. Until then, a correct explanation of the ID format says nothing about whether the lookup that follows is right.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # add OPENROUTER_API_KEY (and/or GEMINI_API_KEY for gemini-* ids)
python -m pytest -q                                   # 37 grader and task-file tests, offline, no key needed
python -m evalkit.run --model nvidia/nemotron-3-ultra-550b-a55b:free --out results/nemotron --trials 2 --temperature 0
python -m evalkit.run --model gemini-3.5-flash --out results/gemini --trials 1 --temperature 0
python -m evalkit.report results/nemotron results/gemini --out results/REPORT.md
```

- Python 3.11 (runs were made with 3.11.4), standard library only for the eval itself; `pytest==9.2.0` for tests (pinned in `requirements.txt`).
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

## Provenance, prior work and sources

**Built during the hackathon.** Everything in this repo (tasks, generator, grader, runner, report, tests, docs) was written during the event: the first commit is 2026-11-06 and the challenge opened 2026-10-30 (see `git log`). An earlier finance version of the tasks was dropped for this topic; it stays only in git history (tag `v0.1.0`). Nothing else pre-existing was reused apart from Python, pytest and the sources below.

- MultiLoKo (Meta, MIT): multilingual local-knowledge benchmark. Idea borrowed (local question in local language and in English); no data or questions copied. Paper: Hupkes and Bogoychev, "MultiLoKo: a multilingual local knowledge benchmark for LLMs spanning 31 languages", https://arxiv.org/abs/2504.10356. Code: https://github.com/facebookresearch/multiloko
- ID layout and province codes: English Wikipedia "Egyptian National Identity Card" (CC BY-SA 4.0), revision used: https://en.wikipedia.org/w/index.php?title=Egyptian_National_Identity_Card&oldid=1377865466. Cross-check: django-localflavor Egypt national-ID validator, https://github.com/django/django-localflavor/blob/master/localflavor/eg/forms.py. All ID numbers in the tasks are invented.
- Landline area code (Damanhur = 45): English Wikipedia "Telephone numbers in Egypt", https://en.wikipedia.org/wiki/Telephone_numbers_in_Egypt.

## AI use

Built with Claude Code assistance (task generator, grader, runner, report, docs). HUMAN REVIEW: (add before submitting: what you checked yourself, e.g. every task, answer-key entry and grading rule, and the 19 failure transcripts)
