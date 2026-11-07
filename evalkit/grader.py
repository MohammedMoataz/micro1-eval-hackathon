"""Scoring. Deterministic checks only; add a new kind by adding a function to GRADERS."""
import re


def _norm(s: str) -> str:
    return " ".join(s.strip().strip(".").lower().split())


def exact(output: str, answer: str) -> bool:
    return _norm(output) == _norm(answer)


def numeric(output: str, answer: str) -> bool:
    # ponytail: compares the LAST number in the output; tolerance fixed at 1e-6.
    nums = re.findall(r"-?\d+(?:\.\d+)?", output.replace(",", ""))
    return bool(nums) and abs(float(nums[-1]) - float(answer)) < 1e-6


def regex(output: str, answer: str) -> bool:
    return re.search(answer, output, re.IGNORECASE | re.DOTALL) is not None


GRADERS = {"exact": exact, "numeric": numeric, "regex": regex}


def grade(task: dict, output: str) -> bool:
    return GRADERS[task["grader"]](output, task["answer"])
