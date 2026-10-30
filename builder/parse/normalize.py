"""Text clean-up for PDF->Markdown conversions.

Two problems are fixed here:

* Broken ligatures. The converter replaced the ligature glyphs ti, tt, fi, ff,
  ft, tf, tti, ... with U+FFFD ("Mul�ple", "o�en", "overfi�ng").
  For each damaged word we try every plausible fill and keep the one that makes
  the most frequent known word. The vocabulary is a word-frequency list built
  from undamaged words in the corpus (Book 3 is entirely clean). If no fill
  makes a known word, a character 4-gram model picks the most plausible fill
  and the word is reported as "guessed".
* Converter noise: "Video covering this content is available online." banners,
  stray <u> tags and split words such as "~~av~~ ailable".
"""

from __future__ import annotations

import itertools
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

BAD = "�"
# Share of each fill among words repaired to a known word in the 2025 L2 books.
FILL_PRIOR = {"ti": 0.868, "tf": 0.046, "f": 0.029, "ft": 0.027, "tt": 0.023, "tti": 0.0045, "t": 0.0026}
FILLS = tuple(FILL_PRIOR) + ("fi", "ff", "fl", "ffi", "ffl", "fb", "fj")
_PRIOR_FLOOR = 0.001
_PRIOR_WEIGHT = 0.15
_SUFFIXES = ("s", "es", "ly", "ally", "ed", "ing", "al", "ation", "ations")
_WORD = re.compile(r"[A-Za-z�]+")
_CLEAN_WORD = re.compile(r"[A-Za-z]+")
_MAX_BAD_PER_WORD = 3


@dataclass
class Vocab:
    counts: Counter[str]
    ngrams: Counter[str] = field(default_factory=Counter)
    _ngram_total: int = 0
    # damaged word (lowercase, "?" for the broken glyph) -> correct word
    overrides: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_texts(cls, texts: list[str]) -> "Vocab":
        counts: Counter[str] = Counter()
        for text in texts:
            for word in _WORD.findall(text):
                if BAD not in word:
                    counts[word.lower()] += 1
        return cls.from_counts(counts)

    @classmethod
    def from_counts(cls, counts: Counter[str]) -> "Vocab":
        ngrams: Counter[str] = Counter()
        for word, n in counts.items():
            padded = f"^{word}$"
            for i in range(len(padded) - 3):
                ngrams[padded[i : i + 4]] += n
        return cls(counts, ngrams, sum(ngrams.values()))

    def save(self, path: Path) -> None:
        lines = [f"{w}\t{n}" for w, n in sorted(self.counts.items(), key=lambda kv: (-kv[1], kv[0]))]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Vocab":
        counts: Counter[str] = Counter()
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                word, n = line.split("\t")
                counts[word] = int(n)
        return cls.from_counts(counts)

    def ngram_score(self, word: str) -> float:
        padded = f"^{word.lower()}$"
        grams = [padded[i : i + 4] for i in range(len(padded) - 3)]
        if not grams:
            return -math.inf
        denom = self._ngram_total + len(self.ngrams) + 1
        return sum(math.log((self.ngrams[g] + 1) / denom) for g in grams) / len(grams)


@dataclass
class RepairStats:
    fixed: Counter[str] = field(default_factory=Counter)
    guessed: Counter[str] = field(default_factory=Counter)  # damaged word -> chosen guess, keyed "orig->guess"


def _fill_case(fill: str, word: str) -> str:
    letters = [c for c in word if c.isalpha() and c != BAD]
    return fill.upper() if letters and all(c.isupper() for c in letters) else fill


def _morph_known(word: str, vocab: Vocab) -> int:
    """Frequency of an inflected relative of `word` (exponential <- exponentially)."""
    w = word.lower()
    forms = [w + s for s in _SUFFIXES]
    forms += [w[: -len(s)] for s in _SUFFIXES if w.endswith(s) and len(w) - len(s) >= 4]
    return max((vocab.counts.get(f, 0) for f in forms), default=0)


def repair_word(word: str, vocab: Vocab) -> tuple[str, bool]:
    """Return (repaired word, True if it is a known word or an inflection of one)."""
    holes = word.count(BAD)
    if holes == 0:
        return word, True
    override = vocab.overrides.get(word.lower().replace(BAD, "?"))
    if override:
        if word[0].isupper():
            override = override.upper() if word.replace(BAD, "").isupper() else override.capitalize()
        return override, True
    if holes > _MAX_BAD_PER_WORD:
        return word.replace(BAD, _fill_case("ti", word)), False
    parts = word.split(BAD)
    cands = []
    for combo in itertools.product(FILLS, repeat=holes):
        cand = parts[0] + "".join(_fill_case(f, word) + p for f, p in zip(combo, parts[1:]))
        prior = sum(math.log(FILL_PRIOR.get(f, _PRIOR_FLOOR)) for f in combo)
        cands.append((cand, prior))

    exact = max(cands, key=lambda c: (vocab.counts.get(c[0].lower(), 0), c[1]))
    if vocab.counts.get(exact[0].lower(), 0):
        return exact[0], True
    morph = max(cands, key=lambda c: (_morph_known(c[0], vocab), c[1]))
    if _morph_known(morph[0], vocab):
        return morph[0], True
    guess = max(cands, key=lambda c: vocab.ngram_score(c[0]) + _PRIOR_WEIGHT * c[1])
    return guess[0], False


def repair_ligatures(text: str, vocab: Vocab, stats: RepairStats | None = None) -> str:
    cache: dict[str, tuple[str, bool]] = {}

    def sub(m: re.Match[str]) -> str:
        word = m.group(0)
        if BAD not in word:
            return word
        if word not in cache:
            cache[word] = repair_word(word, vocab)
        fixed, known = cache[word]
        if stats is not None:
            if known:
                stats.fixed[word] += 1
            else:
                stats.guessed[f"{word} -> {fixed}"] += 1
        return fixed

    return _WORD.sub(sub, text)


_VIDEO_LINE = re.compile(r"Video\s*covering", re.I)
_VIDEO_PHRASES = re.compile(
    r"(?:Video\s*covering|this\s+content\s+is|available\s+online\.?)", re.I
)
_STRIKE_SPLIT = re.compile(r"~~([A-Za-z]+)~~\s?")
_UNDERLINE = re.compile(r"</?u>")
_MARK = re.compile(r"<mark>.*?</mark>")  # converter highlight junk, e.g. "<mark>e—SCSC</mark>"


def clean_line(line: str) -> str | None:
    """Clean converter noise from one line. Returns None if nothing is left."""
    line = _UNDERLINE.sub("", line)
    line = _MARK.sub("", line)
    line = _STRIKE_SPLIT.sub(r"\1", line)
    if _VIDEO_LINE.search(line):
        line = _VIDEO_PHRASES.sub("", line)
        if not re.search(r"[A-Za-z0-9]", line.replace("*", "")):
            return None
    return line.rstrip()


def normalize_text(text: str, vocab: Vocab, stats: RepairStats | None = None) -> list[str]:
    """Normalise a whole book and return its lines, one per source line."""
    text = unicodedata.normalize("NFC", text).replace("\u00a0", " ").replace("\r\n", "\n")
    text = repair_ligatures(text, vocab, stats)
    # Noise-only lines become blank so line numbers still match the source file.
    return [clean_line(raw) or "" for raw in text.split("\n")]
