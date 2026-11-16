// Small, dependency-free charts. Single series in --series-1; coverage uses a validated
// two-step ordinal ramp (--ord-1 studied, --ord-2 practised). Every chart has a hover/tap
// tooltip and prints its key values as text, so nothing depends on color alone.

import { MIN_N, TARGET, formatMs, pct } from "./core/analytics.js";
import { html, useRef, useState } from "./lib.js";

function useTooltip() {
  const [tip, setTip] = useState(null); // {x, y, lines}
  const box = useRef(null);
  const show = (evt, lines) => {
    const r = box.current.getBoundingClientRect();
    const p = evt.touches?.[0] ?? evt;
    setTip({ x: p.clientX - r.left, y: p.clientY - r.top, lines });
  };
  const view = tip && html`<div class="viz-tip" role="tooltip"
      style=${`left:${Math.min(Math.max(tip.x, 70), (box.current?.clientWidth ?? 300) - 70)}px;top:${tip.y}px`}>
    ${tip.lines.map((l, i) => (i ? html`<div>${l}</div>` : html`<strong>${l}</strong>`))}</div>`;
  return { box, show, hide: () => setTip(null), view };
}

/** Horizontal bars of accuracy (0–1) with a target marker. Rows below MIN_N are muted. */
export function AccuracyBars({ rows, label = "Réussite" }) {
  const t = useTooltip();
  return html`<div class="viz-root bars" ref=${t.box} onPointerLeave=${t.hide}>
    <div class="bars-axis small muted"><span>0%</span><span style=${`left:${TARGET * 100}%`}>target ${pct(TARGET)}</span><span>100%</span></div>
    ${rows.map((r) => {
      const lines = [r.label, `${label}: ${pct(r.acc)} (${r.correct}/${r.n})`, r.medianMs != null ? `Temps médian ${formatMs(r.medianMs)}` : null].filter(Boolean);
      return html`<div class=${`bar-row ${r.n >= MIN_N ? "" : "thin"}`} onPointerMove=${(e) => t.show(e, lines)} onClick=${(e) => t.show(e, lines)}>
        <div class="bar-label"><span>${r.label}</span><span class="small muted">${r.n >= MIN_N ? pct(r.acc) : `n = ${r.n}`}</span></div>
        <div class="bar-track"><span class="bar-fill" style=${`width:${(r.acc ?? 0) * 100}%`}></span>
          <span class="bar-target" style=${`left:${TARGET * 100}%`}></span></div>
        <div class="small muted bar-n">${r.n} answered${r.n < MIN_N ? " · too few to judge" : ""}</div>
      </div>`;
    })}
    ${t.view}
  </div>`;
}

/** Readiness per topic: bar = mean mastery, whisker = credible band, tick = target. */
export function ReadinessBars({ rows, target }) {
  const t = useTooltip();
  return html`<div class="viz-root bars" ref=${t.box} onPointerLeave=${t.hide}>
    ${rows.map((r) => {
      const lines = [r.label, `Préparation ${pct(r.mean)} (probablement ${pct(r.lo)}–${pct(r.hi)})`, `${pct(r.coverage)} des objectifs pratiqués`, `Poids ${pct(r.weight)}`];
      return html`<div class="bar-row" onPointerMove=${(e) => t.show(e, lines)} onClick=${(e) => t.show(e, lines)}>
        <div class="bar-label"><span>${r.label}</span><span class="small muted">${pct(r.mean)} · ${pct(r.coverage)} practised</span></div>
        <div class="bar-track"><span class="bar-fill" style=${`width:${r.mean * 100}%`}></span>
          ${r.lo != null ? html`<span class="whisker" style=${`left:${r.lo * 100}%;width:${(r.hi - r.lo) * 100}%`}></span>` : null}
          <span class="bar-target" style=${`left:${target * 100}%`}></span></div>
      </div>`;
    })}
    ${t.view}
  </div>`;
}

const W = 320, H = 130, PAD_L = 28, PAD_B = 18, PAD_T = 10, PAD_R = 8;
const plotH = H - PAD_B - PAD_T;

/** Daily answered counts (columns) for the last N days. */
export function DailyColumns({ rows }) {
  const t = useTooltip();
  const max = Math.max(5, ...rows.map((r) => r.n));
  const step = (W - PAD_L - PAD_R) / rows.length;
  const bw = Math.min(24, step - 2);
  const y = (v) => PAD_T + plotH * (1 - v / max);
  return html`<div class="viz-root" ref=${t.box} onPointerLeave=${t.hide}>
    <svg viewBox=${`0 0 ${W} ${H}`} role="img" aria-label="Questions par jour, 30 derniers jours">
      <line class="grid" x1=${PAD_L} x2=${W - PAD_R} y1=${y(max)} y2=${y(max)} />
      <line class="grid" x1=${PAD_L} x2=${W - PAD_R} y1=${H - PAD_B} y2=${H - PAD_B} />
      <text class="axis" x=${PAD_L - 4} y=${y(max) + 4} text-anchor="end">${max}</text>
      <text class="axis" x=${PAD_L - 4} y=${H - PAD_B + 4} text-anchor="end">0</text>
      ${rows.map((r, i) => {
        const x = PAD_L + i * step + (step - bw) / 2;
        const h = (H - PAD_B) - y(r.n);
        const lines = [r.day, `${r.n} réponses`, r.n ? `${pct(r.correct / r.n)} de réussite` : "pas d'entraînement"];
        return html`<g onPointerMove=${(e) => t.show(e, lines)} onClick=${(e) => t.show(e, lines)}>
          <rect class="hit" x=${PAD_L + i * step} y="0" width=${step} height=${H - PAD_B} />
          ${r.n ? html`<path class="col" d=${roundedTop(x, y(r.n), bw, h, Math.min(4, h))} />` : null}
        </g>`;
      })}
      <text class="axis" x=${PAD_L} y=${H - 3}>${rows[0]?.day.slice(5)}</text>
      <text class="axis" x=${W - PAD_R} y=${H - 3} text-anchor="end">today</text>
    </svg>
    ${t.view}
  </div>`;
}

