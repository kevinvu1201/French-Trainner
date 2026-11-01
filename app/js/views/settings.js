import { downloadAll, forgetKey, isEncrypted, manifest, storageInfo } from "../core/data.js";
import { useEvents } from "../core/events.js";
import { saveSetting, settingsFrom } from "../core/settings.js";
import { downloadProgress, importFile, saveGistSettings, syncGist, useSyncStatus } from "../core/sync.js";
import { fxPrefs, feedback, setFxPref } from "../core/fx.js";
import { getTheme, setTheme } from "../core/theme.js";
import { html, useState } from "../lib.js";
import { useAsync } from "../ui.js";

const THEMES = { system: "Système", light: "Clair", dark: "Sombre" };
const mb = (bytes) => (bytes >= 1024 ** 3 ? `${(bytes / 1024 ** 3).toFixed(1)} GB` : `${(bytes / 1048576).toFixed(1)} MB`);

function ProgressData() {
  const events = useEvents();
  const [msg, setMsg] = useState(null); // {ok, text}
  const [busy, setBusy] = useState(false);
  const gist = useSyncStatus();
  const [token, setToken] = useState(null);
  const [gistId, setGistId] = useState(null);
  const run = async (fn) => {
    setBusy(true); setMsg(null);
    try { setMsg({ ok: true, text: await fn() }); } catch (e) { setMsg({ ok: false, text: e.message }); }
    setBusy(false);
  };
  const exportNow = () => run(async () => `${await downloadProgress()} événements enregistrés dans un fichier.`);
  const importNow = (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) run(async () => {
      const r = await importFile(file);
      return `${r.fresh.length} nouveaux événements ajoutés ; ${r.duplicates} étaient déjà là${r.invalid ? ` ; ${r.invalid} invalides ignorés` : ""}.`;
    });
  };
  const sync = () => run(async () => {
    const settings = { ...gist, token: token ?? gist.token, id: gistId ?? gist.id };
    await saveGistSettings(settings);
    const r = await syncGist(settings);
    setGistId(r.id);
    return `Synchronisé : ${r.pulled} nouveaux événements reçus du Gist ; ${r.pushed} événements y sont maintenant enregistrés.`;
  });
  return html`<section class="card stack">
    <strong>Progrès et appareils</strong>
    <p class="small muted">${events ? `${events.length} événements sur cet appareil.` : ""} Vos progrès sont un journal d'événements : fusionner deux
      appareils ne compte jamais rien en double, et importer deux fois le même fichier ne change rien.</p>
    <div class="row">
      <button class="btn" disabled=${busy} onClick=${exportNow}>Exporter mes progrès</button>
      <label class="btn">Importer des progrès<input type="file" accept="application/json,.json" class="sr-only" onChange=${importNow} /></label>
    </div>
    <details>
      <summary>Synchroniser avec un Gist GitHub privé (facultatif)</summary>
      <p class="small muted">Créez un jeton GitHub avec seulement la permission <code>gist</code>. Il reste sur cet appareil. Laissez l'identifiant du Gist
        vide sur le premier appareil, puis copiez l'identifiant créé sur vos autres appareils. Ensuite, chaque appareil se synchronise tout seul
        à l'ouverture, une minute après vos réponses et quand vous quittez l'application. Ce Gist est distinct de celui de l'application CFA.</p>
      <label class="stack small">Jeton<input type="password" autocomplete="off" value=${token ?? gist?.token ?? ""} onInput=${(e) => setToken(e.target.value)} /></label>
      <label class="stack small">Identifiant du Gist<input type="text" value=${gistId ?? gist?.id ?? ""} onInput=${(e) => setGistId(e.target.value.trim())} /></label>
      <div class="row"><button class="btn primary" disabled=${busy || !(token ?? gist?.token)} onClick=${sync}>Synchroniser</button>
        ${gist?.lastSync ? html`<span class="small muted">Dernière synchronisation : ${new Date(gist.lastSync).toLocaleString("fr-FR")}</span>` : null}</div>
    </details>
    ${msg ? html`<p class="small" role="status" style=${`color:var(${msg.ok ? "--ok" : "--bad"})`}>${msg.text}</p>` : null}
  </section>`;
}

