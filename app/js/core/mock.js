// Mock exam assembly: gap-fill texts of 4 questions, one minute per question, drawn per topic
// in proportion to its weight. A full mock is 40 questions in 40 minutes, a short one 20 in 20.

export const MOCK = { questions: 40, sessions: 1, sessionMs: 40 * 60_000 };

/**
 * Item sets available in a topic chunk: the generated item sets, plus Schweser module-quiz
 * questions that share a case (vignette) treated as an item set.
 */
export function itemSetsFor(chunk) {
  const sets = chunk.item_sets.map((s) => ({
    id: s.id, topic: chunk.topic, title: s.title, vignette: s.vignette, exhibits: s.exhibits ?? [], questions: s.questions,
  }));
  const groups = new Map();
  for (const q of chunk.questions) {
    if (q.source !== "schweser" || !q.vignette || !q.options?.length || !q.answer) continue;
    const key = `${q.module}|${q.vignette}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(q);
  }
  let i = 0;
  for (const [, qs] of groups) {
    if (qs.length < 2) continue;
    i += 1;
    sets.push({ id: `case.${qs[0].module}.${i}`, topic: chunk.topic, title: null, vignette: qs[0].vignette, exhibits: [],
                questions: qs.map((q) => ({ ...q, vignette: null })) });
  }
  return sets;
}

function shuffle(list, rng) {
  const a = [...list];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/**
 * @param setsByTopic Map topic -> item sets
 * @param topics manifest topics (id, weight)
 * @returns {sessions: set[][], plan: [{topic, target, got}]}
 */
export function buildMock(setsByTopic, topics, { questions = MOCK.questions, sessions = MOCK.sessions, rng = Math.random } = {}) {
  const totalW = topics.reduce((s, t) => s + t.weight, 0) || 1;
  const picked = [];
  const plan = [];
  for (const t of topics) {
    const target = Math.round((questions * t.weight) / totalW);
    let got = 0;
    for (const s of shuffle(setsByTopic.get(t.id) ?? [], rng)) {
      if (got >= target) break;
      picked.push(s);
      got += s.questions.length;
    }
    plan.push({ topic: t.id, target, got });
  }
  const order = shuffle(picked, rng);
  const total = order.reduce((s, x) => s + x.questions.length, 0);
  const out = Array.from({ length: sessions }, () => []);
  let acc = 0;
  for (const s of order) {
    const k = Math.min(sessions - 1, Math.floor((acc / Math.max(total, 1)) * sessions));
    out[k].push(s);
    acc += s.questions.length;
  }
  return { sessions: out.filter((x) => x.length), plan };
}

/** Score a submitted session: overall and per topic. */
export function scoreSession(sets, answers) {
  const perTopic = new Map();
  let correct = 0, n = 0;
  for (const s of sets) {
    for (const q of s.questions) {
      const ok = answers[q.id]?.choice === q.answer;
      n += 1; correct += ok ? 1 : 0;
      const t = perTopic.get(s.topic) ?? { topic: s.topic, n: 0, correct: 0 };
      t.n += 1; t.correct += ok ? 1 : 0;
      perTopic.set(s.topic, t);
    }
  }
  return { n, correct, acc: n ? correct / n : 0, perTopic: [...perTopic.values()] };
}
