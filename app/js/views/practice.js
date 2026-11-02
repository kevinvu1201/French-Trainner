import { CONFIDENCE, PACE_MS, answers as answerEvents, formatMs, localDay, pct } from "../core/analytics.js";
import { chunkNow, getChunk, manifest, moduleInfo, topicInfo } from "../core/data.js";
import { getEvents, logEvent } from "../core/events.js";
import { cardStatus, review } from "../core/fsrs.js";
import { confetti, feedback, floatXP } from "../core/fx.js";
import { xpFor } from "../core/game.js";
import { Ring } from "../game-ui.js";
import { LookupTip } from "../lookup.js";
import { renderMath } from "../core/katex.js";
import { href } from "../core/router.js";
import { buildModel } from "../core/mastery.js";
import { settingsFrom } from "../core/settings.js";
import { pickItemSet, pickQuestions, questionMeta, questionPool } from "../core/select.js";
import { planSession, resolveSession } from "../core/smart.js";
import { html, useEffect, useRef, useState } from "../lib.js";
import { AudioPlayer, CardBack, ErrorBox, Loading, Md, useAsync } from "../ui.js";

const DRILL_SIZE = 10;
const QTYPE = { form: "forme", conceptual: "règle", judgement: "usage", vocabulary: "vocabulaire", calculation: "calcul", listening: "compréhension" };
const LETTERS = ["A", "B", "C"];
const paragraphs = (text) => (text ?? "").split(/\n{2,}/).filter(Boolean);

function useTopicData(topicId) {
  return useAsync(async () => {
    const [chunk, events] = await Promise.all([chunkNow(topicId) ?? getChunk(topicId), getEvents()]);
    return { chunk, events };
  }, [topicId]);
}

// ---------------------------------------------------------------- home

export function PracticeHome() {
  const topics = [...manifest().topics].sort((a, b) => b.weight - a.weight);
  return html`<div class="stack">
    <h1>Exercices</h1>
    <section class="card stack smart-entry">
      <strong>Séance intelligente</strong>
      <p class="small muted">Environ 60 % de vos points faibles prioritaires (pondérés par leur importance), 25 % de révisions
        à faire aujourd'hui, 15 % d'entretien de vos points forts. Chaque question indique pourquoi elle a été choisie.</p>
      <div class="row">${[10, 20, 30].map((m) => html`<a class=${`btn ${m === 20 ? "primary" : ""}`} href=${href("practice", "smart", String(m))}>${m} min</a>`)}</div>
    </section>
    <section class="card spread">
      <div><strong>Examen blanc</strong><div class="small muted">Textes à trous chronométrés, tous les thèmes de grammaire</div></div>
      <a class="btn" href="#/practice/mock">Ouvrir</a>
    </section>
    <h2 class="section-title">Par thème</h2>
    <p class="muted small">L'entraînement montre d'abord les questions jamais vues, puis celles que vous avez ratées. Chaque réponse est enregistrée sur cet appareil.</p>
    ${topics.map((t) => html`<section class="card stack">
      <div class="spread"><strong>${t.name}</strong>${t.weight ? html`<span class="chip accent">${(t.weight * 100).toFixed(0)} %</span>` : null}</div>
      <div class="row">
        ${t.counts.questions ? html`<a class="btn" href=${href("practice", "drill", t.id)}>Questions (${t.counts.questions})</a>` : null}
        ${t.counts.item_sets ? html`<a class="btn" href=${href("practice", "set", t.id)}>${t.counts.audio_sets ? "Exercices d'écoute" : "Textes à trous"} (${t.counts.item_sets})</a>` : null}
        ${t.counts.formulas ? html`<a class="btn" href=${href("practice", "cards", t.id)}>Cartes (${t.counts.formulas})</a>` : null}
      </div>
    </section>`)}
  </div>`;
}

// ---------------------------------------------------------------- question card

export function Options({ q, chunk, value, onChange, reveal }) {
  return html`<div class="options" role="radiogroup" aria-label="Réponses">
    ${q.options.map((opt, i) => {
      const letter = LETTERS[i];
      const state = !reveal ? "" : letter === q.answer ? "right" : letter === value.choice ? "wrong" : "";
      return html`<button class=${`option ${state}`} role="radio" aria-checked=${value.choice === letter} disabled=${reveal}
          onClick=${() => onChange({ ...value, choice: letter })}>
        <span class="letter">${letter}</span><${Md} text=${opt} chunk=${chunk} tr=${`${q.id}|${letter}`} />
      </button>`;
    })}
  </div>`;
}

