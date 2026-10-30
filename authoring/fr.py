"""Authoring helpers for the French trainer.

One script per topic builds a Book: its chapters (readings) with modules, sections and LOS go
to content/<topic>.json (a native book, read by the builder without parsing), and each
module's learning layer, questions, gap-fill texts and cards go to generated/<topic>/<module>.json.

    b = Book("subjonctif")
    ch = b.chapter(51, "Le subjonctif", focus=[P("…")], los={"a": "Former …", "b": "…"})
    ch.module(1, "Titre", sections=[("a", [P("…"), TABLE(rows)])],
              chain=[("assumption", "…"), ("mechanism", "…"), ("result", "…")],
              why="…", look=["…"], traps=["…"], distractors=["…"],
              connections=[("m51.2", "extends", "…")],
              questions=[Q("a", 1, "form", "stem", ("right", "why"), [("wrong", "why"), ("wrong", "why")])],
              sets=[S("titre", "texte", [Q, Q, Q, Q])],
              cards=[R("slug", "a", "nom", "recto", "verso", examples=["…"], mistake="…")])
    b.write()

Q's los is a letter of the current chapter or a full id ("los.50.b"). Explanations get the
"Correct. " / "Faux. " prefix the validator checks. Each correct answer goes to the least-used
letter so far, keeping A/B/C balanced across the topic.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from builder.compile import stable_json  # noqa: E402
from builder.incremental import sha1  # noqa: E402

LETTERS = "ABC"


# ---------------------------------------------------------------- blocks

def P(md): return {"t": "p", "md": md}
def H(md): return {"t": "h", "md": md}
def NOTE(md): return {"t": "note", "md": md}
def EX(title): return {"t": "ex", "md": title}
def UL(*items): return {"t": "ul", "items": list(items)}
def TABLE(*rows): return {"t": "table", "rows": [list(r) for r in rows]}


# ---------------------------------------------------------------- items

def Q(los, diff, qtype, stem, right, wrong):
    assert len(wrong) == 2, stem
    return dict(los=los, diff=diff, qtype=qtype, stem=stem, right=right, wrong=wrong)


def S(title, vignette, questions):
    assert len(questions) == 4, title
    return dict(title=title, vignette=vignette, questions=questions)


def LQ(los, stem, options, answer, why):
    """A listening question as printed in the book: options in book order, answer letter, one reason per option."""
    assert len(options) == 3 and len(why) == 3 and answer in LETTERS, stem
    return dict(los=los, stem=stem, options=list(options), answer=answer, why=list(why))


def L(title, context, audio, plays, transcript, questions):
    """A listening set: context, audio file (in config/audio.yaml's folder), listens allowed, transcript, questions."""
    assert 1 <= len(questions) <= 12 and plays in (1, 2), title
    return dict(title=title, vignette=context, audio=audio, plays=plays, transcript=transcript, questions=questions)


def R(slug, los, name, front, back, examples=(), mistake=None):
    return dict(slug=slug, los=[los] if isinstance(los, str) else list(los), name=name, front=front,
                back=back, examples=list(examples), mistake=mistake)


# ---------------------------------------------------------------- book

class Chapter:
    def __init__(self, book: "Book", n: int, title: str, focus: list, los: dict[str, str]):
        self.book, self.n, self.title, self.focus, self.los = book, n, title, focus, los
        self.modules: list[dict] = []
        self.key_concepts: dict[str, list] = {}

    def los_id(self, l: str) -> str:
        return l if l.startswith("los.") else f"los.{self.n:02d}.{l}"

    def module(self, number, title, sections, chain, why, look, traps, distractors,
               connections=(), questions=(), sets=(), cards=(), key=None):
        mid = f"m{self.n:02d}.{number}"
        for letter, _ in sections:
            assert letter in self.los, f"{mid}: unknown LOS {letter}"
        self.modules.append({"number": number, "title": title,
                             "sections": [{"los": [l], "blocks": blocks} for l, blocks in sections], "quiz": []})
        for l, blocks in (key or {}).items():
            self.key_concepts[l] = blocks
        compiled = [{"los": [self.los_id(l)], "blocks": blocks} for l, blocks in sections]
        doc = {
            "module": mid, "source_hash": sha1(stable_json(compiled))[:12],
            "learning": {
                "logic_chain": [{"stage": s, "md": md} for s, md in chain],
                "why_it_matters": why,
                "exam_approach": {"look_first": list(look), "traps": list(traps), "distractors": list(distractors)},
            },
            "connections": [{"to": t, "type": ty, "note": note} for t, ty, note in connections],
            "questions": [self.book.build_q(q, self.los_id(q["los"])) for q in questions],
            "item_sets": [],
            "formulas": [],
        }
        for i, s in enumerate(sets, 1):
            sid = f"set.{mid}.{i:02d}"
            item = {"id": sid, "modules": [mid], "title": s["title"], "vignette": s["vignette"]}
            if "audio" in s:
                item.update(audio=s["audio"], plays=s["plays"], transcript=s["transcript"])
                item["questions"] = [_listening_q(q, self.los_id(q["los"]), f"{sid}.q{k}") for k, q in enumerate(s["questions"], 1)]
            else:
                item["questions"] = [self.book.build_q(q, self.los_id(q["los"]), f"{sid}.q{k}") for k, q in enumerate(s["questions"], 1)]
            doc["item_sets"].append(item)
        for c in cards:
            card = {"id": f"f.{self.n:02d}.{c['slug']}", "los": [self.los_id(l) for l in c["los"]], "name": c["name"],
                    "front": c["front"], "back": c["back"]}
            if c["examples"]:
                card["examples"] = c["examples"]
            if c["mistake"]:
                card["common_mistake"] = c["mistake"]
            doc["formulas"].append(card)
        self.book.generated[mid] = doc
        return mid

    def reading(self) -> dict:
        intro: dict[str, int] = {}
        for m in self.modules:
            for s in m["sections"]:
                for l in s["los"]:
                    intro.setdefault(l, m["number"])
        missing = set(self.los) - intro.keys()
        assert not missing, f"chapter {self.n}: LOS without a section: {sorted(missing)}"
        return {"number": self.n, "title": self.title, "exam_focus": self.focus,
                "los": [{"letter": l, "text": t, "module": intro[l]} for l, t in self.los.items()],
                "key_concepts": self.key_concepts, "modules": self.modules}


def _listening_q(q: dict, los_id: str, qid: str) -> dict:
    """Book order is kept (so the app matches the printed page), unlike generated questions."""
    return {
        "id": qid, "los": los_id, "difficulty": 2, "qtype": "listening", "stem": q["stem"],
        "options": q["options"], "answer": q["answer"],
        "explanations": {l: ("Correct. " if l == q["answer"] else "Faux. ") + w for l, w in zip(LETTERS, q["why"])},
    }


def _dump(doc) -> str:
    # Scripts write gaps as "___" for readability; the app's Markdown reads "_" as italics, so the
    # published text uses the dotted gap of French exercise books.
    return json.dumps(doc, ensure_ascii=False, indent=1).replace("___", "……") + "\n"


class Book:
    def __init__(self, topic: str):
        self.topic = topic
        self.chapters: list[Chapter] = []
        self.generated: dict[str, dict] = {}
        self.counter: Counter = Counter()  # questions per LOS, for ids
        self.tally: Counter = Counter()  # correct answers per letter, for balance

    def chapter(self, n, title, focus, los):
        ch = Chapter(self, n, title, focus, los)
        self.chapters.append(ch)
        return ch

    def build_q(self, q: dict, los_id: str, qid: str | None = None) -> dict:
        if qid is None:
            self.counter[los_id] += 1
            _, ch, letter = los_id.split(".")
            qid = f"q.{ch}.{letter}.{self.counter[los_id]:03d}"
        opts = [(q["right"][0], q["right"][1], True)] + [(t, w, False) for t, w in q["wrong"]]
        tie = int(hashlib.sha1(q["stem"].encode()).hexdigest(), 16)
        pos = min(range(3), key=lambda i: (self.tally[LETTERS[i]], (i - tie) % 3))
        right = opts.pop(0)
        opts.insert(pos, right)
        answer = LETTERS[pos]
        self.tally[answer] += 1
        return {
            "id": qid, "los": los_id, "difficulty": q["diff"], "qtype": q["qtype"], "stem": q["stem"],
            "options": [o[0] for o in opts], "answer": answer,
            "explanations": {LETTERS[i]: ("Correct. " if o[2] else "Faux. ") + o[1] for i, o in enumerate(opts)},
        }

    def write(self) -> None:
        content = ROOT / "content" / f"{self.topic}.json"
        content.parent.mkdir(parents=True, exist_ok=True)
        content.write_text(_dump({"readings": [c.reading() for c in self.chapters]}), encoding="utf-8")
        folder = ROOT / "generated" / self.topic
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
        for mid, doc in self.generated.items():
            (folder / f"{mid}.json").write_text(_dump(doc), encoding="utf-8")
        n_q = sum(len(d["questions"]) for d in self.generated.values())
        n_s = sum(len(d["item_sets"]) for d in self.generated.values())
        n_c = sum(len(d["formulas"]) for d in self.generated.values())
        print(f"{self.topic}: {len(self.chapters)} chapters, {len(self.generated)} modules, "
              f"{n_q} questions, {n_s} gap-fill texts, {n_c} cards; answers {dict(sorted(self.tally.items()))}")
