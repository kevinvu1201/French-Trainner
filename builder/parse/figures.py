"""Classify figures so the report and the repair queue can rank them."""

from __future__ import annotations

import re

from .lines import Figure

KINDS = ("formula", "table", "chart", "noise")


def classify_figure(fig: Figure, caption: str | None = None) -> str:
    if not fig.src:
        return classify(fig.ocr, caption)
    # PDF image: no text to inspect, so use the caption and the shape on the page.
    cap = (caption or "").lower()
    if re.search(r"\b(chart|graph|plot|diagram|curve)\b", cap):
        return "chart"
    if cap.startswith(("figure", "exhibit", "table")):
        return "table"
    return "formula" if fig.h < 70 or fig.w / max(fig.h, 1) > 4 else "table"


def classify(ocr: str, caption: str | None = None) -> str:
    rows = [r for r in ocr.split("\n") if r.strip()]
    text = " ".join(rows)
    alnum = sum(c.isalnum() for c in text)
    if alnum < 4:
        return "noise"
    cap = (caption or "").lower()
    if re.search(r"\b(chart|graph|plot|diagram|curve)\b", cap):
        return "chart"
    digit_share = sum(c.isdigit() for c in text) / max(1, alnum)
    has_eq = "=" in text or re.search(r"\bwhere\s*:", text, re.I) is not None
    if len(rows) >= 3 and digit_share > 0.3 and not has_eq:
        return "table"
    if has_eq:
        return "formula"
    if cap.startswith(("figure", "exhibit", "table")):
        return "table" if len(rows) >= 3 else "chart"
    return "table" if len(rows) >= 3 else "formula"
