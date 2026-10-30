"""Turn normalised book lines into a stream of items: text lines and figures.

Heading depth in the source is unreliable (the same element appears as ## to
###### or as plain bold text), so every line also gets a `plain` form with
heading marks, emphasis and footnote markers stripped. Structural patterns are
matched against `plain`; `md` keeps inline formatting for display.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_HEADING = re.compile(r"^\s*(#{1,6})\s+")
_SUP = re.compile(r"<sup>(.*?)</sup>")
_FIG_START = "<!-- Start of picture text -->"
_FIG_END = "<!-- End of picture text -->"


@dataclass
class Line:
    no: int  # 1-based line number in the source file
    md: str  # display markdown, heading marks removed
    plain: str  # for pattern matching
    heading: bool


@dataclass
class Figure:
    no: int
    ocr: str  # OCR text, one entry per <br>-separated line ("" for PDF images)
    id: str  # content hash, the key for generated repairs
    src: str | None = None  # extracted image file name (PDF sources)
    w: float = 0  # displayed size on the page, in points
    h: float = 0
    inline: bool = False  # symbol inside a sentence; the text carries its [[fig]] token


Item = Line | Figure


def to_plain(md: str) -> str:
    s = _SUP.sub("", md)
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"(?<!\w)_|_(?!\w)", "", s)
    return re.sub(r"\s+", " ", s).strip()


def figure_id(ocr: str) -> str:
    return "fig." + hashlib.sha1(ocr.encode("utf-8")).hexdigest()[:10]


def scan(lines: list[str], start: int = 0, end: int | None = None) -> list[Item]:
    """Items for lines[start:end]. Blank lines are dropped."""
    items: list[Item] = []
    end = len(lines) if end is None else end
    i = start
    while i < end:
        raw = lines[i]
        if _FIG_START in raw:
            buf = raw.split(_FIG_START, 1)[1]
            j = i
            while _FIG_END not in buf and j + 1 < end:
                j += 1
                buf += "\n" + lines[j]
            ocr = buf.split(_FIG_END, 1)[0]
            ocr = "\n".join(p.strip() for p in re.split(r"<br>|\n", ocr) if p.strip())
            items.append(Figure(i + 1, ocr, figure_id(ocr)))
            i = j + 1
            continue
        if raw.strip():
            m = _HEADING.match(raw)
            md = raw[m.end():].strip() if m else raw.strip()
            items.append(Line(i + 1, md, to_plain(md), bool(m)))
        i += 1
    return items
