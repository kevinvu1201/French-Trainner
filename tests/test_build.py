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


GRAMMAR = ("subjonctif", "hypotheses", "relatifs", "discours", "logique")


@pytest.mark.skipif(not (REPO / "content").exists(), reason="real content not present")
def test_real_content_builds_cleanly(tmp_path):
    shutil.copytree(REPO / "config", tmp_path / "config")
    shutil.copytree(REPO / "content", tmp_path / "content")
    shutil.copytree(REPO / "generated", tmp_path / "generated")
    listening = (REPO / "content" / "ecoute.json").exists()  # private (gitignored) listening exercises
    rep = build(Paths(tmp_path)).report
    s = rep["summary"]
    assert s["errors"] == 0 and s["warnings"] == 0, [i["msg"] for i in rep["issues"]][:5]
    # 7 grammar chapters + 7 vocabulary themes (+ 2 listening chapters when present)
    assert s["readings"] == 14 + (2 if listening else 0)
    assert s["los_with_body_marker"] == s["los"]
    topics = {t["id"]: t for t in rep["topics"]}
    for tid, t in topics.items():
        assert t["modules_with_learning"] == t["modules"], tid
    for tid in GRAMMAR:
        assert topics[tid]["generated_questions"] >= 20, tid
    if listening:
        assert topics["ecoute"]["audio_sets"] == 15
        assert len(list((tmp_path / "dist" / "data" / "audio").iterdir())) == 15
    # Every grammar objective is practised by at least 3 standalone questions.
    per_los = Counter(q["los"] for f in (REPO / "generated").glob("*/*.json")
                      for q in json.loads(f.read_text(encoding="utf-8"))["questions"])
    for tid in GRAMMAR:
        chunk = json.loads(next((tmp_path / "dist" / "data" / "chunks").glob(f"{tid}.*.json")).read_text(encoding="utf-8"))
        for l in chunk["los"]:
            assert per_los[l["id"]] >= 3, l["id"]


def _listening_set(n_questions: int, audio: str | None = "track.wav") -> dict:
    q = lambda k: {"id": f"set.m01.2.01.q{k}", "los": "los.01.c", "stem": f"Question {k} ?", "options": ["un", "deux", "trois"],
                   "answer": "B", "difficulty": 2, "qtype": "listening",
                   "explanations": {"A": "Faux. Ce n'est pas dit.", "B": "Correct. C'est dans le document.", "C": "Faux. C'est l'inverse."}}
    s = {"id": "set.m01.2.01", "modules": ["m01.2"], "title": "Écoute", "vignette": "Vous écoutez une émission.",
         "questions": [q(k) for k in range(1, n_questions + 1)]}
    if audio:
        s.update(audio=audio, plays=2, transcript="– Bonjour.\n\n– Au revoir.")
    return s


def _write_generated(project, doc):
    doc["repairs"] = {}  # the fixture's repair points at a figure this book doesn't have
    folder = project / "generated" / "quant"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "m01.2.json").write_text(json.dumps(doc), encoding="utf-8")


def test_listening_audio_is_copied_content_addressed_and_encrypted(project, good_generated, tmp_path):
    from builder.site import build_site
    shutil.copytree(REPO / "app", project / "app")
    audio_dir = tmp_path / "audio-src"
    audio_dir.mkdir()
    (audio_dir / "track.wav").write_bytes(b"RIFF-fake-audio-bytes")
    (project / "config" / "audio.yaml").write_text(f"source: '{audio_dir.as_posix()}'\n", encoding="utf-8")
    good_generated["item_sets"] = [_listening_set(7)]  # listening sets may have any number of questions
    _write_generated(project, good_generated)
    paths = Paths(project)
    res = build(paths)
    assert [i for i in res.report["issues"] if i["level"] == "error"] == []
    files = list((paths.data / "audio").iterdir())
    assert len(files) == 1 and re.fullmatch(r"[0-9a-f]{10}\.wav", files[0].name)
    chunk = json.loads(next((paths.data / "chunks").glob("quant.*.json")).read_text(encoding="utf-8"))
    s = chunk["item_sets"][0]
    assert s["audio"] == f"audio/{files[0].name}" and s["plays"] == 2 and len(s["questions"]) == 7
    manifest = json.loads((paths.data / "manifest.json").read_text(encoding="utf-8"))
    assert next(t for t in manifest["topics"] if t["id"] == "quant")["counts"]["audio_sets"] == 1
    build_site(paths, paths.dist_enc, "fixture-passphrase")
    enc = paths.dist_enc / "data" / "audio" / (files[0].name + ".enc")
    assert enc.exists() and b"fake-audio" not in enc.read_bytes()


def test_listening_audio_missing_is_an_error(project, good_generated):
    good_generated["item_sets"] = [_listening_set(4, audio="absent.mp3")]
    _write_generated(project, good_generated)
    codes = [i["code"] for i in build(Paths(project)).report["issues"] if i["level"] == "error"]
    assert "audio_missing" in codes


def test_question_count_rules_for_sets(project, good_generated):
    # A gap-fill text without audio still needs exactly 4 questions; a listening set needs plays and a transcript.
    good_generated["item_sets"] = [_listening_set(3, audio=None)]
    _write_generated(project, good_generated)
    msgs = [i["msg"] for i in build(Paths(project)).report["issues"] if i["code"] == "schema_generated"]
    assert any("questions" in m for m in msgs)
    bad = _listening_set(5)
    del bad["transcript"]
    good_generated["item_sets"] = [bad]
    _write_generated(project, good_generated)
    msgs = [i["msg"] for i in build(Paths(project)).report["issues"] if i["code"] == "schema_generated"]
    assert any("transcript" in m for m in msgs)


def test_translations_ship_only_while_their_text_is_unchanged(project, good_generated):
    from builder.translations import collect_texts, text_hash
    _write_generated(project, good_generated)
    texts = collect_texts(good_generated["questions"], good_generated["item_sets"])
    stem, opt = texts["q.01.c.001|stem"], texts["q.01.c.001|A"]
    (project / "translations").mkdir()
    (project / "translations" / "quant.json").write_text(json.dumps({
        "q.01.c.001|stem": {"h": text_hash(stem), "en": "Adjusted R2 is closest to:", "s": [[stem, "Adjusted R2 is closest to:"]], "g": {"proche": "close"}},
        "q.01.c.001|A": {"h": "stale0000000", "en": "old", "s": [], "g": {}},  # its text changed since translation
    }), encoding="utf-8")
    paths = Paths(project)
    rep = build(paths).report
    chunk = json.loads(next((paths.data / "chunks").glob("quant.*.json")).read_text(encoding="utf-8"))
    assert set(chunk["translations"]) == {"q.01.c.001|stem"}
    assert chunk["translations"]["q.01.c.001|stem"]["g"] == {"proche": "close"}
    assert any(i["code"] == "translation_stale" for i in rep["issues"])
    manifest = json.loads((paths.data / "manifest.json").read_text(encoding="utf-8"))
    assert next(t for t in manifest["topics"] if t["id"] == "quant")["counts"]["translations"] == 1
    assert opt  # options are collected too
