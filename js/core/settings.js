// User settings live in the event log as {type: "setting", payload: {key, value}}:
// the latest event per key wins, so settings merge across devices like everything else.

import { logEvent } from "./events.js";

export const DEFAULTS = { exam_date: null, daily_minutes: 20, target: null, weekend_ratio: 2, new_cards: 20, daily_xp: 50 };

export function settingsFrom(events) {
  const out = { ...DEFAULTS };
  for (const e of events) if (e.type === "setting") out[e.payload.key] = e.payload.value;
  return out;
}

export const saveSetting = (key, value) => logEvent("setting", { key, value });
