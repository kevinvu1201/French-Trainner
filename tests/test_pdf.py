"""PDF reader on a synthetic PDF that mimics the SchweserNotes layout quirks."""

from pathlib import Path

import pymupdf
import pytest

from builder.parse.lines import Figure
from builder.parse.pdf import read_pdf
from builder.parse.segment import parse_items

BODY, HEAD = 11, 16


class _Writer:
    def __init__(self, doc: pymupdf.Document):
        self.doc, self.page, self.y = doc, None, 0.0
        self.new_page()

    def new_page(self) -> None:
        self.page = self.doc.new_page(width=612, height=792)
        self.y = 60

    def text(self, s: str, size: float = BODY, bold: bool = False, x: float = 72, gap: float = 6) -> None:
        if self.y > 720:
            self.new_page()
        self.page.insert_text((x, self.y), s, fontsize=size, fontname="hebo" if bold else "helv")
        self.y += size + gap

    def same_line(self, label: str, s: str) -> None:
        self.page.insert_text((72, self.y), label, fontsize=BODY, fontname="helv")
        self.page.insert_text((90, self.y), s, fontsize=BODY, fontname="helv")
        self.y += BODY + 6

    def image(self, w: float, h: float, x: float = 72) -> None:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, int(w * 2), int(h * 2)), 0)
        pix.clear_with(200)
        self.page.insert_image(pymupdf.Rect(x, self.y, x + w, self.y + h), pixmap=pix)
        self.y += h + 8


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    doc = pymupdf.open()
    w = _Writer(doc)
    w.text("Learning Outcome Statements (LOS)", HEAD, bold=True, gap=14)
    w.text("1. Sample Regression", bold=True)
    w.text("The candidate should be able to:")
    w.same_line("a.", "describe a multiple regression model.")
    w.same_line("b.", "explain the assumptions of the model and")
    w.text("interpret residual plots.", x=90, gap=6)
    w.same_line("c.", "calculate a predicted value.")
    w.new_page()
    w.text("READING 1", HEAD, bold=True, gap=14)
    w.text("SAMPLE REGRESSION", HEAD, bold=True, gap=14)
    w.text("MODULE 1.1: REGRESSION BASICS", HEAD, bold=True, gap=14)
    w.text("Video covering", 8, x=480, gap=1)
    w.text("this content is", 8, x=480, gap=1)
    w.text("available online.", 8, x=480)
    w.text("LOS 1.a: Describe a multiple regression model.", bold=True)
    w.text("A multiple regression explains a dependent variable with several independent", gap=3)
    w.text("Variables estimated by ordinary least squares.", gap=12)
    w.text("A second paragraph starts here.")
    w.image(30, 30)  # icon-sized: skipped
    w.image(240, 60)  # a formula picture: kept
    w.text("LOS 1.b: Explain the assumptions of the model.", bold=True)
    w.text("LOS 1.c: Calculate a predicted value.", bold=True)
    w.text("Prediction uses every estimated coefficient.")
    w.text("MODULE QUIZ 1.1", bold=True)
    w.text("1. Which assumption does heteroskedasticity violate?")
    w.text("A. Linearity.", x=90)
    w.text("B. Constant variance.", x=90)
    w.text("C. Normality.", x=90)
    w.text("ANSWER KEY FOR MODULE QUIZZES", HEAD, bold=True, gap=14)
    w.text("Module Quiz 1.1", bold=True)
    w.text("1. B Heteroskedasticity is non-constant variance. (Module 1.1, LOS 1.b)")
    w.text("FORMULAS", HEAD, bold=True, gap=14)
    w.text("R2 = RSS / SST")
    path = tmp_path / "Book 9.pdf"
    doc.save(path)
    return path


@pytest.fixture
def book(pdf_path: Path, tmp_path: Path) -> dict:
    items, sha = read_pdf(pdf_path, tmp_path / "img")
    return parse_items(items, pdf_path.name, sha)


def test_los_list_with_separate_labels(book):
    [r] = book["readings"]
    assert [l["letter"] for l in r["los"]] == ["a", "b", "c"]
    assert r["los"][1]["text"] == "explain the assumptions of the model and interpret residual plots."
    assert not [i for i in book["issues"] if i["level"] == "error"]


def test_body_paragraphs_banner_and_figures(book, tmp_path):
    [mod] = book["readings"][0]["modules"]
    a = next(s for s in mod["sections"] if s["los"] == ["a"])["blocks"]
    texts = [b.get("md") for b in a if b["t"] == "p"]
    # Wrapped line joined even though it starts uppercase; short sentence-final line ends the paragraph.
    assert texts[0] == ("A multiple regression explains a dependent variable with several independent "
                        "Variables estimated by ordinary least squares.")
    assert texts[1] == "A second paragraph starts here."
    assert "Video" not in str(mod)
    figs = [b for b in a if b["t"] == "fig"]
    assert len(figs) == 1  # the icon-sized image is dropped
    entry = book["figures"][figs[0]["id"]]
    assert entry["src"].endswith(".png") and (tmp_path / "img" / entry["src"]).exists()
    assert (entry["w"], entry["h"]) == (240.0, 60.0)


def test_quiz_and_answer_key(book):
    [mod] = book["readings"][0]["modules"]
    [q] = mod["quiz"]
    assert q["options"] == ["Linearity.", "Constant variance.", "Normality."]
    assert (q["answer"], q["los"]) == ("B", ["b"])
    assert "R2 = RSS" not in str(book["readings"])


def test_options_in_figure(tmp_path):
    from builder.parse.lines import Line, to_plain
    from builder.parse.quiz import parse_quiz

    items = [Line(1, "1. Which phase and which model are most appropriate?", "", False),
             Figure(1, "", "fig.0123456789", src="fig.0123456789.png", w=300, h=60)]
    items[0].plain = to_plain(items[0].md)
    [q] = parse_quiz(items)
    assert q.options == ["A", "B", "C"] and q.options_in_figure
    assert q.stem.endswith("[[fig.0123456789]]")
