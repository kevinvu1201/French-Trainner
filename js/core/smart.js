// Smart Session: a timed mix of (1) the highest-priority LOS, (2) spaced-repetition reviews
// that are due and (3) maintenance of strong LOS. Every item carries a one-line reason.

import { answers, coverage, pct } from "./analytics.js";
import { pickQuestions, questionPool } from "./select.js";

const DAY = 86_400_000;
const days = (ms) => Math.max(0, Math.round(ms / DAY));

export function sessionSize(minutes, scoring) {
  return Math.max(3, Math.round(minutes / scoring.smart_session.minutes_per_question));
}

/** Split n items by the configured mix; rounding leftovers go to priority. */
export function splitMix(n, mix) {
  const review = Math.round(n * mix.review);
  const maintenance = Math.round(n * mix.maintenance);
  return { priority: n - review - maintenance, review, maintenance };
}

function priorityReason(l, topicName, now) {
  const band = l.lo != null ? ` ±${Math.round(((l.hi - l.lo) / 2) * 100)}` : "";
  const seen = l.last ? `vu il y a ${days(now - l.last)} j` : "pas encore pratiqué";
  return `Priorité: ${topicName} (poids ${pct(l.weight)}), maîtrise ${pct(l.mean)}${band}, ${seen}`;
}

/**
 * Decide what to practise. Returns intents: {kind, topic, los?, qid?, reason}.
 * Questions are resolved later (resolveSession) so only the needed chunks are loaded.
 */
export function planSession(model, manifest, events, minutes) {
  const cfg = manifest.scoring.smart_session;
  const n = sessionSize(minutes, manifest.scoring);
  const want = splitMix(n, cfg.mix);
  const names = new Map(manifest.topics.map((t) => [t.id, t.name]));
  const now = model.now;
  const covered = coverage([...new Set([...model.los.values()].map((l) => l.module))], events);

  // Reviews: due question cards, most overdue (lowest recall) first. Item-set questions need
  // their case text, so they are reviewed through item sets instead.
  const due = [...model.cardMeta]
    .filter(([id, meta]) => meta.kind === "question" && !id.startsWith("set."))
    .map(([id, meta]) => ({ id, meta, st: model.status.get(id) }))
    .filter((c) => c.st.overdueDays >= 0)
    .sort((a, b) => a.st.r - b.st.r);

  const practisable = [...model.los.values()].filter((l) => l.questions > 0);
  const studied = practisable.filter((l) => l.n > 0 || covered.get(l.module) !== "untouched");
  const firstLook = practisable.filter((l) => !studied.includes(l));
  const byPriority = (a, b) => b.priority - a.priority;
  const prioPool = [...studied.sort(byPriority), ...firstLook.sort(byPriority)];
  const strong = practisable
    .filter((l) => l.n >= manifest.scoring.mastery.min_answers && l.mean >= cfg.strong_mastery)
    .sort((a, b) => (a.last ?? 0) - (b.last ?? 0));

  const reviews = due.slice(0, want.review).map((c) => ({
    kind: "review", topic: c.meta.topic, qid: c.id, los: c.meta.los[0],
    reason: `Révision: vue il y a ${days(c.st.elapsedDays * DAY)} j, probabilité de s'en souvenir ${pct(c.st.r)}`,
  }));
  const maint = strong.slice(0, want.maintenance).map((l) => ({
    kind: "maintenance", topic: l.topic, los: l.id,
    reason: `Entretien: objectif solide (maîtrise ${pct(l.mean)}), pas vu depuis ${days(now - l.last)} j`,
  }));
  // Shortfalls in reviews or maintenance are filled with more priority items.
  const prioCount = n - reviews.length - maint.length;
  const taken = new Set(maint.map((x) => x.los));
  const prio = prioPool.filter((l) => !taken.has(l.id)).slice(0, prioCount).map((l) => ({
    kind: "priority", topic: l.topic, los: l.id,
    reason: studied.includes(l) ? priorityReason(l, names.get(l.topic), now)
      : `Découverte: ${names.get(l.topic)} (poids ${pct(l.weight)}), pas encore étudié`,
  }));

  // Interleave so the session doesn't run in blocks.
  const out = [];
  const queues = [prio, reviews, maint];
  while (queues.some((q) => q.length)) for (const q of queues) if (q.length) out.push(q.shift());
  return out;
}

/** Turn intents into concrete questions. getChunk(topic) → Promise<chunk>. */
export async function resolveSession(intents, events, getChunk) {
  const ans = answers(events);
  const chunks = new Map();
  for (const topic of new Set(intents.map((i) => i.topic))) chunks.set(topic, await getChunk(topic));
  const used = new Set();
  const items = [];
  for (const it of intents) {
    const chunk = chunks.get(it.topic);
    let q = null;
    if (it.qid) q = chunk.questions.find((x) => x.id === it.qid && !used.has(x.id)) ?? null;
    if (!q && it.los) {
      const pool = questionPool(chunk).filter((x) => [x.los].flat().includes(it.los) && !used.has(x.id));
      q = pickQuestions(pool, ans, 1)[0] ?? null;
    }
    if (q) {
      used.add(q.id);
      items.push({ q, chunk, topic: it.topic, kind: it.kind, reason: it.reason });
    }
  }
  return items;
}
