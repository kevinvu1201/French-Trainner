// Shared components.

import { figureNow, figureURL } from "./core/data.js";
import { inline, splitFigures } from "./core/md.js";
import { html, useEffect, useState } from "./lib.js";

export function useAsync(fn, deps) {
  const [state, setState] = useState({ value: undefined, error: null, loading: true });
  useEffect(() => {
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.resolve()
      .then(fn)
      .then((value) => live && setState({ value, error: null, loading: false }))
      .catch((error) => live && setState({ value: undefined, error, loading: false }));
    return () => { live = false; };
  }, deps);
  return state;
}

/** Inline markdown; figure tokens inside the text become figures. */
export function Md({ text, chunk, tag = "span" }) {
  const parts = splitFigures(text);
  if (parts.length === 1 && typeof parts[0] === "string") {
    return html`<${tag} dangerouslySetInnerHTML=${{ __html: inline(text) }} />`;
  }
  return html`<${tag}>${parts.map((p) =>
    typeof p === "string" ? html`<span dangerouslySetInnerHTML=${{ __html: inline(p) }} />` : html`<${Fig} id=${p.fig} chunk=${chunk} inText />`)}</${tag}>`;
}

const PT_TO_PX = 4 / 3;

const GLYPH_MAX_PT = 30; // a figure this short inside a sentence is a symbol (R̄²ₐ), drawn inline

export function Fig({ id, chunk, caption, inText = false }) {
  const fig = chunk?.figures?.[id];
  const repair = chunk?.repairs?.[id];
  // Derived from the figure on every render, so a reused component never shows a stale image.
  const src = fig?.src ? figureNow(fig.src) : null;
  const [, rerender] = useState(0);
  const [failedSrc, setFailedSrc] = useState(null);
  const failed = failedSrc === fig?.src;
  useEffect(() => {
    if (!fig?.src || src) return;
    let live = true;
    figureURL(fig.src).then(() => live && rerender((n) => n + 1)).catch(() => live && setFailedSrc(fig.src));
    return () => { live = false; };
  }, [fig?.src]);

  const cap = caption ? html`<figcaption><${Md} text=${caption} /></figcaption>` : null;
  if (fig?.src && inText && fig.h <= GLYPH_MAX_PT) {
    const h = Math.round(fig.h * PT_TO_PX);
    return src ? html`<img class="fig fig-inline" src=${src} style=${`height:${h}px`} alt="" />`
               : html`<span class="fig-inline" style=${`display:inline-block;height:${h}px;width:${Math.round(fig.w * PT_TO_PX)}px`}></span>`;
  }
  if (fig?.src) {
    const w = Math.round(fig.w * PT_TO_PX);
    const style = `width:${w}px;aspect-ratio:${fig.w}/${fig.h}`;
    const body = failed
      ? html`<span class="fig-missing">Figure pas encore disponible hors ligne</span>`
      : src ? html`<img class="fig" src=${src} style=${style} alt=${caption || "Figure"} loading="lazy" decoding="async" />`
            : html`<div class="fig-ph" style=${style}></div>`;
    return html`<figure>${cap}${body}</figure>`;
  }
  if (repair?.kind === "formula") return html`<figure>${cap}<span class="tex" data-display="1" data-tex=${repair.latex}></span></figure>`;
  if (repair?.kind === "table") return html`<figure>${cap}<${Table} rows=${repair.rows} /></figure>`;
  if (repair?.kind === "text") return html`<figure>${cap}<${Md} text=${repair.md} tag="p" /></figure>`;
  if (repair?.kind === "drop" || fig?.kind === "noise") return null;
  return html`<figure>${cap}<span class="fig-missing">Figure indisponible</span></figure>`;
}

function Table({ rows }) {
  const [head, ...body] = rows;
  return html`<table><thead><tr>${head.map((c) => html`<th><${Md} text=${c} /></th>`)}</tr></thead>
    <tbody>${body.map((r) => html`<tr>${r.map((c) => html`<td><${Md} text=${c} /></td>`)}</tr>`)}</tbody></table>`;
}

function Block({ b, chunk }) {
  switch (b.t) {
    case "h": return html`<h3><${Md} text=${b.md} /></h3>`;
    case "p": return html`<${Md} tag="p" text=${b.md} chunk=${chunk} />`;
    case "ul": return html`<ul>${b.items.map((x) => html`<${Md} tag="li" text=${x} chunk=${chunk} />`)}</ul>`;
    case "ol": return html`<ol>${b.items.map((x) => html`<${Md} tag="li" text=${x} chunk=${chunk} />`)}</ol>`;
    case "note": return html`<aside class="note"><b>À noter</b><${Md} text=${b.md} /></aside>`;
    case "cap": return html`<p class="small muted"><strong><${Md} text=${b.md} /></strong></p>`;
    case "fig": return html`<${Fig} id=${b.id} chunk=${chunk} />`;
    case "table": return html`<${Table} rows=${b.rows} />`;
    case "ans": return html`<p class="ex-title">Réponse</p>`;
    default: return null;
  }
}

/** Renders a block list. A worked example runs from its title to the next heading or example. */
export function Blocks({ blocks, chunk }) {
  const out = [];
  for (let i = 0; i < blocks.length; ) {
    const b = blocks[i];
    if (b.t === "ex") {
      let j = i + 1;
      while (j < blocks.length && blocks[j].t !== "ex" && blocks[j].t !== "h") j++;
      out.push(html`<div class="example">
        <p class="ex-title">Exemple<b><${Md} text=${b.md} /></b></p>
        ${blocks.slice(i + 1, j).map((x) => html`<${Block} b=${x} chunk=${chunk} />`)}
      </div>`);
      i = j;
    } else if (b.t === "cap" && blocks[i + 1]?.t === "fig") {
      out.push(html`<${Fig} id=${blocks[i + 1].id} chunk=${chunk} caption=${b.md} />`);
      i += 2;
    } else {
      out.push(html`<${Block} b=${b} chunk=${chunk} />`);
      i++;
    }
  }
  return out;
}

