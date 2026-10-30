"""Validation report: dist/report.json (machine) and dist/report.html (human)."""

from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from typing import Any

from .config import Config, Paths


def reading_rows(books: list[dict[str, Any]], cfg: Config) -> list[dict[str, Any]]:
    rows = []
    for b in books:
        for r in b["readings"]:
            topic = cfg.topic_for_reading(r["number"])
            marked = {l for m in r["modules"] for s in m["sections"] for l in s["los"]}
            quiz = [q for m in r["modules"] for q in m["quiz"]]
            rows.append({
                "book": b["book"], "reading": r["number"], "title": r["title"],
                "topic": topic.id if topic else None, "modules": len(r["modules"]),
                "los": len(r["los"]), "los_marked": len(marked & {l["letter"] for l in r["los"]}),
                "key_concepts": len(r["key_concepts"]),
                "examples": sum(1 for m in r["modules"] for s in m["sections"] for bl in s["blocks"] if bl["t"] == "ex"),
                "quiz": len(quiz), "quiz_answered": sum(1 for q in quiz if q["answer"]),
                "quiz_usable": sum(1 for q in quiz if q["answer"] and q["options"]),
            })
    return sorted(rows, key=lambda r: r["reading"])


def build_report(books: list[dict[str, Any]], compile_issues: list[dict[str, Any]], validation_issues: list[dict[str, Any]],
                 coverage: dict[str, Any], manifest: dict[str, Any], cfg: Config,
                 incremental: dict[str, list[str]]) -> dict[str, Any]:
    issues = []
    for b in books:
        for i in b["issues"]:
            issues.append({**i, "where": b["book"]})
    issues += compile_issues + validation_issues
    guessed: Counter[str] = Counter()
    for b in books:
        guessed.update(b["ligatures"]["guessed"])
    rows = reading_rows(books, cfg)
    return {
        "built_at": manifest["built_at"],
        "content_version": manifest["content_version"],
        "weights_verified": cfg.weights_verified,
        "summary": {
            "books": len(books),
            "readings": len(rows),
            "modules": sum(r["modules"] for r in rows),
            "los": sum(r["los"] for r in rows),
            "los_with_body_marker": sum(r["los_marked"] for r in rows),
            "examples": sum(r["examples"] for r in rows),
            "schweser_questions": sum(r["quiz"] for r in rows),
            "schweser_usable": sum(r["quiz_usable"] for r in rows),
            "figures": sum(t["figures"] for t in coverage["topics"].values()),
            "figures_with_image": sum(t["figures_with_image"] for t in coverage["topics"].values()),
            "figures_repaired": sum(t["figures_repaired"] for t in coverage["topics"].values()),
            "ligatures_fixed": sum(b["ligatures"]["fixed"] for b in books),
            "ligatures_guessed": sum(guessed.values()),
            "errors": sum(1 for i in issues if i["level"] == "error"),
            "warnings": sum(1 for i in issues if i["level"] == "warning"),
        },
        "incremental": incremental,
        "topics": [{"id": t["id"], "name": t["name"], "weight": t["weight"], "range": t["weight_range"],
                    "bytes": t["bytes"], "audio_sets": t["counts"].get("audio_sets", 0),
                    **coverage["topics"][t["id"]]} for t in manifest["topics"]],
        "readings": rows,
        "issues": issues,
        "ligature_guesses": [{"guess": k, "count": n} for k, n in guessed.most_common()],
    }


