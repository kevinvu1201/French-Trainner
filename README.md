# Français B2: grammar and vocabulary trainer

An offline study app (PWA) for the DELF B2. It is built on the same engine as the CFA Level II trainer:
- lessons, 3-option questions with an explanation for every option, and gap-fill texts (_textes à trous_)
- FSRS spaced repetition, a mastery model per objective, and a Smart Session that picks your weak points
- a day-by-day study plan, a timed mock exam, and analytics

The interface is in French.

**Live app:** https://kevinvu1201.github.io/French-Trainner/

## Content

| Topic | Chapters of _Grammaire progressive du français_ (intermédiaire) |
|---|---|
| Le subjonctif | 51 |
| Le conditionnel et les hypothèses | 49, 50 |
| Les pronoms relatifs | 32 |
| Le discours rapporté | 35, 45 |
| Les relations logiques | 52 |
| Vocabulaire DELF B2 | 833 word cards in 7 themes (deck only, not part of the readiness score) |

All explanations, questions and texts are original. No text from the book is copied: the chapter numbers just point you to the matching pages for the book's exercises.

## On the phone (offline)

1. Open the link above in Chrome on Android (or Safari on iPhone).
2. Install it: Chrome menu → **Installer l'application** (Safari: Partager → **Sur l'écran d'accueil**).
3. Open **Réglages → Tout télécharger** once on Wi-Fi.

After that, everything works without a connection. Progress is stored on the device. Use **Réglages → Exporter / Importer**, or the optional private GitHub Gist sync, to move it between devices.

This app uses its own storage and cache names, so it doesn't interfere with the CFA app on the same domain.

## Adding or editing content

Each topic is one script in `authoring/` (for example `authoring/subjonctif.py`), using the helpers in `authoring/fr.py`:

```python
ch = b.chapter(51, "Le subjonctif", focus=[P("…")], los={"a": "Former …"})
ch.module(1, "Titre", sections=[("a", [P("…"), TABLE(...)])], chain=[...], why="…",
          look=[...], traps=[...], distractors=[...],
          questions=[Q("a", 1, "form", "Il faut que tu ___ (finir).", ("finisses", "why"), [("finis", "why"), ("finirais", "why")])],
          sets=[S("Titre", "Texte avec **(1)** ___ …", [Q, Q, Q, Q])],
          cards=[R("slug", "a", "Nom", "Recto", "Verso")])
```

To add a topic, also list its chapters in `config/topics.yaml` and give it a weight in `config/exam_weights.yaml`.

## Build, test, deploy

```bash
python -m venv --system-site-packages .venv && .venv/Scripts/pip install -e ".[dev]"
for s in subjonctif hypotheses relatifs discours logique vocabulaire; do .venv/Scripts/python authoring/$s.py; done
.venv/Scripts/python -m builder build      # dist/ + dist/report.html + dist/review/<topic>.html
.venv/Scripts/python -m builder serve      # http://127.0.0.1:8000
.venv/Scripts/python -m pytest -q          # builder tests + headless-browser tests
.venv/Scripts/python -m builder deploy     # publishes dist/ to the gh-pages branch
```

Before deploying, check that the build reports `0 errors`.
