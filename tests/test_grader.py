import pytest

from evalkit.grader import grade


@pytest.mark.parametrize("kind,answer,good,bad", [
    ("exact", "paris", " Paris. ", "London"),
    ("regex", r"\bfoo\b", "a Foo b", "foobar"),
])
def test_good_passes_bad_fails(kind, answer, good, bad):
    t = {"grader": kind, "answer": answer}
    assert grade(t, good) and not grade(t, bad)


N = {"grader": "numeric", "answer": "12.09"}


@pytest.mark.parametrize("out,ok", [
    ("work...\nANSWER: 12.09", True),
    ("ANSWER: 12.09%", True),             # unit symbols are fine
    ("ANSWER: 12.1", False),              # not rounded to the 2 decimals the prompt asks for
    ("ANSWER: 12.090", True),
    ("ANSWER: -12.09", False),            # sign matters
    ("ANSWER: 7.10", False),              # the trap answer
    ("ANSWER: 12.5", False),
    ("The answer is 12.09", False),       # right number, no ANSWER line
    ("ANSWER: 12.09 (up from 10)", False),  # two numbers on the line: ambiguous
    ("ANSWER: 99\nsome text 12.09", False),  # right number outside the ANSWER line
    ("ANSWER: 99\nANSWER: 12.09", True),  # the last ANSWER line counts
    ("ANSWER: 1,209", False),
    ("ANSWER: −12.09", False),       # unicode minus read as negative
])
def test_numeric(out, ok):
    assert grade(N, out) is ok


def test_numeric_thousands_separator():
    assert grade({"grader": "numeric", "answer": "1739817.0"}, "ANSWER: 1,739,817")