function roundedTop(x, y, w, h, r) {
  return `M${x},${y + h} V${y + r} Q${x},${y} ${x + r},${y} H${x + w - r} Q${x + w},${y} ${x + w},${y + r} V${y + h} Z`;
}

/** Rolling accuracy line (gaps where there are too few answers), with the target as a hairline. */
export function AccuracyLine({ rows, label = "Réussite sur 7 jours", target = TARGET }) {
  const t = useTooltip();
  const step = (W - PAD_L - PAD_R) / Math.max(rows.length - 1, 1);
  const x = (i) => PAD_L + i * step;
  const y = (v) => PAD_T + plotH * (1 - v);
  const segments = [];
  let cur = [];
  rows.forEach((r, i) => {
    if (r.acc == null) { if (cur.length) segments.push(cur); cur = []; } else cur.push([x(i), y(r.acc)]);
  });
  if (cur.length) segments.push(cur);
  const lastIdx = rows.map((r) => r.acc != null).lastIndexOf(true);
  const [hover, setHover] = useState(null);
  const move = (e) => {
    const r = t.box.current.querySelector("svg").getBoundingClientRect();
    const p = e.touches?.[0] ?? e;
    const i = Math.round(((p.clientX - r.left) * (W / r.width) - PAD_L) / step);
    const k = Math.max(0, Math.min(rows.length - 1, i));
    setHover(k);
    const row = rows[k];
    t.show(e, [row.day, row.acc == null ? `pas encore assez de réponses (${row.n})` : `${label} ${pct(row.acc)}`, `${row.n} réponses sur la période`]);
  };
  return html`<div class="viz-root" ref=${t.box} onPointerLeave=${() => { t.hide(); setHover(null); }}>
    <svg viewBox=${`0 0 ${W} ${H}`} role="img" aria-label="Réussite sur sept jours glissants" onPointerMove=${move} onClick=${move}>
      ${[0, 0.5, 1].map((v) => html`<line class="grid" x1=${PAD_L} x2=${W - PAD_R} y1=${y(v)} y2=${y(v)} /><text class="axis" x=${PAD_L - 4} y=${y(v) + 3} text-anchor="end">${v * 100}</text>`)}
      <line class="target" x1=${PAD_L} x2=${W - PAD_R} y1=${y(target)} y2=${y(target)} />
      <text class="axis target-label" x=${PAD_L - 4} y=${y(target) + 3} text-anchor="end">${Math.round(target * 100)}</text>
      ${segments.map((s) => html`<polyline class="line" points=${s.map((p) => p.join(",")).join(" ")} />`)}
      ${lastIdx >= 0 ? html`<circle class="dot" cx=${x(lastIdx)} cy=${y(rows[lastIdx].acc)} r="4" />` : null}
      ${hover != null ? html`<line class="crosshair" x1=${x(hover)} x2=${x(hover)} y1="0" y2=${H - PAD_B} />` : null}
      <rect class="hit" x="0" y="0" width=${W} height=${H} />
    </svg>
    ${t.view}
  </div>`;
}

const STATE_LABEL = { untouched: "Pas commencé", studied: "Étudié", practised: "Pratiqué" };

/** One cell per module, grouped by topic: untouched / studied / practised. */
export function CoverageGrid({ topics, states }) {
  const t = useTooltip();
  return html`<div class="viz-root coverage" ref=${t.box} onPointerLeave=${t.hide}>
    <div class="legend small">${["untouched", "studied", "practised"].map((s) => html`<span><i class=${`cell ${s}`}></i>${STATE_LABEL[s]}</span>`)}</div>
    ${topics.map((topic) => {
      const mods = topic.readings.flatMap((r) => r.modules);
      const counts = { untouched: 0, studied: 0, practised: 0 };
      mods.forEach((m) => counts[states.get(m.id)]++);
      return html`<div class="cov-row">
        <div class="cov-label small"><span>${topic.name}</span><span class="muted">${counts.practised + counts.studied}/${mods.length}</span></div>
        <div class="cov-cells">${mods.map((m) => {
          const lines = [m.title, `Leçon ${m.id.slice(1)} · ${STATE_LABEL[states.get(m.id)]}`];
          return html`<a class=${`cell ${states.get(m.id)}`} href=${`#/m/${m.id}`} aria-label=${`${m.title}: ${STATE_LABEL[states.get(m.id)]}`}
            onPointerMove=${(e) => t.show(e, lines)}></a>`;
        })}</div>
      </div>`;
    })}
    ${t.view}
  </div>`;
}
