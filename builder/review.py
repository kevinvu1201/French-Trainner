"""Human review pages for the generated learning layer: dist/review/<topic>.html.

Local only (the encrypted site never includes them). Renders every module's
learning notes, formula cards, single questions and item sets with answers and
explanations, so a batch can be checked before more topics are generated.
"""

from __future__ import annotations

import html
import re
from typing import Any

from .config import Paths

_FIG = re.compile(r"\[\[(fig\.[0-9a-f]{10})\]\]")


def inline(md: str | None) -> str:
    """Python twin of app/js/core/md.js: escape, then allow the content's inline markup."""
    math: list[str] = []

    def park(display: bool):
        def sub(m: re.Match[str]) -> str:
            attr = ' data-display="1"' if display else ""
            math.append(f'<span class="tex"{attr} data-tex="{m.group(1)}"></span>')
            return f"\x00{len(math) - 1}\x00"
        return sub

    s = html.escape(md or "", quote=True)
    s = re.sub(r"\\\[([\s\S]+?)\\\]", park(True), s)
    s = re.sub(r"\\\(([\s\S]+?)\\\)", park(False), s)
    s = re.sub(r"&lt;(sup|sub)&gt;([\s\S]*?)&lt;/\1&gt;", r"<\1>\2</\1>", s)
    s = re.sub(r"\*\*(?=\S)([\s\S]*?\S)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(^|[^\w*])_(?=\S)([^_]*?\S)_(?!\w)", r"\1<em>\2</em>", s)
    s = _FIG.sub(r'<span class="chip">[figure \1]</span>', s)
    return re.sub(r"\x00(\d+)\x00", lambda m: math[int(m.group(1))], s).replace("\n", "<br>")


def _tex(latex: str) -> str:
    return f'<div class="tex" data-display="1" data-tex="{html.escape(latex, quote=True)}"></div>'


def _table(rows: list[list[str]]) -> str:
    head, *body = rows
    return ("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")


def _question(q: dict[str, Any], number: str) -> str:
    opts = "".join(
        f'<li class="{"right" if letter == q["answer"] else ""}"><b>{letter}.</b> {inline(opt)}'
        f'<div class="why">{inline(q["explanations"][letter])}</div></li>'
        for letter, opt in zip("ABC", q["options"]))
    calc = (f'<div class="small muted">calc check: <code>{html.escape(q["calc"]["expr"])}</code></div>'
            if q.get("calc") else "")
    return (f'<div class="q"><div class="meta">{number} · <code>{q["id"]}</code> · {q["los"].replace("los.", "LOS ")} · '
            f'{q["qtype"]} · difficulty {q["difficulty"]}</div><p>{inline(q["stem"])}</p><ol class="opts">{opts}</ol>{calc}</div>')


def _card(f: dict[str, Any]) -> str:
    """A formula card (LaTeX) or a text card (front/back)."""
    head = f'<div class="card"><b>{inline(f["name"])}</b> <span class="small muted">{", ".join(l.replace("los.", "LOS ") for l in f["los"])}</span>'
    if "latex" not in f:
        examples = "".join(f"<li>{inline(x)}</li>" for x in f.get("examples", []))
        mistake = f'<p><b>Common mistake.</b> {inline(f["common_mistake"])}</p>' if f.get("common_mistake") else ""
        return (head + f'<p><b>Front.</b> {inline(f["front"])}</p><p><b>Back.</b> {inline(f["back"])}</p>'
                + (f'<ul class="small">{examples}</ul>' if examples else "") + mistake + "</div>")
    return (head + f'{_tex(f["latex"])}<ul class="small">'
            + "".join(f'<li><span class="tex" data-tex="{html.escape(v["sym"], quote=True)}"></span>: {inline(v["def"])}</li>' for v in f["variables"])
            + f'</ul><p><b>Intuition.</b> {inline(f["intuition"])}</p><p><b>When to use.</b> {inline(f["when_to_use"])}</p>'
              f'<p><b>Common mistake.</b> {inline(f["common_mistake"])}</p></div>')


