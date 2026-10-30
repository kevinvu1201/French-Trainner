"""Parse Schweser module quizzes and their answer keys.

Quiz section (options are inline, bulleted or on bare lines):

    Use the following information to answer Questions 1 and 2.
    <vignette paragraphs / figures>
    1. The F-statistic ... is closest to: A. 13.54.
       - B. 13.77.
       - C. 16.61.

Answer key section:

    Module Quiz 1.2
    1. **C** RSSU = 9,105 - 4,320 = 4,785 ...
    <figure>
    (Module 1.2, LOS 1.e)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .lines import Figure, Item, Line

_VIGNETTE = re.compile(r"^Use the following information", re.I)
_QNUM = re.compile(r"^(\d{1,2})\.\s+(.*)$")
# Option labels are sometimes glued to a number ("C.9.688").
_OPTIONS = re.compile(
    r"^(?P<stem>.*?)\s*(?:-\s*)?\bA\.(?:\s+|(?=\d))(?P<a>.*?)\s+(?:-\s*)?\bB\.(?:\s+|(?=\d))(?P<b>.*?)\s+"
    r"(?:-\s*)?\bC\.(?:\s+|(?=\d))(?P<c>.*)$",
    re.S,
)
_ENDS_WITH_FIG = re.compile(r"\[\[(fig\.[0-9a-f]+)\]\]\s*$")
_KEY_ITEM = re.compile(r"^(\d{1,2})\.\s+\**([ABC])\**(?:\s+|$)(.*)$")
_LOS_REF = re.compile(r"LOS (\d+)\.([a-z])")
_TRAILING_REF = re.compile(r"\s*\((?:Module [\d.]+,\s*)?LOS [^)]*\)\s*$")


def fig_token(fig_id: str) -> str:
    return f"[[{fig_id}]]"


@dataclass
class RawQuestion:
    number: int
    line: int
    parts: list[str] = field(default_factory=list)  # md lines and [[fig]] tokens
    vignette: list[str] | None = None


@dataclass
class ParsedQuestion:
    number: int
    line: int
    stem: str
    options: list[str] | None
    vignette: str | None
    ocr_options: bool = False  # options were recovered from OCR'd picture text
    options_in_figure: bool = False  # options are printed in the picture that ends the stem


@dataclass
class KeyEntry:
    number: int
    answer: str
    explanation: str
    los_refs: list[tuple[int, str]]
    line: int


def parse_quiz(items: list[Item]) -> list[ParsedQuestion]:
    ocr = {it.id: it.ocr for it in items if isinstance(it, Figure)}
    questions: list[RawQuestion] = []
    vignette: list[str] | None = None
    collecting_vignette = False
    for it in items:
        if isinstance(it, Figure) and it.inline:
            continue  # its token is already in the text
        if isinstance(it, Figure):
            text = fig_token(it.id)
        else:
            text = it.md
            if _VIGNETTE.match(it.plain):
                vignette, collecting_vignette = [], True
                continue
            m = _QNUM.match(it.plain)
            expected = questions[-1].number + 1 if questions else 1
            if m and int(m.group(1)) == expected:
                collecting_vignette = False
                q = RawQuestion(int(m.group(1)), it.no, vignette=vignette)
                q.parts.append(re.sub(r"^\s*\d{1,2}\.\s+", "", text))
                questions.append(q)
                continue
        if collecting_vignette and vignette is not None:
            vignette.append(text)
        elif questions:
            questions[-1].parts.append(text)
        # Text before the first question that isn't a vignette is ignored.

    out: list[ParsedQuestion] = []
    for q in questions:
        body = "\n".join(q.parts)
        m = _OPTIONS.match(body)
        from_ocr = False
        if not m:
            inlined = re.sub(r"\[\[(fig\.[0-9a-f]+)\]\]", lambda f: ocr.get(f.group(1), ""), body)
            m = _OPTIONS.match(inlined)
            from_ocr = m is not None
        options = [m.group(k).strip() for k in ("a", "b", "c")] if m else None
        stem = m.group("stem").strip() if m else body.strip()
        # PDF source: a picture (no OCR text) ending the stem holds the A/B/C table.
        fig = _ENDS_WITH_FIG.search(stem) if options is None else None
        in_figure = bool(fig and not ocr.get(fig.group(1)))
        if in_figure:
            options = ["A", "B", "C"]
        out.append(ParsedQuestion(q.number, q.line, stem, options,
                                  "\n\n".join(q.vignette) if q.vignette else None, from_ocr, in_figure))
    return out


def parse_answer_key(items: list[Item]) -> list[KeyEntry]:
    entries: list[KeyEntry] = []
    for it in items:
        if isinstance(it, Figure) and it.inline:
            continue  # its token is already in the text
        if isinstance(it, Line):
            m = _KEY_ITEM.match(it.md) or _KEY_ITEM.match(it.plain)
            expected = entries[-1].number + 1 if entries else 1
            if m and int(m.group(1)) == expected:
                entries.append(KeyEntry(int(m.group(1)), m.group(2), m.group(3).strip(), [], it.no))
                continue
        if not entries:
            continue
        piece = fig_token(it.id) if isinstance(it, Figure) else it.md
        entries[-1].explanation += "\n\n" + piece
    for e in entries:
        e.los_refs = [(int(r), l) for r, l in _LOS_REF.findall(e.explanation)]
        e.explanation = _TRAILING_REF.sub("", e.explanation).strip()
    return entries
