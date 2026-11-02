// The study plan: a day-by-day schedule of new material that finishes before the final-review
// window. Modules keep curriculum order (heaviest topics first) and are sized by their LOS count;
// weekend days take a bigger share. Only modules you mark finished count as done; unfinished work
// moves to today, and work done early frees up later days (see dailyPlan).

import { logEvent } from "./events.js";

const DAY = 86_400_000;

export function startOfDay(ts) {
  const d = new Date(ts);
  d.setHours(0, 0, 0, 0);
  return d.getTime();
}

export function daysUntil(dateStr, now = Date.now()) {
  if (!dateStr) return null;
  const exam = new Date(`${dateStr}T00:00:00`);
  return Math.round((exam - startOfDay(now)) / DAY);
}

export const isWeekend = (ts) => [0, 6].includes(new Date(ts).getDay());

/** All modules in study order, each with its load (number of LOS, at least 1). */
function modulesInOrder(manifest) {
  const topics = [...manifest.topics].sort((a, b) => b.weight - a.weight);
  return topics.flatMap((t) => t.readings.flatMap((r) => r.modules.map((m) => ({
    ...m, topic: t.id, topicName: t.name, load: Math.max(1, m.los.length),
  }))));
}

/** `count` consecutive days from `start` (calendar days, so DST changes don't shift them). */
function days(start, count, weekendRatio) {
  const d = new Date(start);
  return Array.from({ length: Math.max(0, count) }, (_, k) => {
    const date = new Date(d.getFullYear(), d.getMonth(), d.getDate() + k).getTime();
    return { date, weekend: isWeekend(date), weight: isWeekend(date) ? weekendRatio : 1 };
  });
}

/**
 * Give each day a share of the modules proportional to its weight, keeping their order: a module
 * goes to the first day whose cumulative target covers at least its midpoint.
 */
export function spread(modules, dayList) {
  const out = dayList.map((d) => ({ ...d, modules: [], load: 0 }));
  if (!out.length) return out;
  const total = modules.reduce((s, m) => s + m.load, 0);
  const weights = out.reduce((s, d) => s + d.weight, 0);
  let cum = 0;
  let assigned = 0;
  let i = 0;
  out.forEach((day, k) => {
    cum += day.weight;
    const target = k === out.length - 1 ? Infinity : (total * cum) / weights;
    while (i < modules.length && assigned + modules[i].load / 2 <= target) {
      day.modules.push(modules[i]);
      day.load += modules[i].load;
      assigned += modules[i].load;
      i += 1;
    }
  });
  return out;
}

/**
 * Modules you marked finished before `until`. Only explicit marks count (not the automatic
 * "viewed for a minute" event, not practice answers), and the latest mark wins, so Undo works.
 */
export function finishedModules(events, until = Infinity) {
  const out = new Set();
  for (const e of events) {
    if (e.ts >= until) break; // events are sorted by time
    if (e.type !== "study" || e.payload.auto || !e.payload.module) continue;
    if (e.payload.finished === false) out.delete(e.payload.module);
    else out.add(e.payload.module);
  }
  return out;
}

/** Mark a module finished (or undo that); synced like any other event. */
export const setFinished = (module, topic, finished) => logEvent("study", { module, topic, auto: false, finished });

// Changing any of these settings starts a new plan from that day.
const PLAN_KEYS = new Set(["exam_date", "weekend_ratio", "plan_reset"]);
const STUDY_AHEAD = 3;

const loadOf = (list) => list.reduce((s, m) => s + m.load, 0);

export function dailyPlan(manifest, events, settings, now = Date.now()) {
  const finalReview = manifest.scoring.readiness.final_review_days;
  const ratio = settings.weekend_ratio ?? 2;
  const daysLeft = daysUntil(settings.exam_date, now);
  const modules = modulesInOrder(manifest);
  const finishedNow = finishedModules(events);
  const left = modules.filter((m) => !finishedNow.has(m.id));
  const base = { daysLeft, finalReview, ratio, remaining: left.length, total: modules.length, carried: 0, aheadDays: 0, studyAhead: [] };

  if (daysLeft == null) {
    return { ...base, newDays: null, inFinalReview: false, schedule: [],
             today: left.slice(0, 2).map((m) => ({ ...m, done: false, carried: false })) };
  }
  const newDays = daysLeft - finalReview;
  const finishBy = new Date(`${settings.exam_date}T00:00:00`).getTime() - finalReview * DAY;
  if (newDays <= 0) return { ...base, newDays: 0, finishBy, inFinalReview: true, schedule: [], today: [] };

  // The plan is laid out once, on the day it was last (re)set, and then stays put: unfinished
  // work from past days is carried to today, and work finished early empties later days.
  const today = startOfDay(now);
  const setAt = events.filter((e) => e.type === "setting" && PLAN_KEYS.has(e.payload.key)).at(-1)?.ts ?? now;
  const start = startOfDay(Math.min(setAt, now));
  const atStart = finishedModules(events, start);
  const layout = spread(modules.filter((m) => !atStart.has(m.id)), days(start, daysUntil(settings.exam_date, start) - finalReview, ratio));
  const t = Math.max(0, layout.findIndex((d) => d.date >= today));
  const before = finishedModules(events, today);
  const planned = new Set(layout.flatMap((d) => d.modules.map((m) => m.id)));
  // Past days' leftovers, plus anything un-finished (Undo) after the plan was laid out
  const carried = [
    ...layout.slice(0, t).flatMap((d) => d.modules),
    ...modules.filter((m) => !planned.has(m.id)),
  ].filter((m) => !before.has(m.id));

  const schedule = layout.slice(t).map((d, k) => {
    const mods = k === 0
      ? [...carried.map((m) => ({ ...m, carried: true })), ...d.modules.filter((m) => !before.has(m.id))]
      : d.modules.filter((m) => !finishedNow.has(m.id));
    return { ...d, modules: mods, load: loadOf(mods) };
  });
  const todayList = (schedule[0]?.modules ?? []).map((m) => ({ ...m, carried: !!m.carried, done: finishedNow.has(m.id) }));

  // Ahead: finished more than planned up to the end of today. Behind: less than planned up to
  // the end of yesterday (so a fresh morning isn't "behind" yet). Measured in average days.
  const done = loadOf(layout.flatMap((d) => d.modules).filter((m) => finishedNow.has(m.id)));
  const throughYesterday = loadOf(layout.slice(0, t).flatMap((d) => d.modules));
  const throughToday = throughYesterday + loadOf(layout[t]?.modules ?? []);
  const perDay = loadOf(layout.flatMap((d) => d.modules)) / Math.max(1, layout.length);
  const diff = done > throughToday ? done - throughToday : done < throughYesterday ? done - throughYesterday : 0;
  const aheadDays = perDay ? Math.round((2 * diff) / perDay) / 2 : 0;
  const studyAhead = schedule.slice(1).flatMap((d) => d.modules).slice(0, STUDY_AHEAD);

  return { ...base, newDays, finishBy, inFinalReview: false, schedule, today: todayList, carried: carried.length, aheadDays, studyAhead };
}
