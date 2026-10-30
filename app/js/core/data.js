// Content access. Only meta.json and the manifest are loaded at startup; each topic's
// chunk is fetched (and decrypted, on the published site) the first time it's needed,
// then kept in memory so switching views never waits on the network.

import { checkKey, decrypt, deriveKey, gunzip } from "./crypto.js";
import { kvDel, kvGet, kvSet } from "./store.js";

const BASE = "data/";
const DATA_CACHE = "fr-data-v1";
const state = { meta: null, key: null, manifest: null, chunks: new Map(), loaded: new Map(), figs: new Map(), index: null };

export const isEncrypted = () => Boolean(state.meta?.encrypted);
const url = (path) => BASE + path + (isEncrypted() ? ".enc" : "");

export async function fetchMeta() {
  const res = await fetch(BASE + "meta.json");
  if (!res.ok) throw new Error(`meta.json: HTTP ${res.status}`);
  state.meta = await res.json();
  return state.meta;
}

/** True when the content can be read (unencrypted, or a valid key is stored on this device). */
export async function restoreKey() {
  if (!isEncrypted()) return true;
  const key = await kvGet("key");
  if (key && (await checkKey(key, state.meta))) {
    state.key = key;
    return true;
  }
  return false;
}

export async function unlock(passphrase) {
  const key = await deriveKey(passphrase, state.meta.kdf);
  if (!(await checkKey(key, state.meta))) return false;
  state.key = key;
  await kvSet("key", key);
  return true;
}

export async function forgetKey() {
  await kvDel("key");
  state.key = null;
}

async function getJSON(path) {
  const res = await fetch(url(path));
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  if (!isEncrypted()) return res.json();
  const plain = await gunzip(await decrypt(state.key, await res.arrayBuffer()));
  return JSON.parse(new TextDecoder().decode(plain));
}

export async function loadManifest() {
  state.manifest = await getJSON("manifest.json");
  state.index = buildIndex(state.manifest);
  return state.manifest;
}

function buildIndex(manifest) {
  const modules = [];
  const byModule = new Map();
  const byTopic = new Map();
  for (const topic of manifest.topics) {
    byTopic.set(topic.id, topic);
    for (const reading of topic.readings) {
      for (const module of reading.modules) {
        const entry = { topic, reading, module, i: modules.length };
        modules.push(entry);
        byModule.set(module.id, entry);
      }
    }
  }
  return { modules, byModule, byTopic };
}

export const manifest = () => state.manifest;
export const topicInfo = (id) => state.index.byTopic.get(id);
export const moduleInfo = (id) => state.index.byModule.get(id);
export const neighbours = (id) => {
  const i = moduleInfo(id)?.i;
  return i === undefined ? {} : { prev: state.index.modules[i - 1], next: state.index.modules[i + 1] };
};

let graphPromise;
/** The concept graph (null until generated content exists). */
export function getGraph() {
  if (!state.manifest.graph) return Promise.resolve(null);
  graphPromise ??= getJSON(state.manifest.graph).catch((e) => { graphPromise = undefined; throw e; });
  return graphPromise;
}

/** The topic's chunk if it's already in memory (lets views render without a loading flash). */
export const chunkNow = (topicId) => state.loaded.get(topicId);

export function getChunk(topicId) {
  if (!state.chunks.has(topicId)) {
    const p = getJSON(topicInfo(topicId).chunk).then((chunk) => {
      state.loaded.set(topicId, chunk);
      return chunk;
    });
    p.catch(() => state.chunks.delete(topicId)); // allow a retry
    state.chunks.set(topicId, p);
  }
  return state.chunks.get(topicId);
}

/** Image URL for a figure: a plain path, or a blob URL of the decrypted image. */
export const figureNow = (src) => (isEncrypted() ? state.figs.get(src) : BASE + src);

export async function figureURL(src) {
  if (!isEncrypted()) return BASE + src;
  if (!state.figs.has(src)) {
    const res = await fetch(url(src));
    if (!res.ok) throw new Error(`${src}: HTTP ${res.status}`);
    const bytes = await decrypt(state.key, await res.arrayBuffer());
    state.figs.set(src, URL.createObjectURL(new Blob([bytes], { type: "image/png" })));
  }
  return state.figs.get(src);
}

/** Fetch every chunk and figure so the service worker caches them for offline use. */
export async function downloadAll(onProgress) {
  const topics = state.manifest.topics;
  let done = 0;
  let total = topics.length;
  const figures = [];
  for (const t of topics) {
    const chunk = await getChunk(t.id);
    for (const f of Object.values(chunk.figures)) if (f.src) figures.push(f.src);
    onProgress(++done, (total = topics.length + figures.length));
  }
  const queue = [...new Set(figures)];
  total = topics.length + queue.length;
  const worker = async () => {
    while (queue.length) {
      const src = queue.pop();
      const res = await fetch(url(src));
      if (res.ok) await res.arrayBuffer();
      onProgress(++done, total);
    }
  };
  await Promise.all(Array.from({ length: 6 }, worker));
}

/** Drop cached chunks from older builds (their names no longer appear in the manifest). */
export async function pruneDataCache() {
  if (!("caches" in self)) return;
  const live = new Set(state.manifest.topics.map((t) => new URL(url(t.chunk), location.href).href));
  const cache = await caches.open(DATA_CACHE);
  for (const req of await cache.keys()) {
    if (req.url.includes("/data/chunks/") && !live.has(req.url)) await cache.delete(req);
  }
}

export async function storageInfo() {
  const est = (await navigator.storage?.estimate?.()) ?? {};
  const persisted = (await navigator.storage?.persisted?.()) ?? false;
  return { usage: est.usage ?? 0, quota: est.quota ?? 0, persisted };
}

/** True when the app runs from the home screen / as an installed app rather than in a browser tab. */
export const installed = () => matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;

/**
 * Ask the browser not to evict our storage (progress log, cached content). Without it, Safari
 * clears a site's data after about 7 days without a visit, unless the app is on the home screen.
 */
export async function protectStorage() {
  try {
    if (await navigator.storage?.persisted?.()) return true;
    return (await navigator.storage?.persist?.()) ?? false;
  } catch {
    return false;
  }
}
