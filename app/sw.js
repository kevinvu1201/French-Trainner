// Service worker. The builder fills in VERSION and PRECACHE (see builder/site.py).
//
// Cache names carry an fr- prefix: other apps on this origin (the CFA trainer) use shell-* and
// data-v1, and each app's activate step deletes only its own old shells.
//
// fr-shell-<version>  the app itself, precached at install; replaced when any shell file changes
// fr-data-v1         topic chunks and figures (content-hashed names, so cache-first forever),
//                  plus meta.json / manifest.json (network-first so new content shows up)

const VERSION = "__VERSION__";
const PRECACHE = __PRECACHE__;
const SHELL = `fr-shell-${VERSION}`;
const DATA = "fr-data-v1";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL).then((c) => c.addAll(PRECACHE.map((u) => new Request(u, { cache: "reload" }))))
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith("fr-shell-") && name !== SHELL) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});

self.addEventListener("message", (event) => {
  if (event.data === "SKIP_WAITING") self.skipWaiting();
});

const isFresh = (path) => /\/data\/(meta\.json|manifest\.json(\.enc)?)$/.test(path);

async function networkFirst(request) {
  const cache = await caches.open(DATA);
  try {
    const res = await fetch(request, { cache: "no-cache" });
    if (res.ok) cache.put(request, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(request);
    if (hit) return hit;
    throw err;
  }
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request, { ignoreSearch: true });
  if (hit) return hit;
  const res = await fetch(request);
  if (res.ok) cache.put(request, res.clone());
  return res;
}

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin) return;
  const scope = new URL(self.registration.scope).pathname;
  if (req.mode === "navigate" && (url.pathname === scope || url.pathname === scope + "index.html")) {
    // App routes live in the hash, so navigating to the app is always the shell.
    event.respondWith(caches.match("./", { cacheName: SHELL }).then((hit) => hit || fetch(req)));
    return;
  }
  if (req.mode === "navigate") return; // other pages on the site (e.g. local review pages) go to the network
  if (url.pathname.includes("/data/")) {
    event.respondWith(isFresh(url.pathname) ? networkFirst(req) : cacheFirst(req, DATA));
    return;
  }
  event.respondWith(caches.match(req, { cacheName: SHELL }).then((hit) => hit || fetch(req)));
});
