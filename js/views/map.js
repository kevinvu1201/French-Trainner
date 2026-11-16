// Interactive concept map: modules as nodes (shaded by study state), typed edges as line
// styles, pan/pinch-zoom, tap for details. #/map/<module> focuses a module and highlights
// its prerequisite chain and root gap.

import { coverage, pct } from "../core/analytics.js";
import { getGraph, manifest, moduleInfo } from "../core/data.js";
import { useEvents } from "../core/events.js";
import { prerequisites, rootGap } from "../core/graph.js";
import { buildModel } from "../core/mastery.js";
import { href } from "../core/router.js";
import { html, useMemo, useRef, useState } from "../lib.js";
import { ErrorBox, Loading, useAsync } from "../ui.js";

const SIZE = 1000; // layout units; positions are 0..1 from the builder
const PAD = 60;
const EDGE = {
  requires: { label: "s'appuie sur", dash: "" },
  applies: { label: "utilisé dans", dash: "8 5" },
  contrasts_with: { label: "à comparer avec", dash: "2 4" },
  extends: { label: "approfondit", dash: "10 4 2 4" },
};
const STATE = { untouched: "Pas commencé", studied: "Étudié", practised: "Pratiqué" };

export function ConceptMap({ focus }) {
  const { value: graph, error } = useAsync(getGraph, []);
  const events = useEvents();
  const [selected, setSelected] = useState(focus ?? null);
  const [view, setView] = useState({ x: 0, y: 0, k: 1 });
  const pointers = useRef(new Map());
  const svg = useRef(null);
  const count = events?.length ?? -1;
  const model = useMemo(() => (events ? buildModel(events, manifest(), Date.now()) : null), [count]);

  if (error) return html`<${ErrorBox} error=${error} />`;
  if (graph === undefined || !events) return html`<${Loading} />`;
  if (!graph) return html`<div class="stack"><h1>Carte des notions</h1><p class="muted">La carte apparaît quand les leçons ont des liens entre elles.</p></div>`;

  const states = coverage(graph.nodes.map((n) => n.id), events);
  const P = (n) => [PAD + n.x * (SIZE - 2 * PAD), PAD + n.y * (SIZE - 2 * PAD)];
  const byId = new Map(graph.nodes.map((n) => [n.id, n]));
  const chain = selected ? prerequisites(graph, selected) : new Map();
  const gap = selected ? rootGap(graph, model, manifest(), selected) : null;
  const lit = (id) => !selected || id === selected || chain.has(id);

  // Pan with one pointer, pinch-zoom with two, wheel to zoom.
  const toLocal = (e) => {
    const r = svg.current.getBoundingClientRect();
    return [((e.clientX - r.left) / r.width) * SIZE, ((e.clientY - r.top) / r.height) * SIZE];
  };
  // No pointer capture: it would retarget taps away from the nodes.
  const down = (e) => { pointers.current.set(e.pointerId, toLocal(e)); };
  const up = (e) => pointers.current.delete(e.pointerId);
  const move = (e) => {
    const prev = pointers.current.get(e.pointerId);
    if (!prev) return;
    const cur = toLocal(e);
    if (pointers.current.size === 1) {
      setView((v) => ({ ...v, x: v.x + cur[0] - prev[0], y: v.y + cur[1] - prev[1] }));
    } else if (pointers.current.size === 2) {
      const [other] = [...pointers.current].filter(([id]) => id !== e.pointerId).map(([, p]) => p);
      const d0 = Math.hypot(prev[0] - other[0], prev[1] - other[1]);
      const d1 = Math.hypot(cur[0] - other[0], cur[1] - other[1]);
      if (d0 > 0) zoomAt((d1 / d0), [(cur[0] + other[0]) / 2, (cur[1] + other[1]) / 2]);
    }
    pointers.current.set(e.pointerId, cur);
  };
  const zoomAt = (factor, [cx, cy]) => setView((v) => {
    const k = Math.min(4, Math.max(0.5, v.k * factor));
    const f = k / v.k;
    return { k, x: cx - (cx - v.x) * f, y: cy - (cy - v.y) * f };
  });
  const wheel = (e) => { e.preventDefault(); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, toLocal(e)); };

  const sel = selected && byId.get(selected);
  const info = sel && moduleInfo(sel.id);
  const outgoing = selected ? graph.edges.filter((e) => e.from === selected) : [];
  const incoming = selected ? graph.edges.filter((e) => e.to === selected) : [];

  return html`<div class="stack">
    <div class="spread"><h1 class="h-small">Carte des notions</h1>
      <button class="btn" onClick=${() => { setView({ x: 0, y: 0, k: 1 }); setSelected(null); }}>Réinitialiser</button></div>
    <div class="legend small map-legend viz-root">
      ${Object.entries(STATE).map(([s, label]) => html`<span><i class=${`cell ${s}`}></i>${label}</span>`)}
      ${Object.values(EDGE).map((e) => html`<span><svg width="28" height="8" aria-hidden="true"><line x1="0" y1="4" x2="28" y2="4"
        class="map-edge" stroke-dasharray=${e.dash} /></svg>${e.label}</span>`)}
    </div>
    ${gap ? html`<p class="banner">Notion de base à consolider pour ${info?.module.title ?? selected} : <a href=${href("m", gap.module)}>${moduleInfo(gap.module)?.module.title}</a>
