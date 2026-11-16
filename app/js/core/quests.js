// Daily quests: three small goals drawn from the date (the same on every device), their progress
// read from today's events. Finishing all three unlocks a chest, claimed once per day.

import { localDay } from "./analytics.js";

export const QUEST_CHEST_XP = 40;

const POOL = [
  // one that sends you to a mode
  [{ id: "flux", icon: "📱", label: (n) => `Répondre à ${n} cartes dans le Flux`, need: 20, href: "#/flux" },
   { id: "swipe", icon: "👆", label: (n) => `Swiper ${n} cartes`, need: 25, href: "#/swipe" }],
  // one about quality
  [{ id: "combo", icon: "🔥", label: (n) => `Enchaîner ${n} bonnes réponses`, need: 7, href: "#/flux" },
   { id: "words", icon: "🃏", label: (n) => `Réviser ${n} mots ou règles`, need: 15, href: "#/swipe" }],
  // one about the rest of the app
  [{ id: "xp", icon: "⚡", label: (n) => `Gagner ${n} XP`, need: 80, href: "#/flux" },
   { id: "lesson", icon: "🎓", label: () => "Terminer une leçon", need: 1, href: "#/study" },
   { id: "listen", icon: "🎧", label: () => "Faire un exercice d'écoute", need: 1, href: "#/practice", audio: true }],
];

const hash = (s) => { let h = 2166136261; for (const c of s) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; };

/** What today's events add up to, for the quests. */
export function todayStats(events, now = Date.now()) {
  const day = localDay(now);
  const s = { flux: 0, swipe: 0, words: 0, combo: 0, lesson: 0, listen: 0 };
  const sets = new Set();
  let run = 0;
  for (const e of events) {
    if (localDay(e.ts) !== day) continue;
    const p = e.payload;
    if (e.type === "answer") {
      run = p.correct ? run + 1 : 0;
      s.combo = Math.max(s.combo, run);
      if (p.mode === "feed") s.flux += 1;
      if (p.mode === "swipe") s.swipe += 1;
      if (p.mode === "listening" && p.set) sets.add(p.set);
    } else if (e.type === "review") {
      s.words += 1;
      if (p.src === "feed") s.flux += 1;
      if (p.src === "swipe") s.swipe += 1;
    } else if (e.type === "study" && !p.auto && p.finished !== false) s.lesson += 1;
  }
  s.listen = sets.size;
  return s;
}

/**
 * @param xpToday  XP earned today (from gameState)
 * @returns {{day, quests: {id, icon, label, have, need, done, href}[], allDone, claimed}}
 */
export function dailyQuests(events, xpToday, { audio = false, now = Date.now() } = {}) {
  const day = localDay(now);
  const stats = { ...todayStats(events, now), xp: xpToday };
  const quests = POOL.map((group, i) => {
    const open = group.filter((q) => !q.audio || audio);
    const q = open[hash(`${day}|${i}`) % open.length];
    const have = Math.min(stats[q.id], q.need);
    return { id: q.id, icon: q.icon, label: q.label(q.need), have, need: q.need, done: have >= q.need, href: q.href };
  });
  const claimed = events.some((e) => e.type === "bonus" && e.payload.source === "quests" && e.payload.day === day);
  return { day, quests, allDone: quests.every((q) => q.done), claimed };
}