function Confidence({ value, onChange, disabled }) {
  return html`<div class="confidence">
    <span class="small muted">Êtes-vous sûr(e) ?</span>
    <div class="seg" role="group" aria-label="Confiance">
      ${[1, 2, 3].map((c) => html`<button aria-pressed=${value.conf === c} disabled=${disabled}
        onClick=${() => onChange({ ...value, conf: c })}>${CONFIDENCE[c]}</button>`)}
    </div>
  </div>`;
}

function Feedback({ q, chunk, choice, ms }) {
  const correct = choice === q.answer;
  const { module } = questionMeta(q, chunk);
  const info = module && moduleInfo(module);
  const prereqs = (chunk.learning[module]?.connections ?? []).filter((c) => c.type === "requires");
  return html`<div class=${`feedback ${correct ? "ok" : "bad"}`} role="status">
    <div class="spread"><strong>${correct ? "✓ Correct" : `✗ Faux : la bonne réponse est ${q.answer}`}</strong>
      ${ms != null ? html`<span class="small">${formatMs(ms)} ${ms > PACE_MS ? `· plus de ${formatMs(PACE_MS)}` : ""}</span>` : null}</div>
    ${q.explanations
      ? html`<ul class="why-list">${LETTERS.map((l) => html`<li class=${l === q.answer ? "right" : ""}><b>${l}.</b> <${Md} text=${q.explanations[l]} chunk=${chunk} tr=${`${q.id}|x${l}`} /></li>`)}</ul>`
      : html`<div class="why-list"><${Md} tag="p" text=${q.explanation} chunk=${chunk} /></div>`}
    ${!correct && info ? html`<div class="go-deeper">
      <span class="small muted">Pour comprendre</span>
      <a href=${href("m", module)}>Revoir la leçon : ${info.module.title}</a>
      ${prereqs.map((c) => moduleInfo(c.to) && html`<a href=${href("m", c.to)}>S'appuie sur : ${moduleInfo(c.to).module.title}</a>`)}
      ${prereqs.length ? html`<a href=${href("map", module)}>Remonter aux notions de base sur la carte des notions</a>` : null}
    </div>` : null}
    <${ReportProblem} q=${q} module=${module} />
  </div>`;
}

/** Log a "flag" event so wrong keys or unclear questions can be listed (Analytics) and fixed. */
function ReportProblem({ q, module }) {
  const [note, setNote] = useState("");
  const [sent, setSent] = useState(false);
  if (sent) return html`<p class="small muted">Signalé ✓ La question apparaît dans Progrès → Questions signalées.</p>`;
  const send = async () => {
    await logEvent("flag", { qid: q.id, module: module ?? null, note: note.trim() });
    setSent(true);
  };
  return html`<details class="small report">
    <summary>Signaler un problème avec cette question</summary>
    <textarea rows="2" placeholder="ex. : la bonne réponse devrait être B parce que…" value=${note} onInput=${(e) => setNote(e.target.value)}></textarea>
    <div><button class="btn" onClick=${send}>Signaler</button></div>
  </details>`;
}

export function QuestionCard({ q, chunk, value, onChange, reveal, label, ms, animate }) {
  const ref = useRef(null);
  const { los } = questionMeta(q, chunk);
  useEffect(() => { renderMath(ref.current); }, [q.id, reveal]);
  const verdict = animate && reveal && value.choice ? (value.choice === q.answer ? "is-right" : "is-wrong") : "";
  return html`<article class=${`qcard ${verdict}`} ref=${ref}>
    <div class="small muted">${label} · ${los.map((l) => l.replace(/^los\./, "objectif ")).join(", ")}
      ${q.qtype ? ` · ${QTYPE[q.qtype] ?? q.qtype}` : ""}</div>
    ${q.vignette ? html`<details class="vignette" open>
      <summary>Le texte</summary>${paragraphs(q.vignette).map((p) => html`<${Md} tag="p" text=${p} chunk=${chunk} />`)}</details>` : null}
    <${Md} tag="p" text=${q.stem} chunk=${chunk} tr=${`${q.id}|stem`} />
    <${Options} q=${q} chunk=${chunk} value=${value} onChange=${onChange} reveal=${reveal} />
    <${Confidence} value=${value} onChange=${onChange} disabled=${reveal} />
    ${reveal ? html`<${Feedback} q=${q} chunk=${chunk} choice=${value.choice} ms=${ms} />` : null}
  </article>`;
}

