import { fetchMeta, loadManifest, moduleInfo, protectStorage, pruneDataCache, restoreKey, topicInfo } from "./core/data.js";
import { getEvents } from "./core/events.js";
import { useRoute } from "./core/router.js";
import { startAutoSync } from "./core/sync.js";
import { html, render, useEffect, useState } from "./lib.js";
import { Celebrations } from "./game-ui.js";
import { ErrorBox, Icon } from "./ui.js";
import { Home } from "./views/home.js";
import { ModuleView } from "./views/module.js";
import { Topic, Topics } from "./views/study.js";
import { Unlock } from "./views/unlock.js";

/**
 * A view loaded on first use, so startup only fetches and parses what the first screen needs.
 * (The service worker still caches every module after load, so this costs nothing offline.)
 */
function lazy(load, name) {
  let Component = null;
  let pending = null;
  return function LazyView(props) {
    const [, ready] = useState(0);
    const [error, setError] = useState(null);
    if (Component) return html`<${Component} ...${props} />`;
    pending ??= load().then((m) => { Component = m[name]; });
    pending.then(() => ready(1), (e) => { pending = null; setError(e); });
    return error ? html`<${ErrorBox} error=${error} retry=${() => location.reload()} />` : html`<p class="muted" role="status">Chargement…</p>`;
  };
}

const practice = () => import("./views/practice.js");
const PracticeHome = lazy(practice, "PracticeHome");
const Drill = lazy(practice, "Drill");
const ItemSet = lazy(practice, "ItemSet");
const Cards = lazy(practice, "Cards");
const SmartSession = lazy(practice, "SmartSession");
const Mock = lazy(() => import("./views/mock.js"), "Mock");
const ConceptMap = lazy(() => import("./views/map.js"), "ConceptMap");
const Stats = lazy(() => import("./views/stats.js"), "Stats");
const Settings = lazy(() => import("./views/settings.js"), "Settings");

const TABS = [
  { route: "home", hash: "#/", label: "Accueil", icon: "home" },
  { route: "study", hash: "#/study", label: "Cours", icon: "study" },
  { route: "practice", hash: "#/practice", label: "Exercices", icon: "practice" },
  { route: "stats", hash: "#/stats", label: "Progrès", icon: "stats" },
  { route: "settings", hash: "#/settings", label: "Réglages", icon: "settings" },
];

function view(route) {
  const [a, b] = route.args;
  switch (route.name) {
    case "study": return a ? { title: topicInfo(a)?.name ?? "Cours", back: "#/study", body: html`<${Topic} id=${a} />` }
                           : { title: "Cours", body: html`<${Topics} />` };
    case "m": {
      const info = moduleInfo(a);
      return { title: info?.topic.name ?? "Leçon", back: info ? `#/study/${info.topic.id}` : "#/study", tab: "study",
               body: html`<${ModuleView} id=${a} los=${b} />` };
    }
    case "practice": {
      const [mode, topic, module] = route.args;
      const back = { back: "#/practice", tab: "practice" };
      if (mode === "mock") return { title: "Examen blanc", ...back, body: html`<${Mock} />` };
      if (mode === "smart") return { title: "Séance intelligente", ...back, body: html`<${SmartSession} minutes=${topic ?? "30"} />` };
      if (mode === "drill" && topic) return { title: "Entraînement", ...back, body: html`<${Drill} topic=${topic} module=${module} />` };
      if (mode === "set" && topic) return { title: topicInfo(topic)?.counts.audio_sets ? "Écoute" : "Texte à trous", ...back,
                                            body: html`<${ItemSet} key=${module ?? topic} topic=${topic} module=${module} />` };
      if (mode === "cards" && topic) return { title: "Cartes", ...back, body: html`<${Cards} topic=${topic} />` };
      return { title: "Exercices", body: html`<${PracticeHome} />` };
    }
    case "stats": return { title: "Progrès", body: html`<${Stats} />` };
    case "map": return { title: "Carte des notions", back: "#/study", tab: "study", body: html`<${ConceptMap} key=${a ?? "all"} focus=${a} />` };
    case "settings": return { title: "Réglages", body: html`<${Settings} />` };
    default: return { title: "Français B2", tab: "home", body: html`<${Home} />` };
  }
}

