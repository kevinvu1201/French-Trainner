"""Compile parsed books (+ generated learning layer) into per-topic chunks and a manifest.

Chunks are content-addressed (`chunks/<topic>.<hash>.json`), so a rebuild
only writes topics whose content changed, and browsers/service workers can
cache them forever. IDs come from reading/module/LOS labels, never file order.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .config import Config, Paths
from .graph import build_graph
from .incremental import image_dir, sha1
from .translations import load_for_chunk

CHUNK_SCHEMA = 1
_FIG_TOKEN = re.compile(r"\[\[(fig\.[0-9a-f]{10})\]\]")


def rid(n: int) -> str: return f"r{n:02d}"
def mid(n: int, m: int) -> str: return f"m{n:02d}.{m}"
def lid(n: int, letter: str) -> str: return f"los.{n:02d}.{letter}"


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass
class CompileResult:
    manifest: dict[str, Any]
    chunks: dict[str, dict[str, Any]]  # topic -> chunk
    written: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    issues: list[dict[str, Any]] = field(default_factory=list)


def _issue(issues: list[dict[str, Any]], level: str, code: str, msg: str, where: str | None = None) -> None:
    issues.append({"level": level, "code": code, "msg": msg, "line": None, "where": where})


def _fig_refs(obj: Any, out: set[str]) -> None:
    if isinstance(obj, str):
        out.update(_FIG_TOKEN.findall(obj))
    elif isinstance(obj, dict):
        if obj.get("t") == "fig":
            out.add(obj["id"])
        for v in obj.values():
            _fig_refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _fig_refs(v, out)


def load_generated(paths: Paths, topic: str, issues: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """generated/<topic>/<module>.json -> {module id: data}. Schema checks happen in validate."""
    out: dict[str, dict[str, Any]] = {}
    folder = paths.generated / topic
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            _issue(issues, "error", "generated_bad_json", f"{f.name}: {e}", str(f))
            continue
        data["_file"] = f"{topic}/{f.name}"
        out[data.get("module", f.stem)] = data
    return out


def build_chunks(books: list[dict[str, Any]], cfg: Config, paths: Paths) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Returns (chunks by topic, figure registry by id, issues)."""
    issues: list[dict[str, Any]] = []
    figures: dict[str, dict[str, Any]] = {}
    for b in books:
        figures.update(b["figures"])

    chunks: dict[str, dict[str, Any]] = {
        t.id: {"schema": CHUNK_SCHEMA, "topic": t.id, "readings": [], "modules": [], "los": [],
               "questions": [], "item_sets": [], "formulas": [], "learning": {}, "figures": {}, "repairs": {},
               "translations": {}}
        for t in cfg.topics
    }
    for b in books:
        for r in b["readings"]:
            n = r["number"]
            topic = cfg.topic_for_reading(n)
            if topic is None:
                _issue(issues, "error", "reading_without_topic", f"Reading {n} is not mapped in config/topics.yaml", b["book"])
                continue
            ch = chunks[topic.id]
            reading = {"id": rid(n), "n": n, "title": r["title"], "exam_focus": r["exam_focus"], "modules": [], "los": []}
            ch["readings"].append(reading)
            for mod in r["modules"]:
                sections = [{"los": [lid(n, l) for l in s["los"]], "blocks": s["blocks"],
                             **({"cont": True} if s.get("cont") else {})} for s in mod["sections"]]
                m_id = mid(n, mod["number"])
                reading["modules"].append(m_id)
                ch["modules"].append({"id": m_id, "reading": rid(n), "n": mod["number"],
                                      "title": mod["title"] or f"Module {n}.{mod['number']}",
                                      "hash": sha1(stable_json(sections))[:12], "sections": sections})
                for q in mod["quiz"]:
                    if not q["options"] or not q["answer"]:
                        continue  # unusable; already reported by the parser
                    ch["questions"].append({
                        "id": f"sq.{n:02d}.{mod['number']}.{q['n']}", "source": "schweser", "module": m_id,
                        "los": [lid(n, l) for l in q["los"]], "vignette": q["vignette"], "stem": q["stem"],
                        "options": q["options"], "ocr_options": q["ocr_options"],
                        "options_in_figure": q.get("options_in_figure", False), "answer": q["answer"],
                        "explanation": q["explanation"] or "",
                    })
            spans: dict[str, list[str]] = {}  # LOS id -> every module it appears in
            for m in ch["modules"]:
                if m["reading"] == rid(n):
                    for s in m["sections"]:
                        for l in s["los"]:
                            if m["id"] not in spans.setdefault(l, []):
                                spans[l].append(m["id"])
            for los in r["los"]:
                l_id = lid(n, los["letter"])
                home = mid(n, los["module"] or 0)
                reading["los"].append(l_id)
                ch["los"].append({"id": l_id, "reading": rid(n), "module": home,
                                  "modules": spans.get(l_id) or [home],
                                  "letter": los["letter"], "text": los["text"],
                                  "verb": (los["text"].split() or ["?"])[0].lower().strip(",."),
                                  "key_concepts": r["key_concepts"].get(los["letter"], [])})

    for topic, ch in chunks.items():
        ch["readings"].sort(key=lambda r: r["n"])
        _merge_generated(ch, load_generated(paths, topic, issues), issues)
        ch["translations"], stale = load_for_chunk(paths.root / "translations" / f"{topic}.json", ch)
        if stale:
            _issue(issues, "warning", "translation_stale",
                   f"{topic}: {stale} translations no longer match their text; run authoring/translate.py {topic}")
        refs: set[str] = set()
        _fig_refs([ch["readings"], ch["modules"], ch["los"], ch["questions"]], refs)
        ch["figures"] = {f: _figure_out(figures[f]) for f in sorted(refs) if f in figures}
        for missing in sorted(refs - figures.keys()):
            _issue(issues, "error", "figure_ref_missing", f"{topic}: reference to unknown figure {missing}")
    return chunks, figures, issues


