"""Offline translations for tap-to-translate: which texts get translated, under which keys.

Shared by authoring/translate.py (which asks Gemini) and compile (which ships the
translations whose source text still matches). Keys:
  <qid>|stem, <qid>|A..C (options), <qid>|xA..xC (explanations),
  <set id>|v<i> (context / gap-fill paragraphs), <set id>|t<i> (transcript paragraphs)
Texts are stored as displayed: Markdown ** and _ markers removed (the app taps rendered text).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

LETTERS = "ABC"


def text_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def paragraphs(text: str | None) -> list[str]:
    """Same split as the app's paragraphs() in app/js/views/practice.js."""
    return [p for p in re.split(r"\n{2,}", text or "") if p]


def displayed(text: str) -> str:
    return re.sub(r"\*\*|(?<!\w)_|_(?!\w)", "", text)


def collect_texts(questions: list[dict[str, Any]], item_sets: list[dict[str, Any]]) -> dict[str, str]:
    texts: dict[str, str] = {}
    all_q = [q for q in questions if q.get("explanations")]
    for s in item_sets:
        all_q += s["questions"]
        for i, p in enumerate(paragraphs(s.get("vignette"))):
            texts[f"{s['id']}|v{i}"] = p
        for i, p in enumerate(paragraphs(s.get("transcript"))):
            texts[f"{s['id']}|t{i}"] = p
    for q in all_q:
        texts[f"{q['id']}|stem"] = q["stem"]
        for l, opt in zip(LETTERS, q["options"]):
            texts[f"{q['id']}|{l}"] = opt
        for l in LETTERS:
            texts[f"{q['id']}|x{l}"] = q["explanations"][l]
    return {k: displayed(v) for k, v in texts.items()}


def load_for_chunk(path: Path, chunk: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Translations from translations/<topic>.json whose source text is unchanged, plus how many were stale."""
    if not path.exists():
        return {}, 0
    stored = json.loads(path.read_text(encoding="utf-8"))
    texts = collect_texts(chunk["questions"], chunk["item_sets"])
    out, stale = {}, 0
    for key, text in texts.items():
        t = stored.get(key)
        if not t:
            continue
        if t.get("h") != text_hash(text):
            stale += 1
            continue
        out[key] = {"en": t["en"], "s": t.get("s", []), "g": t.get("g", {})}
    return out, stale
