from collections import Counter

import pytest

from builder.parse.normalize import BAD, RepairStats, Vocab, clean_line, repair_ligatures, repair_word


@pytest.mark.parametrize("damaged, expected", [
    (f"Mul{BAD}ple", "Multiple"),        # ti
    (f"o{BAD}en", "often"),              # ft
    (f"be{BAD}er", "better"),            # tt
    (f"Por{BAD}olio", "Portfolio"),      # tf
    (f"Coef{BAD}icient", "Coefficient"), # f
    (f"overfi{BAD}ng", "overfitting"),   # tti
    (f"{BAD}me", "time"),
])
def test_repair_known_words(vocab, damaged, expected):
    assert repair_word(damaged, vocab) == (expected, True)


def test_repair_preserves_all_caps(vocab):
    assert repair_word(f"MUL{BAD}PLE", vocab)[0] == "MULTIPLE"


def test_unknown_word_falls_back_to_ti_prior():
    v = Vocab.from_counts(Counter({"nation": 50, "station": 40, "ration": 10}))
    fixed, known = repair_word(f"globaliza{BAD}on", v)
    assert (fixed, known) == ("globalization", False)


def test_inflected_relative_counts_as_known():
    v = Vocab.from_counts(Counter({"exponentially": 3}))
    assert repair_word(f"exponen{BAD}al", v) == ("exponential", True)


def test_override_wins_and_keeps_capitalisation():
    v = Vocab.from_counts(Counter({"setiled": 99}))
    v.overrides = {"se?led": "settled"}
    assert repair_word(f"Se{BAD}led", v) == ("Settled", True)


def test_repair_stats(vocab):
    stats = RepairStats()
    out = repair_ligatures(f"a mul{BAD}ple model o{BAD}en works", vocab, stats)
    assert out == "a multiple model often works"
    assert sum(stats.fixed.values()) == 2 and not stats.guessed


@pytest.mark.parametrize("line, expected", [
    ("Video covering this content is available online.", None),
    ("Video covering this content is ~~av~~ ailable online.", None),
    ("Video covering <u>this content is</u> available online.", None),
    ("Video covering this content is **LOS 10.a: Explain", "**LOS 10.a: Explain"),
    ("**KEY CONCEPTS** <mark>e—SCSC</mark>", "**KEY CONCEPTS**"),
    ("plain text", "plain text"),
])
def test_clean_line(line, expected):
    got = clean_line(line)
    assert (got.strip() if got else got) == expected