function Tabs({ active, className }) {
  return html`<nav class=${className} aria-label="Navigation principale">
    ${TABS.map((t) => html`<a class="tab" href=${t.hash} aria-current=${active === t.route ? "page" : undefined}>
      <${Icon} name=${t.icon} /><span>${t.label}</span></a>`)}
  </nav>`;
}

function UpdateToast() {
  const [waiting, setWaiting] = useState(null);
  useEffect(() => {
    const onUpdate = (e) => setWaiting(e.detail);
    addEventListener("sw-update", onUpdate);
    return () => removeEventListener("sw-update", onUpdate);
  }, []);
  if (!waiting) return null;
  const apply = () => {
    updateRequested = true;
    waiting.postMessage("SKIP_WAITING");
  };
  return html`<div class="toast" role="status">Nouvelle version disponible
    <button class="btn primary" onClick=${apply}>Recharger</button></div>`;
}

function App() {
  const route = useRoute();
  const v = view(route);
  const active = v.tab ?? route.name;
  useEffect(() => { document.title = `${v.title} · Français B2`; }, [v.title]);
  return html`<div class="shell">
    <header class="topbar">
      ${v.back ? html`<a class="back btn" href=${v.back} aria-label="Retour" style="border:0;background:none">‹</a>` : null}
      <div class="title">${v.title}</div>
      <${Tabs} active=${active} className="topnav" />
    </header>
    <main>${v.body}</main>
    <${Tabs} active=${active} className="tabbar" />
    <${UpdateToast} />
    <${Celebrations} />
  </div>`;
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  navigator.serviceWorker.register("sw.js").then((reg) => {
    const announce = (worker) => dispatchEvent(new CustomEvent("sw-update", { detail: worker }));
    if (reg.waiting && navigator.serviceWorker.controller) announce(reg.waiting);
    reg.addEventListener("updatefound", () => {
      const worker = reg.installing;
      worker?.addEventListener("statechange", () => {
        if (worker.state === "installed" && navigator.serviceWorker.controller) announce(worker);
      });
    });
  }).catch(() => { /* offline support unavailable (e.g. plain http on a LAN IP) */ });
  // Reload only when the user accepted an update. The first install also fires
  // controllerchange (clients.claim), and reloading then would wipe whatever is on screen.
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (updateRequested) location.reload();
  });
}

let updateRequested = false;
const root = document.getElementById("app");
root.textContent = ""; // drop the static "Loading…" placeholder before Preact takes over

async function start() {
  try {
    await loadManifest();
  } catch (error) {
    return render(html`<main><${ErrorBox} error=${error} retry=${() => location.reload()} /></main>`, root);
  }
  render(html`<${App} />`, root);
  pruneDataCache().catch(() => {});
  protectStorage();
  startAutoSync();
}

async function boot() {
  // Precaching the shell competes with the first load for bandwidth and CPU, so it waits for the
  // load event (every preloaded module and data file is in by then). Offline use only needs it to
  // finish before the next visit.
  if (document.readyState === "complete") registerServiceWorker();
  else addEventListener("load", registerServiceWorker, { once: true });
  // The progress log doesn't depend on the data key; read it while meta and the manifest load.
  getEvents().catch(() => {});
  try {
    await fetchMeta();
  } catch (error) {
    return render(html`<main><${ErrorBox} error=${error} retry=${() => location.reload()} /></main>`, root);
  }
  if (await restoreKey()) return start();
  render(html`<${Unlock} onUnlocked=${start} />`, root);
}

boot();
