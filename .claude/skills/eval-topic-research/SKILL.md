---
name: eval-topic-research
description: Use when picking or validating the topic of an AI eval or benchmark hackathon entry - "what should the eval test", "do frontier models really fail at X", "has this benchmark been done", prior-art and originality checks, or deciding between candidate eval ideas.
---

# Eval Topic Research

Merges two research skills: the async, cited-report flow of sanjay3290/deep-research and the tiered-source, checkpointed, self-stopping loop of Anjos2/recursive-research. It is cut down to one question: **is there a real, explainable failure here that nobody has already benchmarked?**

The Gemini Deep Research script ($2-5 per run, needs a key) is not used. Use WebSearch and WebFetch, or the `researcher` subagent per thread.

## 1. Ask once, then go

Ask the user one time, then run without further questions:
1. Domains they know well (judges reward expertise).
2. Time budget (default: 45 min).

## 2. Score candidates (weighted decision matrix)

Generate 5-8 candidate topics and score each one from 1 to 5:

| Criterion | Weight |
|---|---|
| Frontier models plausibly fail **for a nameable reason** | 5 |
| Every task can have one defensible answer | 5 |
| Deterministic grading possible (exact / numeric / regex) | 4 |
| Synthetic or public data only | 3 |
| User has domain expertise | 3 |
| Not already a known benchmark | 4 |

Keep the top 3.

## 3. Inversion pass (Munger), mandatory

For each of the top 3, answer in writing:
- How is this a **trick question** rather than a real limitation?
- Which existing benchmark already covers it? Search `"<topic> benchmark LLM"`, arXiv, Papers with Code, and Hugging Face datasets.
- What would make a model pass it for the wrong reason (memorized dataset, leaked answer)?

Drop any candidate that cannot survive these questions.

## 4. Probe before committing

Write 2 draft tasks for the top pick and run them on one cheap model plus one frontier model (`python -m evalkit.run`). If the frontier model passes both easily, go back to step 2.

## 5. Source tiers

- **Tier 1**: peer-reviewed papers, official model cards and docs, standards.
- **Tier 2**: arXiv preprints, maintained benchmark repos, known researchers' blogs.
- **Tier 3**: blogs that cite Tier 1 or Tier 2.
- **Reject**: unsourced posts, SEO aggregators, AI-written listicles.

Every claim of the form "models fail at X" needs at least one Tier 1 or Tier 2 source, or your own probe result.

## 6. Checkpoint and stop

Write `docs/research/<slug>.md` after each step: candidates, scores, inversion answers, sources with tiers, probe results. This lets the work survive `/clear`. Stop when one topic passes steps 3 and 4, or when the time budget runs out. Then pick the best surviving topic and say what is still uncertain.

**Output:** the 2-line idea for README "The eval", the failure hypothesis, prior art to disclose, and links.

## Red flags

- "Models are bad at math/counting letters": known and benchmarked. Not original.
- No probe run: the failure is assumed, not shown.
- Only Tier 3 sources behind the main claim.
