// Pure functions over the event log. No DOM, no storage: easy to test.

export const MIN_N = 5; // below this many answers, show the count but draw no conclusion
export const PACE_MS = 60_000; // grammar pace: one minute per question (a gap-fill text of 4 in 4 min)
export const TARGET = 0.7;

export const answers = (events) => events.filter((e) => e.type === "answer");

export function median(values) {
  if (!values.length) return null;
  const s = [...values].sort((a, b) => a - b);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

/** Group answers by key(s); an answer tagged with several LOS counts once for each. */
export function groupStats(ans, keyFn) {
  const groups = new Map();
  for (const e of ans) {
    const keys = [keyFn(e)].flat().filter(Boolean);
    for (const k of keys) {
      const g = groups.get(k) ?? { key: k, n: 0, correct: 0, ms: [] };
      g.n += 1;
      g.correct += e.payload.correct ? 1 : 0;
      g.ms.push(e.payload.ms);
      groups.set(k, g);
    }
  }
  return [...groups.values()].map((g) => ({
    key: g.key, n: g.n, correct: g.correct, acc: g.correct / g.n,
    enough: g.n >= MIN_N, medianMs: median(g.ms),
  }));
}

export const CONFIDENCE = { 1: "Au hasard", 2: "Hésitant", 3: "Sûr" };

/** Accuracy at each confidence level, plus the two dangerous lists. Mock answers carry no
 * confidence rating (the exam doesn't ask for one), so they're left out. */
export function calibration(all) {
  const ans = all.filter((e) => e.payload.mode !== "mock");
  const levels = [1, 2, 3].map((c) => {
    const sub = ans.filter((e) => e.payload.confidence === c);
    const correct = sub.filter((e) => e.payload.correct).length;
    return { confidence: c, label: CONFIDENCE[c], n: sub.length, acc: sub.length ? correct / sub.length : null };
  });
  return {
    levels,
    // Sure but wrong: the most dangerous case. Guessed and right: knowledge you may not have.
    sureWrong: ans.filter((e) => e.payload.confidence === 3 && !e.payload.correct),
    luckyRight: ans.filter((e) => e.payload.confidence === 1 && e.payload.correct),
  };
}

export function localDay(ts) {
  const d = new Date(ts);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** One row per calendar day for the last `days` days (oldest first), including empty days. */
export function daily(ans, days = 30, now = Date.now()) {
  const rows = [];
  const index = new Map();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setHours(12, 0, 0, 0);
    d.setDate(d.getDate() - i);
    const key = localDay(d.getTime());
    index.set(key, rows.length);
    rows.push({ day: key, n: 0, correct: 0 });
  }
  for (const e of ans) {
    const i = index.get(localDay(e.ts));
    if (i !== undefined) {
      rows[i].n += 1;
      rows[i].correct += e.payload.correct ? 1 : 0;
    }
  }
  return rows;
}

/** Trailing-window accuracy per day; null until the window holds MIN_N answers. */
export function rollingAccuracy(rows, window = 7) {
  return rows.map((_, i) => {
    const slice = rows.slice(Math.max(0, i - window + 1), i + 1);
    const n = slice.reduce((s, r) => s + r.n, 0);
    const c = slice.reduce((s, r) => s + r.correct, 0);
    return { day: rows[i].day, n, acc: n >= MIN_N ? c / n : null };
  });
}

/** Per module: "practised" (answered questions), "studied" (marked/read) or "untouched". */
export function coverage(moduleIds, events) {
  const studied = new Set();
  const practised = new Set();
  for (const e of events) {
    if (e.type === "study" && e.payload.module) studied.add(e.payload.module);
    if (e.type === "answer" && e.payload.module) practised.add(e.payload.module);
  }
  return new Map(moduleIds.map((m) => [m, practised.has(m) ? "practised" : studied.has(m) ? "studied" : "untouched"]));
}

export function formatMs(ms) {
  if (ms == null) return "—";
  const s = Math.round(ms / 1000);
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export const pct = (x, digits = 0) => (x == null ? "—" : `${(x * 100).toFixed(digits)}%`);

const MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];

/** "28 oct. 2026" in local time. Avoids toLocaleDateString, whose first call loads locale data
 * (~170 ms on a throttled phone, on the startup path). */
export function formatDate(value) {
  const d = new Date(value);
  return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}
