# Topic research: Kaggle-style data-science tasks (2026-11-07)

Question: is there a real, explainable failure in Kaggle-style data work that a single-prompt eval can show?
Budget: 30 minutes. Probes ran 1 trial each, temperature 0, through `evalkit.run`.

## Prior art

| Source | Tier | Relevance |
|---|---|---|
| DABstep, Adyen (arXiv 2506.23719) | 2 | Multi-step data-agent tasks; best agent 14.55% on hard tasks (o4-mini, June 2025). Agents run code, so it does not cover single-prompt answering. Known benchmark. |
| DiscRun-Bench (ICMLA, UNLV) | 2 | Names "silent assumption-failure" in LLM data prep as the most consequential failure. |
| Kaggle Benchmarks hub, kaggle.com/benchmarks | 3 | Community leaderboards; no official data-science-task leaderboard found. |
| 36-case data-science judgment benchmark (dev.to write-up, Kaggle leaderboard) | 3 | Small, self-reported; measures advice, not computed answers. |

No published benchmark was found for "paste a Kaggle CSV extract plus its data dictionary and ask a number", or for predicting the output of pandas cells.

## Probes

| Probe | Trap | gemini-3.5-flash | nemotron-3-ultra (free) |
|---|---|---|---|
| 40-row house-prices extract | dictionary says LotArea 0 = not recorded | pass | pass |
| 41-row transactions extract | dictionary says repeated ids are export duplicates | pass | pass |
| 240-row transactions extract | duplicates + EUR rows converted at a dictionary rate | pass (33 s) | pass (196 s) |
| pandas cell: left merge + groupby | many-to-many merge duplicates rows; NaN group key dropped | pass (80 s) | pass (48 s) |
| pandas cell: parse_dates + std | month-first date parsing; std uses ddof=1 | pass (80 s) | pass (55 s) |

All answers were computed by code (the pandas ones by executing the cell under pandas 2.2.3). Prompts and raw outputs are in the session scratchpad, not shipped.

## Conclusion

Current thinking models (including free ones) handle every single-trap Kaggle-style task we tried: they apply data-dictionary rules over 240 rows and know the pandas defaults usually blamed for silent bugs. Together with the finance v1/v2 results (8/8 on both sets), no single-trap design has produced a failure so far.

Not tested yet, and the most likely places to find a failure:
- several traps stacked in one long excerpt (several tables, footnotes, restatements, units);
- answers that need exact arithmetic over many hundreds of rows;
- non-thinking or smaller models (weaker claim: "smaller models fail").

Topic switching stopped here because of the deadline (Mon 9 Nov 07:15 Cairo).

## Kaggle competitions and benchmarks scan (kaggle.com/competitions, kaggle.com/benchmarks, 2026-11-07)

Low top scores on Kaggle-hosted leaderboards (Tier 2-3: lab/team-run leaderboards, scores as displayed):

| Benchmark | Top score | Fits a single-prompt, deterministic, free-model eval? |
|---|---|---|
| SciCode (multi-step scientific code) | 14-18% | Partly: numeric answers possible, but failure is long exact computation |
| SpreadsheetBench 2 (end-to-end spreadsheet workflows) | 35% | Partly: the failure comes from agentic file work, not one prompt |
| SEC-bench Pro V8 (vulnerability reproduction) | 42% | No: needs a sandbox |
| MultiLoKo (local knowledge, 31 languages) | 57% | Yes, but answers need sourced local facts |
| ITBench (IT automation) | 58% | No: environment needed |
| FACTS Multimodal | 60% | No: images |
| AA-LCR v1.1 (reasoning over 72k-115k-token document sets, single call) | 85% (15% still wrong) | Yes: single call, exact answers |

Kaggle community benchmarks close to our finance idea are saturated: "Indian Business Data: GST, UPI and Lakh-Crore" 100% / 100% / 99%, "Spec, Hash or Guess: VeriFactu" 100%. This matches our probes.

Competitions with known model failures (ARC Prize 2026 ARC-AGI-2/3, Squares in Squares, Name That LLM) are existing benchmarks or need search/optimization, so originality would be weak.
