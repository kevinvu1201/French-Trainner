import { chunkNow, getChunk, manifest, topicInfo } from "../core/data.js";
import { href } from "../core/router.js";
import { html } from "../lib.js";
import { Blocks, useAsync } from "../ui.js";

export function Topics() {
  return html`<div class="stack">
    <div class="spread"><h1>Cours</h1>${manifest().graph ? html`<a class="btn" href="#/map">Carte des notions</a>` : null}</div>
    <ul class="list">
      ${manifest().topics.map((t) => html`<li><a href=${href("study", t.id)}>
        <div class="grow"><strong>${t.name}</strong>
          <div class="sub">${t.readings.length} ${t.readings.length > 1 ? "chapitres" : "chapitre"} · ${t.counts.modules} leçons · ${t.counts.los} objectifs${t.counts.formulas ? ` · ${t.counts.formulas} cartes` : ""}</div></div>
        ${t.weight ? html`<span class="chip accent">${(t.weight * 100).toFixed(0)} %</span>` : html`<span class="chip">cartes</span>`}<span class="chev">›</span>
      </a></li>`)}
    </ul>
  </div>`;
}

export function Topic({ id }) {
  const topic = topicInfo(id);
  // The reading list comes from the manifest (instant); exam-focus notes need the chunk.
  const { value: chunk } = useAsync(() => chunkNow(id) ?? getChunk(id), [id]);
  if (!topic) return html`<p>Thème inconnu.</p>`;
  const readings = new Map((chunk?.readings ?? []).map((r) => [r.id, r]));

  return html`<div class="stack">
    <div class="crumbs"><a href="#/study">Cours</a></div>
    <h1>${topic.name}</h1>
    <p class="muted small">${topic.weight ? `${(topic.weight * 100).toFixed(0)} % de votre préparation en grammaire` : "Révision par cartes, hors score de préparation"}</p>
    ${topic.readings.map((r) => html`<section>
      <h2 class="section-title">${r.n >= 90 ? "Thème" : `Chapitre ${r.n}`}</h2>
      <h3 style="margin:0 0 8px">${r.title}</h3>
      ${readings.get(r.id)?.exam_focus?.length ? html`<details class="card" style="margin-bottom:10px">
        <summary>Pour le DELF B2</summary><div class="reader"><${Blocks} blocks=${readings.get(r.id).exam_focus} chunk=${chunk} /></div>
      </details>` : null}
      <ul class="list">
        ${r.modules.map((m) => html`<li><a href=${href("m", m.id)}>
          <div class="grow"><div>${m.title}</div><div class="sub">Leçon ${m.id.slice(1)} · ${m.los.length} ${m.los.length > 1 ? "objectifs" : "objectif"}</div></div>
          <span class="chev">›</span>
        </a></li>`)}
      </ul>
    </section>`)}
  </div>`;
}
