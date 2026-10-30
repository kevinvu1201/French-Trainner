import { formatDate, localDay } from "../core/analytics.js";
import { chunkNow, getChunk, moduleInfo, neighbours } from "../core/data.js";
import { getEvents, logEvent, useEvents } from "../core/events.js";
import { finishedModules, setFinished } from "../core/plan.js";
import { questionPool } from "../core/select.js";
import { renderMath } from "../core/katex.js";
import { href } from "../core/router.js";
import { kvSet } from "../core/store.js";
import { html, useEffect, useRef, useState } from "../lib.js";
import { Blocks, ErrorBox, FormulaCards, LearningPanel, Loading, Md } from "../ui.js";

const losLabel = (id) => id.replace(/^los\./, "Objectif ");

function useChunk(topicId) {
  const [state, setState] = useState(() => ({ chunk: chunkNow(topicId), error: null }));
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const now = chunkNow(topicId);
    if (now) return setState({ chunk: now, error: null });
    let live = true;
    setState({ chunk: null, error: null });
    getChunk(topicId).then((chunk) => live && setState({ chunk, error: null }))
      .catch((error) => live && setState({ chunk: null, error }));
    return () => { live = false; };
  }, [topicId, attempt]);
  return { ...state, retry: () => setAttempt((n) => n + 1) };
}

const AUTO_STUDY_MS = 60_000; // reading a lesson this long counts as studied for coverage (once per day), not finished

