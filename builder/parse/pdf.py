"""Read a SchweserNotes PDF into the same Line/Figure item stream as the Markdown reader.

The PDFs carry clean text (no broken ligatures) and real font information, so:

* bold/italic/superscript/subscript spans become **, _, <sup>, <sub>;
* lines noticeably larger than the book's body font are headings (books are
  typeset at different sizes, so the threshold is relative);
* paragraphs are rebuilt from PDF lines: a line continues the previous one
  when it has the same style, sits directly below it in the same column and
  doesn't start with a list/option marker ("1.", "A.", "a.", bullets);
* every figure (formulas and tables are pictures in these books) is rendered
  from its area on the page to a PNG, so the app shows the original image.
  Small icons reused across many pages (video, quiz, note badges) are skipped.
"""

from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

import pymupdf
from PIL import Image

from .lines import Figure, Item, Line, to_plain
from .normalize import clean_line

READER_VERSION = 7
HEADING_RATIO = 1.18  # heading = font at least this much larger than the book's body text
ICON_MAX_PT = 45  # images smaller than this in both directions are badges
REPEATED_ICON_PAGES = 5
RENDER_ZOOM = 2.0  # 144 dpi: sharp on phones, small files
PALETTE_COLOURS = 16

_MARKER = re.compile(r"^(?:\d{1,2}\.|[A-C]\.|[a-z]\.|[-•●▪◦])(?:\s|$)")
_BULLET = re.compile(r"^[•●▪◦]\s*")
_SENTENCE_END = re.compile(r"[.:?!)]\**\s*$")
# Structural markers always start a paragraph; the one-line ones never absorb the next line.
_STRUCTURAL = re.compile(r"^(?:READING \d|MODULE \d|MODULE QUIZ|LOS \d+\.[a-z]|EXAM FOCUS|KEY CONCEPTS|ANSWER KEY|Module Quiz \d)", re.I)
_STRUCTURAL_LINE = re.compile(r"^(?:READING \d+(?:\s*&\s*\d+)?|EXAM FOCUS|KEY CONCEPTS|MODULE QUIZ [\d.,\s]+|Module Quiz [\d.,\s]+)$", re.I)
_VIDEO = re.compile(r"Video\s*covering|this\s*content\s*is|available\s*online\.?", re.I)


def _style(span: dict[str, Any], line_size: float, baseline: float) -> tuple[bool, bool, str]:
    font = span["font"]
    bold = bool(span["flags"] & 16) or "Bold" in font or "Black" in font
    italic = bool(span["flags"] & 2) or "Italic" in font or "Oblique" in font
    pos = ""
    if span["flags"] & 1:
        pos = "sup"
    elif span["size"] < 0.85 * line_size and span["origin"][1] > baseline + 0.8:
        pos = "sub"
    elif span["size"] < 0.85 * line_size and span["origin"][1] < baseline - 0.8:
        pos = "sup"
    return bold, italic, pos


def _wrap(text: str, bold: bool, italic: bool, pos: str) -> str:
    m = re.match(r"^(\s*)(.*?)(\s*)$", text, re.S)
    assert m
    lead, core, trail = m.groups()
    if not core:
        return text
    if pos:
        core = f"<{pos}>{core}</{pos}>"
    if italic and not pos and len(core) > 1:
        core = f"_{core}_"
    if bold and not pos:
        core = f"**{core}**"
    return lead + core + trail


def _line_md(line: dict[str, Any]) -> tuple[str, str, float, bool]:
    """Returns (markdown, plain text, font size, all-bold) for one PDF line."""
    spans = [s for s in line["spans"] if s["text"]]
    if not spans:
        return "", "", 0.0, False
    main = max(spans, key=lambda s: len(s["text"].strip()) * s["size"])
    size, baseline = main["size"], main["origin"][1]
    runs: list[tuple[tuple[bool, bool, str], str]] = []
    for s in spans:
        st = _style(s, size, baseline)
        if runs and runs[-1][0] == st:
            runs[-1] = (st, runs[-1][1] + s["text"])
        else:
            runs.append((st, s["text"]))
    md = "".join(_wrap(t, *st) for st, t in runs)
    plain = "".join(t for _, t in runs)
    all_bold = all(st[0] for st, t in runs if t.strip())
    return md, plain, size, all_bold


