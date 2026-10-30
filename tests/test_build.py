import json
from collections import Counter
import re
import shutil
from pathlib import Path

import pytest

from builder.config import Paths
from builder.pipeline import build

REPO = Path(__file__).parent.parent


def _chunk(paths: Paths, topic: str) -> dict:
    manifest = json.loads((paths.data / "manifest.json").read_text(encoding="utf-8"))
    entry = next(t for t in manifest["topics"] if t["id"] == topic)
    return json.loads((paths.data / entry["chunk"]).read_text(encoding="utf-8"))


def test_build_ids_and_outputs(project):
    paths = Paths(project)
    res = build(paths)
    assert res.ok, [i for i in res.report["issues"] if i["level"] == "error"]
    quant = _chunk(paths, "quant")
    assert [l["id"] for l in quant["los"]] == ["los.01.a", "los.01.b", "los.01.c", "los.01.d"]
    assert [m["id"] for m in quant["modules"]] == ["m01.1", "m01.2"]
    assert {q["id"] for q in quant["questions"]} == {"sq.01.1.1", "sq.01.2.1", "sq.01.2.2"}
    refs = {f for q in quant["questions"] for f in re.findall(r"\[\[(fig\.[0-9a-f]+)\]\]", q["explanation"])}
    assert refs and refs <= set(quant["figures"])
    assert (paths.dist / "report.html").exists()


def test_incremental_rebuild(project):
    paths = Paths(project)
    first = build(paths).report["incremental"]
    assert first["reparsed"] == ["Book 9.md"]
    second = build(paths).report["incremental"]
    assert second["reparsed"] == [] and second["cached"] == ["Book 9.md"]
    assert second["written"] == []

    # Edit reading 2 only: IDs stay stable and only that topic's chunk is rewritten.
    book = paths.content / "Book 9.md"
    book.write_text(book.read_text(encoding="utf-8").replace(
        "The mean-reverting level is b0 / (1 − b1).",
        "A new first paragraph.\n\nThe mean-reverting level is b0 / (1 − b1)."), encoding="utf-8")
    before = [l["id"] for l in _chunk(paths, "economics")["los"]]
    third = build(paths).report["incremental"]
    assert third["reparsed"] == ["Book 9.md"]
    assert third["written"] == ["economics"] and third["unchanged"] == ["quant"]
    assert [l["id"] for l in _chunk(paths, "economics")["los"]] == before
    assert len(list((paths.data / "chunks").glob("economics.*.json"))) == 1  # stale chunk removed


def test_generated_layer_is_merged_validated_and_staleness_tracked(project, good_generated):
    paths = Paths(project)
    build(paths)
    mod_hash = next(m for m in _chunk(paths, "quant")["modules"] if m["id"] == "m01.2")["hash"]
    gen = good_generated
    gen["source_hash"] = mod_hash
    gen["repairs"] = {}
    gen["questions"][0]["options"] = ["0.596", "0.630", "0.596"]  # distractor C also correct -> calc error
    (paths.generated / "quant").mkdir(parents=True)
    target = paths.generated / "quant" / "m01.2.json"
    target.write_text(json.dumps(gen), encoding="utf-8")

    rep = build(paths).report
    assert any(i["code"] == "calc_mismatch" for i in rep["issues"])

    gen["questions"][0]["options"][2] = "0.700"
    gen["source_hash"] = "outdated"
    target.write_text(json.dumps(gen), encoding="utf-8")
    rep = build(paths).report
    assert rep["summary"]["errors"] == 0
    assert any(i["code"] == "generated_stale" for i in rep["issues"])
    quant = _chunk(paths, "quant")
    assert "m01.2" in quant["learning"] and quant["formulas"][0]["id"] == "f.01.adj-r2"
    assert next(m for m in quant["modules"] if m["id"] == "m01.2")["stale_generated"] is True


@pytest.mark.skipif(not (REPO / "content").exists(), reason="real content not present")
def test_real_content_builds_cleanly(tmp_path):
    shutil.copytree(REPO / "config", tmp_path / "config")
    shutil.copytree(REPO / "content", tmp_path / "content")
    shutil.copytree(REPO / "generated", tmp_path / "generated")
    rep = build(Paths(tmp_path)).report
    s = rep["summary"]
    assert s["errors"] == 0 and s["warnings"] == 0, [i["msg"] for i in rep["issues"]][:5]
    assert s["readings"] == 14  # 7 grammar chapters + 7 vocabulary themes
    assert s["los_with_body_marker"] == s["los"]
    topics = {t["id"]: t for t in rep["topics"]}
    for tid, t in topics.items():
        assert t["modules_with_learning"] == t["modules"], tid
        if tid != "vocabulaire":
            assert t["generated_questions"] >= 20, tid
    # Every grammar objective is practised by at least 3 standalone questions.
    per_los = Counter(q["los"] for f in (REPO / "generated").glob("*/*.json")
                      for q in json.loads(f.read_text(encoding="utf-8"))["questions"])
    for t in rep["topics"]:
        if t["id"] == "vocabulaire":
            continue
        chunk = json.loads((tmp_path / "dist" / "data" / f"chunks").joinpath(
            next(p.name for p in (tmp_path / "dist" / "data" / "chunks").glob(f"{t['id']}.*.json"))).read_text(encoding="utf-8"))
        for l in chunk["los"]:
            assert per_los[l["id"]] >= 3, l["id"]
