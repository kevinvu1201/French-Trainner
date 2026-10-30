import { ReadinessBars } from "../charts.js";
import { formatDate, pct } from "../core/analytics.js";
import { installed, manifest, moduleInfo } from "../core/data.js";
import { useEvents } from "../core/events.js";
import { buildModel, streak } from "../core/mastery.js";
import { dailyPlan, setFinished } from "../core/plan.js";
import { href } from "../core/router.js";
import { saveSetting, settingsFrom } from "../core/settings.js";
import { kvGet, kvSet } from "../core/store.js";
import { useSyncStatus } from "../core/sync.js";
import { html, useMemo, useState } from "../lib.js";
import { Loading, useAsync } from "../ui.js";

const DAY = 86_400_000;
const losLabel = (id) => id.replace(/^los\./, "Objectif ");

/** Shown while the browser may still clear our data: not installed and storage not marked persistent. */
function InstallHint() {
  const [hidden, setHidden] = useState(false);
  const { value: show } = useAsync(async () => !installed() && !(await navigator.storage?.persisted?.()) && !(await kvGet("installHintDismissed")), []);
  if (!show || hidden) return null;
  const dismiss = () => { setHidden(true); kvSet("installHintDismissed", true); };
  return html`<div class="banner stack" role="note">
    <span>Vos progrès sont enregistrés dans ce navigateur, qui peut les effacer si vous ne revenez pas pendant un moment. Installez l'application pour les protéger
      (et pour l'utiliser hors ligne) : sur Android, menu Chrome → <b>Installer l'application</b> ; sur iPhone, Safari → Partager → <b>Sur l'écran d'accueil</b>.
      Exporter ou synchroniser vos progrès (Réglages) en garde aussi une copie.</span>
    <div><button class="btn" onClick=${dismiss}>Compris</button></div>
  </div>`;
}

const WEEKDAYS = ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."];
const plural = (n, word) => `${n} ${word}${n > 1 ? "s" : ""}`;
const dayLabel = (ts) => `${WEEKDAYS[new Date(ts).getDay()]} ${new Date(ts).getDate()}`;

/** Plan modules with a tick box to mark each finished (the row itself opens the module). */
function PlanList({ modules }) {
  return html`<ul class="list plan-list">${modules.map((mod) => html`<li>
    <button class=${`tick ${mod.done ? "on" : ""}`} aria-pressed=${!!mod.done} aria-label=${`Terminé : ${mod.title}`}
      onClick=${() => setFinished(mod.id, mod.topic, !mod.done)}>${mod.done ? "✓" : ""}</button>
    <a href=${href("m", mod.id)}><div class="grow"><div class=${mod.done ? "muted" : ""}>${mod.title}</div>
      <div class="sub">${mod.topicName} · ${plural(mod.load, "objectif")}${mod.carried ? " · " : ""}${mod.carried ? html`<span class="chip review">en retard</span>` : null}</div></div>
      <span class="chev">›</span></a></li>`)}</ul>`;
}

