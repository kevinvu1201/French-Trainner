"""Segment one normalised book into readings -> modules -> LOS sections.

Structure is recognised by text patterns on `Line.plain`, never by heading
depth. Every structural doubt is recorded as an issue for the validation
report instead of being silently guessed.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from . import figures as figs
from .lines import Figure, Item, Line, scan
from .los import ReadingEntry, parse_los_list
from .normalize import RepairStats, Vocab, normalize_text
from .quiz import KeyEntry, parse_answer_key, parse_quiz

PARSER_VERSION = 7

_LOS_HEADING = re.compile(r"^Learning Outcome Statements", re.I)
_READING = re.compile(r"^READING (\d+)(?:\s*&\s*(\d+))?$")
# Section markers tolerate a short tail of OCR junk ("ANSWER KEY FOR MODULE QUIZZES Po").
_FORMULAS = re.compile(r"^FORMULAS\b.{0,12}$")
_TOPIC_QUIZ = re.compile(r"^Topic Quiz\b", re.I)
_EXAM_FOCUS = re.compile(r"^EXAM FOCUS\b.{0,12}$", re.I)
_MODULE = re.compile(r"^MODULE (\d+)\.(\d+)(?:\s*:\s*(.*)|\s*)$", re.I)
# Combined quizzes ("MODULE QUIZ 7.4, 7.5, 7.6") are filed under the first module;
# each question's answer-key LOS references still tag it precisely.
_MODULE_QUIZ = re.compile(r"^MODULE QUIZ (\d+)\.(\d+)\b", re.I)
_KEY_CONCEPTS = re.compile(r"^KEY CONCEPTS\b.{0,12}$", re.I)
_ANSWER_KEY = re.compile(r"^ANSWER KEY FOR MODULE QUIZZES\b.{0,12}$", re.I)
_CONTENTS_MODULE = re.compile(
    r"Module (\d+)\.(\d+):\s*(.+?)(?=\s+Module \d+\.\d+:|\s+Key Concepts|\s+Answer Key|\s+READING|\s+Topic Quiz|$)"
)
_AK_MODULE = re.compile(r"^Module Quiz (\d+)\.(\d+)(?:\s*,\s*\d+\.\d+)*$", re.I)
_LOS_MARK = re.compile(
    r"^LOS (\d+)\.([a-z])((?:\s*(?:,|and|&)\s*(?:\d+\.)?[a-z]\b)*)\s*(?::\s*(.*))?$"
)
_EXAMPLE = re.compile(r"^(?:EXAMPLE\b|Example\s*\d*\s*:)\s*\d*\s*:?\s*(.*)$")
_ANSWER = re.compile(r"^Answers?(?: to [^:]{1,40})?:\s*(.*)$")
_NOTE = re.compile(r"^PROFESSOR.S NOTE$", re.I)
_CAPTION = re.compile(r"^(Figure|Exhibit|Table)\s+\d+(\.\d+)*\s*[:.]", re.I)
_BULLET = re.compile(r"^\s*[-•]\s+(.*)$")
_ORDERED = re.compile(r"^\s*\d{1,2}\.\s+(.*)$")
_SENTENCE_END = re.compile(r"[.:?!)\]\"”’]\s*$")


@dataclass
class Issue:
    level: str  # "error" | "warning" | "info"
    code: str
    msg: str
    line: int | None = None


@dataclass
class Section:
    los: list[str]  # LOS letters this section covers ([] = module preamble)
    line: int
    items: list[Item] = field(default_factory=list)


@dataclass
class Module:
    reading: int
    number: int
    title: str
    line: int
    sections: list[Section] = field(default_factory=list)
    quiz_items: list[Item] = field(default_factory=list)


@dataclass
class ReadingCtx:
    numbers: list[int]
    line: int
    body_title: str = ""
    focus_items: list[Item] = field(default_factory=list)
    kc_items: dict[str, list[Item]] = field(default_factory=dict)  # "7.a" -> items
    ak_items: dict[str, list[Item]] = field(default_factory=dict)  # "7.2" -> items


# ---------------------------------------------------------------- blocks


def to_blocks(items: list[Item], figreg: dict[str, dict[str, Any]], book: str) -> list[dict[str, Any]]:
    """Convert items to display blocks, re-joining paragraphs split by page breaks."""
    blocks: list[dict[str, Any]] = []
    note_open = False
    for it in items:
        last = blocks[-1] if blocks else None
        if isinstance(it, Figure) and it.inline:
            if it.id not in figreg:
                figreg[it.id] = _fig_entry(it, None, book)
            continue
        if isinstance(it, Figure):
            caption = last["md"] if last and last["t"] == "cap" else None
            if it.id not in figreg:
                figreg[it.id] = _fig_entry(it, caption, book)
            blocks.append({"t": "fig", "id": it.id})
            note_open = False
            continue
        p, md = it.plain, it.md
        if _EXAMPLE.match(p):
            # Title from the markdown so R<sup>2</sup> survives; the card styles it bold anyway.
            title = re.sub(r"^\s*(?:EXAMPLE\b|Example\s*\d*\s*:)\s*\d*\s*:?\s*", "", md.replace("**", ""))
            blocks.append({"t": "ex", "md": title.strip()})
        elif m := _ANSWER.match(p):
            blocks.append({"t": "ans"})
            if m.group(1).strip():
                blocks.append({"t": "p", "md": re.sub(r"^\**Answers?[^:]*:\**\s*", "", md)})
        elif _NOTE.match(p):
            blocks.append({"t": "note", "md": ""})
            note_open = True
            continue
        elif _CAPTION.match(p):
            blocks.append({"t": "cap", "md": p})
        elif md.startswith("|"):
            cells = [c.strip() for c in md.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            if last and last["t"] == "table":
                last["rows"].append(cells)
            else:
                blocks.append({"t": "table", "rows": [cells]})
        elif (m := _BULLET.match(md)) and not it.heading:
            if last and last["t"] == "ul":
                last["items"].append(m.group(1).strip())
            else:
                blocks.append({"t": "ul", "items": [m.group(1).strip()]})
        elif (m := _ORDERED.match(md)) and not it.heading:
            if last and last["t"] == "ol":
                last["items"].append(m.group(1).strip())
            else:
                blocks.append({"t": "ol", "items": [m.group(1).strip()]})
        elif it.heading:
            # Drop heading emphasis but keep <sup>/<sub> (R<sup>2</sup>).
            blocks.append({"t": "h", "md": re.sub(r"\*\*|(?<!\w)_|_(?!\w)", "", md).strip()})
        else:
            continues = p[:1].islower()
            if note_open and last and last["t"] == "note":
                last["md"] = f"{last['md']} {md}".strip()
                continue
            if continues and last and last["t"] == "p" and not _SENTENCE_END.search(last["md"]):
                last["md"] += " " + md
            elif continues and last and last["t"] in ("ul", "ol") and not _SENTENCE_END.search(last["items"][-1]):
                last["items"][-1] += " " + md
            else:
                blocks.append({"t": "p", "md": md})
        note_open = False
    return blocks


# ---------------------------------------------------------------- book


def _find(items: list[Item], pattern: re.Pattern[str], start: int = 0, heading_only: bool = False) -> int | None:
    for i in range(start, len(items)):
        it = items[i]
        if isinstance(it, Line) and pattern.match(it.plain) and (it.heading or not heading_only):
            return i
    return None


def _find_los_list(items: list[Item]) -> int | None:
    """The LOS heading that starts the master list (the CONTENTS page has one too)."""
    i = _find(items, _LOS_HEADING, heading_only=True)
    first = i
    while i is not None:
        window = [it for it in items[i + 1 : i + 6] if isinstance(it, Line)]
        if any(re.match(r"^-?\s*The candidate should be able to", it.plain, re.I) for it in window):
            return i
        i = _find(items, _LOS_HEADING, i + 1, heading_only=True)
    return first


def parse_book(text: str, name: str, vocab: Vocab) -> dict[str, Any]:
    """Parse one Markdown book (PDF->Markdown conversion, with OCR'd figures)."""
    stats = RepairStats()
    items = scan(normalize_text(text, vocab, stats))
    return parse_items(items, name, hashlib.sha1(text.encode("utf-8")).hexdigest(),
                       {"fixed": sum(stats.fixed.values()), "guessed": dict(stats.guessed)})


def _fig_entry(fig: Figure, caption: str | None, book: str) -> dict[str, Any]:
    entry: dict[str, Any] = {"kind": figs.classify_figure(fig, caption), "caption": caption,
                             "where": f"{book}:{fig.no}", "ocr": fig.ocr}
    if fig.src:
        entry.update(src=fig.src, w=fig.w, h=fig.h)
    return entry


def parse_items(items: list[Item], name: str, sha: str, ligatures: dict[str, Any] | None = None) -> dict[str, Any]:
    """Parse a book's item stream. Returns a JSON-serialisable dict (cached by the incremental build).

    `Item.no` is a line number for Markdown sources and a page number for PDFs.
    """
    issues: list[Issue] = []
    ligatures = ligatures or {"fixed": 0, "guessed": {}}

    los_start = _find_los_list(items)
    if los_start is None:
        return _fail(name, sha, "no_los_list", "No 'Learning Outcome Statements' heading found")
    body_start = _find(items, _READING, los_start + 1)
    if body_start is None:
        return _fail(name, sha, "no_body", "No 'READING n' heading after the LOS list")
    body_end = _find(items, _FORMULAS, body_start, heading_only=True) or len(items)

    master = parse_los_list([it for it in items[los_start + 1 : body_start] if isinstance(it, Line)])
    readings_ctx, modules = _segment_body(items[body_start:body_end], issues)

    # Body module headers are ALL CAPS; the CONTENTS pages list them in proper case.
    contents = " ".join(it.plain for it in items[:los_start] if isinstance(it, Line))
    for m in _CONTENTS_MODULE.finditer(contents):
        mod = modules.get(f"{int(m.group(1))}.{int(m.group(2))}")
        if mod is not None:
            mod.title = m.group(3).strip()

    figreg: dict[str, dict[str, Any]] = {}
    readings = _assemble(name, master, readings_ctx, modules, figreg, issues)
    # Figures referenced only from quiz/answer text ([[fig.x]] tokens) aren't seen by to_blocks.
    for it in items[body_start:body_end]:
        if isinstance(it, Figure) and it.id not in figreg:
            figreg[it.id] = _fig_entry(it, None, name)
    return {
        "book": name,
        "sha": sha,
        "parser_version": PARSER_VERSION,
        "readings": readings,
        "figures": figreg,
        "ligatures": ligatures,
        "issues": [asdict(i) for i in issues],
    }


def _fail(name: str, sha: str, code: str, msg: str) -> dict[str, Any]:
    return {"book": name, "sha": sha,
            "parser_version": PARSER_VERSION, "readings": [], "figures": {},
            "ligatures": {"fixed": 0, "guessed": {}},
            "issues": [asdict(Issue("error", code, msg))]}


def _segment_body(items: list[Item], issues: list[Issue]) -> tuple[list[ReadingCtx], dict[str, Module]]:
    readings: list[ReadingCtx] = []
    modules: dict[str, Module] = {}
    state = "skip"
    reading: ReadingCtx | None = None
    module: Module | None = None
    target: list[Item] | None = None

    def open_module(r: int, n: int, title: str, line: int) -> Module:
        key = f"{r}.{n}"
        if key in modules:
            issues.append(Issue("warning", "duplicate_module", f"Module {key} appears twice", line))
            return modules[key]
        if reading and r not in reading.numbers:
            issues.append(Issue("error", "module_reading_mismatch",
                                f"Module {key} inside READING {reading.numbers}", line))
        mod = Module(r, n, title, line)
        mod.sections.append(Section([], line))
        modules[key] = mod
        return mod

    for it in items:
        if isinstance(it, Line):
            p = it.plain
            if m := _READING.match(p):
                nums = [int(m.group(1))] + ([int(m.group(2))] if m.group(2) else [])
                reading = ReadingCtx(nums, it.no)
                readings.append(reading)
                module, state, target = None, "title", reading.focus_items
                continue
            if reading is None:
                continue
            if _TOPIC_QUIZ.match(p):
                state, target = "skip", None
                continue
            if state == "title":
                reading.body_title = p
                state = "intro"
                continue
            if _EXAM_FOCUS.match(p):
                state, target = "focus", reading.focus_items
                continue
            if state == "ak" and (m := _AK_MODULE.match(p)):
                target = reading.ak_items.setdefault(f"{int(m.group(1))}.{int(m.group(2))}", [])
                continue
            if (m := _MODULE_QUIZ.match(p)) and state != "ak":
                key = f"{int(m.group(1))}.{int(m.group(2))}"
                if key not in modules:
                    issues.append(Issue("error", "quiz_without_module", f"MODULE QUIZ {key} has no module", it.no))
                    open_module(int(m.group(1)), int(m.group(2)), "", it.no)
                module = modules[key]
                state, target = "quiz", module.quiz_items
                continue
            if (m := _MODULE.match(p)) and state != "ak":
                module = open_module(int(m.group(1)), int(m.group(2)), (m.group(3) or "").strip(), it.no)
                state, target = "module", module.sections[-1].items
                continue
            if _KEY_CONCEPTS.match(p):
                state, target = "kc", None
                continue
            if _ANSWER_KEY.match(p):
                state, target = "ak", None
                continue
            if state == "kc" and (m := re.match(r"^LOS (\d+)\.([a-z])\b", p)):
                target = reading.kc_items.setdefault(f"{int(m.group(1))}.{m.group(2)}", [])
                continue
            if (m := _LOS_MARK.match(p)) and m.group(4) is not None and state not in ("kc", "ak"):
                r = int(m.group(1))
                letters = [m.group(2)] + re.findall(r"([a-z])\b", m.group(3) or "")
                if module is None or state in ("focus", "intro"):
                    issues.append(Issue("warning", "los_before_module",
                                        f"LOS {r}.{m.group(2)} appears before any MODULE header; implicit module created", it.no))
                    module = open_module(r, 0, "", it.no)
                elif state == "quiz":
                    issues.append(Issue("warning", "los_after_quiz",
                                        f"LOS {r}.{m.group(2)} follows MODULE QUIZ {module.reading}.{module.number} without a new MODULE header", it.no))
                if module.reading != r:
                    issues.append(Issue("error", "los_reading_mismatch",
                                        f"LOS {r}.{m.group(2)} inside module {module.reading}.{module.number}", it.no))
                sec = Section(letters, it.no)
                module.sections.append(sec)
                state, target = "module", sec.items
                continue
            if re.match(r"^LOS \d+\.$", p) or re.search(r"\*\*LOS \d+\.\s*$", it.md):
                issues.append(Issue("warning", "broken_los_marker", f"Truncated LOS marker: {p[:80]}", it.no))
        if state in ("skip", "title") or target is None:
            continue
        target.append(it)
    return readings, modules


def _assemble(book: str, master: list[ReadingEntry], ctxs: list[ReadingCtx], modules: dict[str, Module],
              figreg: dict[str, dict[str, Any]], issues: list[Issue]) -> list[dict[str, Any]]:
    by_num = {r.number: r for r in master}
    ctx_by_num = {n: c for c in ctxs for n in c.numbers}
    out: list[dict[str, Any]] = []

    for n in sorted(set(by_num) | set(ctx_by_num)):
        entry, ctx = by_num.get(n), ctx_by_num.get(n)
        if entry is None:
            issues.append(Issue("error", "reading_not_in_los_list", f"READING {n} is in the body but not the LOS list", ctx.line if ctx else None))
        if ctx is None:
            issues.append(Issue("error", "reading_not_in_body", f"Reading {n} is in the LOS list but has no body", entry.line if entry else None))
            continue
        master_letters = [l.letter for l in entry.los] if entry else []
        mods = sorted((m for m in modules.values() if m.reading == n), key=lambda m: m.number)

        # LOS -> module, from body markers.
        los_module: dict[str, int] = {}
        for mod in mods:
            for sec in mod.sections:
                for letter in sec.los:
                    los_module.setdefault(letter, mod.number)
                    if letter not in master_letters:
                        issues.append(Issue("error", "los_not_in_master",
                                            f"LOS {n}.{letter} in body but not in the LOS list", sec.line))

        # Quizzes and answer keys.
        quiz_by_module: dict[int, list[dict[str, Any]]] = {}
        key_refs: dict[str, int] = {}
        for mod in mods:
            mkey = f"{n}.{mod.number}"
            qs = parse_quiz(mod.quiz_items)
            keys = {k.number: k for k in parse_answer_key(ctx.ak_items.get(mkey, []))}
            for q in qs:
                k: KeyEntry | None = keys.get(q.number)
                if q.options is None:
                    issues.append(Issue("warning", "quiz_options_not_found",
                                        f"Module Quiz {mkey} Q{q.number}: could not split A/B/C options", q.line))
                elif q.options_in_figure:
                    issues.append(Issue("info", "quiz_options_in_figure",
                                        f"Module Quiz {mkey} Q{q.number}: options are printed in the figure; shown as A/B/C buttons", q.line))
                elif q.ocr_options:
                    issues.append(Issue("info", "quiz_options_from_ocr",
                                        f"Module Quiz {mkey} Q{q.number}: options recovered from OCR text; check them", q.line))
                if k is None:
                    issues.append(Issue("warning", "quiz_answer_missing",
                                        f"Module Quiz {mkey} Q{q.number}: no answer-key entry", q.line))
                los_refs = sorted({l for r, l in (k.los_refs if k else []) if r == n})
                for letter in los_refs:
                    key_refs.setdefault(letter, mod.number)
                quiz_by_module.setdefault(mod.number, []).append({
                    "n": q.number, "line": q.line, "vignette": q.vignette, "stem": q.stem,
                    "options": q.options, "ocr_options": q.ocr_options, "options_in_figure": q.options_in_figure,"answer": k.answer if k else None,
                    "explanation": k.explanation if k else None, "los": los_refs,
                })
            if not qs and mod.number:
                issues.append(Issue("info", "no_module_quiz", f"Module {mkey} has no quiz", mod.line))
            extra = set(keys) - {q.number for q in qs}
            if extra:
                issues.append(Issue("warning", "answer_without_question",
                                    f"Answer key {mkey} has entries {sorted(extra)} with no parsed question", mod.line))

        # Master-list LOS with no body marker: infer the module, and say so.
        for letter in master_letters:
            if letter in los_module:
                continue
            if letter in key_refs:
                los_module[letter], how = key_refs[letter], "answer-key LOS references"
            else:
                prev = [los_module[l] for l in master_letters if l < letter and l in los_module]
                los_module[letter] = prev[-1] if prev else (mods[0].number if mods else 0)
                how = "the preceding LOS"
            issues.append(Issue("warning", "los_module_inferred",
                                f"LOS {n}.{letter} has no body marker; assigned to module {n}.{los_module[letter]} from {how}",
                                entry.line if entry else None))

        # An LOS often runs across several modules but is marked only in the first. A module
        # with no LOS marker of its own continues the LOS still in effect.
        modules_out = []
        running: list[str] = []
        for mod in mods:
            sections = []
            unmarked = not any(s.los for s in mod.sections)
            for s in mod.sections:
                if not (s.items or s.los):
                    continue
                cont = unmarked and bool(running)
                sections.append({"los": list(running) if cont else s.los, "cont": cont,
                                 "blocks": to_blocks(s.items, figreg, book)})
                if s.los:
                    running = s.los
            modules_out.append({"number": mod.number, "title": mod.title, "line": mod.line,
                                "sections": sections, "quiz": quiz_by_module.get(mod.number, [])})

        out.append({
            "number": n,
            "title": entry.title if entry else ctx.body_title.title(),
            "line": ctx.line,
            "exam_focus": to_blocks(ctx.focus_items, figreg, book),
            "los": [{"letter": l.letter, "text": l.text, "module": los_module.get(l.letter)} for l in (entry.los if entry else [])],
            "key_concepts": {k.split(".")[1]: to_blocks(v, figreg, book) for k, v in ctx.kc_items.items() if int(k.split(".")[0]) == n},
            "modules": modules_out,
        })
    return out
