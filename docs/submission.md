# Submission text

## Short description (paste into HackerRank; same text as the README section)

An English + Arabic eval of whether a model recalls the arbitrary province-code table inside the 14-digit Egyptian national ID or only guesses fluently: 10 tasks (20 rows), a deterministic grader with 37 offline tests, run on two free-tier models. `nvidia/nemotron-3-ultra-550b-a55b:free` named the right governorate in 4 of 23 graded attempts while passing all 16 control attempts, and once cited an "official CAPMAS/Ministry of Interior coding" for a wrong answer; `gemini-3.5-flash` passed 20 of 20. This is a capability gradient between two models, not a frontier-model failure, and the tasks were kept after probing (selection effect).
