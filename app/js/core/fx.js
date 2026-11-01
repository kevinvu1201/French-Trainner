// Feedback effects: short synthesized sounds (no files to download), vibration, confetti and
// floating "+XP" labels. Preferences are per device (localStorage); motion effects respect
// prefers-reduced-motion.

const KEY = "fr-fx";
const DEFAULTS = { sound: true, vibrate: true };

export function fxPrefs() {
  try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY) ?? "{}") }; } catch { return { ...DEFAULTS }; }
}
export function setFxPref(key, value) {
  try { localStorage.setItem(KEY, JSON.stringify({ ...fxPrefs(), [key]: value })); } catch { /* private mode */ }
}
export const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

let ctx;
function tone(freq, start, dur, { type = "sine", gain = 0.12, slide = 0 } = {}) {
  ctx ??= new (window.AudioContext || window.webkitAudioContext)();
  const t = ctx.currentTime + start;
  const osc = ctx.createOscillator();
  const g = ctx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, t);
  if (slide) osc.frequency.exponentialRampToValueAtTime(freq * slide, t + dur);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(gain, t + 0.01);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  osc.connect(g).connect(ctx.destination);
  osc.start(t);
  osc.stop(t + dur + 0.02);
}

const SOUNDS = {
  right: () => { tone(660, 0, 0.12); tone(990, 0.08, 0.18); },
  combo: (n = 1) => { const b = 660 * 2 ** (Math.min(n, 12) / 12); tone(b, 0, 0.1); tone(b * 1.5, 0.07, 0.2, { gain: 0.1 }); },
  wrong: () => { tone(220, 0, 0.22, { type: "triangle", gain: 0.1, slide: 0.7 }); },
  flip: () => { tone(520, 0, 0.06, { type: "triangle", gain: 0.06 }); },
  card: () => { tone(784, 0, 0.09, { gain: 0.08 }); },
  done: () => { [523, 659, 784, 1047].forEach((f, i) => tone(f, i * 0.09, 0.22, { gain: 0.1 })); },
  level: () => { [523, 659, 784, 1047, 1319].forEach((f, i) => tone(f, i * 0.11, 0.35, { gain: 0.11 })); tone(1568, 0.6, 0.5, { gain: 0.08 }); },
  badge: () => { tone(880, 0, 0.12); tone(1175, 0.1, 0.12); tone(1760, 0.2, 0.3, { gain: 0.08 }); },
};
const BUZZ = { right: 15, combo: [10, 30, 10], wrong: [40, 40, 40], done: [20, 40, 60], level: [30, 50, 30, 50, 120], badge: [20, 30, 60] };

/** Play the feedback for an event kind: right, combo, wrong, flip, card, done, level, badge. */
export function feedback(kind, arg) {
  const p = fxPrefs();
  if (p.sound) { try { SOUNDS[kind]?.(arg); } catch { /* no audio */ } }
  if (p.vibrate && BUZZ[kind]) navigator.vibrate?.(BUZZ[kind]);
}

/** "+12 XP" rising from an element. */
export function floatXP(anchor, text) {
  if (!anchor || reducedMotion()) return;
  const r = anchor.getBoundingClientRect();
  const el = document.createElement("div");
  el.className = "xp-float";
  el.textContent = text;
  el.style.left = `${r.left + r.width / 2}px`;
  el.style.top = `${r.top + window.scrollY}px`;
  document.body.append(el);
  el.addEventListener("animationend", () => el.remove());
}

/** A burst of confetti over the whole screen. */
export function confetti({ pieces = 120, duration = 2400 } = {}) {
  if (reducedMotion()) return;
  const canvas = document.createElement("canvas");
  canvas.className = "confetti";
  const dpr = window.devicePixelRatio || 1;
  canvas.width = innerWidth * dpr;
  canvas.height = innerHeight * dpr;
  document.body.append(canvas);
  const g = canvas.getContext("2d");
  g.scale(dpr, dpr);
  const colors = ["#2b4c9b", "#e63946", "#f4a261", "#2a9d8f", "#ffd166", "#8ecae6"];
  const parts = Array.from({ length: pieces }, () => ({
    x: innerWidth / 2 + (Math.random() - 0.5) * 120, y: innerHeight * 0.35,
    vx: (Math.random() - 0.5) * 14, vy: -Math.random() * 14 - 4, r: Math.random() * Math.PI,
    vr: (Math.random() - 0.5) * 0.3, w: 6 + Math.random() * 6, h: 8 + Math.random() * 8,
    c: colors[(Math.random() * colors.length) | 0],
  }));
  const start = performance.now();
  const step = (t) => {
    const k = (t - start) / duration;
    g.clearRect(0, 0, innerWidth, innerHeight);
    for (const p of parts) {
      p.vy += 0.35; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr;
      g.save(); g.globalAlpha = Math.max(0, 1 - k); g.translate(p.x, p.y); g.rotate(p.r);
      g.fillStyle = p.c; g.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); g.restore();
    }
    if (k < 1) requestAnimationFrame(step); else canvas.remove();
  };
  requestAnimationFrame(step);
}
