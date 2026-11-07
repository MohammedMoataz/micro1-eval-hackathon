"""Scoring. Deterministic checks only; add a new kind by adding a function to GRADERS."""
import re
import unicodedata


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


_AR_MARKS = re.compile("[ً-ْـ]")  # tashkeel + tatweel
_AR_FOLD = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})


def _fold(s: str) -> str:
    """Case, Arabic diacritics, alef/teh-marbuta/alef-maqsura variants, markdown and edge punctuation."""
    s = unicodedata.normalize("NFKC", s)
    s = _AR_MARKS.sub("", s).translate(_AR_FOLD).lower()
    s = re.sub(r"[*_`\"'“”‘’«».,;:!؟،]", " ", s)
    return " ".join(s.split())


def answer_set(output: str, answer: str) -> bool:
    """Reads the LAST `ANSWER: ...` line; passes only if the whole line equals one of the accepted variants
    (`answer` is variants joined by `|`). "Ismailia, not Sharqia" fails; so does a missing ANSWER line."""
    lines = re.findall(r"(?im)^\W*answer\s*[:=]\s*(.+)$", output)
    return bool(lines) and _fold(lines[-1]) in {_fold(v) for v in answer.split("|")}


GRADERS = {"exact": exact, "numeric": numeric, "regex": regex, "answer_set": answer_set}


def grade(task: dict, output: str) -> bool:
    return GRADERS[task["grader"]](output, task["answer"])
