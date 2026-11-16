// The endless feed behind Flux (scroll) and Swipe: one stream mixing quick questions, "juste ou
// faux ?" sentences, vocabulary and rule cards, and reward chests. What comes next is chosen like
// the Smart Session (due reviews, weak objectives, then new material), and whatever is missed
// comes back a few cards later.

import { answers as answerEvents, localDay } from "./analytics.js";
import { cardStatus, review } from "./fsrs.js";
import { lastAnswers, questionPool } from "./select.js";

const LETTERS = ["A", "B", "C"];
const BLANK = "……";
const MIX = { question: 0.35, tf: 0.2, word: 0.45 };
const CHEST_GAP = [6, 10]; // a chest every 6 to 10 cards
export const CHEST_NEED = 5; // answers needed since the previous chest to open one
const RETRY_AFTER = [3, 5]; // a missed card returns after this many others

/**
 * The sentence a question makes with one of its options, the option in bold; null when the stem
 * isn't a single-blank sentence. The hint after the blank, "(finir)", is part of the exercise only.
 */
export function tfSentence(q, letter) {
  const opt = q.options?.[LETTERS.indexOf(letter)];
  if (!opt || q.stem.split(BLANK).length !== 2 || /[:→\n]/.test(q.stem)) return null;
  return q.stem.replace(new RegExp(`${BLANK}(\\s*\\([^()]*\\))?`), `**${opt}**`);
}

/** A short text card (a word or expression and its meaning) can be asked as a multiple choice. */
const isWord = (c) => c.front.length <= 40 && c.back.length <= 40 && !c.examples?.length && !c.common_mistake;

/** Chest contents: mostly small, sometimes big, rarely a jackpot. */
export function rollChest(rng = Math.random) {
  const r = rng();
  if (r < 0.01) return 100;
  if (r < 0.1) return 50;
  if (r < 0.4) return 20 + Math.floor(rng() * 11);
  return 5 + Math.floor(rng() * 11);
}

const between = ([lo, hi], rng) => lo + Math.floor(rng() * (hi - lo + 1));
const shuffled = (list, rng) => list.map((x) => [rng(), x]).sort((a, b) => a[0] - b[0]).map((p) => p[1]);

/**
 * Text cards in the order to show them: due under FSRS (lowest recall first), then new ones up
 * to today's allowance, then the rest, weakest memory first (extra practice once the day is done).
 */
export function wordOrder(cards, events, now, { retention = 0.9, newPerDay = 20 } = {}) {
  const ids = new Set(cards.map((c) => c.card.id));
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
  const due = [], words = [], rules = [], rest = [];
  for (const c of cards) {
    const st = state.get(c.card.id);
    if (!st) { (isWord(c.card) ? words : rules).push({ ...c, isNew: true }); continue; }
    const s = cardStatus(st, now, retention);
    (s.overdueDays >= 0 ? due : rest).push({ ...c, r: s.r });
  }
  // New cards: three words for each rule card, so the day's allowance isn't spent on rules alone.
  const fresh = [];
  while (words.length || rules.length) fresh.push(...words.splice(0, 3), ...rules.splice(0, 1));
  const byRecall = (a, b) => a.r - b.r;
  const room = Math.max(0, newPerDay - newToday);
  return [...due.sort(byRecall), ...fresh.slice(0, room), ...rest.sort(byRecall), ...fresh.slice(room)];
}

/**
 * @param chunks  Map(topic id -> chunk)
 * @param model   buildModel(...) result, for due questions and objective priorities
 * @param kinds   which card kinds to emit: question, tf, word (chests come with any)
 * @param wordModes  how words are asked: flip (self-graded), mcq (pick the meaning), listen (hear it, pick the meaning)
 * @returns {{next: (n: number) => object[], retry: (item: object) => void}}
 */
