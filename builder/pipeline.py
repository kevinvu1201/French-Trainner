"""The build: parse (incremental) -> compile chunks -> validate -> report."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from .compile import build_chunks, write_outputs
from .config import Paths, load_config
from .incremental import parse_all
from .report import build_report, write_report
from .review import write_reviews
from .validate import validate_all


@dataclass
class BuildResult:
    report: dict[str, Any]
    seconds: float

    @property
    def ok(self) -> bool:
        return self.report["summary"]["errors"] == 0


def build(paths: Paths, force: bool = False) -> BuildResult:
    t0 = time.perf_counter()
    cfg = load_config(paths)
    parsed = parse_all(paths, cfg, force=force)
    chunks, figures, compile_issues = build_chunks(parsed.books, cfg, paths)
    out = write_outputs(chunks, cfg, paths)
    validation_issues, coverage = validate_all(out.manifest, chunks, figures, cfg, paths)
    report = build_report(parsed.books, compile_issues, validation_issues, coverage, out.manifest, cfg, {
        "reparsed": parsed.reparsed, "cached": parsed.cached, "written": out.written, "unchanged": out.unchanged,
    })
    write_report(report, paths)
    report["reviews"] = write_reviews(chunks, {t.id: t.name for t in cfg.topics}, paths)
    return BuildResult(report, time.perf_counter() - t0)
