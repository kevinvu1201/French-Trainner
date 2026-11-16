import { chunkNow, getChunk, manifest, topicInfo } from "../core/data.js";
import { useEvents } from "../core/events.js";
import { lessonProgress } from "../core/plan.js";
import { href } from "../core/router.js";
import { html } from "../lib.js";
import { Blocks, LessonBar, useAsync } from "../ui.js";

export function Topics() {
  const events = useEvents();
  const progress = events ? lessonProgress(manifest(), events) : null;
  return html`<div class="stack">
    <div class="spread"><h1>Cours</h1>${manifest().graph ? html`<a class="btn" href="#/map">Carte des notions</a>` : null}</div>
    ${progress ? html`<section class="card"><${LessonBar} done=${progress.done} total=${progress.total} label="Leçons terminées, tout le cours" big /></section>` : null}
    <ul class="list">
      ${manifest().topics.map((t) => html`<li><a href=${href("study", t.id)}>
        <div class="grow"><strong>${t.name}</strong>
          <div class="sub">${t.readings.length} ${t.readings.length > 1 ? "chapitres" : "chapitre"} · ${t.counts.modules} leçons · ${t.counts.los} objectifs${t.counts.formulas ? ` · ${t.counts.formulas} cartes` : ""}</div>
          ${progress ? html`<${LessonBar} done=${progress.topics.get(t.id).done} total=${progress.topics.get(t.id).total} label="Terminées" />` : null}</div>
        ${t.weight ? html`<span class="chip accent">${(t.weight * 100).toFixed(0)} %</span>` : html`<span class="chip">cartes</span>`}<span class="chev">›</span>
      </a></li>`)}
    </ul>
  </div>`;
}

export function Topic({ id }) {
  const topic = topicInfo(id);
  // The reading list comes from the manifest (instant); exam-focus notes need the chunk.
  const { value: chunk } = useAsync(() => chunkNow(id) ?? getChunk(id), [id]);
  const events = useEvents();
  if (!topic) return html`<p>Thème inconnu.</p>`;
  const progress = events ? lessonProgress(manifest(), events) : null;
  const tp = progress?.topics.get(id);
  const readings = new Map((chunk?.readings ?? []).map((r) => [r.id, r]));

  return html`<div class="stack">
    <div class="crumbs"><a href="#/study">Cours</a></div>
    <h1>${topic.name}</h1>
    <p class="muted small">${topic.weight ? `${(topic.weight * 100).toFixed(0)} % de votre préparation` : "Révision par cartes, hors score de préparation"}</p>
    ${tp ? html`<section class="card"><${LessonBar} done=${tp.done} total=${tp.total} big /></section>` : null}
    ${topic.readings.map((r) => html`<section>
      <h2 class="section-title">${r.n >= 90 ? "Thème" : `Chapitre ${r.n}`}</h2>
      <h3 style="margin:0 0 8px">${r.title}</h3>
      ${readings.get(r.id)?.exam_focus?.length ? html`<details class="card" style="margin-bottom:10px">
        <summary>Pour le DELF B2</summary><div class="reader"><${Blocks} blocks=${readings.get(r.id).exam_focus} chunk=${chunk} /></div>
      </details>` : null}
      <ul class="list">
        ${r.modules.map((m) => html`<li><a href=${href("m", m.id)}>
          <div class="grow"><div class=${progress?.finished.has(m.id) ? "muted" : ""}>${m.title}</div><div class="sub">Leçon ${m.id.slice(1)} · ${m.los.length} ${m.los.length > 1 ? "objectifs" : "objectif"}</div></div>
          ${progress?.finished.has(m.id) ? html`<span class="chip done-chip">✓ Terminée</span>` : null}
          <span class="chev">›</span>
        </a></li>`)}
      </ul>
    </section>`)}
  </div>`;
}
