import { AccuracyBars, AccuracyLine, CoverageGrid, DailyColumns } from "../charts.js";
import {
  MIN_N, PACE_MS, TARGET, answers, calibration, coverage, daily, formatDate, formatMs, groupStats, median, pct, rollingAccuracy,
} from "../core/analytics.js";
import { manifest, moduleInfo } from "../core/data.js";
import { useEvents } from "../core/events.js";
import { buildModel, readinessTrend } from "../core/mastery.js";
import { settingsFrom } from "../core/settings.js";
import { href } from "../core/router.js";
import { html, useEffect, useState } from "../lib.js";
import { BadgeGrid, useGame } from "../game-ui.js";
import { Loading } from "../ui.js";

const losLabel = (id) => id.replace(/^los\./, "Objectif ");

export function Stats() {
  const events = useEvents();
  if (!events) return html`<${Loading} />`;
  const m = manifest();
  const ans = answers(events);
  const topicName = new Map(m.topics.map((t) => [t.id, t.name]));
  const modules = m.topics.flatMap((t) => t.readings.flatMap((r) => r.modules));
  const states = coverage(modules.map((x) => x.id), events);

  if (!ans.length) {
    return html`<div class="stack">
      <h1>Progrès</h1>
      <p class="muted">Pas encore de réponses. Faites quelques exercices : votre réussite, votre rythme et votre calibrage apparaîtront ici.</p>
      <a class="btn primary" href="#/practice">Commencer</a>
      <h2 class="section-title">Avancement</h2>
      <${CoverageGrid} topics=${m.topics} states=${states} />
      <${Reported} events=${events} />
    </div>`;
  }

  const correct = ans.filter((e) => e.payload.correct).length;
  const medMs = median(ans.map((e) => e.payload.ms));
  const cal = calibration(ans);
  const byTopic = groupStats(ans, (e) => e.payload.topic)
    .map((g) => ({ ...g, label: topicName.get(g.key) ?? g.key }))
    .sort((a, b) => b.n - a.n);
  const byLos = groupStats(ans, (e) => e.payload.los);
  const days = daily(ans, 30);
  const rolling = rollingAccuracy(days);
  const overPace = ans.filter((e) => e.payload.ms > PACE_MS).length;
  const sc = m.scoring;
  const target = settingsFrom(events).target ?? undefined;
  const model = buildModel(events, m, Date.now(), { target });

  return html`<div class="stack">
    <h1>Progrès</h1>
    ${(() => { const game = useGame(events); return html`<h2 class="section-title">Badges · ${game.earned.size} / 20 · meilleure série ${game.bestCombo} 🔥</h2>
      <${BadgeGrid} game=${game} />`; })()}
    <div class="tiles">
      <div class="tile"><div class="k">Réponses</div><div class="v">${ans.length}</div><div class="sub">${events.filter((e) => e.type === "review").length} cartes révisées</div></div>
      <div class="tile"><div class="k">Réussite</div><div class="v">${ans.length >= MIN_N ? pct(correct / ans.length) : "—"}</div>
        <div class="sub">${correct}/${ans.length} · objectif ${pct(TARGET)}</div></div>
      <div class="tile"><div class="k">Temps médian</div><div class="v">${formatMs(medMs)}</div>
        <div class="sub">${pct(overPace / ans.length)} au-delà de ${formatMs(PACE_MS)}</div></div>
      <div class="tile"><div class="k">Sûr mais faux</div><div class="v">${cal.sureWrong.length}</div><div class="sub">les plus dangereuses</div></div>
    </div>

    <h2 class="section-title">Préparation</h2>
    <div class="card">
      <div class="spread"><div><div class="small muted">Préparation pondérée</div>
        <div class="hero">${pct(model.overall.mean)}</div>
        <div class="small muted">probablement ${pct(model.overall.lo)}–${pct(model.overall.hi)} · objectif ${pct(model.overall.target)}</div></div>
        <span class=${`chip ${model.overall.mean >= model.overall.target ? "maintenance" : "review"}`}>
          ${model.overall.mean >= model.overall.target ? "Objectif atteint" : `encore ${Math.round((model.overall.target - model.overall.mean) * 100)} points`}</span></div>
      <div class="small muted" style="margin-top:8px">Préparation, en fin de journée</div>
      <${ReadinessTrend} events=${events} target=${model.overall.target} />
    </div>

    <h2 class="section-title">Maîtrise par objectif (pratiqués)</h2>
    ${(() => {
      const rows = [...model.los.values()].filter((l) => l.n > 0).sort((a, b) => b.priority - a.priority);
      return html`<details class="card" open=${rows.length <= 12}>
        <summary>${rows.length} objectifs, par priorité</summary>
        <div class="table-wrap"><table>
          <thead><tr><th>Objectif</th><th class="n">n</th><th class="n">Maîtrise</th><th class="n">Fourchette</th><th class="n">Mémoire</th><th class="n">Priorité</th></tr></thead>
          <tbody>${rows.map((l) => html`<tr>
            <td><a href=${href("practice", "drill", l.topic, l.module)}>${losLabel(l.id)}</a></td>
            <td class="n">${l.n}</td><td class="n">${pct(l.mean)}</td><td class="n">${pct(l.lo)}–${pct(l.hi)}</td>
            <td class="n">${pct(l.recall)}</td><td class="n">${l.priority.toFixed(3)}</td></tr>`)}</tbody>
        </table></div>
      </details>`;
    })()}
    <details class="card">
      <summary>Comment la maîtrise et la priorité sont calculées</summary>
      <p class="small">Chaque réponse compte avec un poids 0,5^(âge / ${sc.mastery.half_life_days} jours). La maîtrise est la moyenne d'une loi Beta a posteriori dont l'a priori
        (poids de ${sc.mastery.prior_strength} réponses) est centré sur votre réussite dans le thème pour un objectif pratiqué, et sur ${pct(sc.mastery.untouched_mean)} (le hasard) sinon.
        Une bonne réponse « au hasard » compte pour ${sc.mastery.guess_credit} succès. La fourchette est l'intervalle de crédibilité à ${pct(sc.mastery.interval)}.</p>
      <div class="formula-box">priorité = (1 − maîtrise) × poids du thème × max(${sc.priority.forgetting_floor}, 1 − mémoire) × (1 + ${sc.priority.uncertainty_k} / √(n + 1))</div>
      <p class="small">La mémoire est la probabilité FSRS-4.5 de répondre encore juste aujourd'hui aux questions de l'objectif (rétention visée
        ${pct(sc.spaced_repetition.desired_retention)}). Un objectif jamais pratiqué compte 1 pour l'oubli.
        Les séances intelligentes mélangent ${pct(sc.smart_session.mix.priority)} de priorités, ${pct(sc.smart_session.mix.review)} de révisions et
        ${pct(sc.smart_session.mix.maintenance)} d'entretien. Modifiez <code>config/priority.yaml</code> puis reconstruisez pour changer ces réglages.</p>
    </details>

    <h2 class="section-title">Réussite par thème</h2>
    <${AccuracyBars} rows=${byTopic} />

    <h2 class="section-title">Objectifs les plus faibles (au moins ${MIN_N} réponses)</h2>
    ${(() => {
      const weak = byLos.filter((g) => g.enough).sort((a, b) => a.acc - b.acc).slice(0, 8);
      const thin = byLos.filter((g) => !g.enough).length;
      return html`${weak.length ? html`<ul class="list">${weak.map((g) => {
        const { topic, module } = locateLos(g.key, m);
        return html`<li><a href=${module ? href("practice", "drill", topic, module) : href("practice", "drill", topic)}>
          <div class="grow"><strong>${losLabel(g.key)}</strong><div class="sub">${g.correct}/${g.n} justes · médiane ${formatMs(g.medianMs)}</div></div>
          <span class=${`chip ${g.acc < TARGET ? "warn" : ""}`}>${pct(g.acc)}</span><span class="chev">›</span></a></li>`;
      })}</ul>` : html`<p class="muted small">Aucun objectif n'a encore ${MIN_N} réponses ou plus.</p>`}
      ${thin ? html`<p class="small muted">${thin} autres objectifs ont moins de ${MIN_N} réponses : pas encore de conclusion.</p>` : null}`;
    })()}

    <h2 class="section-title">Calibrage</h2>
    <p class="small muted">Si vous êtes bien calibré(e), vos réponses « Sûr » sont presque toujours justes et vos réponses « Au hasard » environ 1 fois sur 3.</p>
    <${AccuracyBars} label="Réussite" rows=${cal.levels.map((l) => ({ key: l.confidence, label: l.label, n: l.n, acc: l.acc, correct: Math.round((l.acc ?? 0) * l.n) }))} />
    ${cal.sureWrong.length ? html`<details class="card">
      <summary>Sûr mais faux (${cal.sureWrong.length})</summary>
      <ul class="plain">${cal.sureWrong.slice(-10).reverse().map((e) => html`<li>
        <a href=${href("m", e.payload.module)}>${moduleInfo(e.payload.module)?.module.title ?? e.payload.module}</a>
        <span class="small muted"> · ${e.payload.los.map(losLabel).join(", ")} · ${formatDate(e.ts)}</span></li>`)}</ul>
    </details>` : null}
    ${cal.luckyRight.length ? html`<p class="small muted">${cal.luckyRight.length} réponses justes « au hasard » : considérez ces objectifs comme pas encore acquis.</p>` : null}

    <h2 class="section-title">Les 30 derniers jours</h2>
    <div class="card"><div class="small muted">Questions par jour</div><${DailyColumns} rows=${days} /></div>
    <div class="card"><div class="small muted">Réussite sur 7 jours glissants · trait épais = objectif de ${pct(TARGET)} (affiché dès ${MIN_N} réponses sur la période)</div><${AccuracyLine} rows=${rolling} /></div>
    <details class="card"><summary>Vue en tableau</summary>
      <div class="table-wrap"><table><thead><tr><th>Jour</th><th class="n">Réponses</th><th class="n">Justes</th><th class="n">Réussite 7 j</th></tr></thead>
      <tbody>${days.filter((d) => d.n).reverse().map((d) => html`<tr><td>${d.day}</td><td class="n">${d.n}</td><td class="n">${d.correct}</td>
        <td class="n">${pct(rolling.find((r) => r.day === d.day)?.acc)}</td></tr>`)}</tbody></table></div>
    </details>

    <h2 class="section-title">Avancement</h2>
    <${CoverageGrid} topics=${m.topics} states=${states} />

    <${Reported} events=${events} />
  </div>`;
}