def _figure_out(fig: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"kind": fig["kind"], "caption": fig["caption"]}
    if fig.get("src"):
        out.update(src=f"img/{fig['src']}", w=fig["w"], h=fig["h"])
    else:
        out["ocr"] = fig["ocr"]
    return out


def _sync_images(chunks: dict[str, dict[str, Any]], paths: Paths) -> int:
    """Copy referenced figure images from .cache/img to dist/data/img; drop unreferenced ones."""
    src_dir, out_dir = image_dir(paths), paths.data / "img"
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = {f["src"].removeprefix("img/") for ch in chunks.values() for f in ch["figures"].values() if f.get("src")}
    for name in wanted:
        target = out_dir / name
        if not target.exists() and (src_dir / name).exists():
            shutil.copyfile(src_dir / name, target)
    for old in out_dir.iterdir():
        if old.name not in wanted:
            old.unlink()
    return len(wanted)


def _sync_audio(chunks: dict[str, dict[str, Any]], cfg: Config, paths: Paths, issues: list[dict[str, Any]]) -> None:
    """Copy each audio file an item set names (from cfg.audio_source) to dist/data/audio/<sha1-10><ext>
    and point the set at it. Content-addressed names can be cached forever; unreferenced files are removed."""
    out_dir = paths.data / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted: set[str] = set()
    for topic, ch in chunks.items():
        for s in ch["item_sets"]:
            name = s.get("audio")
            if not name or name.startswith("audio/"):
                continue
            src = cfg.audio_source / name if cfg.audio_source else None
            if src is None or not src.is_file():
                _issue(issues, "error", "audio_missing", f"{topic} {s['id']}: audio file {name} not found in {cfg.audio_source}")
                s.pop("audio")
                continue
            target = f"{sha1(src.read_bytes())[:10]}{src.suffix.lower()}"
            if not (out_dir / target).exists():
                shutil.copyfile(src, out_dir / target)
            s["audio"] = f"audio/{target}"
            wanted.add(target)
    for old in out_dir.iterdir():
        if old.name not in wanted:
            old.unlink()


def _content_bytes(paths: Paths, topics_meta: list[dict[str, Any]], graph_path: str | None) -> int:
    """Size of everything "Download all content" fetches: topic chunks, figure images, audio and the graph."""
    total = sum(t["bytes"] for t in topics_meta)
    total += sum(f.stat().st_size for d in ("img", "audio") if (paths.data / d).exists()
                 for f in (paths.data / d).iterdir() if f.is_file())
    if graph_path:
        total += (paths.data / graph_path).stat().st_size
    return total


