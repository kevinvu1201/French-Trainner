// FSRS-4.5 spaced repetition (Free Spaced Repetition Scheduler), default parameters.
// A card's memory state is (stability S in days, difficulty D in 1..10). Recall probability
// after t days is R = (1 + FACTOR·t/S)^DECAY; the next interval is when R falls to the
// desired retention. State is rebuilt by replaying the event log, never stored.

export const W = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031, 1.6474,
  0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755];
const DECAY = -0.5;
const FACTOR = 19 / 81; // makes R = 0.9 exactly when t = S
const DAY = 86_400_000;

const clampD = (d) => Math.min(10, Math.max(1, d));
const initDifficulty = (g) => clampD(W[4] - (g - 3) * W[5]);

export const retrievability = (elapsedDays, stability) => (1 + (FACTOR * elapsedDays) / stability) ** DECAY;

export function intervalDays(stability, retention = 0.9) {
  return (stability / FACTOR) * (retention ** (1 / DECAY) - 1);
}

/** Apply one review with grade g (1 Again, 2 Hard, 3 Good, 4 Easy) at time ts. */
export function review(card, g, ts) {
  if (!card) {
    return { s: W[g - 1], d: initDifficulty(g), last: ts, reps: 1, lapses: g === 1 ? 1 : 0 };
  }
  const t = Math.max(0, (ts - card.last) / DAY);
  const r = retrievability(t, card.s);
  const d = clampD(W[7] * initDifficulty(3) + (1 - W[7]) * (card.d - W[6] * (g - 3)));
  let s;
  if (g === 1) {
    s = W[11] * card.d ** -W[12] * ((card.s + 1) ** W[13] - 1) * Math.exp(W[14] * (1 - r));
  } else {
    const hard = g === 2 ? W[15] : 1;
    const easy = g === 4 ? W[16] : 1;
    s = card.s * (1 + Math.exp(W[8]) * (11 - card.d) * card.s ** -W[9] * (Math.exp(W[10] * (1 - r)) - 1) * hard * easy);
  }
  return { s, d, last: ts, reps: card.reps + 1, lapses: card.lapses + (g === 1 ? 1 : 0) };
}

/** Recall probability now and the due time for a card. */
export function cardStatus(card, now, retention = 0.9) {
  const elapsed = Math.max(0, (now - card.last) / DAY);
  const due = card.last + intervalDays(card.s, retention) * DAY;
  return { r: retrievability(elapsed, card.s), due, overdueDays: (now - due) / DAY, elapsedDays: elapsed };
}

/** Grade for a practice answer, from config (wrong → Again; right → by confidence). */
export function gradeAnswer(payload, cfg) {
  if (!payload.correct) return cfg.grade_wrong;
  return payload.confidence === 1 ? cfg.grade_right_guess : payload.confidence === 2 ? cfg.grade_right_unsure : cfg.grade_right_sure;
}
