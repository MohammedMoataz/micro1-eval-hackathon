## nvidia/nemotron-3-ultra-550b-a55b:free (2026-11-08, 2 trials, temperature 0.0)

| metric | value |
|---|---|
| pass rate | 51.3% (95% CI 32.4% to 70.0%, bootstrap over tasks) |
| pass@2 (any trial right) | 60.0% |
| pass^2 (all trials right) | 40.0% |
| API errors (not graded) | 1 |
| graded attempts | 39 over 20 tasks |
| runtime | 1804.1 s |

## gemini-3.5-flash (2026-11-08, 1 trials, temperature 0.0)

| metric | value |
|---|---|
| pass rate | 100.0% (95% CI 100.0% to 100.0%, bootstrap over tasks) |
| pass@1 (any trial right) | 100.0% |
| pass^1 (all trials right) | 100.0% |
| API errors (not graded) | 0 |
| graded attempts | 20 over 20 tasks |
| runtime | 179.1 s |

## Accuracy by trap type (model x trap)

| model | area-code | id-code |
|---|---|---|
| nvidia/nemotron-3-ultra-550b-a55b:free | 100.0% | 45.7% |
| gemini-3.5-flash | 100.0% | 100.0% |

## Passes per task (task x model)

| task | nvidia/nemotron-3-ultra-550b-a55b:free | gemini-3.5-flash |
|---|---|---|
| eg-abroad-01-ar | 2/2 | 1/1 |
| eg-abroad-01-en | 2/2 | 1/1 |
| eg-area-01-ar | 2/2 | 1/1 |
| eg-area-01-en | 2/2 | 1/1 |
| eg-code-01-ar | 2/2 | 1/1 |
| eg-code-01-en | 2/2 | 1/1 |
| eg-count-01-ar | 2/2 | 1/1 |
| eg-count-01-en | 2/2 | 1/1 |
| eg-gov-01-ar | 1/2 | 1/1 |
| eg-gov-01-en | 0/1 | 1/1 |
| eg-gov-02-ar | 0/2 | 1/1 |
| eg-gov-02-en | 0/2 | 1/1 |
| eg-gov-03-ar | 0/2 | 1/1 |
| eg-gov-03-en | 0/2 | 1/1 |
| eg-gov-04-ar | 1/2 | 1/1 |
| eg-gov-04-en | 0/2 | 1/1 |
| eg-gov-05-ar | 1/2 | 1/1 |
| eg-gov-05-en | 0/2 | 1/1 |
| eg-gov-06-ar | 0/2 | 1/1 |
| eg-gov-06-en | 1/2 | 1/1 |