function PaceLine({ plan }) {
  const d = plan.aheadDays;
  const rebalance = html`<button class="btn" onClick=${() => saveSetting("plan_reset", new Date().toISOString().slice(0, 10))}>Rééquilibrer le plan</button>`;
  if (d === 0) return html`<p class="small" style="color:var(--ok)">Dans les temps</p>`;
  return html`<div class="spread"><span class="small" style=${`color:var(${d > 0 ? "--ok" : "--warn"})`}>
      ${d > 0 ? `${plural(Math.abs(d), "jour")} d'avance` : `${plural(Math.abs(d), "jour")} de retard`}
      <span class="muted">${d > 0 ? " · rééquilibrez pour alléger chaque jour" : " · rééquilibrez pour répartir le retard sur les jours restants"}</span></span>
    ${rebalance}</div>`;
}

function PlanSummary({ plan }) {
  if (plan.daysLeft == null) return html`<p class="small muted">${plan.remaining} leçons sur ${plan.total} pas encore commencées.${" "}
    <a href="#/settings">Indiquez la date de votre examen</a> pour obtenir un plan jour par jour.</p>`;
  if (plan.inFinalReview) return html`<p class="small">Période de révision finale : pas de nouvelle leçon. Privilégiez les séances intelligentes et les révisions.</p>`;
  const today = plan.schedule[0];
  const done = plan.today.filter((m) => m.done).length;
  return html`<p class="small muted">${plan.remaining} leçons sur ${plan.total} à terminer d'ici le ${formatDate(plan.finishBy)} (les ${plan.finalReview} derniers jours
    avant l'examen sont réservés aux révisions). Le week-end compte ${plan.ratio} fois la charge d'un jour de semaine.</p>
    <${PaceLine} plan=${plan} />
    ${plan.today.length ? html`<p class="small"><strong>Aujourd'hui : ${plural(plan.today.length, "leçon")} · ${plural(today.load, "objectif")}</strong>${done ? ` · ${done} terminée(s)` : ""}
      ${plan.carried ? html` · ${plan.carried} en retard des jours précédents` : null}</p>` : null}`;
}

/** The next seven days as small cells, then the whole schedule on demand. */
function WeekAhead({ schedule }) {
  const week = schedule.slice(1, 8);
  return html`${week.length ? html`<div>
      <div class="small muted">Les prochains jours (leçons · objectifs)</div>
      <div class="week">${week.map((d) => html`<div class=${`day ${d.weekend ? "weekend" : ""}`}>
        <div class="wd">${WEEKDAYS[new Date(d.date).getDay()]} ${new Date(d.date).getDate()}</div><strong>${d.modules.length}</strong>
        <div class="wd">${d.load} obj.</div></div>`)}</div>
    </div>` : null}
    <details>
      <summary class="small">Tout le planning (${schedule.length} jours)</summary>
      <ul class="plain small schedule">${schedule.map((d, k) => html`<li class=${d.weekend ? "weekend" : ""}>
        <strong>${k === 0 ? "Aujourd'hui" : dayLabel(d.date)}</strong> <span class="muted">${formatDate(d.date)} · ${plural(d.load, "objectif")}</span>
        <div>${d.modules.length ? d.modules.map((m) => m.title).join(" · ") : html`<span class="muted">Jour de révision</span>`}</div></li>`)}</ul>
    </details>`;
}

/** One line of Gist sync state, once sync is set up. */
function SyncLine() {
  const s = useSyncStatus();
  if (!s?.token || !s.id) return null;
  if (s.lastError) return html`<p class="small" style="color:var(--bad)">Échec de la synchronisation (${s.lastError}). <a href="#/settings">Voir les réglages</a></p>`;
  return s.lastSync ? html`<p class="small muted">Synchronisé avec vos autres appareils ${formatAgo(s.lastSync)}</p>` : null;
}

function formatAgo(ts) {
  const min = Math.round((Date.now() - ts) / 60_000);
  if (min < 1) return "à l'instant";
  if (min < 60) return `il y a ${min} min`;
  return min < 1440 ? `il y a ${Math.round(min / 60)} h` : `le ${formatDate(ts)}`;
}

export function Home() {
  const m = manifest();
  const events = useEvents();
  const { value: last } = useAsync(() => kvGet("lastModule"), []);
  const count = events?.length ?? -1;
  const settings = useMemo(() => (events ? settingsFrom(events) : null), [count]);
  const model = useMemo(() => (events ? buildModel(events, m, Date.now(), { target: settings.target ?? undefined }) : null), [count]);
  if (!events) return html`<${Loading} />`;

  const target = model.overall.target;
  const plan = dailyPlan(m, events, settings);
  const days = streak(events);
  const dueQuestions = [...model.cardMeta].filter(([id, c]) => c.kind === "question" && !id.startsWith("set.") && model.status.get(id).overdueDays >= 0).length;
  const dueCards = [...model.cardMeta].filter(([id, c]) => c.kind === "formula" && model.status.get(id).overdueDays >= 0);
  // Due cards decide which deck the button opens; with none due, it opens the vocabulary deck for new cards.
  const cardTopic = dueCards.length ? mostCommon(dueCards.map(([, c]) => c.topic))
    : m.topics.find((t) => t.counts.formulas && !t.weight)?.id ?? null;
  const weak = [...model.los.values()].filter((l) => l.n > 0).sort((a, b) => b.priority - a.priority).slice(0, 5);
  const lastInfo = last && moduleInfo(last);
  const answered = events.some((e) => e.type === "answer");

  return html`<div class="stack">
    <h1>Français B2</h1>
    ${!m.weights_verified ? html`<p class="banner">Les poids des thèmes ne sont pas encore validés (<code>config/exam_weights.yaml</code>).</p>` : null}
    <${InstallHint} />
    <${SyncLine} />

    <div class="tiles">
      <a class="tile" href=${plan.daysLeft == null ? "#/settings" : "#/"} style="text-decoration:none;color:inherit">
        <div class="k">DELF B2</div>
        <div class="v">${plan.daysLeft == null ? "Date ?" : plan.daysLeft >= 0 ? plural(plan.daysLeft, "jour") : "Passé"}</div>
        <div class="sub">${settings.exam_date ? formatDate(`${settings.exam_date}T00:00`) : "touchez pour la régler"}</div></a>
      <div class="tile"><div class="k">Préparation</div><div class="v">${answered ? pct(model.overall.mean) : "—"}</div>
        <div class="sub">${answered ? `probablement ${pct(model.overall.lo)}–${pct(model.overall.hi)} · objectif ${pct(target)}` : "entraînez-vous pour l'estimer"}</div></div>
      <div class="tile"><div class="k">Série</div><div class="v">${plural(days, "jour")}</div><div class="sub">d'affilée avec de l'entraînement</div></div>
      <div class="tile"><div class="k">À réviser</div><div class="v">${dueQuestions + dueCards.length}</div>
        <div class="sub">${dueQuestions} questions · ${dueCards.length} cartes</div></div>
    </div>

    <section class="card stack">
      <strong>Le plan du jour</strong>
      <${PlanSummary} plan=${plan} />
      ${plan.today.length ? html`<${PlanList} modules=${plan.today} />`
        : plan.schedule.length ? html`<p class="small muted">Pas de nouvelle leçon aujourd'hui. Une séance intelligente entretient ce que vous avez déjà vu.</p>` : null}
      ${plan.schedule.length && plan.today.every((m) => m.done) && plan.studyAhead.length ? html`
        ${plan.today.length ? html`<p class="small" style="color:var(--ok)"><strong>Fini pour aujourd'hui ✓</strong></p>` : null}
        <p class="small"><strong>Prendre de l'avance</strong><span class="muted"> · chaque leçon terminée en avance allège les jours suivants</span></p>
        <${PlanList} modules=${plan.studyAhead} />` : null}
      ${plan.schedule.length ? html`<${WeekAhead} schedule=${plan.schedule} />` : null}
      <div class="row">
        <a class="btn primary" href=${href("practice", "smart", String(settings.daily_minutes))}>Séance intelligente · ${settings.daily_minutes} min</a>
        ${cardTopic ? html`<a class="btn" href=${href("practice", "cards", cardTopic)}>Cartes${dueCards.length ? ` (${dueCards.length} à revoir)` : ""}</a>` : null}
        ${lastInfo ? html`<a class="btn" href=${href("m", last)}>Reprendre la lecture</a>` : null}
      </div>
    </section>

    ${weak.length ? html`<h2 class="section-title">Points faibles (priorité la plus haute)</h2>
      <ul class="list">${weak.map((l) => html`<li><a href=${href("practice", "drill", l.topic, l.module)}>
        <div class="grow"><strong>${losLabel(l.id)}</strong>
          <div class="sub">maîtrise ${pct(l.mean)} (${pct(l.lo)}–${pct(l.hi)}) · ${plural(l.n, "réponse")} · ${l.last ? `il y a ${plural(Math.round((Date.now() - l.last) / DAY), "jour")}` : ""}</div></div>
        <span class=${`chip ${l.mean < target ? "warn" : ""}`}>${pct(l.mean)}</span><span class="chev">›</span></a></li>`)}</ul>` : null}

    <h2 class="section-title">Préparation par thème</h2>
    <p class="small muted">Maîtrise moyenne des objectifs de chaque thème ; un objectif jamais pratiqué compte au niveau du hasard.
      Le trait fin montre la fourchette probable ; le repère indique votre objectif de ${pct(target)}.</p>
    <${ReadinessBars} target=${target} rows=${[...model.topics.values()].filter((t) => t.weight > 0).sort((a, b) => b.weight - a.weight)
      .map((t) => ({ label: t.name, mean: t.mean, lo: t.lo, hi: t.hi, coverage: t.coverage, weight: t.weight }))} />
    <p class="small muted">Contenu ${m.content_version} · mis à jour le ${formatDate(m.built_at)}</p>
  </div>`;
}

function mostCommon(list) {
  const counts = new Map();
  for (const x of list) counts.set(x, (counts.get(x) ?? 0) + 1);
  return [...counts].sort((a, b) => b[1] - a[1])[0][0];
}
