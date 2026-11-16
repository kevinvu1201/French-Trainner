// Choosing what to practise next. (Phase 6 replaces this with priority + spaced repetition.)

/** Latest answer event per question id. */
export function lastAnswers(ans) {
  const last = new Map();
  for (const e of ans) {
    const prev = last.get(e.payload.qid);
    if (!prev || e.ts >= prev.ts) last.set(e.payload.qid, e);
  }
  return last;
}

/** Unseen questions first, then ones last answered wrongly, then the rest; random within each tier. */
export function pickQuestions(pool, ans, n, rng = Math.random) {
  const last = lastAnswers(ans);
  const tier = (q) => {
    const e = last.get(q.id);
    return !e ? 0 : e.payload.correct ? 2 : 1;
  };
  return pool
    .map((q) => ({ q, score: tier(q) + rng() }))
    .sort((a, b) => a.score - b.score)
    .slice(0, n)
    .map((x) => x.q);
}

/** An item set the user hasn't attempted, else the one attempted longest ago. */
export function pickItemSet(sets, ans, rng = Math.random) {
  if (!sets.length) return null;
  const lastTs = new Map();
  for (const e of ans) if (e.payload.set) lastTs.set(e.payload.set, Math.max(lastTs.get(e.payload.set) ?? 0, e.ts));
  return sets
    .map((s) => ({ s, score: (lastTs.get(s.id) ?? -1) + rng() }))
    .sort((a, b) => a.score - b.score)[0].s;
}

/** Usable questions for a topic (optionally one module), excluding item-set questions. */
export function questionPool(chunk, moduleId = null) {
  const losModules = new Map(chunk.los.map((l) => [l.id, l.modules]));
  return chunk.questions.filter((q) => {
    if (!q.options?.length || !q.answer) return false;
    if (!moduleId) return true;
    if (q.source === "schweser") return q.module === moduleId;
    return (losModules.get(q.los) ?? []).includes(moduleId);
  });
}

/** Normalised facts about a question, whichever source it comes from. */
export function questionMeta(q, chunk) {
  const los = [q.los].flat().filter(Boolean);
  const home = chunk.los.find((l) => l.id === los[0]);
  return { los, module: q.module ?? home?.module ?? null };
}