function ModuleActions({ id, topic, chunk }) {
  const events = useEvents();
  const finished = events && finishedModules(events).has(id)
    ? events.filter((e) => e.type === "study" && !e.payload.auto && e.payload.module === id).at(-1) : null;
  const practisable = questionPool(chunk, id).length;
  const moduleLos = new Set(chunk.los.filter((l) => l.modules.includes(id)).map((l) => l.id));
  const cards = chunk.formulas.filter((f) => f.los.some((l) => moduleLos.has(l))).length;
  const listening = chunk.item_sets.filter((s) => s.audio && s.modules.includes(id));
  useEffect(() => {
    const timer = setTimeout(async () => {
      const today = localDay(Date.now());
      const list = await getEvents();
      if (!list.some((e) => e.type === "study" && e.payload.module === id && localDay(e.ts) === today)) {
        logEvent("study", { module: id, topic, auto: true });
      }
    }, AUTO_STUDY_MS);
    return () => clearTimeout(timer);
  }, [id]);
  return html`<section class="card row module-actions">
    ${practisable ? html`<a class="btn primary" href=${href("practice", "drill", topic, id)}>S'entraîner sur cette leçon (${practisable})</a>` : null}
    ${!practisable && cards ? html`<a class="btn primary" href=${href("practice", "cards", topic)}>Réviser les cartes (${cards})</a>` : null}
    ${listening.length ? html`<a class="btn primary" href=${href("practice", "set", topic, id)}>🎧 ${listening.length > 1
      ? `Écouter (${listening.length} exercices)` : "Écouter l'exercice"}</a>` : null}
    ${finished ? html`<span class="small muted">✓ Terminé le ${formatDate(finished.ts)}</span>
        <button class="btn" onClick=${() => setFinished(id, topic, false)}>Annuler</button>`
      : html`<button class="btn" onClick=${() => setFinished(id, topic, true)}>Marquer comme terminé</button>`}
  </section>`;
}

const FIRST_PAINT_BLOCKS = 12; // the rest render right after the first paint so long modules open fast

function firstPaint(sections) {
  const out = [];
  let used = 0;
  for (const s of sections) {
    if (used >= FIRST_PAINT_BLOCKS) break;
    const room = FIRST_PAINT_BLOCKS - used;
    out.push(s.blocks.length > room ? { ...s, blocks: s.blocks.slice(0, room), partial: true } : s);
    used += s.blocks.length;
  }
  return out;
}

export function ModuleView({ id, los }) {
  const info = moduleInfo(id);
  const { chunk, error, retry } = useChunk(info?.topic.id);
  const root = useRef(null);
  const [complete, setComplete] = useState(null); // id of the module whose sections are all rendered

  useEffect(() => { if (info) kvSet("lastModule", id); }, [id]);
  useEffect(() => {
    if (!chunk) return;
    // After the first paint (rAF runs before it, the timeout after it), render the rest.
    let timer;
    const frame = requestAnimationFrame(() => { timer = setTimeout(() => setComplete(id), 0); });
    return () => { cancelAnimationFrame(frame); clearTimeout(timer); };
  }, [id, chunk]);
  const allRendered = complete === id;
  useEffect(() => {
    if (!chunk) return;
    const target = los && document.getElementById(los);
    if (target) target.scrollIntoView();
    else if (!los || allRendered) window.scrollTo(0, 0);
    if (allRendered) renderMath(root.current);
  }, [id, los, chunk, allRendered]);

  if (!info) return html`<p>Leçon inconnue.</p>`;
  const { topic, reading, module } = info;
  const head = html`<div class="crumbs"><a href=${href("study", topic.id)}>${topic.name}</a> › ${reading.n >= 90 ? "Thème" : `Chapitre ${reading.n}`} : ${reading.title}</div>
    <h1>${module.title}</h1>`;
  if (error) return html`<div class="reader">${head}<${ErrorBox} error=${error} retry=${retry} /></div>`;
  if (!chunk) return html`<div class="reader">${head}<${Loading} /></div>`;

  const mod = chunk.modules.find((m) => m.id === id);
  const losById = new Map(chunk.los.filter((l) => l.modules.includes(id)).map((l) => [l.id, l]));
  const quizCount = chunk.questions.filter((q) => q.module === id && q.source === "schweser").length;
  const { prev, next } = neighbours(id);

  return html`<article class="reader" ref=${root}>
    ${head}
    <div class="row" style="margin:6px 0 14px">
      <span class="chip">Leçon ${id.slice(1)}</span>
      <span class="chip">${losById.size} ${losById.size > 1 ? "objectifs" : "objectif"}</span>
      ${quizCount ? html`<span class="chip">Quiz · ${quizCount} questions</span>` : null}
      ${mod.stale_generated ? html`<span class="chip warn">Les notes datent d'une version antérieure du cours</span>` : null}
    </div>

    <nav class="card" aria-label="Objectifs">
      <div class="small muted" style="margin-bottom:4px">Dans cette leçon, vous apprenez à</div>
      <ul class="los-index">${[...losById.values()].map((l) => html`<li>
        <a href=${href("m", id, l.id)}><span class="id">${l.letter}.</span><span>${l.text}</span></a></li>`)}</ul>
    </nav>

    <${LearningPanel} learning=${chunk.learning[id]} />
    <${FormulaCards} formulas=${chunk.formulas.filter((f) => f.los.some((l) => losById.has(l)))} />

    ${(allRendered ? mod.sections : firstPaint(mod.sections)).map((s) => html`<section>
      ${s.los.map((l) => html`<div class="los-card" id=${l}>
        <div class="id">${losLabel(l)}${s.cont ? " · suite" : ""}</div><div class="text">${losById.get(l)?.text ?? ""}</div>
      </div>`)}
      <${Blocks} blocks=${s.blocks} chunk=${chunk} />
      ${s.partial || s.cont ? null : s.los.filter((l) => losById.get(l)?.key_concepts.length).map((l) => html`<details class="key-concepts">
        <summary>À retenir · ${losLabel(l)}</summary>
        <${Blocks} blocks=${losById.get(l).key_concepts} chunk=${chunk} />
      </details>`)}
    </section>`)}

    <${ModuleActions} id=${id} topic=${topic.id} chunk=${chunk} />

    <nav class="pager" aria-label="Leçons">
      ${prev ? html`<a href=${href("m", prev.module.id)}><div class="dir">‹ Précédente</div><${Md} text=${prev.module.title} /></a>` : html`<span></span>`}
      ${next ? html`<a class="next" href=${href("m", next.module.id)}><div class="dir">Suivante ›</div><${Md} text=${next.module.title} /></a>` : null}
    </nav>
  </article>`;
}
