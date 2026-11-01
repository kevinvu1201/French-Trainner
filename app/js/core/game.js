// The game layer: XP, levels, daily goal, streak and badges, all derived from the event log
// (nothing is stored separately), so they merge across devices like the rest of the progress.

import { localDay } from "./analytics.js";
import { streak } from "./mastery.js";

/** XP for one event. Effort always earns something; being right (and sure) earns more. */
export function xpFor(e) {
  const p = e.payload;
  switch (e.type) {
    case "answer":
      if (p.mode === "listening") return p.correct ? 15 : 3;
      if (p.mode === "mock") return p.correct ? 8 : 2;
      return p.correct ? (p.confidence === 3 ? 12 : 10) : 2;
    case "review": return p.grade >= 3 ? 5 : 2;
    case "study": return p.auto || p.finished === false ? 0 : 20;
    case "session": return p.kind === "mock" ? 50 : 0;
    default: return 0;
  }
}

// Level n → n+1 costs 100 + 50·(n − 1) XP: quick early levels, then a steady climb.
const levelCost = (n) => 100 + 50 * (n - 1);
export const TITLES = ["Touriste", "Curieux", "Voyageur", "Flâneur", "Habitué", "Bavard", "Parisien", "Conteur",
  "Orateur", "Débatteur", "Écrivain", "Critique", "Polyglotte", "Diplômé B2", "Académicien"];
export const titleFor = (level) => TITLES[Math.min(level, TITLES.length) - 1];

export function levelFor(xp) {
  let level = 1;
  let rest = xp;
  while (rest >= levelCost(level)) { rest -= levelCost(level); level += 1; }
  return { level, title: titleFor(level), into: rest, need: levelCost(level) };
}

/**
 * Badges: id, icon, name, how to earn it, and test(stats) → true once earned.
 * stats = running totals while replaying the log, so each badge gets the time it was earned.
 */
export const BADGES = [
  { id: "first", icon: "🌱", name: "Premier pas", how: "Répondre à une première question", test: (s) => s.answers >= 1 },
  { id: "q50", icon: "✏️", name: "Échauffé", how: "Répondre à 50 questions", test: (s) => s.answers >= 50 },
  { id: "q250", icon: "📚", name: "Assidu", how: "Répondre à 250 questions", test: (s) => s.answers >= 250 },
  { id: "q1000", icon: "🏛️", name: "Infatigable", how: "Répondre à 1 000 questions", test: (s) => s.answers >= 1000 },
  { id: "combo10", icon: "🔥", name: "En feu", how: "10 bonnes réponses d'affilée", test: (s) => s.bestCombo >= 10 },
  { id: "combo25", icon: "☄️", name: "Inarrêtable", how: "25 bonnes réponses d'affilée", test: (s) => s.bestCombo >= 25 },
  { id: "streak3", icon: "📅", name: "Régulier", how: "3 jours d'affilée", test: (s) => s.streak >= 3 },
  { id: "streak7", icon: "🗓️", name: "Une semaine !", how: "7 jours d'affilée", test: (s) => s.streak >= 7 },
  { id: "streak30", icon: "🏆", name: "Un mois !", how: "30 jours d'affilée", test: (s) => s.streak >= 30 },
  { id: "cards100", icon: "🃏", name: "Collectionneur", how: "Réviser 100 cartes", test: (s) => s.reviews >= 100 },
  { id: "cards500", icon: "🗂️", name: "Lexicographe", how: "Réviser 500 cartes", test: (s) => s.reviews >= 500 },
  { id: "ear", icon: "🎧", name: "Oreille fine", how: "Terminer un exercice d'écoute", test: (s) => s.listeningSets >= 1 },
  { id: "ear15", icon: "📻", name: "Auditeur", how: "Terminer 15 exercices d'écoute", test: (s) => s.listeningSets >= 15 },
  { id: "perfect", icon: "💯", name: "Sans faute", how: "Un texte à trous ou une écoute 100 % juste", test: (s) => s.perfectSets >= 1 },
  { id: "lesson10", icon: "🎓", name: "Bon élève", how: "Terminer 10 leçons", test: (s) => s.lessons >= 10 },
  { id: "mock", icon: "📝", name: "Examen blanc", how: "Terminer un examen blanc", test: (s) => s.mocks >= 1 },
  { id: "early", icon: "🌅", name: "Lève-tôt", how: "S'entraîner avant 8 h", test: (s) => s.early },
  { id: "night", icon: "🦉", name: "Oiseau de nuit", how: "S'entraîner après 22 h", test: (s) => s.night },
  { id: "lvl5", icon: "⭐", name: "Niveau 5", how: "Atteindre le niveau 5", test: (s) => s.level >= 5 },
  { id: "lvl10", icon: "🌟", name: "Niveau 10", how: "Atteindre le niveau 10", test: (s) => s.level >= 10 },
];

