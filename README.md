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
└── scripts/               # helpers
    └── make_zip.py        # builds dist/eval.zip, fails if over 50 MB
```

### Conventions

- **Tasks are data, not code.** `data/tasks.jsonl` holds every task so the grader and the tasks can change independently.
- **Grader is tested.** Run `pytest` before every submission. A grader that cannot reject a wrong answer is the most common eval bug.
- **Deterministic runs.** Temperature 0 and fixed seeds where the provider allows it. Record model id, date and parameters next to each result.
- **Raw outputs are kept** for the runs behind your claims, so judges can check scoring without paying for model calls.
- **No secrets.** Keys come from environment variables only. Check `git log` and the ZIP before submitting.
- **Large files stay out.** The ZIP limit is 50 MB. Host big data elsewhere and link it here with fetch instructions.
- **One command to run, one to report.** Anything more and a judge may give up.

## Delivery plan

Deadline is Mon 9 Nov 2026, 07:15 Cairo. **Plan: finish and submit everything today (Sat 7 Nov).** Sun 8 Nov is the safety buffer and resubmitting is allowed until the deadline.

Suggested time blocks for today:

| Block | Steps |
|-------|-------|
| 1. Setup and idea | 1 to 2 |
| 2. Tasks, grader, runner | 3 to 5 |
| 3. Model runs and failure check | 6 to 7 |
| 4. Docs and clean-room test | 8 to 9 |
| 5. Video, ZIP, submit | 10 to 13 |

Cut scope, not steps: 5 solid tasks beat 10 shaky ones.

**Steps**
1. **Read the Instructions tab** on HackerRank: format, rubric, reference examples, and what Q1 (upload) and Q2 (subjective) ask. This decides the folder layout.
2. **Pick one narrow topic** in a domain you know, where frontier models really fail. Not a trick question. Write the idea in 2 lines and check it has a clear correct answer.
3. **Draft 5 to 10 tasks** in `data/tasks.jsonl` (id, prompt, expected answer or rubric, metadata). Public or synthetic data only.
4. **Build the grader.** Prefer deterministic checks. Add `tests/test_grader.py` with known-good and known-bad answers, and confirm wrong answers are rejected.
5. **Write the runner.** Load tasks, call the model through an OpenAI-compatible client (OpenRouter), save raw outputs. Temperature 0, record model id and date.

6. **Run on models.** Free model first to debug, then at least one frontier model. API cost is yours.
7. **Check the failures.** Confirm models fail for the intended reason, not a bad task or grader. Fix and rerun if not. Write `docs/failure_analysis.md` with examples.
8. **Finish this README.** Fill every `TODO`: what it tests, who it is for, why it matters, run commands, runtime, cost, expected results.
9. **Clean-room test.** Clone into a fresh folder, new venv, follow only the README. Fix whatever breaks.
10. **Record the video** (5 min max): problem, how it works, how it is graded, what it reveals. Upload to YouTube, Drive, Loom or Vimeo. Open the link in an incognito window and check the audio.
11. **Build the ZIP.** Code only, under 50 MB, no `.env`, keys, videos or `.venv`. Open it and scan for secrets.

12. **Upload the ZIP**, paste the video link, fill in the short description. Run the checklist below.
13. **Click Submit only after everything is uploaded.** It is final.

Resubmitting before the deadline is allowed; only the latest complete submission counts. Questions: hackathon@micro1.ai.

## Suggested skills and tools

This is an eval-design task, not model training. Heavy ML skills matter only if the chosen domain needs them.

**Core skills**
- Task design: unambiguous prompts, one defensible answer, difficulty that frontier models fail for a real reason.
- Grader design: exact match, programmatic checks, or rubric/LLM judge. Test the grader on known-good and known-bad answers.
- Dataset handling: plain JSON/JSONL/CSV, versioned, public or synthetic, checked for duplicates and answer leakage.
- Reproducibility: pinned dependencies, fixed seeds, temperature 0, one-command run, expected results documented.
- Writing: a clear README and a 5-minute video that explain the failure.

**Tools to install** (suggestions from general knowledge, not verified against current docs)
- Python 3 with `uv` or `venv` for a pinned environment.
- `pandas` or `polars` to build and check the task dataset; `pytest` for the grader tests.
- An OpenAI-compatible client pointed at OpenRouter to run many models with one key.
- Optional: `inspect-ai` as an eval framework. The FAQ does not require any framework; plain scripts are fine.
- Only if the domain needs them: `scikit-learn`, PyTorch, Hugging Face `datasets`.

**Project Claude Code skills** (in `.claude/skills/`, loaded automatically in this repo, excluded from the ZIP)

| Skill | Delivery steps | Built from |
|-------|----------------|------------|
| `eval-topic-research` | 1-2: pick and validate the topic, prior-art check | sanjay3290/deep-research + Anjos2/recursive-research |
| `eval-task-design` | 3-4: tasks, grader choice, grader tests | README core skills |
| `eval-data-audit` | 3, 6-7: `audit.py` checks tasks and results | coffeefuelbump/csv-data-summarizer |
| `eval-failure-analysis` | 7: classify every failure, write `docs/failure_analysis.md` | recursive-research "no self-confirmation" |
| `eval-submission` | 8-13: README, clean-room, secrets, ZIP, video, submit | README checklist |
| `ml-domain-tasks` | only if the topic is ML | the three community skills below |

**Community Claude Code skills** (unvetted, small install counts; read the SKILL.md before installing; the useful parts are distilled into `ml-domain-tasks`)
- [ml-model-training](https://claudemarketplaces.com/skills/secondsky/claude-skills/ml-model-training): scikit-learn, PyTorch, TensorFlow pipelines.
- [pytorch](https://claudemarketplaces.com/skills/mindrally/skills/pytorch): nn.Module patterns, mixed precision.
- [ml-expert](https://claudemarketplaces.com/skills/personamanagmentlayer/pcl/ml-expert): boilerplate templates.
- Marketplace: [mcpmarket data-science-ml](https://mcpmarket.com/tools/skills/categories/data-science-ml).

**Reading**
- [Making LLM Evaluation Reproducible in Python](https://pretalx.com/euroscipy-2026/talk/FT7JQV/)
- [LLM eval libraries 2026](https://futureagi.com/blog/best-llm-eval-libraries-2026) (vendor blog, treat rankings with caution)

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