export function createFeed({ chunks, events, model, names = new Map(), now = Date.now(), rng = Math.random, retention = 0.9,
                             newPerDay = 20, kinds = ["question", "tf", "word"], wordModes = ["flip", "mcq"], chests = true }) {
  const last = lastAnswers(answerEvents(events));
  const maxPriority = Math.max(1e-9, ...[...(model?.los.values() ?? [])].map((l) => l.priority));
  const questions = [];
  const cards = [];
  for (const [topic, chunk] of chunks) {
    for (const q of questionPool(chunk)) {
      const e = last.get(q.id);
      const due = e && (model?.status.get(q.id)?.overdueDays ?? -1) >= 0;
      const why = due ? "Révision" : !e ? "Nouveau" : e.payload.correct ? "Entretien" : "Raté la dernière fois";
      const base = due ? 0 : !e ? 1 : e.payload.correct ? 3 : 0.5;
      const priority = (model?.los.get([q.los].flat()[0])?.priority ?? 0) / maxPriority;
      questions.push({ q, chunk, topic, why, score: base - 2 * priority });
    }
    for (const card of chunk.formulas) if (!card.latex && card.front && card.back) cards.push({ card, topic });
  }
  const order = (list) => list.map((x) => ({ x, s: x.score + rng() * 1.5 })).sort((a, b) => a.s - b.s).map((p) => p.x);
  const wordsByTopic = new Map();
  for (const c of cards) if (isWord(c.card)) wordsByTopic.set(c.topic, [...(wordsByTopic.get(c.topic) ?? []), c.card]);

  const pools = { question: [], tf: [], word: [] };
  const refill = {
    question: () => order(questions),
    tf: () => shuffled(questions.filter((x) => tfSentence(x.q, x.q.answer)), rng),
    word: (again) => (again ? shuffled(cards, rng) : wordOrder(cards, events, now, { retention, newPerDay })),
  };
  const started = new Set();
  const used = new Set(); // question ids shown this round, so a question and its sentence don't appear side by side
  const retries = [];
  let emitted = 0;
  let streak = { kind: null, n: 0 };
  let nextChest = between(CHEST_GAP, rng);
  let chestCount = 0;
  let uid = 0;

  function take(kind) {
    for (let pass = 0; pass < 2; pass++) {
      if (!pools[kind].length) { pools[kind] = refill[kind](started.has(kind)); started.add(kind); if (pass) used.clear(); }
      while (pools[kind].length) {
        const x = pools[kind].shift();
        if (kind === "word" || !used.has(x.q.id)) return x;
      }
    }
    return null;
  }

  function wordItem(x) {
    const pool = (wordsByTopic.get(x.topic) ?? []).filter((c) => c.id !== x.card.id && c.back !== x.card.back);
    const askable = isWord(x.card) && pool.length >= 2;
    const modes = wordModes.filter((m) => m === "flip" || askable);
    const mode = modes[Math.floor(rng() * modes.length)] ?? "flip";
    const item = { kind: "word", card: x.card, topic: x.topic, isNew: !!x.isNew, mode, tag: names.get(x.topic) ?? "" };
    if (mode !== "flip") {
      const wrong = shuffled(pool, rng).slice(0, 2).map((c) => ({ text: c.back, right: false }));
      item.options = shuffled([{ text: x.card.back, right: true }, ...wrong], rng);
    }
    return item;
  }

  function make(kind) {
    const x = take(kind);
    if (!x) return null;
    if (kind === "word") return wordItem(x);
    used.add(x.q.id);
    const base = { q: x.q, chunk: x.chunk, topic: x.topic, tag: names.get(x.topic) ?? "" };
    if (kind === "question") return { kind, ...base, why: x.why };
    // Half the sentences are right; the others use one of the wrong options.
    const wrong = LETTERS.filter((l, i) => l !== x.q.answer && x.q.options[i] != null);
    const letter = rng() < 0.5 || !wrong.length ? x.q.answer : wrong[Math.floor(rng() * wrong.length)];
    return { kind, ...base, letter, text: tfSentence(x.q, letter), truth: letter === x.q.answer };
  }

  function pickKind() {
    const open = kinds.filter((k) => (k !== "question" && k !== "tf" ? cards.length : questions.length)
      && !(streak.kind === k && streak.n >= 2 && kinds.length > 1));
    const total = open.reduce((s, k) => s + MIX[k], 0);
    let r = rng() * total;
    for (const k of open) { r -= MIX[k]; if (r <= 0) return k; }
    return open[open.length - 1] ?? null;
  }

  function one() {
    if (chests && emitted >= nextChest) {
      nextChest = emitted + 1 + between(CHEST_GAP, rng);
      return { kind: "chest", ordinal: ++chestCount };
    }
    const k = retries.findIndex((r) => r.at <= emitted);
    if (k >= 0) return { ...retries.splice(k, 1)[0].item, retry: true, why: "Revanche" };
    for (let tries = 0; tries < 6; tries++) {
      const kind = pickKind();
      const item = kind && make(kind);
      if (item) {
        streak = streak.kind === kind ? { kind, n: streak.n + 1 } : { kind, n: 1 };
        return item;
      }
      streak = { kind, n: 9 }; // nothing of that kind: try another
    }
    return null;
  }

  return {
    size: { questions: questions.length, cards: cards.length },
    next(n) {
      const out = [];
      while (out.length < n) {
        const item = one();
        if (!item) break;
        emitted += 1;
        out.push({ ...item, uid: `c${++uid}` });
      }
      return out;
    },
    /** Bring a missed card back a few cards later. */
    retry(item) {
      const { uid: _uid, retry: _retry, ...rest } = item;
      retries.push({ item: rest, at: emitted + between(RETRY_AFTER, rng) });
    },
  };
}
