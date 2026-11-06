# micro1 Eval Hackathon

Solo entry for the [micro1 Eval Hackathon](https://www.micro1.ai/hackathon/faq): build a rigorous, reproducible **eval** (tasks + grader) that shows something frontier AI models still cannot do.

> Status: eval topic not chosen yet. Fill the `TODO` markers once it is.

## Deadline

Submissions close **Mon 9 Nov 2026, 07:15 Cairo time** (05:15 GMT). Resubmitting is allowed until then; only the latest complete submission counts. Winners are announced 23 Nov 2026.

## What to submit (via the HackerRank event page)

| # | Item | Limits |
|---|------|--------|
| 1 | Eval as a **ZIP**, code only | max 50 MB, includes README, no keys, no video |
| 2 | **Video** walkthrough link | max 5 min, opens without permission |
| 3 | Short **description** | what was built, what it shows about model limits |

## What judges look for

- A real limitation that matters in practice, not a trick question.
- 5 to 10 clear tasks, each with a defensible correct answer.
- A reliable grader: no false passes, no false fails.
- Frontier models fail for a reason you can explain.
- Reproducible in a clean environment, original, public or synthetic data only.

## The eval (TODO)

- **What it tests:** TODO
- **Who it is for:** TODO
- **Why it matters:** TODO

## Run it (TODO: verify from a clean clone)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # add your own OPENROUTER_API_KEY
python -m evalkit.run --model <model-id> --out results/<run-name>
python -m evalkit.report results/<run-name>
```

Approximate runtime: TODO. Approximate cost per model: TODO. Expected headline results: see `results/`.

## Folder structure

Keep the repo small and flat. Everything a judge needs is reachable from this README.

```
.
├── README.md              # this file; the first thing judges read
├── requirements.txt       # pinned versions (or pyproject.toml + uv.lock)
├── .env.example           # variable names only, never real keys
├── .gitignore             # .env, .venv, __pycache__, raw model outputs not worth shipping
├── data/
│   ├── tasks.jsonl        # one task per line: id, prompt, expected answer/rubric, metadata
│   └── README.md          # source, licence, how synthetic data was generated
├── evalkit/               # the code, as a package
│   ├── run.py             # load tasks -> call model -> save raw outputs
│   ├── models.py          # one thin client (OpenAI-compatible, e.g. OpenRouter)
│   ├── grader.py          # scoring logic, deterministic where possible
│   └── report.py          # results -> table / summary
├── tests/
│   ├── test_grader.py     # known-good answers pass, known-bad answers fail
│   └── test_tasks.py      # schema check, unique ids, no duplicate prompts
├── results/               # small result files for the headline claims (json/csv/md)
│   └── <model>__<date>/
├── docs/
│   └── failure_analysis.md  # where and why models fail, with examples
└── scripts/               # optional helpers (data generation, packaging the ZIP)
    └── make_zip.sh
```

### Conventions

- **Tasks are data, not code.** `data/tasks.jsonl` holds every task so the grader and the tasks can change independently.
- **Grader is tested.** Run `pytest` before every submission. A grader that cannot reject a wrong answer is the most common eval bug.
- **Deterministic runs.** Temperature 0 and fixed seeds where the provider allows it. Record model id, date and parameters next to each result.
- **Raw outputs are kept** for the runs behind your claims, so judges can check scoring without paying for model calls.
- **No secrets.** Keys come from environment variables only. Check `git log` and the ZIP before submitting.
- **Large files stay out.** The ZIP limit is 50 MB. Host big data elsewhere and link it here with fetch instructions.
- **One command to run, one to report.** Anything more and a judge may give up.

## Pre-submission checklist

- [ ] ZIP opens and is under 50 MB
- [ ] README runs end to end from a clean clone
- [ ] `pytest` passes
- [ ] No API keys, passwords or private data anywhere
- [ ] Results shown for at least one frontier model, with failure analysis
- [ ] Video link opens without permission and plays with audio
- [ ] Description filled in
- [ ] Earlier work or existing benchmarks disclosed, if any

## Contact

Organizers: hackathon@micro1.ai