def render_topic(chunk: dict[str, Any], topic_name: str) -> str:
    los_text = {l["id"]: l["text"] for l in chunk["los"]}
    parts = []
    n_q = n_sets = 0
    for mod in chunk["modules"]:
        learning = chunk["learning"].get(mod["id"])
        if not learning:
            continue
        mod_los = [l for l in chunk["los"] if mod["id"] in l["modules"]]
        a = learning["exam_approach"]
        chain = "".join(f'<li><span class="stage">{s["stage"]}</span> {inline(s["md"])}</li>' for s in learning["logic_chain"])
        conns = "".join(f'<li><span class="chip">{c["type"].replace("_", " ")}</span> <code>{c["to"]}</code> {inline(c["note"])}</li>'
                        for c in learning.get("connections", []))
        formulas = "".join(_card(f) for f in chunk["formulas"] if set(f["los"]) & {l["id"] for l in mod_los})
        singles = [q for q in chunk["questions"] if q.get("source") != "schweser" and q["los"] in {l["id"] for l in mod_los}
                   and not q["id"].startswith("set.")]
        sets = [s for s in chunk["item_sets"] if mod["id"] in s["modules"] and s["id"].startswith(f"set.{mod['id']}.")]
        n_q += len(singles)
        n_sets += len(sets)
        qs = "".join(_question(q, f"Q{i}") for i, q in enumerate(singles, 1))
        sets_html = "".join(
            f'<div class="set"><h4>Item set: {inline(s.get("title", s["id"]))} <code>{s["id"]}</code></h4>'
            f'<div class="vignette">{inline(s["vignette"])}</div>'
            + "".join(f'<div class="exhibit"><b>{inline(e["title"])}</b>{_table(e["rows"])}</div>' for e in s.get("exhibits", []))
            + "".join(_question(q, f"{s['id'].split('.')[-1]}-Q{i}") for i, q in enumerate(s["questions"], 1)) + "</div>"
            for s in sets)
        parts.append(f"""<section id="{mod['id']}">
<h2>{mod['id']} · {inline(mod['title'])}</h2>
<ul class="los">{''.join(f'<li><b>{l["id"].replace("los.", "LOS ")}</b> {inline(l["text"])}</li>' for l in mod_los)}</ul>
<h3>Why it matters</h3><p>{inline(learning['why_it_matters'])}</p>
<h3>Logic chain</h3><ol class="chain">{chain}</ol>
<h3>Exam approach</h3><div class="grid3">
<div><b>Look at first</b><ul>{''.join(f'<li>{inline(x)}</li>' for x in a['look_first'])}</ul></div>
<div><b>Traps</b><ul>{''.join(f'<li>{inline(x)}</li>' for x in a['traps'])}</ul></div>
<div><b>Distractors</b><ul>{''.join(f'<li>{inline(x)}</li>' for x in a['distractors'])}</ul></div></div>
<h3>Connections</h3><ul>{conns}</ul>
<h3>Formula cards</h3>{formulas or '<p class="muted">None for this module.</p>'}
<h3>Questions ({len(singles)})</h3>{qs}
<h3>Item sets ({len(sets)})</h3>{sets_html}
</section>""")
    toc = "".join(f'<a href="#{m["id"]}">{m["id"]}</a>' for m in chunk["modules"] if m["id"] in chunk["learning"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Review: {html.escape(topic_name)}</title>
<link rel="stylesheet" href="../vendor/katex/katex.min.css">
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e4e1d8;--card:#fff;--accent:#2f5d8a;--soft:#e6eef6;--ok:#2e6b3a;--oksoft:#e5f3e8}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#151514;--fg:#ecebe6;--muted:#a3a19a;--line:#34332f;--card:#1d1d1b;--accent:#8db7e0;--soft:#1f2d3b;--ok:#9fd3a8;--oksoft:#17301c}}}}
:root[data-theme=dark]{{--bg:#151514;--fg:#ecebe6;--muted:#a3a19a;--line:#34332f;--card:#1d1d1b;--accent:#8db7e0;--soft:#1f2d3b;--ok:#9fd3a8;--oksoft:#17301c}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;overflow-wrap:break-word}}
main{{max-width:900px;margin:0 auto;padding:24px 16px 80px}} h1{{margin:0 0 4px}} h2{{margin:48px 0 8px;padding-top:12px;border-top:2px solid var(--accent)}}
h3{{margin:24px 0 8px;font-size:1rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}} code{{font:12.5px ui-monospace,Consolas,monospace}}
.muted{{color:var(--muted)}} .small{{font-size:.85rem}} .toc{{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}} .toc a{{padding:2px 8px;border:1px solid var(--line);border-radius:6px;text-decoration:none;color:var(--accent)}}
.chip{{display:inline-block;padding:0 7px;border-radius:99px;background:var(--soft);color:var(--accent);font-size:.75rem}}
.card,.q,.set{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}}
.set{{border-color:var(--accent)}} .vignette{{background:var(--soft);padding:10px 12px;border-radius:8px}} .exhibit{{margin:10px 0;overflow-x:auto}}
table{{border-collapse:collapse;font-size:.9rem}} td,th{{border:1px solid var(--line);padding:3px 8px}}
.meta{{font-size:.78rem;color:var(--muted)}} .opts{{list-style:none;padding:0;margin:6px 0}} .opts li{{padding:6px 10px;border-radius:8px;margin:4px 0;border:1px solid var(--line)}}
.opts li.right{{background:var(--oksoft);border-color:var(--ok)}} .why{{font-size:.88rem;color:var(--muted);margin-top:2px}} .right .why{{color:var(--ok)}}
.chain .stage{{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);margin-right:6px}}
.grid3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}} .los{{padding-left:18px}} .katex-display{{overflow-x:auto}}
</style></head><body><main>
<h1>Review: {html.escape(topic_name)}</h1>
<p class="muted">{len(parts)} modules · {n_q} single questions · {n_sets} item sets ({n_sets * 4} questions). Correct options are highlighted; each option shows its explanation.</p>
<div class="toc">{toc}</div>
{''.join(parts)}
</main>
<script src="../vendor/katex/katex.min.js"></script>
<script>document.querySelectorAll('.tex').forEach(el => {{ try {{ katex.render(el.dataset.tex, el, {{displayMode: el.dataset.display === '1', throwOnError: false}}); }} catch (e) {{}} }});</script>
</body></html>"""


def write_reviews(chunks: dict[str, dict[str, Any]], names: dict[str, str], paths: Paths) -> list[str]:
    out_dir = paths.dist / "review"
    written = []
    for topic, chunk in chunks.items():
        target = out_dir / f"{topic}.html"
        if not chunk["learning"]:
            target.unlink(missing_ok=True)
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(render_topic(chunk, names[topic]), encoding="utf-8")
        written.append(topic)
    return written
