// Service worker. The builder fills in VERSION and PRECACHE (see builder/site.py).
//
// Cache names carry an fr- prefix: other apps on this origin (the CFA trainer) use shell-* and
// data-v1, and each app's activate step deletes only its own old shells.
//
// fr-shell-<version>  the app itself, precached at install; replaced when any shell file changes
// fr-data-v1         topic chunks and figures (content-hashed names, so cache-first forever),
//                  plus meta.json / manifest.json (network-first so new content shows up)

const VERSION = "c966b543e8a9";
const PRECACHE = ["./", "css/app.css", "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "index.html", "js/charts.js", "js/core/analytics.js", "js/core/crypto.js", "js/core/data.js", "js/core/events.js", "js/core/fsrs.js", "js/core/fx.js", "js/core/game.js", "js/core/graph.js", "js/core/katex.js", "js/core/mastery.js", "js/core/md.js", "js/core/mock.js", "js/core/plan.js", "js/core/router.js", "js/core/select.js", "js/core/settings.js", "js/core/smart.js", "js/core/stats-math.js", "js/core/store.js", "js/core/sync.js", "js/core/theme.js", "js/game-ui.js", "js/lib.js", "js/lookup.js", "js/main.js", "js/ui.js", "js/views/home.js", "js/views/map.js", "js/views/mock.js", "js/views/module.js", "js/views/practice.js", "js/views/settings.js", "js/views/stats.js", "js/views/study.js", "js/views/unlock.js", "manifest.webmanifest", "vendor/katex/fonts/KaTeX_AMS-Regular.woff2", "vendor/katex/fonts/KaTeX_Caligraphic-Bold.woff2", "vendor/katex/fonts/KaTeX_Caligraphic-Regular.woff2", "vendor/katex/fonts/KaTeX_Fraktur-Bold.woff2", "vendor/katex/fonts/KaTeX_Fraktur-Regular.woff2", "vendor/katex/fonts/KaTeX_Main-Bold.woff2", "vendor/katex/fonts/KaTeX_Main-BoldItalic.woff2", "vendor/katex/fonts/KaTeX_Main-Italic.woff2", "vendor/katex/fonts/KaTeX_Main-Regular.woff2", "vendor/katex/fonts/KaTeX_Math-BoldItalic.woff2", "vendor/katex/fonts/KaTeX_Math-Italic.woff2", "vendor/katex/fonts/KaTeX_SansSerif-Bold.woff2", "vendor/katex/fonts/KaTeX_SansSerif-Italic.woff2", "vendor/katex/fonts/KaTeX_SansSerif-Regular.woff2", "vendor/katex/fonts/KaTeX_Script-Regular.woff2", "vendor/katex/fonts/KaTeX_Size1-Regular.woff2", "vendor/katex/fonts/KaTeX_Size2-Regular.woff2", "vendor/katex/fonts/KaTeX_Size3-Regular.woff2", "vendor/katex/fonts/KaTeX_Size4-Regular.woff2", "vendor/katex/fonts/KaTeX_Typewriter-Regular.woff2", "vendor/katex/katex.min.css", "vendor/katex/katex.min.js", "vendor/preact-htm.js"];
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