const STAGE = { assumption: "Le principe", mechanism: "Le fonctionnement", result: "Ce qu'il faut savoir", interpretation: "À retenir" };
const EDGE = { requires: "S'appuie sur", applies: "Utilisé dans", contrasts_with: "À comparer avec", extends: "Pour aller plus loin" };

/** The generated learning layer for a module (the reasoning, why it matters, exam strategy). */
export function LearningPanel({ learning, moduleTitle }) {
  if (!learning) return null;
  const a = learning.exam_approach;
  return html`<section class="panel stack">
    <div class="card"><div class="small muted">Pourquoi c'est important au DELF B2</div><${Md} tag="p" text=${learning.why_it_matters} /></div>
    <details class="card" open>
      <summary>L'essentiel en 4 étapes</summary>
      <ol class="chain">${learning.logic_chain.map((s) => html`<li><div class="stage">${STAGE[s.stage]}</div><${Md} text=${s.md} /></li>`)}</ol>
    </details>
    <details class="card">
      <summary>Stratégie pour les exercices</summary>
      <p class="small muted">Regardez d'abord</p><ul>${a.look_first.map((x) => html`<${Md} tag="li" text=${x} />`)}</ul>
      <p class="small muted">Pièges fréquents</p><ul>${a.traps.map((x) => html`<${Md} tag="li" text=${x} />`)}</ul>
      <p class="small muted">Mauvaises réponses typiques</p><ul>${a.distractors.map((x) => html`<${Md} tag="li" text=${x} />`)}</ul>
    </details>
    ${learning.connections?.length ? html`<details class="card">
      <summary>Liens avec d'autres leçons</summary>
      <ul>${learning.connections.map((c) => html`<li><span class="chip accent">${EDGE[c.type]}</span>${" "}
        <a href=${"#/m/" + c.to}>${c.to}</a> — <${Md} text=${c.note} /></li>`)}</ul>
    </details>` : null}
  </section>`;
}

/** A text card's content: the rule (back), examples and the common mistake. */
export function CardBack({ card }) {
  return html`<${Md} tag="p" text=${card.back} />
    ${card.examples?.length ? html`<ul class="small">${card.examples.map((x) => html`<${Md} tag="li" text=${x} />`)}</ul>` : null}
    ${card.common_mistake ? html`<p class="small"><strong>Erreur fréquente.</strong> <${Md} text=${card.common_mistake} /></p>` : null}`;
}

/** Review cards for the LOS of a module: text cards (front/back) or formula cards (LaTeX, rendered lazily by KaTeX). */
export function FormulaCards({ formulas }) {
  if (!formulas.length) return null;
  return html`<details class="card panel">
    <summary>Cartes de révision (${formulas.length})</summary>
    ${formulas.map((f) => !f.latex ? html`<div class="formula">
      <div class="small muted"><${Md} text=${f.front} /></div>
      <${CardBack} card=${f} />
    </div>` : html`<div class="formula">
      <div class="small muted">${f.name}</div>
      <div class="tex" data-display="1" data-tex=${f.latex}></div>
      <ul class="small">${f.variables.map((v) => html`<li><span class="tex" data-tex=${v.sym}></span>: <${Md} text=${v.def} /></li>`)}</ul>
      <p class="small"><strong>Intuition.</strong> <${Md} text=${f.intuition} /></p>
      <p class="small"><strong>When to use.</strong> <${Md} text=${f.when_to_use} /></p>
      <p class="small"><strong>Common mistake.</strong> <${Md} text=${f.common_mistake} /></p>
    </div>`)}
  </details>`;
}

export function Loading({ label = "Chargement…" }) {
  return html`<p class="muted" role="status">${label}</p>`;
}

export function ErrorBox({ error, retry }) {
  const offline = !navigator.onLine;
  return html`<div class="card stack">
    <p><strong>${offline ? "Vous êtes hors ligne et ce contenu n'est pas encore téléchargé." : "Un problème est survenu pendant le chargement."}</strong></p>
    <p class="small muted">${String(error?.message ?? error)}</p>
    ${retry ? html`<button class="btn" onClick=${retry}>Réessayer</button>` : null}
  </div>`;
}

const ICONS = {
  home: "M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z",
  study: "M4 4.5A1.5 1.5 0 0 1 5.5 3H20v15H5.5A1.5 1.5 0 0 0 4 19.5zM4 19.5A1.5 1.5 0 0 0 5.5 21H20",
  practice: "M9 11l3 3 8-8M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9",
  stats: "M4 20V11M10 20V5M16 20v-6M3 20h18",
  settings: "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm7.4-3a7.4 7.4 0 0 0-.1-1.2l2-1.6-2-3.4-2.4 1a7.6 7.6 0 0 0-2-1.2L14.5 3h-5l-.4 2.6a7.6 7.6 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.6a7.4 7.4 0 0 0 0 2.4l-2 1.6 2 3.4 2.4-1a7.6 7.6 0 0 0 2 1.2l.4 2.6h5l.4-2.6a7.6 7.6 0 0 0 2-1.2l2.4 1 2-3.4-2-1.6c.1-.4.1-.8.1-1.2z",
};

export function Icon({ name }) {
  return html`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d=${ICONS[name]} /></svg>`;
}