def _join(a: str, b: str) -> str:
    if a.endswith("-") and not a.endswith(" -"):
        return a + b.lstrip()
    return f"{a.rstrip()} {b.lstrip()}"


class _Para:
    __slots__ = ("md", "size", "bold", "x0", "y0", "y1", "last_x1")

    def __init__(self, md: str, size: float, bold: bool, bbox: tuple[float, float, float, float]):
        self.md, self.size, self.bold = md, size, bold
        self.x0, self.y0, self.y1, self.last_x1 = bbox[0], bbox[1], bbox[3], bbox[2]


_LineT = tuple[str, str, float, bool, tuple[float, float, float, float]]


def _lines(block: dict[str, Any]) -> list[_LineT]:
    out = []
    for line in block["lines"]:
        md, plain, size, bold = _line_md(line)
        if plain.strip():
            out.append((md, plain, size, bold, tuple(line["bbox"])))
    return out


def _continues(prev: _Para, md: str, plain: str, size: float, bold: bool, bbox: tuple[float, ...],
               body: float, right: float) -> bool:
    if _MARKER.match(plain.lstrip()) or _STRUCTURAL.match(plain.lstrip()):
        return False
    if _STRUCTURAL_LINE.match(to_plain(prev.md)):
        return False
    # A sentence ending on a short line closes the paragraph.
    if prev.last_x1 < right - 30 and _SENTENCE_END.search(prev.md):
        return False
    if abs(prev.size - size) > 0.6 or prev.bold != bold:
        return False
    if (prev.size >= body * HEADING_RATIO) != (size >= body * HEADING_RATIO):
        return False
    gap = bbox[1] - prev.y1
    return -2 <= gap <= 0.6 * size and -3 <= bbox[0] - prev.x0 <= 24


def _merge_baselines(lines: list[_LineT]) -> list[_LineT]:
    """Join pieces typeset on the same baseline ("f." label + its text, sorted by x)."""
    out: list[_LineT] = []
    for line in lines:
        if out:
            md, plain, size, bold, bb = out[-1]
            nb = line[4]
            if abs(nb[1] - bb[1]) < 2 and abs(nb[3] - bb[3]) < 2 and nb[0] >= bb[2] - 1:
                out[-1] = (f"{md} {line[0]}", f"{plain} {line[1]}", max(size, line[2]), bold and line[3],
                           (bb[0], min(bb[1], nb[1]), nb[2], max(bb[3], nb[3])))
                continue
        out.append(line)
    return out


def _paragraphs(lines: list[_LineT], body: float) -> list[_Para]:
    # Right edge of the text column on this page, from body-size lines.
    right = max((l[4][2] for l in lines if abs(l[2] - body) < 0.6), default=0.0)
    paras: list[_Para] = []
    for md, plain, size, bold, bbox in lines:
        if paras and _continues(paras[-1], md, plain, size, bold, bbox, body, right):
            prev = paras[-1]
            prev.md = _join(prev.md, md)
            prev.y1 = max(prev.y1, bbox[3])
            prev.last_x1 = bbox[2]
            continue
        paras.append(_Para(md, size, bold, bbox))
    return paras


def _body_size(doc: pymupdf.Document) -> float:
    weight: dict[float, int] = defaultdict(int)
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    weight[round(span["size"], 1)] += len(span["text"].strip())
    return max(weight, key=weight.get) if weight else 10.0


def _inline_anchor(bbox: pymupdf.Rect, lines: list[_LineT], body: float) -> _LineT | None:
    """The text line an image sits inside, if it's a glyph-sized picture tight against the words.

    Badges (video, quiz) sit apart from text (>6pt gap) or next to lines that were dropped.
    """
    if bbox.height > 2.2 * body:
        return None
    cy = (bbox.y0 + bbox.y1) / 2
    for line in lines:
        lb = line[4]
        if lb[1] - 1 <= cy <= lb[3] + 1 and (abs(lb[2] - bbox.x0) <= 6 or abs(bbox.x1 - lb[0]) <= 6):
            return line
    return None