export async function recordAnswer(q, chunk, topic, value, ms, mode, extra = {}) {
  const { los, module } = questionMeta(q, chunk);
  await logEvent("answer", {
    qid: q.id, los, topic, module, correct: value.choice === q.answer, ms: Math.round(ms),
    confidence: value.conf, mode, choice: value.choice, ...extra,
  });
}

// ---------------------------------------------------------------- session runner (drill + smart)

/**
 * Laptop shortcuts: handler(key) runs on every keydown outside text fields and returns false when
 * it didn't use the key. Re-registered each render so it always sees the current state.
 */
function useShortcuts(handler) {
  useEffect(() => {
    const onKey = (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey || e.target.closest?.("input, textarea, select, summary, a")) return;
      if (handler(e.key) !== false) e.preventDefault();
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  });
}

/** Runs a queue of {q, chunk, topic, reason?, kind?} one question at a time. */
function Runner({ items, title, mode, again }) {
  const [i, setI] = useState(0);
  const [value, setValue] = useState({ choice: null, conf: null });
  const [revealed, setRevealed] = useState(false);
  const [results, setResults] = useState([]);
  const [combo, setCombo] = useState(0);
  const shownAt = useRef(Date.now());
  const shownItems = useRef(items);
  const actions = useRef(null);
  const submitted = useRef(false); // one answer per question, even if the auto-submit and a tap race

  // Start over when "again" brings a new queue. Not on mount: the effect runs after the first
  // paint, and resetting then would wipe an answer picked in between.
  useEffect(() => {
    if (shownItems.current === items) return;
    shownItems.current = items;
    setI(0); setResults([]); setValue({ choice: null, conf: null }); setRevealed(false); setCombo(0);
    submitted.current = false;
    shownAt.current = Date.now();
  }, [items]);
  // Picking a confidence after an answer submits at once: one tap fewer per question.
  useEffect(() => { if (value.choice && value.conf && !revealed && i < items.length) submit(); }, [value.conf]);

  if (!items.length) return html`<div class="stack"><h1>${title}</h1><p>Pas encore de questions pour cette sélection.</p>
    <a class="btn" href="#/practice">Retour aux exercices</a></div>`;
  if (i >= items.length) return html`<${Summary} results=${results} title=${title} again=${again} />`;

  const { q, chunk, topic, reason, kind } = items[i];
  async function submit() {
    if (revealed || submitted.current) return;
    submitted.current = true;
    const ms = Date.now() - shownAt.current;
    const correct = value.choice === q.answer;
    const xp = xpFor({ type: "answer", payload: { mode, correct, confidence: value.conf } });
    const streakNow = correct ? combo + 1 : 0;
    setRevealed(true);
    setCombo(streakNow);
    setResults((r) => [...r, { q, correct, ms, conf: value.conf, xp, combo: streakNow }]);
    feedback(correct ? (streakNow >= 3 ? "combo" : "right") : "wrong", streakNow);
    floatXP(actions.current, correct && streakNow >= 3 ? `+${xp} XP · ×${streakNow}` : `+${xp} XP`);
    await recordAnswer(q, chunk, topic, value, ms, mode, kind ? { smart: kind } : {});
  }
  const next = () => {
    submitted.current = false;
    setI(i + 1); setValue({ choice: null, conf: null }); setRevealed(false);
    shownAt.current = Date.now();
    window.scrollTo(0, 0);
  };
  useShortcuts((key) => {
    if (!revealed && LETTERS.includes(key.toUpperCase())) setValue((v) => ({ ...v, choice: key.toUpperCase() }));
    else if (!revealed && ["1", "2", "3"].includes(key)) setValue((v) => ({ ...v, conf: Number(key) }));
    else if (key === "Enter" && revealed) next();
    else if (key === "Enter" && value.choice && value.conf) submit();
    else return false;
  });
  return html`<div class="stack">
    <div class="spread"><h1 class="h-small">${title}</h1>
      <span class="row" style="gap:6px">${combo >= 2 ? html`<span class="combo" key=${combo}>🔥 ×${combo}</span>` : null}
        <span class="chip">${i + 1} / ${items.length}</span></span></div>
    <p class="small muted kbd-hint">Clavier : A/B/C réponse · 1/2/3 confiance · Entrée valider ou suivant</p>
    <${LookupTip} />
    <div class="progress session"><span style=${`width:${(100 * (i + (revealed ? 1 : 0))) / items.length}%`}></span></div>
    ${reason ? html`<p class="reason small"><span class=${`chip ${kind}`}>${reason.split(": ")[0]}</span> ${reason.split(": ").slice(1).join(": ")}</p>` : null}
    <${QuestionCard} key=${q.id} q=${q} chunk=${chunk} value=${value} onChange=${setValue}
      reveal=${revealed} label=${`Question ${i + 1}`} ms=${results[i]?.ms} animate />
    <div class="row sticky-actions" ref=${actions}>
      ${!revealed
        ? html`<button class="btn primary" disabled=${!value.choice || !value.conf} onClick=${submit}>
            ${!value.choice ? "Choisissez une réponse" : !value.conf ? "Indiquez votre confiance" : "Valider"}</button>`
        : html`<button class="btn primary" onClick=${next}>${i + 1 < items.length ? "Question suivante" : "Voir le bilan"}</button>`}
    </div>
  </div>`;
}

