// The progress log: every answer, card review and study mark is an immutable event
// {id, v, device, ts, type, payload}. Nothing is ever stored as a running total, so
// merging two devices' logs is a union by id (see builder/schemas/event.schema.json).

import { useEffect, useState } from "../lib.js";
import { allEvents, kvGet, kvSet, putEvent, resetConnection } from "./store.js";

let devicePromise;
let eventsPromise;
const listeners = new Set();

/** UUIDv7: 48-bit millisecond timestamp + randomness, so ids sort by time. */
export function uuidv7(ts = Date.now()) {
  const b = crypto.getRandomValues(new Uint8Array(16));
  let t = ts;
  for (let i = 5; i >= 0; i--) {
    b[i] = t % 256;
    t = Math.floor(t / 256);
  }
  b[6] = (b[6] & 0x0f) | 0x70;
  b[8] = (b[8] & 0x3f) | 0x80;
  const h = [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

export function deviceId() {
  devicePromise ??= kvGet("device").then(async (id) => {
    if (id) return id;
    const fresh = crypto.randomUUID();
    await kvSet("device", fresh);
    return fresh;
  });
  return devicePromise;
}

/** All events, sorted by time. Loaded once, then kept current in memory. */
export function getEvents() {
  eventsPromise ??= allEvents().then((list) => list.sort((a, b) => a.ts - b.ts));
  return eventsPromise;
}

export async function logEvent(type, payload, ts = Date.now()) {
  const event = { id: uuidv7(ts), v: 1, device: await deviceId(), ts, type, payload };
  await putEvent(event);
  (await getEvents()).push(event);
  listeners.forEach((fn) => fn());
  return event;
}

const TYPES = new Set(["answer", "review", "study", "setting", "session", "flag"]);

/** Minimal structural check (mirrors builder/schemas/event.schema.json). */
export function isEvent(e) {
  return e && typeof e === "object" && typeof e.id === "string" && e.v === 1 && Number.isInteger(e.ts)
    && TYPES.has(e.type) && e.payload && typeof e.payload === "object";
}

/** Union by id: events already present (same id) are skipped, so re-importing is harmless. */
export function mergeEvents(local, incoming) {
  const known = new Set(local.map((e) => e.id));
  const fresh = [];
  let invalid = 0;
  for (const e of incoming) {
    if (!isEvent(e)) { invalid += 1; continue; }
    if (known.has(e.id)) continue;
    known.add(e.id);
    fresh.push(e);
  }
  return { fresh, duplicates: incoming.length - fresh.length - invalid, invalid };
}

/** Call fn whenever the log changes (new or imported events); returns an unsubscribe function. */
export function onEventsChanged(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Add another device's events to this device's log. */
export async function importEvents(incoming) {
  const current = await getEvents();
  const result = mergeEvents(current, incoming);
  for (const e of result.fresh) await putEvent(e);
  current.push(...result.fresh);
  current.sort((a, b) => a.ts - b.ts);
  listeners.forEach((fn) => fn());
  return result;
}

const LOAD_WATCHDOG_MS = 8000;

/** Breadcrumbs for diagnosing slow or stuck loads: inspect window.__cfaTrace in devtools. */
function trace(msg) {
  (globalThis.__cfaTrace ??= []).push(`${Math.round(performance.now())}ms ${msg}`);
}

/** Re-render when the log changes; returns the events array (or null while loading). */
export function useEvents() {
  const [, bump] = useState(0);
  const [events, setEvents] = useState(null);
  useEffect(() => {
    let live = true;
    let loaded = false;
    const load = (attempt) => {
      trace(`load ${attempt} start`);
      getEvents().then((list) => {
        trace(`load ${attempt} done: ${list.length} events`);
        loaded = true;
        if (live) setEvents(list);
      }, (err) => trace(`load ${attempt} failed: ${err}`));
    };
    load(1);
    // Rarely the first load never settles (seen intermittently in headless testing). Rather than
    // show "Loading…" forever, drop the stuck promise and connection and try again.
    const watchdog = setTimeout(() => {
      if (loaded || !live) return;
      console.warn("Progress log did not load in time; retrying with a fresh connection");
      eventsPromise = undefined;
      resetConnection();
      load(2);
    }, LOAD_WATCHDOG_MS);
    const fn = () => bump((n) => n + 1);
    listeners.add(fn);
    return () => { live = false; clearTimeout(watchdog); listeners.delete(fn); };
  }, []);
  return events;
}