def write_report(report: dict[str, Any], paths: Paths) -> None:
    paths.dist.mkdir(parents=True, exist_ok=True)
    (paths.dist / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    (paths.dist / "report.html").write_text(render_html(report), encoding="utf-8")


def _e(x: Any) -> str:
    return html.escape(str(x))


def _loc(issue: dict[str, Any]) -> str:
    """'Book 1.pdf p.23' for PDFs (line = page), 'Book 1.md:812' for Markdown."""
    where, line = issue.get("where") or "", issue.get("line")
    if not line:
        return where
    return f"{where} p.{line}" if where.endswith(".pdf") else f"{where}:{line}"


def render_html(rep: dict[str, Any]) -> str:
    s = rep["summary"]
    status = "fail" if s["errors"] else ("warn" if s["warnings"] else "ok")
    status_text = {"fail": f"{s['errors']} errors", "warn": "No errors", "ok": "Clean"}[status]

    cards = [
        ("Readings", s["readings"], "42 expected"),
        ("Modules", s["modules"], ""),
        ("LOS", s["los"], f"{s['los_with_body_marker']} with a body marker"),
        ("Worked examples", s["examples"], ""),
        ("Schweser quiz questions", s["schweser_questions"], f"{s['schweser_usable']} usable (options + answer)"),
        ("Figures", s["figures"], f"{s['figures_with_image']} original images, {s['figures_repaired']} rebuilt"),
        ("Ligatures fixed", s["ligatures_fixed"], f"{s['ligatures_guessed']} guessed (Markdown sources only)"),
        ("Warnings", s["warnings"], ""),
    ]
    card_html = "".join(f'<div class="card"><div class="k">{_e(k)}</div><div class="v">{_e(v)}</div><div class="sub">{_e(sub)}</div></div>'
                        for k, v, sub in cards)

    weight_banner = "" if rep["weights_verified"] else (
        '<p class="banner">Topic weights in <code>config/exam_weights.yaml</code> are <b>unverified</b>. '
        "Check them against CFA Institute's Level II exam page, then set <code>verified: true</code>.</p>")

    trows = "".join(
        f"<tr><td>{_e(t['name'])}</td><td class=n>{t['weight']*100:.1f}%</td><td class=n>{t['range'][0]:g}–{t['range'][1]:g}%</td>"
        f"<td class=n>{t['modules']}</td><td class=n>{t['los']}</td><td class=n>{t['schweser_questions']}</td>"
        f"<td class=n>{t['modules_with_learning']}/{t['modules']}</td><td class=n>{t['los_with_min_questions']}/{t['los']}</td>"
        f"<td class=n>{t['modules_with_min_item_sets']}/{t['modules']}</td>"
        f"<td class=n>{t['figures_repaired']}/{t['figures']}</td><td class=n>{t['bytes']/1024:.0f} KB</td></tr>"
        for t in rep["topics"])

    rrows = "".join(
        f"<tr><td class=n>{r['reading']}</td><td>{_e(r['title'])}</td><td>{_e(r['topic'] or '—')}</td>"
        f"<td class=n>{r['modules']}</td><td class=n>{r['los']}</td>"
        f"<td class=n{'' if r['los_marked'] == r['los'] else ' data-bad'}>{r['los_marked']}</td>"
        f"<td class=n>{r['key_concepts']}</td><td class=n>{r['examples']}</td>"
        f"<td class=n>{r['quiz']}</td><td class=n{'' if r['quiz_usable'] == r['quiz'] else ' data-bad'}>{r['quiz_usable']}</td></tr>"
        for r in rep["readings"])

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for i in rep["issues"]:
        groups[(i["level"], i["code"])].append(i)
    order = {"error": 0, "warning": 1, "info": 2}
    issue_html = ""
    for (level, code), items in sorted(groups.items(), key=lambda kv: (order.get(kv[0][0], 3), kv[0][1])):
        lis = "".join(f"<li><code>{_e(_loc(i))}</code> {_e(i['msg'])}</li>" for i in items[:300])
        more = f"<li>… {len(items) - 300} more in report.json</li>" if len(items) > 300 else ""
        issue_html += (f'<details{" open" if level == "error" else ""}><summary><span class="lvl {level}">{level}</span> '
                       f"<b>{_e(code)}</b> <span class=muted>({len(items)})</span></summary><ul>{lis}{more}</ul></details>")
    if not issue_html:
        issue_html = "<p class=muted>No issues.</p>"

    lig = "".join(f"<tr><td><code>{_e(g['guess'])}</code></td><td class=n>{g['count']}</td></tr>" for g in rep["ligature_guesses"])
    inc = rep["incremental"]

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Report</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e4e1d8;--card:#fff;--accent:#2f5d8a;--bad:#b3261e;--badbg:#fbe9e7;--warn:#8a5a00;--warnbg:#fff4d6;--ok:#2e6b3a;--okbg:#e5f3e8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#151514;--fg:#ecebe6;--muted:#a3a19a;--line:#2e2d2a;--card:#1d1d1b;--accent:#8db7e0;--bad:#f2b8b5;--badbg:#3b1d1b;--warn:#f0c86a;--warnbg:#3a2f12;--ok:#9fd3a8;--okbg:#17301c}}}}
:root[data-theme=dark]{{--bg:#151514;--fg:#ecebe6;--muted:#a3a19a;--line:#2e2d2a;--card:#1d1d1b;--accent:#8db7e0;--bad:#f2b8b5;--badbg:#3b1d1b;--warn:#f0c86a;--warnbg:#3a2f12;--ok:#9fd3a8;--okbg:#17301c}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 64px}}
h1{{font-size:1.6rem;margin:0 0 4px}} h2{{font-size:1.15rem;margin:36px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
.muted{{color:var(--muted)}} code{{font:12.5px ui-monospace,Consolas,monospace}}
.status{{display:inline-block;padding:2px 10px;border-radius:99px;font-weight:600;font-size:.85rem}}
.status.ok{{background:var(--okbg);color:var(--ok)}} .status.warn{{background:var(--warnbg);color:var(--warn)}} .status.fail{{background:var(--badbg);color:var(--bad)}}
.banner{{background:var(--warnbg);color:var(--warn);padding:10px 14px;border-radius:8px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.card .k{{color:var(--muted);font-size:.8rem}} .card .v{{font-size:1.5rem;font-weight:650;font-variant-numeric:tabular-nums}} .card .sub{{color:var(--muted);font-size:.78rem}}
.scroll{{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}}
table{{border-collapse:collapse;width:100%;font-size:.88rem}}
th,td{{padding:6px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}}
th{{color:var(--muted);font-weight:600;font-size:.78rem;position:sticky;top:0;background:var(--card)}}
td.n,th.n{{text-align:right;font-variant-numeric:tabular-nums}}
td[data-bad]{{color:var(--bad);font-weight:600}}
details{{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:6px 0;padding:6px 12px}}
summary{{cursor:pointer}} details ul{{margin:8px 0;padding-left:18px;font-size:.88rem}} details li{{margin:3px 0}}
.lvl{{font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;padding:1px 6px;border-radius:4px}}
.lvl.error{{background:var(--badbg);color:var(--bad)}} .lvl.warning{{background:var(--warnbg);color:var(--warn)}} .lvl.info{{background:var(--line);color:var(--muted)}}
</style></head><body><main>
<h1>Build report</h1>
<p class=muted>Built {_e(rep['built_at'])} · content {_e(rep['content_version'])} · <span class="status {status}">{status_text}</span></p>
{weight_banner}
<div class=cards>{card_html}</div>
<p class=muted>Incremental: re-parsed {_e(', '.join(inc['reparsed']) or 'none')}; cached {_e(', '.join(inc['cached']) or 'none')}.
Chunks written: {_e(', '.join(inc['written']) or 'none')}; unchanged: {_e(', '.join(inc['unchanged']) or 'none')}.</p>

<h2>Topics</h2>
<div class=scroll><table><thead><tr><th>Topic</th><th class=n>Weight</th><th class=n>Range</th><th class=n>Modules</th><th class=n>LOS</th>
<th class=n>Schweser Qs</th><th class=n>Learning</th><th class=n>LOS ≥5 Qs</th><th class=n>Mods ≥2 sets</th><th class=n>Figs repaired</th><th class=n>Chunk</th></tr></thead>
<tbody>{trows}</tbody></table></div>

<h2>Readings</h2>
<p class=muted>Red: some LOS have no body marker (module was inferred), or some quiz questions are unusable.</p>
<div class=scroll><table><thead><tr><th class=n>#</th><th>Reading</th><th>Topic</th><th class=n>Modules</th><th class=n>LOS</th><th class=n>Marked</th>
<th class=n>Key concepts</th><th class=n>Examples</th><th class=n>Quiz</th><th class=n>Usable</th></tr></thead><tbody>{rrows}</tbody></table></div>

<h2>Issues</h2>
{issue_html}

<h2>Guessed ligature repairs ({len(rep['ligature_guesses'])})</h2>
<p class=muted>Words with a broken ligature that didn't match a known word. Add wrong ones to <code>config/ligature_overrides.yaml</code>.</p>
<details><summary>Show list</summary><div class=scroll><table><thead><tr><th>damaged → chosen</th><th class=n>count</th></tr></thead><tbody>{lig}</tbody></table></div></details>
</main></body></html>
"""