/** Questions reported from the feedback panel, with a plain-text copy to send for fixing. */
function Reported({ events }) {
  const [copied, setCopied] = useState(false);
  const flags = events.filter((e) => e.type === "flag");
  if (!flags.length) return null;
  const text = flags.map((e) => `${e.payload.qid}: ${e.payload.note || "(pas de note)"}`).join("\n");
  const copy = () => navigator.clipboard?.writeText(text).then(() => setCopied(true), () => {});
  return html`<h2 class="section-title">Questions signalées</h2>
    <div class="card stack">
      <ul class="plain">${flags.slice().reverse().map((e) => html`<li><code>${e.payload.qid}</code>
        ${e.payload.module ? html` · <a href=${href("m", e.payload.module)}>${moduleInfo(e.payload.module)?.module.title ?? e.payload.module}</a>` : null}
        <span class="small muted"> · ${formatDate(e.ts)}</span><div class="small">${e.payload.note || "(pas de note)"}</div></li>`)}</ul>
      <div class="row"><button class="btn" onClick=${copy}>${copied ? "Copié ✓" : "Copier la liste"}</button>
        <span class="small muted">Collez-la à Claude pour faire corriger ces questions dans la prochaine version.</span></div>
    </div>`;
}

/** Topic and first module containing an LOS, from the manifest. */
function locateLos(losId, m) {
  for (const t of m.topics) {
    for (const r of t.readings) {
      const mod = r.modules.find((x) => x.los.includes(losId));
      if (mod) return { topic: t.id, module: mod.id };
    }
  }
  return { topic: m.topics[0].id, module: null };
}

/** The 30-day readiness line replays the log 30 times, so it's computed after first paint. */
function ReadinessTrend({ events, target }) {
  const [rows, setRows] = useState(null);
  useEffect(() => {
    const timer = setTimeout(() => setRows(readinessTrend(events, manifest(), 30)), 0);
    return () => clearTimeout(timer);
  }, [events.length]);
  return rows ? html`<${AccuracyLine} rows=${rows} label="Préparation" target=${target} />`
              : html`<p class="small muted" role="status">Calcul de la tendance…</p>`;
}
