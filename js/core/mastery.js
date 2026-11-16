// The knowledge model, rebuilt from the event log: mastery per LOS (recency-weighted Beta
// posterior with a credible interval), FSRS memory state per card, priority per LOS and
// readiness per topic. All parameters come from manifest.scoring (config/priority.yaml).

import { cardStatus, gradeAnswer, review } from "./fsrs.js";
import { betaInterval } from "./stats-math.js";

const DAY = 86_400_000;
const Z_FOR_LEVEL = { 0.8: 1.2816, 0.9: 1.6449, 0.95: 1.96, 0.99: 2.5758 }; // two-sided normal quantiles

/** Every LOS with its topic, first module and exam weight, from the manifest. */
export function losIndex(manifest) {
  const index = new Map();
  for (const t of manifest.topics) {
    for (const r of t.readings) {
      for (const m of r.modules) {
        for (const l of m.los) {
          if (!index.has(l)) index.set(l, { id: l, topic: t.id, module: m.id, weight: t.weight,
            questions: manifest.los_questions?.[l] ?? 0 });
        }
      }
    }
  }
  return index;
}

/**
 * @param events  sorted event log
 * @param opts.ci false skips credible intervals (fast path for trend lines)
 * @param opts.meansOnly skips FSRS and priority (readiness trend needs only mastery means)
 * @param opts.target readiness target override (Settings)
 */
