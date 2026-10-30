"""Build-time verification of calculation questions.

A calculation question carries `calc: {inputs, expr, scale?, tol?}`. The
expression is evaluated with a whitelist-only AST walker (no eval), and the
result must match the first number in the correct option (times `scale`, e.g.
100 for an option written as a percentage) within relative tolerance `tol`.
Each wrong option must miss by more than `tol`, so no distractor is also right.
"""

from __future__ import annotations

import ast
import math
import operator
import re
from typing import Any

_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow}
_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {"ln": math.log, "log": math.log, "log10": math.log10, "exp": math.exp, "sqrt": math.sqrt,
          "abs": abs, "min": min, "max": max, "sum": lambda *a: sum(a)}
_NUMBER = re.compile(r"(?<![\w.])([-−–]?)\s*[$€£¥]?\s*(\()?(\d[\d,]*(?:\.\d+)?|\.\d+)")


class CalcError(ValueError):
    pass


def evaluate(expr: str, inputs: dict[str, float]) -> float:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise CalcError(f"syntax error in expr: {e.msg}") from e

    def ev(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name):
            if node.id in inputs:
                return float(inputs[node.id])
            raise CalcError(f"unknown name '{node.id}'")
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return _UNARY[type(node.op)](ev(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS and not node.keywords:
            return float(_FUNCS[node.func.id](*(ev(a) for a in node.args)))
        raise CalcError(f"disallowed syntax: {ast.dump(node)[:60]}")

    try:
        return ev(tree)
    except (ZeroDivisionError, OverflowError, ValueError) as e:
        if isinstance(e, CalcError):
            raise
        raise CalcError(f"math error: {e}") from e


def first_number(text: str) -> float | None:
    """First number in an option: '$1,200', '−£40,000', '-5.4%', '(0.25)', '−3.1' are all handled."""
    m = _NUMBER.search(re.sub(r"<[^>]+>", " ", text))
    if not m:
        return None
    value = float(m.group(3).replace(",", ""))
    negative = bool(m.group(1)) or bool(m.group(2))
    return -value if negative else value


def _close(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-9)


def check_question(q: dict[str, Any]) -> list[str]:
    calc = q.get("calc")
    if not calc:
        return []
    try:
        result = evaluate(calc["expr"], calc["inputs"]) * float(calc.get("scale", 1))
    except CalcError as e:
        return [str(e)]
    tol = float(calc.get("tol", 0.005))
    errors = []
    letters = ["A", "B", "C"]
    for letter, option in zip(letters, q["options"]):
        value = first_number(option)
        if letter == q["answer"]:
            if value is None:
                errors.append(f"correct option {letter} has no number")
            elif not _close(value, result, tol):
                errors.append(f"expr gives {result:.6g} but correct option {letter} is {value:g}")
        elif value is not None and _close(value, result, tol):
            errors.append(f"wrong option {letter} ({value:g}) also matches {result:.6g}")
    return errors