def _merge_generated(ch: dict[str, Any], gen: dict[str, dict[str, Any]], issues: list[dict[str, Any]]) -> None:
    modules = {m["id"]: m for m in ch["modules"]}
    for m_id, data in gen.items():
        mod = modules.get(m_id)
        if mod is None:
            _issue(issues, "error", "generated_unknown_module", f"{data['_file']}: module {m_id} not in topic {ch['topic']}", data["_file"])
            continue
        if data.get("source_hash") != mod["hash"]:
            mod["stale_generated"] = True
            _issue(issues, "warning", "generated_stale",
                   f"{data['_file']}: source module changed since generation (hash {data.get('source_hash')} != {mod['hash']})", data["_file"])
        ch["learning"][m_id] = {**data.get("learning", {}), "connections": data.get("connections", [])}
        ch["questions"].extend(data.get("questions", []))
        ch["item_sets"].extend(data.get("item_sets", []))
        ch["formulas"].extend(data.get("formulas", []))
        ch["repairs"].update(data.get("repairs", {}))


def write_outputs(chunks: dict[str, dict[str, Any]], cfg: Config, paths: Paths) -> CompileResult:
    out_dir = paths.data / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)
    _sync_images(chunks, paths)
    result = CompileResult({}, chunks)
    _sync_audio(chunks, cfg, paths, result.issues)
    topics_meta = []
    for t in cfg.topics:
        ch = chunks[t.id]
        body = stable_json(ch)
        name = f"{t.id}.{sha1(body)[:10]}.json"
        target = out_dir / name
        if target.exists():
            result.unchanged.append(t.id)
        else:
            target.write_text(body, encoding="utf-8")
            result.written.append(t.id)
        for old in out_dir.glob(f"{t.id}.*.json"):
            if old.name != name:
                old.unlink()
        topics_meta.append({
            "id": t.id, "name": t.name, "weight": round(t.weight, 4), "weight_range": list(t.weight_range),
            "chunk": f"chunks/{name}", "bytes": len(body.encode("utf-8")),
            "counts": {"readings": len(ch["readings"]), "modules": len(ch["modules"]), "los": len(ch["los"]),
                       "questions": len(ch["questions"]), "item_sets": len(ch["item_sets"]),
                       "formulas": len(ch["formulas"]), "figures": len(ch["figures"]),
                       "repairs": len(ch["repairs"]), "learning": len(ch["learning"]),
                       "audio_sets": sum(1 for s in ch["item_sets"] if s.get("audio")),
                       "translations": len(ch["translations"])},
            "readings": [{"id": r["id"], "n": r["n"], "title": r["title"],
                          "modules": [{"id": m["id"], "title": m["title"],
                                       "los": [l["id"] for l in ch["los"] if m["id"] in l["modules"]]}
                                      for m in ch["modules"] if m["reading"] == r["id"]]}
                         for r in ch["readings"]],
        })
    # Practice material per LOS, so the Smart Session can plan without loading every chunk.
    los_questions: dict[str, int] = {}
    for ch in chunks.values():
        for q in ch["questions"]:
            if q.get("options") and q.get("answer"):
                for l in [q["los"]] if isinstance(q["los"], str) else q["los"]:
                    los_questions[l] = los_questions.get(l, 0) + 1
    graph = build_graph(chunks, [t.id for t in cfg.topics])
    graph_path = None
    for old in paths.data.glob("graph.*.json"):
        old.unlink()
    if graph:
        body = stable_json(graph)
        graph_path = f"graph.{sha1(body)[:10]}.json"
        (paths.data / graph_path).write_text(body, encoding="utf-8")
    manifest = {
        "schema": CHUNK_SCHEMA,
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "content_version": sha1("".join(t["chunk"] for t in topics_meta))[:12],
        "weights_verified": cfg.weights_verified,
        "aliases": cfg.aliases,
        "graph": graph_path,
        "scoring": cfg.scoring,
        "los_questions": dict(sorted(los_questions.items())),
        "content_bytes": _content_bytes(paths, topics_meta, graph_path),
        "topics": topics_meta,
    }
    (paths.data / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    result.manifest = manifest
    return result