function StudySettings() {
  const events = useEvents();
  if (!events) return null;
  const s = settingsFrom(events);
  const defaultTarget = manifest().scoring.readiness.target;
  const target = s.target ?? defaultTarget;
  return html`<section class="card stack">
    <strong>Plan de travail</strong>
    <div class="spread"><span>Objectif quotidien<span class="small muted" style="display:block">XP par jour (une question juste ≈ 10 XP)</span></span>
      <div class="seg" role="group" aria-label="Objectif quotidien">${[30, 50, 100, 150].map((n) => html`<button aria-pressed=${s.daily_xp === n}
        onClick=${() => saveSetting("daily_xp", n)}>${n}</button>`)}</div></div>
    <label class="spread"><span>Date du DELF B2</span>
      <input type="date" value=${s.exam_date ?? ""} onChange=${(e) => saveSetting("exam_date", e.target.value || null)} /></label>
    <div class="spread"><span>Séance intelligente quotidienne</span>
      <div class="seg" role="group" aria-label="Minutes par jour">${[10, 20, 30].map((m) => html`<button aria-pressed=${s.daily_minutes === m}
        onClick=${() => saveSetting("daily_minutes", m)}>${m} min</button>`)}</div></div>
    <div class="spread"><span>Nouvelles cartes par jour<span class="small muted" style="display:block">dans chaque paquet (vocabulaire, règles)</span></span>
      <div class="seg" role="group" aria-label="Nouvelles cartes par jour">${[10, 20, 30, 50].map((n) => html`<button aria-pressed=${s.new_cards === n}
        onClick=${() => saveSetting("new_cards", n)}>${n}</button>`)}</div></div>
    <div class="spread"><span>Charge du week-end<span class="small muted" style="display:block">par rapport à un jour de semaine, dans le plan</span></span>
      <div class="seg" role="group" aria-label="Charge du week-end">${[1, 1.5, 2, 3].map((r) => html`<button aria-pressed=${s.weekend_ratio === r}
        onClick=${() => saveSetting("weekend_ratio", r)}>${r}×</button>`)}</div></div>
    <label class="spread"><span>Objectif de préparation (%)</span>
      <input type="number" min="50" max="95" step="1" value=${Math.round(target * 100)} style="width:6em"
        onChange=${(e) => { const v = Number(e.target.value); if (v >= 50 && v <= 95) saveSetting("target", v / 100); }} /></label>
    <p class="small muted">Les réglages sont enregistrés avec vos progrès : ils vous suivent d'un appareil à l'autre.</p>
  </section>`;
}

export function Settings() {
  const [theme, setThemeState] = useState(getTheme());
  const [fx, setFx] = useState(fxPrefs());
  const [dl, setDl] = useState(null); // {done, total} | "done" | Error
  const [tick, setTick] = useState(0);
  const { value: storage } = useAsync(storageInfo, [tick]);
  const m = manifest();

  const pickTheme = (t) => { setTheme(t); setThemeState(t); };
  const download = async () => {
    setDl({ done: 0, total: m.topics.length });
    try {
      await navigator.storage?.persist?.();
      await downloadAll((done, total) => setDl({ done, total }));
      setDl("done");
    } catch (e) {
      setDl(e);
    }
    setTick((n) => n + 1);
  };
  const lock = async () => { await forgetKey(); location.reload(); };

  return html`<div class="stack">
    <h1>Réglages</h1>

    <${StudySettings} />
    <${ProgressData} />

    <section class="card stack">
      <strong>Sons et vibrations</strong>
      <label class="spread"><span>Sons de réussite</span><input type="checkbox" checked=${fx.sound}
        onChange=${(e) => { setFxPref("sound", e.target.checked); setFx(fxPrefs()); if (e.target.checked) feedback("right"); }} /></label>
      <label class="spread"><span>Vibrations</span><input type="checkbox" checked=${fx.vibrate}
        onChange=${(e) => { setFxPref("vibrate", e.target.checked); setFx(fxPrefs()); }} /></label>
    </section>

    <section class="card stack">
      <strong>Apparence</strong>
      <div class="seg" role="group" aria-label="Thème">
        ${["system", "light", "dark"].map((t) => html`<button aria-pressed=${theme === t} onClick=${() => pickTheme(t)}>
          ${THEMES[t]}</button>`)}
      </div>
    </section>

    <section class="card stack">
      <strong>Hors ligne</strong>
      <p class="small muted">Les thèmes que vous ouvrez sont enregistrés automatiquement. Téléchargez tout une fois en Wi-Fi pour réviser partout, même sans réseau (dans le train par exemple).</p>
      ${dl && typeof dl === "object" && !(dl instanceof Error) ? html`
        <div class="progress" role="progressbar" aria-valuenow=${dl.done} aria-valuemax=${dl.total}>
          <span style=${`width:${(100 * dl.done) / Math.max(dl.total, 1)}%`}></span></div>
        <p class="small muted">${dl.done} fichiers sur ${dl.total}</p>`
      : html`<div><button class="btn primary" onClick=${download}>${dl === "done" ? "Téléchargé ✓ Vérifier à nouveau" : "Tout télécharger"}</button></div>`}
      ${dl instanceof Error ? html`<p class="small" style="color:var(--bad)">Téléchargement interrompu : ${dl.message}</p>` : null}
      ${storage ? html`<p class="small muted">L'application utilise ${mb(storage.usage)} sur cet appareil${m.content_bytes ? ` (tout le contenu fait environ ${Math.max(1, Math.ceil(m.content_bytes / 1048576))} Mo)` : ""}
        ${storage.persisted ? " · protégé contre le nettoyage automatique" : ""}</p>` : null}
    </section>

    ${isEncrypted() ? html`<section class="card stack">
      <strong>Phrase de passe</strong>
      <p class="small muted">Cet appareil mémorise la phrase de passe. Oubliez-la pour verrouiller à nouveau le contenu.</p>
      <div><button class="btn" onClick=${lock}>Oublier la phrase de passe</button></div>
    </section>` : null}

    <section class="card small muted">
      Contenu ${m.content_version} · mis à jour le ${new Date(m.built_at).toLocaleString("fr-FR")}
    </section>
  </div>`;
}