export function Drill({ topic, module }) {
  const { value: data, error } = useTopicData(topic);
  const [run, setRun] = useState(0);
  const [items, setItems] = useState(null);
  useEffect(() => {
    if (!data) return;
    const picked = pickQuestions(questionPool(data.chunk, module), answerEvents(data.events), DRILL_SIZE);
    setItems(picked.map((q) => ({ q, chunk: data.chunk, topic })));
  }, [data, module, run]);
  if (error) return html`<${ErrorBox} error=${error} />`;
  if (!data || !items) return html`<${Loading} />`;
  const title = module ? moduleInfo(module)?.module.title : topicInfo(topic)?.name;
  return html`<${Runner} items=${items} title=${title} mode="drill" again=${() => setRun((n) => n + 1)} />`;
}

export function SmartSession({ minutes }) {
  const [run, setRun] = useState(0);
  const { value: items, error } = useAsync(async () => {
    const events = await getEvents();
    const model = buildModel(events, manifest(), Date.now(), { target: settingsFrom(events).target ?? undefined });
    const intents = planSession(model, manifest(), events, Number(minutes) || 30);
    return resolveSession(intents, events, getChunk);
  }, [minutes, run]);
  if (error) return html`<${ErrorBox} error=${error} />`;
  if (!items) return html`<${Loading} label="Préparation de votre séance…" />`;
  return html`<${Runner} items=${items} title=${`Séance intelligente · ${minutes} min`} mode="smart" again=${() => setRun((n) => n + 1)} />`;
}

