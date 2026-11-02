"""Pre-translate exercise text for offline tap-to-translate, with Gemini.

Collects every translatable text from generated/<topic>/*.json under a stable key:
  <qid>|stem, <qid>|A..C (options), <qid>|xA..xC (explanations),
  <set id>|v<i> (context/gap-fill paragraphs), <set id>|t<i> (transcript paragraphs)
and writes translations/<topic>.json: {key: {h, en, s: [[fr, en], ...], g: {word: meaning}}}.
Texts already translated (same hash h) are skipped, so re-running only sends what changed.

Usage:  GEMINI_API_KEY=... python authoring/translate.py [topic ...]
Model:  config/translate.yaml (model: ...). The key is read from the environment only.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from builder.translations import collect_texts, text_hash as sha1  # noqa: E402

OUT = ROOT / "translations"
BATCH = 20

PROMPT = """You help a B1 learner of French preparing the DELF B2. For each French text below, return:
- "en": a natural English translation of the whole text;
- "s": the text split into sentences, as [french sentence, english translation] pairs, keeping the French exactly as given;
- "g": glosses for the words a B1 learner may not know (anything above A2 level, plus idioms): keys are the word exactly as
  written in the text, in lowercase (for elisions like "l'avocat" use "avocat"); values give the meaning IN THIS CONTEXT and,
  when different, the dictionary form in parentheses, e.g. "strike (la grève)". Never name a tense, mood or grammatical
  category (no "subjunctive", "conditional", ...): the texts are grammar exercises and that would give answers away.
  Gaps written "……" are blanks to fill: translate them as "…".
Return a JSON object mapping each id to {"en": ..., "s": [...], "g": {...}}.

Texts:
"""


def collect(topic_dir: Path) -> dict[str, str]:
    questions, item_sets = [], []
    for f in sorted(topic_dir.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        questions += doc.get("questions", [])
        item_sets += doc.get("item_sets", [])
    return collect_texts(questions, item_sets)


def ask_gemini(batch: dict[str, str], model: str, key: str) -> dict:
    body = {
        "contents": [{"parts": [{"text": PROMPT + json.dumps(batch, ensure_ascii=False, indent=1)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    for attempt in range(6):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as res:
                data = json.loads(res.read())
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 5:
                wait = 15 * (attempt + 1)
                print(f"  Gemini {e.code}, retrying in {wait}s…")
                time.sleep(wait)
                continue
            raise SystemExit(f"Gemini error {e.code}: {e.read().decode(errors='replace')[:400]}")
        except (KeyError, json.JSONDecodeError) as e:
            if attempt < 5:
                print(f"  unreadable answer ({e}), retrying…")
                continue
            raise
    raise SystemExit("Gemini kept failing")


def translate_topic(topic: str, model: str, key: str) -> None:
    texts = collect(ROOT / "generated" / topic)
    target = OUT / f"{topic}.json"
    have = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    todo = {k: v for k, v in texts.items() if have.get(k, {}).get("h") != sha1(v)}
    out = {k: v for k, v in have.items() if k in texts}  # drop texts that no longer exist
    print(f"{topic}: {len(texts)} texts, {len(texts) - len(todo)} already translated, {len(todo)} to do")
    items = list(todo.items())
    for i in range(0, len(items), BATCH):
        batch = dict(items[i:i + BATCH])
        answer = ask_gemini(batch, model, key)
        for k, fr in batch.items():
            a = answer.get(k)
            if not isinstance(a, dict) or not a.get("en"):
                print(f"  missing translation for {k}; it will be retried next run")
                continue
            out[k] = {"h": sha1(fr), "en": a["en"], "s": [p for p in a.get("s", []) if isinstance(p, list) and len(p) == 2],
                      "g": {w.lower(): m for w, m in (a.get("g") or {}).items() if isinstance(m, str)}}
        OUT.mkdir(exist_ok=True)
        target.write_text(json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"  {min(i + BATCH, len(items))}/{len(items)}")


def main() -> None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Set GEMINI_API_KEY (free key: aistudio.google.com → Get API key).")
    model = (yaml.safe_load((ROOT / "config" / "translate.yaml").read_text(encoding="utf-8")) or {}).get("model", "gemini-2.5-flash")
    topics = sys.argv[1:] or sorted(p.name for p in (ROOT / "generated").iterdir() if p.is_dir() and p.name != "vocabulaire")
    for topic in topics:
        translate_topic(topic, model, key)


if __name__ == "__main__":
    main()
