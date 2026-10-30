"""Incremental parsing: a book is re-parsed only when something it depends on changed.

Sources in content/ are PDFs (preferred: clean text, real figure images),
PDF->Markdown conversions, or native JSON books (*.json) written by the authoring
scripts, which are already in the parsed shape and skip the parser. Cache key per book = source SHA-1 + parser version,
plus the PDF reader version for PDFs, or the vocabulary and ligature-override
hashes for Markdown. The Markdown vocabulary is frozen in .cache/vocab.tsv the
first time it is built; `python -m builder vocab` rebuilds it deliberately.
Figure images extracted from PDFs live in .cache/img/.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import Config, Paths
from .parse.normalize import Vocab
from .parse.pdf import READER_VERSION, read_pdf
from .parse.segment import PARSER_VERSION, parse_book, parse_items


def sha1(data: str | bytes) -> str:
    return hashlib.sha1(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def book_files(paths: Paths) -> list[Path]:
    return sorted([*paths.content.glob("*.pdf"), *paths.content.glob("*.md"), *paths.content.glob("*.json")])


def load_native(raw: bytes, name: str) -> dict[str, Any]:
    """A native JSON book: {readings: [...]} in the parsed-book shape, without figures."""
    book = json.loads(raw.decode("utf-8"))
    return {"book": name, "sha": sha1(raw), "parser_version": "native", "readings": book["readings"],
            "figures": {}, "ligatures": {"fixed": 0, "guessed": {}}, "issues": []}


def image_dir(paths: Paths) -> Path:
    return paths.cache / "img"


def build_vocab(paths: Paths) -> Path:
    texts = [p.read_text(encoding="utf-8") for p in book_files(paths) if p.suffix == ".md"]
    target = paths.cache / "vocab.tsv"
    target.parent.mkdir(parents=True, exist_ok=True)
    Vocab.from_texts(texts).save(target)
    return target


def load_vocab(paths: Paths, cfg: Config) -> tuple[Vocab, str]:
    path = paths.cache / "vocab.tsv"
    if not path.exists():
        build_vocab(paths)
    vocab = Vocab.load(path)
    vocab.overrides = {k.lower(): v for k, v in cfg.ligature_overrides.items()}
    key = sha1(path.read_bytes() + json.dumps(vocab.overrides, sort_keys=True).encode())
    return vocab, key


@dataclass
class ParseResult:
    books: list[dict[str, Any]]
    reparsed: list[str] = field(default_factory=list)
    cached: list[str] = field(default_factory=list)


def _images_present(book: dict[str, Any], img_dir: Path) -> bool:
    return all((img_dir / f["src"]).exists() for f in book["figures"].values() if f.get("src"))


def parse_all(paths: Paths, cfg: Config, force: bool = False) -> ParseResult:
    files = book_files(paths)
    vocab, vocab_key = load_vocab(paths, cfg) if any(p.suffix == ".md" for p in files) else (None, "")
    img_dir = image_dir(paths)
    cache_dir = paths.cache / "books"
    cache_dir.mkdir(parents=True, exist_ok=True)
    result = ParseResult([])
    live = set()
    for path in files:
        raw = path.read_bytes()
        if path.suffix == ".json":
            result.books.append(load_native(raw, path.name))
            result.reparsed.append(path.name)
            continue
        extra = f"pdf{READER_VERSION}" if path.suffix == ".pdf" else vocab_key
        key = f"{sha1(raw)}:{PARSER_VERSION}:{extra}"
        cache_file = cache_dir / f"{path.name}.json"
        live.add(cache_file.name)
        if not force and cache_file.exists():
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached.get("cache_key") == key and _images_present(cached, img_dir):
                result.books.append(cached)
                result.cached.append(path.name)
                continue
        if path.suffix == ".pdf":
            items, sha = read_pdf(path, img_dir)
            book = parse_items(items, path.name, sha)
        else:
            assert vocab is not None
            book = parse_book(raw.decode("utf-8"), path.name, vocab)
        book["cache_key"] = key
        cache_file.write_text(json.dumps(book, ensure_ascii=False), encoding="utf-8")
        result.books.append(book)
        result.reparsed.append(path.name)
    for stale in cache_dir.glob("*.json"):
        if stale.name not in live:
            stale.unlink()
    return result
