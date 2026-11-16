// Moving progress between devices: a JSON file (export/import) or an optional private GitHub
// Gist. Both carry the raw event log; merging is a union by event id, so nothing is ever
// double-counted or overwritten. The Gist token stays on this device (kv), never in the log.

import { useEffect, useState } from "../lib.js";
import { deviceId, getEvents, importEvents, onEventsChanged } from "./events.js";
import { kvGet, kvSet } from "./store.js";

export const FORMAT = "fr-b2-progress";
const GIST_FILE = "fr-b2-progress.json";
const API = "https://api.github.com";

export async function progressDocument() {
  return { format: FORMAT, version: 1, exported_at: new Date().toISOString(), device: await deviceId(), events: await getEvents() };
}

export function parseProgress(text) {
  let doc;
  try {
    doc = JSON.parse(text);
  } catch {
    throw new Error("Ce fichier n'est pas un JSON valide.");
  }
  if (doc?.format !== FORMAT || !Array.isArray(doc.events)) throw new Error("Ce fichier n'est pas une sauvegarde de progrès Français B2.");
  if (doc.version > 1) throw new Error("Ce fichier vient d'une version plus récente de l'application : mettez d'abord cet appareil à jour.");
  return doc.events;
}

export async function downloadProgress() {
  const doc = await progressDocument();
  const blob = new Blob([JSON.stringify(doc)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `francais-b2-progres-${doc.exported_at.slice(0, 10)}.json`;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 10_000);
  return doc.events.length;
}

export async function importFile(file) {
  return importEvents(parseProgress(await file.text()));
}

// ---------------------------------------------------------------- Gist

export const gistSettings = async () => (await kvGet("gist")) ?? { token: "", id: "", lastSync: null };
export const saveGistSettings = (s) => kvSet("gist", s);

async function gh(path, token, init = {}) {
  const res = await fetch(API + path, {
    ...init,
    headers: { Accept: "application/vnd.github+json", Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...init.headers },
  });
  if (!res.ok) {
    const hint = res.status === 401 ? " (vérifiez le jeton)" : res.status === 404 ? " (vérifiez l'identifiant du Gist et la permission gist du jeton)" : "";
    throw new Error(`GitHub ${res.status}${hint}`);
  }
  return res.json();
}

/**
 * Pull the Gist, merge it into this device, push the union back.
 * Creates a secret Gist on first use. Returns {pulled, pushed, id}.
 */
export async function syncGist(settings) {
  if (!settings.token) throw new Error("Ajoutez d'abord un jeton GitHub avec la permission gist.");
  let pulled = { fresh: [] };
  let remoteCount = -1;
  let id = settings.id;
  if (id) {
    const gist = await gh(`/gists/${id}`, settings.token);
    const file = gist.files?.[GIST_FILE];
    if (file) {
      const text = file.truncated ? await (await fetch(file.raw_url)).text() : file.content;
      const remote = parseProgress(text);
      remoteCount = remote.length;
      pulled = await importEvents(remote);
    }
  }
  const doc = await progressDocument();
  // This device now holds the union of both logs; if that is no bigger than the Gist, the Gist
  // already has everything and rewriting it would only add a revision.
  if (doc.events.length !== remoteCount) {
    const body = JSON.stringify({ description: "Français B2 : progrès (journal d'événements)", files: { [GIST_FILE]: { content: JSON.stringify(doc) } } });
    const saved = id ? await gh(`/gists/${id}`, settings.token, { method: "PATCH", body })
                     : await gh("/gists", settings.token, { method: "POST", body: JSON.stringify({ ...JSON.parse(body), public: false }) });
    id = saved.id;
  }
  await saveGistSettings({ ...settings, id, lastSync: Date.now(), lastError: null });
  status.forEach((fn) => fn());
  return { pulled: pulled.fresh.length, pushed: doc.events.length, id };
}

// ---------------------------------------------------------------- automatic sync

const AUTO_DELAY_MS = 60_000;
const status = new Set();
let running = null;
let timer = null;

/**
 * Sync quietly once a Gist is set up (token and id, so it never creates a Gist on its own).
 * Failures are recorded for the Home screen instead of thrown; offline it does nothing.
 */
export function autoSync() {
  clearTimeout(timer);
  timer = null;
  running ??= (async () => {
    const settings = await gistSettings();
    if (!settings.token || !settings.id || !navigator.onLine) return;
    try {
      await syncGist(settings);
    } catch (e) {
      await saveGistSettings({ ...settings, lastError: e.message });
      status.forEach((fn) => fn());
    }
  })().finally(() => { running = null; });
  return running;
}

/** Start background sync: now, a minute after new answers, when the app is hidden or reopened, and when back online. */
export function startAutoSync() {
  autoSync();
  // Events imported by a sync land here too; the follow-up sync then finds nothing new and stops.
  onEventsChanged(() => {
    clearTimeout(timer);
    timer = setTimeout(autoSync, AUTO_DELAY_MS);
  });
  document.addEventListener("visibilitychange", async () => {
    if (document.visibilityState === "hidden") {
      if (timer) autoSync(); // push pending answers before the phone suspends the app
    } else if (Date.now() - ((await gistSettings()).lastSync ?? 0) > AUTO_DELAY_MS) {
      autoSync();
    }
  });
  addEventListener("online", () => autoSync());
}

/** Gist settings that re-render when a sync finishes; null while loading. */
export function useSyncStatus() {
  const [value, setValue] = useState(null);
  useEffect(() => {
    const load = () => gistSettings().then(setValue);
    load();
    status.add(load);
    return () => status.delete(load);
  }, []);
  return value;
}