${" "}(maîtrise ${pct(gap.mean)}${gap.practised ? "" : ", pas encore pratiquée"})</p>` : null}
    <div class="viz-root map-wrap">
      <svg ref=${svg} class="map" viewBox=${`0 0 ${SIZE} ${SIZE}`} role="img" aria-label="Carte des leçons et de leurs liens"
        onPointerDown=${down} onPointerMove=${move} onPointerUp=${up} onPointerCancel=${up} onWheel=${wheel}>
        <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" class="map-arrow" /></marker></defs>
        <g transform=${`translate(${view.x} ${view.y}) scale(${view.k})`}>
          ${graph.edges.map((e) => {
            const a = byId.get(e.from), b = byId.get(e.to);
            if (!a || !b) return null;
            const [x1, y1] = P(a), [x2, y2] = P(b);
            const len = Math.hypot(x2 - x1, y2 - y1) || 1;
            const r = 16 / len;
            const on = lit(e.from) && lit(e.to);
            return html`<line class=${`map-edge ${on ? "" : "dim"} ${selected && on && e.type === "requires" ? "chain" : ""}`}
              x1=${x1 + (x2 - x1) * r} y1=${y1 + (y2 - y1) * r} x2=${x2 - (x2 - x1) * r} y2=${y2 - (y2 - y1) * r}
              stroke-dasharray=${EDGE[e.type]?.dash ?? ""} marker-end="url(#arrow)" />`;
          })}
          ${graph.nodes.map((n) => {
            const [x, y] = P(n);
            return html`<g class=${`map-node ${lit(n.id) ? "" : "dim"} ${n.id === selected ? "sel" : ""} ${gap?.module === n.id ? "gap" : ""}`}
                transform=${`translate(${x} ${y})`} onClick=${(ev) => { ev.stopPropagation(); setSelected(n.id); }}>
              <circle r="22" class="hit" /><circle r="13" class=${`cell-fill ${states.get(n.id)}`} />
              <text y="34" text-anchor="middle">${n.id.slice(1).replace(/^0/, "")}</text>
            </g>`;
          })}
        </g>
      </svg>
    </div>
    ${sel ? html`<section class="card stack">
      <div class="small muted">${info?.topic.name} · Leçon ${sel.id.slice(1)} · ${STATE[states.get(sel.id)]}</div>
      <strong>${sel.title}</strong>
      ${outgoing.length ? html`<div><div class="small muted">Cette leçon</div><ul class="plain">${outgoing.map((e) => html`<li>
        <span class="chip">${EDGE[e.type].label}</span> <a href=${href("map", e.to)} onClick=${() => setSelected(e.to)}>${byId.get(e.to)?.title}</a></li>`)}</ul></div>` : null}
      ${incoming.length ? html`<div><div class="small muted">Utilisée par</div><ul class="plain">${incoming.map((e) => html`<li>
        <a href=${href("map", e.from)} onClick=${() => setSelected(e.from)}>${byId.get(e.from)?.title}</a> <span class="chip">${EDGE[e.type].label}</span></li>`)}</ul></div>` : null}
      <div class="row"><a class="btn primary" href=${href("m", sel.id)}>Ouvrir la leçon</a>
        <a class="btn" href=${href("practice", "drill", info?.topic.id ?? "", sel.id)}>S'entraîner</a></div>
    </section>` : html`<p class="small muted">Touchez une leçon pour voir ses liens. Glissez pour déplacer, pincez ou faites défiler pour zoomer.
      Les flèches vont d'une leçon vers celles sur lesquelles elle s'appuie ou où elle est utilisée.</p>`}
  </div>`;
}
