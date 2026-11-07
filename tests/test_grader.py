import pytest

from evalkit.grader import grade


@pytest.mark.parametrize("kind,answer,good,bad", [
    ("exact", "paris", " Paris. ", "London"),
    ("numeric", "42", "The answer is 42", "The answer is 43"),
    ("numeric", "1000", "1,000", "100"),
    ("regex", r"\bfoo\b", "a Foo b", "foobar"),
])
def test_good_passes_bad_fails(kind, answer, good, bad):
    t = {"grader": kind, "answer": answer}
    assert grade(t, good) and not grade(t, bad)
