import math

import pytest

from builder.calc import CalcError, check_question, evaluate, first_number


def test_evaluate_arithmetic_and_functions():
    assert evaluate("1 - (n - 1) / (n - k - 1) * (1 - r2)", {"n": 60, "k": 5, "r2": 0.63}) == pytest.approx(0.5957, abs=1e-4)
    assert evaluate("ln(exp(2)) + sqrt(16)", {}) == pytest.approx(6)
    assert evaluate("-x ** 2", {"x": 3}) == -9


@pytest.mark.parametrize("expr", ["__import__('os')", "x.real", "[1][0]", "open('f')", "y"])
def test_evaluate_rejects_anything_else(expr):
    with pytest.raises(CalcError):
        evaluate(expr, {"x": 1})


def test_evaluate_math_errors_are_calc_errors():
    with pytest.raises(CalcError):
        evaluate("1 / 0", {})


@pytest.mark.parametrize("text, value", [
    ("13.54.", 13.54), ("$1,200", 1200), ("-5.4%", -5.4), ("(0.25)", -0.25), ("−3.1", -3.1),
    ("AAA: 18.0%", 18.0), ("−£40,000", -40000), ("€9,400", 9400), ("none", None),
])
def test_first_number(text, value):
    got = first_number(text)
    assert got == value if value is None else math.isclose(got, value)


def _q(options, answer="A", **calc):
    return {"options": options, "answer": answer,
            "calc": {"inputs": {"n": 60, "k": 5, "r2": 0.63}, "expr": "1 - (n-1)/(n-k-1)*(1-r2)", **calc}}


def test_check_question_passes():
    assert check_question(_q(["0.596.", "0.630.", "0.700."])) == []
    assert check_question(_q(["59.6%", "63.0%", "70.0%"], scale=100)) == []


def test_check_question_catches_wrong_answer_and_ambiguous_distractor():
    errs = check_question(_q(["0.596", "0.630", "0.700"], answer="B"))
    assert any("correct option B is 0.63" in e for e in errs)
    assert any("wrong option A" in e for e in errs)
    errs = check_question(_q(["0.596", "0.5961", "0.700"]))
    assert errs == ["wrong option B (0.5961) also matches 0.595741"]


def test_non_calc_question_is_skipped():
    assert check_question({"options": ["a", "b", "c"], "answer": "A"}) == []