def _icon_xrefs(doc: pymupdf.Document) -> set[int]:
    pages: dict[int, set[int]] = defaultdict(set)
    for i, page in enumerate(doc):
        for info in page.get_image_info(xrefs=True):
            if info["xref"]:
                pages[info["xref"]].add(i)
    return {x for x, p in pages.items() if len(p) >= REPEATED_ICON_PAGES}


def _render(page: pymupdf.Page, bbox: pymupdf.Rect, img_dir: Path) -> tuple[str, str]:
    pix = page.get_pixmap(clip=bbox, matrix=pymupdf.Matrix(RENDER_ZOOM, RENDER_ZOOM), alpha=False)
    # A 16-colour adaptive palette keeps text sharp and colour shading intact at ~1/6 the size.
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).quantize(PALETTE_COLOURS)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    png = buf.getvalue()
    fig_id = "fig." + hashlib.sha1(png).hexdigest()[:10]
    name = f"{fig_id}.png"
    target = img_dir / name
    if not target.exists():
        target.write_bytes(png)
    return fig_id, name


def _clean(md: str) -> str:
    md = clean_line(unicodedata.normalize("NFC", md).replace("\u00a0", " ")) or ""
    md = _BULLET.sub("- ", md)
    md = md.replace("****", "").replace("**  **", " ")
    return re.sub(r"[ \t]{2,}", " ", md).strip()


def read_pdf(path: Path, img_dir: Path) -> tuple[list[Item], str]:
    """Returns (items, sha1 of the file). Figure images are written to img_dir."""
    raw = path.read_bytes()
    img_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(stream=raw, filetype="pdf")
    icons = _icon_xrefs(doc)
    body = _body_size(doc)
    items: list[Item] = []
    for pno, page in enumerate(doc, start=1):
        lines = []
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            text = "".join(s["text"] for l in block["lines"] for s in l["spans"])
            if _VIDEO.search(text) and not re.search(r"[A-Za-z0-9]", _VIDEO.sub("", text)):
                continue
            lines.extend(_lines(block))
        placed: list[tuple[float, float, Item]] = []
        blocks_imgs = []
        for info in page.get_image_info(xrefs=True):
            bbox = pymupdf.Rect(info["bbox"]) & page.rect
            if bbox.is_empty:
                continue
            # Badges are reused on many pages and can sit right beside a heading; never inline them.
            anchor = None if info["xref"] in icons else _inline_anchor(bbox, lines, body)
            if anchor is not None:
                # A symbol drawn as a tiny picture inside a sentence (R̄²ₐ): keep it in the text.
                fig_id, name = _render(page, bbox, img_dir)
                token = f"[[{fig_id}]]"
                lines.append((token, token, anchor[2], anchor[3], (bbox.x0, anchor[4][1], bbox.x1, anchor[4][3])))
                placed.append((bbox.y0, bbox.x0, Figure(pno, "", fig_id, src=name, w=round(bbox.width, 1),
                                                        h=round(bbox.height, 1), inline=True)))
            elif not ((bbox.width < ICON_MAX_PT and bbox.height < ICON_MAX_PT) or info["xref"] in icons):
                blocks_imgs.append(bbox)
        lines.sort(key=lambda l: (round(l[4][1]), l[4][0]))
        lines = _merge_baselines(lines)
        for para in _paragraphs(lines, body):
            md = _clean(para.md)
            if md:
                placed.append((para.y0, para.x0, Line(pno, md, to_plain(md), para.size >= body * HEADING_RATIO)))
        for bbox in blocks_imgs:
            fig_id, name = _render(page, bbox, img_dir)
            placed.append((bbox.y0, bbox.x0,
                           Figure(pno, "", fig_id, src=name, w=round(bbox.width, 1), h=round(bbox.height, 1))))
        placed.sort(key=lambda p: (round(p[0], 1), p[1]))
        items.extend(item for _, _, item in placed)
    return items, hashlib.sha1(raw).hexdigest()