function useCountUp(target, ms = 900) {
  const [n, setN] = useState(0);
  useEffect(() => {
    const start = performance.now();
    let frame;
    const step = (t) => { const k = Math.min(1, (t - start) / ms); setN(Math.round(target * (1 - (1 - k) ** 3))); if (k < 1) frame = requestAnimationFrame(step); };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [target]);
  return n;
}

const verdict = (share) => share === 1 ? ["Parfait !", "Un sans-faute. Chapeau 🎩"] : share >= 0.8 ? ["Excellent !", "Vous maîtrisez bien ce point."]
  : share >= 0.6 ? ["Bien joué", "Encore un effort sur les questions ratées."] : ["On continue !", "Chaque erreur corrigée ici, c'est un point gagné le jour de l'examen."];

function Summary({ results, title, again }) {
  const right = results.filter((r) => r.correct).length;
  const avg = results.reduce((s, r) => s + r.ms, 0) / Math.max(results.length, 1);
  const sureWrong = results.filter((r) => !r.correct && r.conf === 3).length;
  const missed = results.filter((r) => !r.correct);
  const xp = results.reduce((s, r) => s + (r.xp ?? 0), 0);
  const best = Math.max(0, ...results.map((r) => r.combo ?? 0));
  const share = right / Math.max(results.length, 1);
  const shown = useCountUp(xp);
  const [head, sub] = verdict(share);
  useEffect(() => { feedback("done"); if (share >= 0.8) confetti(); }, []);
  return html`<div class="stack">
    <section class="summary-hero">
      <${Ring} value=${share} size=${132} stroke=${12} done=${share >= 0.8}><strong>${right}/${results.length}</strong><span>${pct(share)}</span></${Ring}>
      <div class="summary-head">${head}</div>
      <div class="small">${sub}</div>
      <div class="summary-xp">+${shown} XP</div>
      ${best >= 3 ? html`<div class="small">Meilleure série : 🔥 ×${best}</div>` : null}
    </section>
    <h1 class="h-small">${title}</h1>
    <div class="tiles">
      <div class="tile"><div class="k">Temps moyen</div><div class="v">${formatMs(avg)}</div><div class="sub">objectif ${formatMs(PACE_MS)}</div></div>
      <div class="tile"><div class="k">Sûr mais faux</div><div class="v">${sureWrong}</div><div class="sub">les plus dangereuses</div></div>
    </div>
    ${missed.length ? html`<section class="card"><strong>À revoir</strong><ul class="plain">${missed.map((r) => html`<li>
      <${Md} text=${r.q.stem.length > 110 ? r.q.stem.slice(0, 110) + "…" : r.q.stem} /></li>`)}</ul></section>` : null}
    <div class="row"><button class="btn primary" onClick=${again}>Une autre série</button>
      <a class="btn" href="#/practice">Retour aux exercices</a><a class="btn" href="#/stats">Voir mes progrès</a></div>
  </div>`;
}

// ---------------------------------------------------------------- item sets

export function ItemSet({ topic, module }) {
  const { value: data, error } = useTopicData(topic);
  const [run, setRun] = useState(0);
  const [set, setSet] = useState(null);
  const [values, setValues] = useState([]);
  const [done, setDone] = useState(null); // {ms}
  const startedAt = useRef(Date.now());
  const root = useRef(null);

  useEffect(() => {
    if (!data) return;
    const sets = module ? data.chunk.item_sets.filter((s) => s.modules.includes(module)) : data.chunk.item_sets;
    const picked = pickItemSet(sets, answerEvents(data.events));
    setSet(picked);
    setValues((picked?.questions ?? []).map(() => ({ choice: null, conf: null })));
    setDone(null);
    startedAt.current = Date.now();
    window.scrollTo(0, 0);
  }, [data, run, module]);
  useEffect(() => { renderMath(root.current); }, [set]);

  if (error) return html`<${ErrorBox} error=${error} />`;
  if (!data) return html`<${Loading} />`;
  if (!set) return html`<div class="stack"><h1>${topicInfo(topic)?.name}</h1><p>Pas encore d'exercice pour ce thème.</p>
    <a class="btn" href="#/practice">Retour aux exercices</a></div>`;

  const complete = values.every((v) => v.choice && v.conf);
  const submit = async () => {
    const ms = Date.now() - startedAt.current;
    setDone({ ms });
    const mode = set.audio ? "listening" : "item_set";
    const right = set.questions.filter((q, k) => values[k].choice === q.answer).length;
    const xp = set.questions.reduce((s, q, k) => s + xpFor({ type: "answer", payload: { mode, correct: values[k].choice === q.answer, confidence: values[k].conf } }), 0);
    feedback(right / set.questions.length >= 0.5 ? "done" : "wrong");
    if (right === set.questions.length) confetti();
    floatXP(root.current?.querySelector(".sticky-actions") ?? root.current, `+${xp} XP`);
    for (const [k, q] of set.questions.entries()) {
      await recordAnswer(q, data.chunk, topic, values[k], ms / set.questions.length, set.audio ? "listening" : "item_set", { set: set.id });
    }
  };
  const score = done ? set.questions.filter((q, k) => values[k].choice === q.answer).length : 0;
  const pace = PACE_MS * set.questions.length;

  return html`<div class="stack" ref=${root}>
    <div class="spread"><h1 class="h-small">${set.title ?? "Texte à trous"}</h1><span class="chip">${topicInfo(topic)?.name}</span></div>
    ${set.audio ? html`<${AudioPlayer} key=${set.id} src=${set.audio} plays=${set.plays} title=${set.title ?? "Écoute"} />` : null}
    <${LookupTip} />
    <section class="vignette-full">${paragraphs(set.vignette).map((p, i) => html`<${Md} tag="p" text=${p} chunk=${data.chunk} tr=${`${set.id}|v${i}`} />`)}
      ${(set.exhibits ?? []).map((ex) => html`<div class="exhibit"><div class="small"><strong><${Md} text=${ex.title} /></strong></div>
        <div class="table-wrap"><table><thead><tr>${ex.rows[0].map((c) => html`<th><${Md} text=${c} /></th>`)}</tr></thead>
        <tbody>${ex.rows.slice(1).map((r) => html`<tr>${r.map((c) => html`<td><${Md} text=${c} /></td>`)}</tr>`)}</tbody></table></div></div>`)}
    </section>
    ${set.questions.map((q, k) => html`<${QuestionCard} key=${q.id} q=${q} chunk=${data.chunk} value=${values[k]}
      onChange=${(v) => setValues((vals) => vals.map((old, j) => (j === k ? v : old)))} reveal=${!!done} label=${`Question ${k + 1} sur ${set.questions.length}`} animate />`)}
    ${done ? html`<div class=${`card spread set-score ${score === set.questions.length ? "perfect" : ""}`}><strong>${score === set.questions.length ? "💯 " : ""}${score} / ${set.questions.length} bonnes réponses</strong>
        ${set.audio ? null : html`<span class="small">${formatMs(done.ms)} ${done.ms > pace ? `· au-delà des ${formatMs(pace)} prévues` : `· dans les ${formatMs(pace)} prévues`}</span>`}</div>
      ${set.transcript ? html`<details class="card transcript" open>
        <summary>Transcription</summary>
        <p class="small muted">Relisez les passages qui contiennent les réponses, puis réécoutez en mode entraînement (décochez « Mode examen »).</p>
        <div class="reader">${paragraphs(set.transcript).map((p, i) => html`<${Md} tag="p" text=${p} tr=${`${set.id}|t${i}`} />`)}</div>
      </details>` : null}
      <div class="row"><button class="btn primary" onClick=${() => setRun((n) => n + 1)}>${set.audio ? "Exercice suivant" : "Texte suivant"}</button>
        <a class="btn" href="#/practice">Retour aux exercices</a></div>`
      : html`<div class="row sticky-actions"><button class="btn primary" disabled=${!complete} onClick=${submit}>
          ${complete ? "Valider le texte" : `Répondez aux ${set.questions.length} questions (avec votre confiance)`}</button></div>`}
  </div>`;
}

// ---------------------------------------------------------------- review cards

const GRADES = [[1, "Revoir"], [2, "Difficile"], [3, "Bien"], [4, "Facile"]];

/**
 * Today's queue for a deck: cards due under FSRS (lowest recall first), then cards never reviewed,
 * up to the daily allowance of new cards (counting those already started today).
 */
export function cardQueue(cards, events, now, { retention = 0.9, newPerDay = 20, extraNew = 0 } = {}) {
  const ids = new Set(cards.map((c) => c.id));
  const state = new Map();
  const firstSeen = new Map();
  for (const e of events) {
    const id = e.type === "review" ? e.payload.card : null;
    if (!ids.has(id)) continue;
    state.set(id, review(state.get(id), e.payload.grade, e.ts));
    if (!firstSeen.has(id)) firstSeen.set(id, e.ts);
  }
  const today = localDay(now);
  const newToday = [...firstSeen.values()].filter((ts) => localDay(ts) === today).length;
  const due = [];
  const fresh = [];
  for (const c of cards) {
    const st = state.get(c.id);
    if (!st) fresh.push(c);
    else {
      const s = cardStatus(st, now, retention);
      if (s.overdueDays >= 0) due.push({ c, r: s.r });
    }
  }
  due.sort((a, b) => a.r - b.r);
  const room = Math.max(0, newPerDay + extraNew - newToday);
  return { queue: [...due.map((d) => d.c), ...fresh.slice(0, room)], due: due.length, fresh: fresh.length, newToday, room };
}

export function Cards({ topic }) {
  const { value: data, error } = useTopicData(topic);
  const [extraNew, setExtraNew] = useState(0);
  const [queue, setQueue] = useState(null);
  const [stats, setStats] = useState(null);
  const [shown, setShown] = useState(false);
  const [done, setDone] = useState(0);
  const shownAt = useRef(Date.now());
  const root = useRef(null);

  useEffect(() => {
    if (!data) return;
    const settings = settingsFrom(data.events);
    const q = cardQueue(data.chunk.formulas, data.events, Date.now(), {
      retention: manifest().scoring.spaced_repetition.desired_retention, newPerDay: settings.new_cards, extraNew });
    setQueue(q.queue);
    setStats(q);
    setShown(false);
    shownAt.current = Date.now();
  }, [data, extraNew]);
  useEffect(() => { renderMath(root.current); }, [queue?.[0]?.id, shown]);

  const f = queue?.[0];
  const cardEl = useRef(null);
  const reveal = () => { feedback("flip"); setShown(true); };
  const grade = async (g) => {
    feedback(g >= 3 ? "card" : "flip");
    floatXP(cardEl.current, `+${xpFor({ type: "review", payload: { grade: g } })} XP`);
    await logEvent("review", { card: f.id, topic, los: f.los, grade: g, ms: Date.now() - shownAt.current });
    // "Revoir" brings the card back at the end of today's queue, as in Anki's relearning step.
    setQueue((q) => (g === 1 ? [...q.slice(1), f] : q.slice(1)));
    setDone((n) => n + 1);
    setShown(false);
    shownAt.current = Date.now();
  };
  // Registered on every render (before any early return), so the handler always sees the current card.
  useShortcuts((key) => {
    if (!f) return false;
    if (!shown && (key === " " || key === "Enter")) reveal();
    else if (shown && ["1", "2", "3", "4"].includes(key)) grade(Number(key));
    else return false;
  });

  if (error) return html`<${ErrorBox} error=${error} />`;
  if (!data || !queue) return html`<${Loading} />`;
  const name = topicInfo(topic)?.name;
  if (!data.chunk.formulas.length) return html`<div class="stack"><h1>${name}</h1><p>Pas de cartes pour ce thème.</p></div>`;
  if (!queue.length) {
    return html`<div class="stack">
      <h1 class="h-small">${name}</h1>
      <section class="card stack">
        <strong>${done ? `Terminé pour aujourd'hui ✓ (${done} cartes)` : "Rien à réviser pour l'instant ✓"}</strong>
        <p class="small muted">Les cartes reviennent quand vous êtes sur le point de les oublier.
          ${stats.fresh ? ` Il reste ${stats.fresh} nouvelles cartes ; vous en avez commencé ${stats.newToday} aujourd'hui.` : " Toutes les cartes ont été vues au moins une fois."}</p>
        <div class="row">
          ${stats.fresh ? html`<button class="btn primary" onClick=${() => { setExtraNew((n) => n + 10); setDone(0); }}>10 nouvelles cartes de plus</button>` : null}
          <a class="btn" href="#/practice">Retour aux exercices</a>
        </div>
      </section>
    </div>`;
  }

  const isNew = !data.events.some((e) => e.type === "review" && e.payload.card === f.id);
  return html`<div class="stack" ref=${root}>
    <div class="spread"><h1 class="h-small">${name}</h1>
      <span class="chip">${queue.length} à faire${isNew ? " · nouvelle" : ""}</span></div>
    <p class="small muted kbd-hint">Clavier : Espace pour retourner · 1 à 4 pour noter</p>
    <article class=${`card flashcard ${shown ? "flipped" : ""}`} key=${f.id} ref=${cardEl} onClick=${() => !shown && reveal()}>
      ${f.latex ? html`<div class="small muted">${f.name}</div><p><strong>Quand l'utiliser.</strong> <${Md} text=${f.when_to_use} /></p>`
        : html`${f.name !== f.front ? html`<div class="small muted">${f.name}</div>` : null}
          <h2 class="h-small"><${Md} text=${f.front} /></h2>`}
      ${shown ? (f.latex ? html`<div class="tex" data-display="1" data-tex=${f.latex}></div>
          <p class="small"><strong>Erreur fréquente.</strong> <${Md} text=${f.common_mistake} /></p>`
        : html`<hr /><${CardBack} card=${f} />`)
      : html`<p class="muted small">Répondez dans votre tête ou à voix haute, puis retournez la carte.</p>`}
    </article>
    <div class="row sticky-actions">
      ${shown ? GRADES.map(([g, label]) => html`<button class=${`btn ${g === 3 ? "primary" : ""}`} onClick=${() => grade(g)}>${label}</button>`)
              : html`<button class="btn primary" onClick=${reveal}>Voir la réponse</button>`}
    </div>
  </div>`;
}