export function buildModel(events, manifest, now = Date.now(), opts = {}) {
  const cfg = manifest.scoring;
  const m = cfg.mastery;
  const weightOf = (ts) => 0.5 ** ((now - ts) / DAY / m.half_life_days);
  const credit = (p) => (p.correct ? (p.confidence === 1 ? m.guess_credit : 1) : 0);

  const topicAcc = new Map(); // topic -> {s, f}
  const losAcc = new Map(); // los -> {s, f, n, last}
  const cards = new Map(); // card id -> FSRS state
  const cardMeta = new Map(); // card id -> {kind, topic, los, module}
  const losCards = new Map(); // los -> Set(card id)

  for (const e of events) {
    if (e.ts > now) break;
    const p = e.payload;
    if (e.type === "answer") {
      const w = weightOf(e.ts);
      const c = credit(p);
      const t = topicAcc.get(p.topic) ?? { s: 0, f: 0 };
      t.s += w * c; t.f += w * (1 - c);
      topicAcc.set(p.topic, t);
      for (const l of p.los ?? []) {
        const a = losAcc.get(l) ?? { s: 0, f: 0, n: 0, last: 0 };
        a.s += w * c; a.f += w * (1 - c); a.n += 1; a.last = Math.max(a.last, e.ts);
        losAcc.set(l, a);
        if (!losCards.has(l)) losCards.set(l, new Set());
        losCards.get(l).add(p.qid);
      }
      if (opts.meansOnly) continue;
      cards.set(p.qid, review(cards.get(p.qid), gradeAnswer(p, cfg.spaced_repetition), e.ts));
      cardMeta.set(p.qid, { kind: "question", topic: p.topic, los: p.los ?? [], module: p.module });
    } else if (e.type === "review" && p.card && !opts.meansOnly) {
      cards.set(p.card, review(cards.get(p.card), p.grade, e.ts));
      cardMeta.set(p.card, { kind: "formula", topic: p.topic, los: p.los ?? [] });
    }
  }

  const retention = cfg.spaced_repetition.desired_retention;
  const status = new Map([...cards].map(([id, c]) => [id, cardStatus(c, now, retention)]));
  const ciCache = new Map();
  const interval = (a, b) => {
    if (opts.ci === false) return [null, null];
    const key = `${a.toFixed(4)}|${b.toFixed(4)}`;
    if (!ciCache.has(key)) ciCache.set(key, betaInterval(a, b, m.interval));
    return ciCache.get(key);
  };

  const los = new Map();
  for (const info of losIndex(manifest).values()) {
    // Prior: a practised LOS shrinks toward its topic's accuracy; an unpractised one stays at
    // the guessing level, so readiness never credits material you haven't touched.
    const t = topicAcc.get(info.topic);
    const tn = t ? t.s + t.f : 0;
    const acc = losAcc.get(info.id) ?? { s: 0, f: 0, n: 0, last: 0 };
    const priorMean = acc.n > 0 && tn >= m.min_answers ? t.s / tn : m.untouched_mean;
    const a = m.prior_strength * priorMean + acc.s;
    const b = m.prior_strength * (1 - priorMean) + acc.f;
    const mean = a / (a + b);
    const [lo, hi] = interval(a, b);
    const rs = opts.meansOnly ? [] : [...(losCards.get(info.id) ?? [])].map((id) => status.get(id).r);
    const recall = rs.length ? rs.reduce((x, y) => x + y, 0) / rs.length : null;
    const forgetting = recall == null ? 1 : Math.max(cfg.priority.forgetting_floor, 1 - recall);
    const uncertainty = 1 + cfg.priority.uncertainty_k / Math.sqrt(acc.n + 1);
    const priority = (1 - mean) * info.weight * forgetting * uncertainty;
    const variance = (a * b) / ((a + b) ** 2 * (a + b + 1));
    los.set(info.id, { ...info, n: acc.n, last: acc.last || null, mean, lo, hi, variance, recall, forgetting, uncertainty, priority });
  }

  // Readiness: average LOS mastery per topic (untouched LOS count at their guessing prior), then
  // weight topics by exam weight. The band treats LOS estimates as independent: the variance
  // of an average of L estimates is Σ var / L², so it narrows as more LOS are covered.
  const z = Z_FOR_LEVEL[m.interval] ?? 1.645;
  const band = (mean, variance) => (opts.ci === false ? [null, null]
    : [Math.max(0, mean - z * Math.sqrt(variance)), Math.min(1, mean + z * Math.sqrt(variance))]);
  const target = opts.target ?? cfg.readiness.target;
  const topics = new Map();
  for (const t of manifest.topics) {
    const list = [...los.values()].filter((l) => l.topic === t.id);
    const L = list.length || 1;
    const mean = list.reduce((s, l) => s + l.mean, 0) / L;
    const variance = list.reduce((s, l) => s + l.variance, 0) / L ** 2;
    const [lo, hi] = band(mean, variance);
    topics.set(t.id, {
      id: t.id, name: t.name, weight: t.weight, mean, variance, lo, hi,
      coverage: list.length ? list.filter((l) => l.n > 0).length / list.length : 0, losCount: list.length,
    });
  }
  const totalW = [...topics.values()].reduce((s, t) => s + t.weight, 0) || 1;
  const overallMean = [...topics.values()].reduce((s, t) => s + t.weight * t.mean, 0) / totalW;
  const overallVar = [...topics.values()].reduce((s, t) => s + (t.weight / totalW) ** 2 * t.variance, 0);
  const [olo, ohi] = band(overallMean, overallVar);
  const overall = { mean: overallMean, lo: olo, hi: ohi, target };
  return { los, topics, overall, cards, cardMeta, status, now };
}

/** Readiness at the end of each of the last `days` days (means only, for a trend line). */
export function readinessTrend(events, manifest, days = 30, now = Date.now()) {
  const rows = [];
  for (let i = days - 1; i >= 0; i--) {
    const end = new Date(now);
    end.setHours(23, 59, 59, 999);
    end.setDate(end.getDate() - i);
    const t = Math.min(end.getTime(), now);
    const model = buildModel(events, manifest, t, { ci: false, meansOnly: true });
    const n = events.filter((e) => e.type === "answer" && e.ts <= t).length;
    rows.push({ day: new Date(t).toISOString().slice(0, 10), acc: n ? model.overall.mean : null, n });
  }
  return rows;
}

/** Consecutive days (ending today, or yesterday if nothing yet today) with any activity. */
export function streak(events, now = Date.now()) {
  const days = new Set(events.filter((e) => e.type !== "setting").map((e) => new Date(e.ts).toDateString()));
  const d = new Date(now);
  if (!days.has(d.toDateString())) d.setDate(d.getDate() - 1);
  let n = 0;
  while (days.has(d.toDateString())) { n++; d.setDate(d.getDate() - 1); }
  return n;
}
