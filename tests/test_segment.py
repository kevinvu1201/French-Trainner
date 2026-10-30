import pytest

from builder.parse.lines import Line
from builder.parse.los import parse_los_list
from builder.parse.segment import parse_book


@pytest.fixture
def book(sample_text, vocab):
    return parse_book(sample_text, "Book 9.md", vocab)


def _line(no, md, heading=False):
    from builder.parse.lines import to_plain
    return Line(no, md, to_plain(md), heading)


def test_los_list_splits_run_together_items_and_joins_wraps():
    items = [
        _line(1, "**1.   Sample**", heading=True),
        _line(2, "The candidate should be able to:"),
        _line(3, "- a. describe one thing."),
        _line(4, "- b. explain two. c. evaluate three."),
        _line(5, "- d. calculate four and explain how"),
        _line(6, "the result is interpreted."),
    ]
    [r] = parse_los_list(items)
    assert [l.letter for l in r.los] == ["a", "b", "c", "d"]
    assert r.los[1].text == "explain two."
    assert r.los[3].text == "calculate four and explain how the result is interpreted."


def test_los_continues_into_unmarked_modules():
    from builder.parse.segment import parse_items

    lines = ["Learning Outcome Statements (LOS)|h", "1. Sample", "The candidate should be able to:",
             "a. describe one.", "b. explain two.", "READING 1|h", "SAMPLE|h",
             "MODULE 1.1: ONE|h", "**LOS 1.a: Describe one.**", "Text for a.",
             "MODULE 1.2: TWO|h", "More text, still about a.",  # no marker: continues 1.a
             "MODULE 1.3: THREE|h", "An intro sentence.", "**LOS 1.b: Explain two.**", "Text for b."]
    items = [_line(i, s.split("|")[0], heading=s.endswith("|h")) for i, s in enumerate(lines, 1)]
    [r] = parse_items(items, "t.pdf", "sha")["readings"]
    m1, m2, m3 = r["modules"]
    assert [(s["los"], s["cont"]) for s in m2["sections"]] == [(["a"], True)]
    # A module with its own marker keeps its intro unattributed rather than guessing.
    assert [(s["los"], s["cont"]) for s in m3["sections"]] == [([], False), (["b"], False)]


def test_readings_and_titles(book):
    assert [r["number"] for r in book["readings"]] == [1, 2]
    assert book["readings"][0]["title"] == "Sample Regression"
    # Module titles come from the CONTENTS pages, not the ALL-CAPS body header.
    assert [m["title"] for m in book["readings"][0]["modules"]] == ["Regression Basics and Assumptions", "Measuring Fit"]


def test_los_assignment_and_inference(book):
    r1 = {l["letter"]: l for l in book["readings"][0]["los"]}
    assert {k: v["module"] for k, v in r1.items()} == {"a": 1, "b": 1, "c": 2, "d": 2}
    assert r1["b"]["text"] == "explain the assumptions of the model."  # ligature repaired, inline split
    codes = [(i["code"], i["msg"]) for i in book["issues"]]
    assert any(c == "los_module_inferred" and "LOS 1.d" in m for c, m in codes)
    assert any(c == "los_module_inferred" and "LOS 2.b" in m for c, m in codes)
    assert not any(i["level"] == "error" for i in book["issues"])


def test_blocks(book):
    sections = book["readings"][0]["modules"][0]["sections"]
    a = next(s for s in sections if s["los"] == ["a"])["blocks"]
    # Page-break split paragraph is re-joined; video banner removed; note captured.
    assert a[0]["t"] == "p" and "is often estimated by ordinary least squares" in a[0]["md"]
    assert a[1] == {"t": "note", "md": "Remember that the slope is a partial effect."}
    b = next(s for s in sections if s["los"] == ["b"])["blocks"]
    assert b == [{"t": "ul", "items": ["Linearity between Y and the X variables.", "Homoskedastic residuals."]}]
    c = book["readings"][0]["modules"][1]["sections"][-1]["blocks"]
    kinds = [bl["t"] for bl in c]
    assert kinds == ["h", "cap", "fig", "ex", "p", "ans", "p"]
    assert c[0]["md"] == "Adjusted R<sup>2</sup>"
    assert c[3]["md"] == "Calculating adjusted R2"
    assert book["figures"][c[2]["id"]]["kind"] == "formula"
    assert book["figures"][c[2]["id"]]["caption"].startswith("Figure 1.1")


def test_quizzes(book):
    m11, m12 = book["readings"][0]["modules"]
    [q] = m11["quiz"]
    assert q["options"] == ["Linearity.", "Constant residual variance.", "Independence of X variables."]
    assert (q["answer"], q["los"]) == ("B", ["b"])
    q1, q2 = m12["quiz"]
    assert q1["vignette"] == "A model has n = 60, k = 5 and R2 = 0.63."
    assert q1["options"] == ["0.596.", "0.630.", "0.700."] and q1["answer"] == "A"
    assert "[[fig." in q1["explanation"] and "(Module" not in q1["explanation"]
    assert q2["vignette"] == q1["vignette"]
    assert q2["options"][1] == "lower adjusted R2." and q2["answer"] == "B"


def test_key_concepts_and_topic_quiz_skipped(book):
    r1, r2 = book["readings"]
    assert set(r1["key_concepts"]) == {"a", "c"}
    assert r2["key_concepts"]["a"][0]["md"].startswith("Level equals")
    # "Topic Quiz" page text must not leak into reading 2.
    assert "finished this topic" not in str(r2)
    # The FORMULAS appendix ends the body.
    assert "RSS / SST" not in str(book["readings"])
