// Game components: the Home hero (level, daily goal ring, streak, week), the badge grid, and the
// celebration layer that reacts to new XP (level-ups, badges, daily goal) anywhere in the app.

import { getEvents, onEventsChanged } from "./core/events.js";
import { confetti, feedback } from "./core/fx.js";
import { BADGES, gameState } from "./core/game.js";
import { settingsFrom } from "./core/settings.js";
import { html, useEffect, useState } from "./lib.js";

const WEEKDAYS = ["D", "L", "M", "M", "J", "V", "S"];

export function useGame(events) {
  return events ? gameState(events, settingsFrom(events)) : null;
}

/** Circular progress ring with content in the middle. */
export function Ring({ value, size = 92, stroke = 9, children, done }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const v = Math.max(0, Math.min(1, value));
  return html`<div class=${`ring ${done ? "done" : ""}`} style=${`width:${size}px;height:${size}px`}>
    <svg viewBox=${`0 0 ${size} ${size}`} aria-hidden="true">
      <circle class="ring-bg" cx=${size / 2} cy=${size / 2} r=${r} stroke-width=${stroke} />
      <circle class="ring-fg" cx=${size / 2} cy=${size / 2} r=${r} stroke-width=${stroke}
        stroke-dasharray=${c} stroke-dashoffset=${c * (1 - v)} transform=${`rotate(-90 ${size / 2} ${size / 2})`} />
    </svg>
    <div class="ring-in">${children}</div>
  </div>`;
}

export function GameHero({ game }) {
  const max = Math.max(game.goal, ...game.week.map((d) => d.xp));
  return html`<section class="hero-card">
    <div class="hero-top">
      <div class="level-badge" aria-label=${`Niveau ${game.level}`}><span>${game.level}</span></div>
      <div class="grow">
        <div class="hero-title">${game.title}</div>
        <div class="xp-bar" role="progressbar" aria-valuenow=${game.into} aria-valuemax=${game.need}>
          <span style=${`width:${(100 * game.into) / game.need}%`}></span></div>
        <div class="small hero-sub">${game.into} / ${game.need} XP vers le niveau ${game.level + 1} · ${game.xp} XP au total</div>
      </div>
    </div>
    <div class="hero-row">
      <${Ring} value=${game.today / game.goal} done=${game.goalDone}>
        <strong>${game.today}</strong><span>/ ${game.goal} XP</span>
      </${Ring}>
      <div class="flame" data-on=${game.streak > 0}>
        <div class="flame-icon" aria-hidden="true">🔥</div>
        <strong>${game.streak}</strong><span>${game.streak > 1 ? "jours" : "jour"}</span>
      </div>
      <div class="week" aria-label="XP des 7 derniers jours">
        ${game.week.map((d, i) => html`<div class=${`wcol ${i === 6 ? "today" : ""} ${d.xp >= game.goal ? "met" : ""}`} title=${`${d.xp} XP`}>
          <div class="wbar"><span style=${`height:${max ? (100 * d.xp) / max : 0}%`}></span></div>
          <div class="wd">${WEEKDAYS[d.date.getDay()]}</div></div>`)}
      </div>
    </div>
    <p class="small hero-msg">${message(game)}</p>
  </section>`;
}

function message(g) {
  if (g.goalDone) return g.today >= 2 * g.goal ? "Objectif doublé aujourd'hui. Impressionnant ! 🎉" : "Objectif du jour atteint ✓ Encore un peu pour la série parfaite ?";
  if (g.today === 0) return g.streak ? `Ne cassez pas votre série de ${g.streak} jours : une petite séance suffit.` : "Une séance de 5 minutes pour lancer votre série ?";
  return `Plus que ${g.goal - g.today} XP pour l'objectif du jour.`;
}

export function BadgeGrid({ game, limit }) {
  const list = BADGES.map((b) => ({ ...b, at: game.earned.get(b.id) }));
  const shown = limit ? [...list.filter((b) => b.at), ...list.filter((b) => !b.at)].slice(0, limit) : list;
  return html`<div class="badges">
    ${shown.map((b) => html`<div class=${`badge ${b.at ? "on" : ""}`} title=${b.how}>
      <div class="badge-icon" aria-hidden="true">${b.at ? b.icon : "🔒"}</div>
      <div class="badge-name">${b.name}</div>
      <div class="badge-how">${b.how}</div>
    </div>`)}
  </div>`;
}

/**
 * Watches the log; when new XP brings a level-up, a badge or the daily goal, celebrates it.
 * The state at load is the baseline, so opening the app never replays old celebrations.
 */
export function Celebrations() {
  const [queue, setQueue] = useState([]);
  useEffect(() => {
    let prev = null;
    const check = async () => {
      const events = await getEvents();
      const g = gameState(events, settingsFrom(events));
      if (prev) {
        const found = [];
        if (g.level > prev.level) found.push({ kind: "level", level: g.level, title: g.title });
        for (const b of BADGES) if (g.earned.has(b.id) && !prev.earned.has(b.id)) found.push({ kind: "badge", badge: b });
        if (g.goalDone && !prev.goalDone && g.today > 0) found.push({ kind: "goal", today: g.today, streak: g.streak });
        if (found.length) setQueue((q) => [...q, ...found]);
      }
      prev = g;
    };
    check();
    return onEventsChanged(check);
  }, []);
  const item = queue[0];
  useEffect(() => {
    if (!item) return;
    if (item.kind === "level") { feedback("level"); confetti({ pieces: 200, duration: 3200 }); }
    else { feedback("badge"); if (item.kind === "goal") confetti({ pieces: 90 }); }
    if (item.kind === "level") return;
    const t = setTimeout(() => setQueue((q) => q.slice(1)), 3200);
    return () => clearTimeout(t);
  }, [item]);
  if (!item) return null;
  const close = () => setQueue((q) => q.slice(1));
  if (item.kind === "level") {
    return html`<div class="levelup" role="dialog" aria-label="Nouveau niveau" onClick=${close}>
      <div class="levelup-card">
        <div class="small">Nouveau niveau !</div>
        <div class="levelup-num">${item.level}</div>
        <div class="levelup-title">${item.title}</div>
        <button class="btn primary" onClick=${close}>Continuer</button>
      </div>
    </div>`;
  }
  return html`<div class="celebrate-toast" role="status" onClick=${close}>
    ${item.kind === "badge"
      ? html`<span class="ct-icon">${item.badge.icon}</span><div><strong>Badge débloqué : ${item.badge.name}</strong><div class="small">${item.badge.how}</div></div>`
      : html`<span class="ct-icon">🎯</span><div><strong>Objectif du jour atteint !</strong><div class="small">${item.today} XP · série de ${item.streak} jour${item.streak > 1 ? "s" : ""}</div></div>`}
  </div>`;
}
