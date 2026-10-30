"""Project paths and YAML configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def content(self) -> Path: return self.root / "content"
    @property
    def generated(self) -> Path: return self.root / "generated"
    @property
    def config(self) -> Path: return self.root / "config"
    @property
    def app(self) -> Path: return self.root / "app"
    @property
    def dist(self) -> Path: return self.root / "dist"
    @property
    def data(self) -> Path: return self.dist / "data"
    @property
    def dist_enc(self) -> Path: return self.root / "dist-enc"
    @property
    def cache(self) -> Path: return self.root / ".cache"


@dataclass(frozen=True)
class Topic:
    id: str
    name: str
    readings: tuple[int, ...]  # reading (chapter) numbers in this topic
    weight: float  # normalised to sum to 1 across topics
    weight_range: tuple[float, float]


@dataclass(frozen=True)
class Config:
    topics: list[Topic]
    weights_verified: bool
    ligature_overrides: dict[str, str]
    aliases: dict[str, str]
    scoring: dict[str, Any]  # config/priority.yaml, shipped to the app in the manifest
    audio_source: Path | None = None  # config/audio.yaml: folder holding the audio files item sets name

    def topic_for_reading(self, n: int) -> Topic | None:
        return next((t for t in self.topics if n in t.readings), None)


def _yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_config(paths: Paths) -> Config:
    topics_cfg = _yaml(paths.config / "topics.yaml").get("topics", [])
    weights_cfg = _yaml(paths.config / "exam_weights.yaml")
    raw_weights: dict[str, tuple[float, float, float]] = {}
    for tid, w in (weights_cfg.get("weights") or {}).items():
        lo, hi = float(w["min"]), float(w["max"])
        raw_weights[tid] = (lo, hi, float(w.get("use", (lo + hi) / 2)))
    total = sum(v[2] for v in raw_weights.values()) or 1.0

    topics = []
    for t in topics_cfg:
        lo, hi, use = raw_weights.get(t["id"], (0.0, 0.0, 0.0))
        # `readings: [first, last]` is a range; `chapters: [a, b, c]` lists non-contiguous chapters.
        if "chapters" in t:
            numbers = tuple(int(n) for n in t["chapters"])
        else:
            first, last = t["readings"]
            numbers = tuple(range(int(first), int(last) + 1))
        topics.append(Topic(t["id"], t["name"], numbers, use / total, (lo, hi)))
    return Config(
        topics=topics,
        weights_verified=bool(weights_cfg.get("verified", False)),
        ligature_overrides=_yaml(paths.config / "ligature_overrides.yaml").get("overrides") or {},
        aliases=_yaml(paths.config / "id_aliases.yaml").get("aliases") or {},
        scoring=_yaml(paths.config / "priority.yaml"),
        audio_source=Path(src) if (src := _yaml(paths.config / "audio.yaml").get("source")) else None,
    )
