"""Scoring. Deterministic checks only; add a new kind by adding a function to GRADERS."""
import re


def _norm(s: str) -> str:
    return " ".join(s.strip().strip(".").lower().split())


def exact(output: str, answer: str) -> bool:
    return _norm(output) == _norm(answer)


def numeric(output: str, answer: str) -> bool:
    """Reads the LAST line of the form `ANSWER: <number>`; no such line, or not exactly one number on it, fails.
    Passes when within half a unit of the answer's last decimal (the prompt states the rounding)."""
    lines = re.findall(r"(?im)^\W*answer\s*[:=]\s*(.+)$", output)
    if not lines:
        return False
    nums = re.findall(r"-?\d+(?:\.\d+)?", lines[-1].replace(",", "").replace("−", "-"))
    if len(nums) != 1:
        return False
    tol = 0.5 * 10 ** -(len(answer.split(".")[1]) if "." in answer else 0) + 1e-9
    return abs(float(nums[0]) - float(answer)) <= tol


def regex(output: str, answer: str) -> bool:
    return re.search(answer, output, re.IGNORECASE | re.DOTALL) is not None


GRADERS = {"exact": exact, "numeric": numeric, "regex": regex}


def grade(task: dict, output: str) -> bool:
    return GRADERS[task["grader"]](output, task["answer"])
