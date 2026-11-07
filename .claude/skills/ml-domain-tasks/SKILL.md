---
name: ml-domain-tasks
description: Use only when the chosen eval topic is itself about machine learning (training, PyTorch, scikit-learn, data leakage, overfitting, metrics) and tasks or reference answers need ML code or ML ground truth.
---

# ML Domain Tasks

Distilled from the three community skills the README lists: secondsky/ml-model-training, mindrally/pytorch, and personamanagmentlayer/ml-expert. They mostly teach how to *train* models. This hackathon *evaluates* models, so only the parts that turn into gradable tasks or trustworthy ground truth are kept. MLOps, serving, and diffusion material was dropped.

## Ground truth must be computed, not recalled

When an answer depends on running ML code (a metric, a shape, a split size), generate it with a script in `scripts/`, with seeds fixed:

```python
import random, numpy as np
random.seed(0); np.random.seed(0)
# torch.manual_seed(0) only if torch is needed; pin its version in requirements.txt
```

Store the script output as `answer` and the script path in `metadata.source`. Never hand-type a number that a model could dispute.

## Task ideas with one defensible answer

These are the classic mistakes from the source skills, turned into eval tasks that models often get wrong:

| Pitfall | Task shape | Grader |
|---|---|---|
| Data leakage (scaler fit before the split) | Show a code snippet and ask "does test information leak? Answer yes or no, then the line number" | `regex` |
| Test set used for tuning | Describe a pipeline and ask which reported number is optimistic | `exact` |
| Class imbalance | Give a confusion matrix and ask for precision or recall of the minority class | `numeric` |
| Shape bookkeeping | Give an `nn.Sequential` and an input shape, ask for the output shape | `exact` |
| Split arithmetic | Give 70/15/15 of N with integer rounding as sklearn does it, ask for the test size | `numeric` |

## Keep the repo light

- Add `scikit-learn` or `torch` to `requirements.txt` **only if** the runner or grader imports them. Ground-truth scripts can document their own extra installs.
- The ZIP limit is 50 MB: no model weights and no datasets in the repo. Use synthetic arrays generated from a seed.
