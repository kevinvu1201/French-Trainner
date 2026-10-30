from __future__ import annotations

import copy
import shutil
from collections import Counter
from pathlib import Path

import pytest

from builder.parse.normalize import Vocab

FIXTURES = Path(__file__).parent / "fixtures"
REPO = Path(__file__).parent.parent

# Words a real corpus would contain undamaged.
KNOWN_WORDS = ("multiple often partial assumptions calculating mean reverting stationarity "
               "time institute portfolio better after written coefficient overfitting").split()


@pytest.fixture
def sample_text() -> str:
    return (FIXTURES / "sample_book.md").read_text(encoding="utf-8")


@pytest.fixture
def vocab(sample_text: str) -> Vocab:
    v = Vocab.from_texts([sample_text])
    counts = Counter(v.counts)
    counts.update({w: 5 for w in KNOWN_WORDS})
    return Vocab.from_counts(counts)


# The fixture book's two topics, equally weighted (the real config weights the French topics).
FIXTURE_WEIGHTS = "verified: true\nweights:\n  quant: {min: 5, max: 10}\n  economics: {min: 5, max: 10}\n"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A throwaway project root with the real config and the fixture book."""
    shutil.copytree(REPO / "config", tmp_path / "config")
    (tmp_path / "content").mkdir()
    shutil.copy(FIXTURES / "sample_book.md", tmp_path / "content" / "Book 9.md")
    # The fixture's readings are 1-2; map them to two topics.
    (tmp_path / "config" / "topics.yaml").write_text(
        "topics:\n  - {id: quant, name: Quant, readings: [1, 1]}\n  - {id: economics, name: Econ, readings: [2, 2]}\n",
        encoding="utf-8")
    (tmp_path / "config" / "exam_weights.yaml").write_text(FIXTURE_WEIGHTS, encoding="utf-8")
    return tmp_path


_GOOD_GENERATED = {
    "module": "m01.2",
    "source_hash": "abc123",
    "learning": {
        "logic_chain": [
            {"stage": "assumption", "md": "OLS assumptions hold."},
            {"stage": "mechanism", "md": "R2 rises with every added variable."},
            {"stage": "result", "md": "Adjusted R2 penalises k."},
        ],
        "why_it_matters": "Choosing between competing models.",
        "exam_approach": {"look_first": ["n and k"], "traps": ["using R2 instead"], "distractors": ["SST"]},
    },
    "connections": [{"to": "m01.1", "type": "requires", "note": "Uses the regression set-up."}],
    "questions": [{
        "id": "q.01.c.001", "los": "los.01.c", "stem": "Adjusted R2 is closest to:",
        "options": ["0.596", "0.630", "0.700"], "answer": "A",
        "explanations": {"A": "Correct. 1 − (59/54)(0.37) = 0.596.", "B": "Wrong. That is R², not adjusted R².",
                         "C": "Wrong. The penalty term has the wrong sign."},
        "difficulty": 2, "qtype": "calculation",
        "calc": {"inputs": {"n": 60, "k": 5, "r2": 0.63}, "expr": "1-(n-1)/(n-k-1)*(1-r2)"},
    }],
    "item_sets": [],
    "formulas": [{
        "id": "f.01.adj-r2", "los": ["los.01.c"], "name": "Adjusted R²",
        "latex": "\\bar R^2 = 1 - \\frac{n-1}{n-k-1}(1-R^2)",
        "variables": [{"sym": "n", "def": "observations"}],
        "intuition": "Penalty for extra regressors.", "when_to_use": "Comparing models.",
        "common_mistake": "Using k+1 in place of k.",
    }],
    "repairs": {"fig.0123456789": {"kind": "formula", "latex": "R^2"}},
}


@pytest.fixture
def good_generated() -> dict:
    """A valid generated/<topic>/<module>.json document."""
    return copy.deepcopy(_GOOD_GENERATED)
