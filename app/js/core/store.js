// IndexedDB: "kv" for small values (settings, the unlock key, last position) and
// "events" for the progress event log (used from the practice phase on).
// Falls back to memory when IndexedDB is unavailable (some private-browsing modes).

// Its own database: the CFA app is served from the same origin (kevinvu1201.github.io).
const DB_NAME = "fr-b2";
const DB_VERSION = 1;
const memory = new Map();
const memoryEvents = [];
let dbPromise;

function open() {
  dbPromise ??= new Promise((resolve) => {
    let req;
    try {
      req = indexedDB.open(DB_NAME, DB_VERSION);
    } catch {
      return resolve(null);
    }
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains("kv")) db.createObjectStore("kv");
      if (!db.objectStoreNames.contains("events")) {
        db.createObjectStore("events", { keyPath: "id" }).createIndex("ts", "ts");
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => resolve(null);
    req.onblocked = () => console.warn("IndexedDB open is blocked by another tab of this app");
  });
  return dbPromise;
}

/** Forget the cached connection (used when a load appears stuck); the next call reopens. */
export function resetConnection() {
  const old = dbPromise;
  dbPromise = undefined;
  old?.then((db) => db?.close()).catch(() => {});
}

async function run(store, mode, fn) {
  const db = await open();
  if (!db) return undefined;
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, mode);
    const req = fn(tx.objectStore(store));
    tx.oncomplete = () => resolve(req?.result);
    tx.onerror = () => reject(tx.error);
  });
}

export async function kvGet(key) {
  const db = await open();
  return db ? run("kv", "readonly", (s) => s.get(key)) : memory.get(key);
}

export async function kvSet(key, value) {
  const db = await open();
  if (!db) return void memory.set(key, value);
  await run("kv", "readwrite", (s) => s.put(value, key));
}

export async function kvDel(key) {
  const db = await open();
  if (!db) return void memory.delete(key);
  await run("kv", "readwrite", (s) => s.delete(key));
}

/** Store one event. put() makes re-importing the same event (same id) a no-op. */
export async function putEvent(event) {
  const db = await open();
  if (!db) return void memoryEvents.push(event);
  await run("events", "readwrite", (s) => s.put(event));
}

export async function allEvents() {
  const db = await open();
  if (!db) return [...memoryEvents];
  return (await run("events", "readonly", (s) => s.getAll())) ?? [];
}
