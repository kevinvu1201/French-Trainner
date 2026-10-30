"""Parse the "Learning Outcome Statements (LOS)" master list at the front of each book.

The master list is the source of truth for reading titles and LOS IDs:

    ###### **1.   Multiple Regression**
    The candidate should be able to:
    - a. describe the types of investment problems ...
    - h. explain the types of heteroskedasticity ... i. explain serial correlation ...

Items sometimes run together on one line (h and i above) or wrap onto a
following paragraph; both are handled.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .lines import Line

_READING = re.compile(r"^(\d{1,2})\.\s+(.+)$")
_ITEM = re.compile(r"^-?\s*([a-z])\.\s+(.*)$")
_CANDIDATE = re.compile(r"^-?\s*The candidate should be able to", re.I)


@dataclass
class LosEntry:
    reading: int
    letter: str
    text: str
    line: int


@dataclass
class ReadingEntry:
    number: int
    title: str
    line: int
    los: list[LosEntry] = field(default_factory=list)


def _split_inline(text: str, next_letter: str) -> list[tuple[str, str]]:
    """Split "... inference. i. explain serial ..." when `i` is the next expected letter."""
    out: list[tuple[str, str]] = []
    letter = None
    while True:
        m = re.search(rf"(?<=[.;])\s+({re.escape(next_letter)})\.\s+(?=[a-z])", text)
        if not m:
            break
        out.append((letter, text[: m.start()].strip()) if letter else ("", text[: m.start()].strip()))
        letter = m.group(1)
        text = text[m.end():]
        next_letter = chr(ord(next_letter) + 1)
    out.append((letter or "", text.strip()))
    return out


def parse_los_list(items: list[Line]) -> list[ReadingEntry]:
    readings: list[ReadingEntry] = []
    cur: ReadingEntry | None = None
    for it in items:
        p = it.plain
        if _CANDIDATE.match(p):
            continue
        m = _READING.match(p)
        if m and (it.heading or not _ITEM.match(p)) and not p.startswith("-"):
            cur = ReadingEntry(int(m.group(1)), m.group(2).strip(), it.no)
            readings.append(cur)
            continue
        if cur is None:
            continue
        m = _ITEM.match(p)
        if m and (not cur.los or m.group(1) == chr(ord(cur.los[-1].letter) + 1)):
            letter, rest = m.group(1), m.group(2)
            parts = _split_inline(rest, chr(ord(letter) + 1))
            cur.los.append(LosEntry(cur.number, letter, parts[0][1], it.no))
            for extra_letter, extra_text in parts[1:]:
                cur.los.append(LosEntry(cur.number, extra_letter, extra_text, it.no))
        elif cur.los:
            # Wrapped continuation of the previous LOS.
            cur.los[-1].text = f"{cur.los[-1].text} {p.lstrip('- ')}".strip()
    return readings
