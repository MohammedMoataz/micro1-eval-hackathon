---
name: eval-submission
description: Use when finishing an eval hackathon entry - filling README TODOs, clean-room reproducibility test, building the ZIP, writing the video script or short description, scanning for secrets, or before clicking Submit on HackerRank.
---

# Eval Submission

Covers delivery steps 8-13. Do the gates in order. Each one needs evidence (a command and its output) before you move on.

## Gate 1: README complete (step 8)

```bash
git grep -n "TODO" -- README.md data/ docs/failure_analysis.md
```

The search must return nothing (run it after committing; `git grep` only sees tracked files). The README must state: what the eval tests, who it is for, why it matters, the run and report commands, runtime, cost per model, and headline results with their `results/` path.

## Gate 2: Tests and audit

```bash
pytest -q
python .claude/skills/eval-data-audit/audit.py
```

## Gate 3: Clean-room (step 9)

```powershell
git clone . $env:TEMP\cleanroom; cd $env:TEMP\cleanroom
python -m venv .venv; .venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest -q
# then follow ONLY the README run commands, with one cheap model
```

Fix anything that breaks in the repo, not in the clean-room copy. Uncommitted files will be missing from the clone, so commit first. Delete the clone afterwards.

## Gate 4: Secrets

```bash
git log -p | grep -iE "sk-or-|sk-ant-|api[_-]?key *= *[^ ]{8,}|bearer "
git grep -iE "sk-or-|sk-ant-|OPENROUTER_API_KEY=[^ ]"
python -c "import zipfile,re;z=zipfile.ZipFile('dist/eval.zip');print([n for n in z.namelist() if re.search(rb'sk-or-|sk-ant-',z.read(n))])"
```

The `f"Bearer {key}"` line in `evalkit/models.py` is an expected hit; it is code, not a key. `.env.example` may contain variable names only. Any hit means you rotate the key **first**, then remove it from the history.

## Gate 5: ZIP (step 11)

```bash
python scripts/make_zip.py
python -c "import zipfile;n=zipfile.ZipFile('dist/eval.zip').namelist();print(len(n));print([x for x in n if x == '.env' or x.startswith(('.venv/','.claude/','.git/')) or x.endswith(('.mp4','.mov'))])"
```

The second command must print `[]`. The ZIP must be under 50 MB and include the README.

## Gate 6: Video (step 10), 5 minutes maximum

| Time | Beat |
|---|---|
| 0:00-0:40 | The limitation, and why it matters in practice |
| 0:40-1:40 | One task on screen: prompt, correct answer, how it was derived |
| 1:40-2:40 | Grader, and the tests proving it rejects wrong answers |
| 2:40-4:00 | Live run plus report: the headline number, one failure quoted |
| 4:00-5:00 | Why models fail, limits of the eval, how to reproduce |

Open the link in an incognito window and check that the audio plays.

## Gate 7: Description (2-4 sentences)

What was built, which limitation it shows, the headline number, and how many tasks and models.

## Gate 8: Submit (steps 12-13)

Upload the ZIP, paste the video link, fill in the description, and tick the README pre-submission checklist. **Submit is final.** Confirm with the user before clicking it.