/** Everything the game screens need, from the sorted event log. */
export function gameState(events, settings, now = Date.now()) {
  const s = { answers: 0, reviews: 0, combo: 0, bestCombo: 0, listeningSets: 0, perfectSets: 0, lessons: 0, mocks: 0,
              early: false, night: false, streak: 0, level: 1, xp: 0 };
  const earned = new Map(); // badge id -> ts
  const sets = new Map(); // set id -> {n, right}
  const days = new Set();
  const byDay = new Map();
  for (const e of events) {
    const xp = xpFor(e);
    s.xp += xp;
    if (xp) byDay.set(localDay(e.ts), (byDay.get(localDay(e.ts)) ?? 0) + xp);
    const p = e.payload;
    if (e.type === "answer") {
      s.answers += 1;
      s.combo = p.correct ? s.combo + 1 : 0;
      s.bestCombo = Math.max(s.bestCombo, s.combo);
      if (p.set) {
        const k = `${p.set}|${Math.floor(e.ts / 60_000)}`; // one attempt = answers logged together
        const a = sets.get(k) ?? { n: 0, right: 0, listening: p.mode === "listening" };
        a.n += 1; a.right += p.correct ? 1 : 0;
        sets.set(k, a);
        if (a.n >= 3 && a.right === a.n && !a.counted) { a.counted = true; s.perfectSets += 1; }
        if (a.listening && !a.done) { a.done = true; s.listeningSets += 1; }
      }
    } else if (e.type === "review") s.reviews += 1;
    else if (e.type === "study" && !p.auto && p.finished !== false) s.lessons += 1;
    else if (e.type === "session" && p.kind === "mock") s.mocks += 1;
    if (xp) {
      const h = new Date(e.ts).getHours();
      if (h < 8) s.early = true;
      if (h >= 22) s.night = true;
      days.add(new Date(e.ts).toDateString());
      s.streak = runLength(days, e.ts);
    }
    s.level = levelFor(s.xp).level;
    for (const b of BADGES) if (!earned.has(b.id) && b.test(s)) earned.set(b.id, e.ts);
  }
  const today = byDay.get(localDay(now)) ?? 0;
  const week = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(now);
    d.setHours(12, 0, 0, 0);
    d.setDate(d.getDate() - (6 - i));
    return { day: localDay(d.getTime()), date: d, xp: byDay.get(localDay(d.getTime())) ?? 0 };
  });
  const goal = settings?.daily_xp ?? 50;
  return { ...levelFor(s.xp), xp: s.xp, today, goal, goalDone: today >= goal, week, streak: streak(events, now),
           bestCombo: s.bestCombo, earned, stats: s };
}

/** Consecutive days with XP ending on the day of ts. */
function runLength(days, ts) {
  const d = new Date(ts);
  let n = 0;
  while (days.has(d.toDateString())) { n++; d.setDate(d.getDate() - 1); }
  return n;
}
