"""Schema validation, cross-reference checks and calculation checks."""

from __future__ import annotations

import json
from collections import Counter
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from . import calc
from .compile import load_generated
from .config import Config, Paths

SCHEMA_DIR = Path(__file__).parent / "schemas"
MIN_QUESTIONS_PER_LOS = 5
MIN_ITEM_SETS_PER_MODULE = 2
MIN_EXPLANATION_CHARS = 15  # catches a bare "Wrong." / "Correct."; short but specific reasons are fine
MAX_ANSWER_SHARE = 0.5  # warn if one letter is the answer this often (students learn the pattern)
WRONG_PREFIXES = ("Wrong", "Faux")  # explanations of wrong options start with one of these


@cache
def _registry() -> Registry:
    resources = []
    for f in SCHEMA_DIR.glob("*.schema.json"):
        schema = json.loads(f.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


@cache
def validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=_registry())


def schema_errors(name: str, doc: Any, where: str, limit: int = 20) -> list[dict[str, Any]]:
    out = []
    for err in sorted(validator(name).iter_errors(doc), key=lambda e: list(e.absolute_path))[:limit]:
        path = "/".join(str(p) for p in err.absolute_path)
        out.append({"level": "error", "code": f"schema_{name}", "msg": f"{where} /{path}: {err.message[:300]}",
                    "line": None, "where": where})
    return out


def validate_all(manifest: dict[str, Any], chunks: dict[str, dict[str, Any]], figures: dict[str, Any],
                 cfg: Config, paths: Paths) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Returns (issues, coverage stats)."""
    issues: list[dict[str, Any]] = []
    issues += schema_errors("manifest", manifest, "manifest.json")

    all_modules = {m["id"] for ch in chunks.values() for m in ch["modules"]}
    coverage: dict[str, Any] = {"topics": {}}
    for topic, ch in chunks.items():
        issues += schema_errors("chunk", ch, f"chunk:{topic}")
        los_ids = {l["id"] for l in ch["los"]}
        modules = {m["id"] for m in ch["modules"]}

        for raw in load_generated(paths, topic, []).values():
            where = raw.pop("_file")
            issues += schema_errors("generated", raw, where)
            for q in raw.get("questions", []) + [q for s in raw.get("item_sets", []) for q in s.get("questions", [])]:
                if q.get("los") not in los_ids:
                    issues.append(_err("generated_unknown_los", f"{where} {q.get('id')}: LOS {q.get('los')} not in topic", where))
                for e in calc.check_question(q):
                    issues.append(_err("calc_mismatch", f"{where} {q.get('id')}: {e}", where))
                issues += _lint_question(q, where)
            for f in raw.get("formulas", []):
                for l in f.get("los", []):
                    if l not in los_ids:
                        issues.append(_err("generated_unknown_los", f"{where} {f.get('id')}: LOS {l} not in topic", where))
            for c in raw.get("connections", []):
                if c.get("to") not in all_modules:
                    issues.append(_err("connection_unknown_module", f"{where}: connection to unknown module {c.get('to')}", where))
            for s in raw.get("item_sets", []):
                for m in s.get("modules", []):
                    if m not in all_modules:
                        issues.append(_err("item_set_unknown_module", f"{where} {s.get('id')}: unknown module {m}", where))
            for fig in raw.get("repairs", {}):
                if fig not in figures:
                    issues.append(_err("repair_unknown_figure", f"{where}: repair for unknown figure {fig}", where))

        ids = Counter(q["id"] for q in ch["questions"])
        ids.update(q["id"] for s in ch["item_sets"] for q in s.get("questions", []))
        for qid, n in ids.items():
            if n > 1:
                issues.append(_err("duplicate_question_id", f"{topic}: question id {qid} used {n} times", topic))

        generated = [q for q in ch["questions"] if q.get("source") != "schweser"]
        generated += [q for s in ch["item_sets"] for q in s.get("questions", [])]
        letters = Counter(q["answer"] for q in generated)
        if len(generated) >= 30 and max(letters.values()) > MAX_ANSWER_SHARE * len(generated):
            issues.append({"level": "warning", "code": "answer_position_skew", "line": None, "where": topic,
                           "msg": f"{topic}: correct answers by position {dict(letters)}; one letter exceeds {MAX_ANSWER_SHARE:.0%}"})

        gen_q = Counter(q["los"] for q in ch["questions"] if q.get("source") != "schweser")
        sets = Counter(m for s in ch["item_sets"] for m in s.get("modules", []))
        fig_kinds = Counter(f["kind"] for f in ch["figures"].values())
        repaired = sum(1 for f in ch["figures"] if f in ch["repairs"])
        coverage["topics"][topic] = {
            "los": len(los_ids),
            "los_with_min_questions": sum(1 for l in los_ids if gen_q[l] >= MIN_QUESTIONS_PER_LOS),
            "modules": len(modules),
            "modules_with_learning": len(ch["learning"]),
            "modules_with_min_item_sets": sum(1 for m in modules if sets[m] >= MIN_ITEM_SETS_PER_MODULE),
            "schweser_questions": sum(1 for q in ch["questions"] if q.get("source") == "schweser"),
            "generated_questions": sum(gen_q.values()),
            "figures": len(ch["figures"]),
            "figures_by_kind": dict(fig_kinds),
            "figures_repaired": repaired,
            "figures_with_image": sum(1 for f in ch["figures"].values() if f.get("src")),
        }
    return issues, coverage


def _err(code: str, msg: str, where: str) -> dict[str, Any]:
    return {"level": "error", "code": code, "msg": msg, "line": None, "where": where}


def _lint_question(q: dict[str, Any], where: str) -> list[dict[str, Any]]:
    """Content checks that schemas can't express."""
    out = []
    qid, ans, expl = q.get("id"), q.get("answer"), q.get("explanations") or {}
    for letter, text in expl.items():
        expected = ("Correct",) if letter == ans else WRONG_PREFIXES
        if not text.startswith(expected):
            out.append(_err("answer_key_mismatch",
                            f"{where} {qid}: explanation {letter} should start with {' or '.join(expected)!r} (answer is {ans})", where))
        if len(text) < MIN_EXPLANATION_CHARS:
            out.append({"level": "warning", "code": "thin_explanation", "line": None, "where": where,
                        "msg": f"{where} {qid}: explanation {letter} is too short to teach anything: {text!r}"})
    opts = [o.strip().lower() for o in q.get("options", [])]
    if len(set(opts)) != len(opts):
        out.append(_err("duplicate_options", f"{where} {qid}: options repeat", where))
    return out
