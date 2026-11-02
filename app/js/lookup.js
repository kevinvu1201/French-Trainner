// Tap-to-translate. Text rendered with a data-tr key (question stems, options, explanations,
// gap-fill and listening paragraphs) can be tapped: the word under the finger is looked up in
// the offline translations shipped with the topic (meaning in context + the sentence in English).
// Answer options are buttons, so there it's a long-press. Online, "Expliquer avec l'IA" asks
// Gemini with the user's own key; answers are cached on the device.

import { findTranslation } from "./core/data.js";
import { kvGet, kvSet } from "./core/store.js";
import { html, useEffect, useRef, useState } from "./lib.js";

export const DEFAULT_MODEL = "gemini-2.5-flash";
export const aiSettings = async () => (await kvGet("gemini")) ?? { key: "", model: DEFAULT_MODEL };
export const saveAiSettings = (s) => kvSet("gemini", s);

const WORD = /[\p{L}\p{M}\d'’-]/u;
const LONG_PRESS_MS = 450;

/** Character offset of (node, offset) within root's text. */
function textOffset(root, node, offset) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let total = 0;
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (n === node) return total + offset;
    total += n.textContent.length;
  }
  return -1;
}

/** Text offset of the word whose box contains (x, y), found by measuring each word. Used where the
 * caret APIs return nothing useful, as inside buttons (answer options). */
function offsetByBoxes(root, x, y) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let total = 0;
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    for (const m of n.textContent.matchAll(/[\p{L}\p{M}\d'’-]+/gu)) {
      const r = document.createRange();
      r.setStart(n, m.index);
      r.setEnd(n, m.index + m[0].length);
      for (const b of r.getClientRects()) {
        if (x >= b.left - 2 && x <= b.right + 2 && y >= b.top - 2 && y <= b.bottom + 2) return total + m.index;
      }
    }
    total += n.textContent.length;
  }
  return -1;
}

function caretAt(x, y) {
  if (document.caretRangeFromPoint) {
    const r = document.caretRangeFromPoint(x, y);
    return r && { node: r.startContainer, offset: r.startOffset };
  }
  const p = document.caretPositionFromPoint?.(x, y);
  return p && { node: p.offsetNode, offset: p.offset };
}

/** The word around position i of text, without elided articles (l’, d’, qu’…) or edge punctuation. */
export function wordAt(text, i) {
  if (i < 0 || i > text.length) return null;
  let a = i;
  let b = i;
  if (!WORD.test(text[a] ?? "") && WORD.test(text[a - 1] ?? "")) a -= 1, b -= 1;
  while (a > 0 && WORD.test(text[a - 1])) a--;
  while (b < text.length && WORD.test(text[b])) b++;
  let word = text.slice(a, b);
  let start = a;
  const elided = word.match(/^(?:[a-zà-ÿ]{1,3}|jusqu|lorsqu|puisqu|quoiqu)['’]/i);
  if (elided && i >= a + elided[0].length) { start += elided[0].length; word = word.slice(elided[0].length); }
  const trimmed = word.replace(/^[-'’]+|[-'’]+$/g, "");
  start += word.indexOf(trimmed);
  return trimmed ? { word: trimmed, start, end: start + trimmed.length } : null;
}

/** The sentence pair [fr, en] covering position i, matching the stored sentences against the text in order. */
export function sentenceAt(entry, text, i) {
  let from = 0;
  for (const [fr, en] of entry.s ?? []) {
    const at = text.indexOf(fr.trim(), from);
    if (at < 0) continue;
    if (i >= at && i <= at + fr.length) return { fr: fr.trim(), en };
    from = at + fr.length;
  }
  return { fr: text, en: entry.en };
}

export function glossFor(entry, word) {
  const g = entry?.g ?? {};
  const w = word.toLowerCase();
  return g[w] ?? g[w.replace(/[’']/g, "'")] ?? g[w.replace(/s$/, "")] ?? null;
}

/** Exercise context for the AI prompt, read from the question card around the tapped text. */
function contextOf(el) {
  const card = el.closest(".qcard");
  if (!card) return null;
  const stem = card.querySelector("[data-tr$='|stem']")?.textContent ?? "";
  const options = [...card.querySelectorAll(".option")].map((o) => o.textContent.trim());
  const answered = Boolean(card.querySelector(".feedback")) || card.querySelector(".option")?.disabled === true;
  return { stem, options, answered };
}

export async function explainWithAI({ word, sentence, context }, settings, fetchFn = fetch) {
  const hidden = context && !context.answered
    ? "The learner has NOT answered this exercise yet: do not reveal, hint at or evaluate which option is correct. "
    : "";
  const prompt = `You help a B1 learner of French preparing the DELF B2. ${hidden}`
    + `Explain the French word "${word}" as used in this sentence: "${sentence}".`
    + (context?.stem ? ` Exercise question: "${context.stem}". Options: ${context.options.join(" | ")}.` : "")
    + ` Reply in English as JSON: {"meaning": meaning in this context, "lemma": dictionary form with article for nouns,`
    + ` "note": one short usage or nuance note, "translation": the whole sentence in English}.`;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${settings.model || DEFAULT_MODEL}:generateContent?key=${encodeURIComponent(settings.key)}`;
  const res = await fetchFn(url, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { responseMimeType: "application/json", temperature: 0.2 } }),
  });
  if (!res.ok) throw new Error(res.status === 400 || res.status === 403 ? "Clé Gemini refusée : vérifiez-la dans Réglages." : `Gemini ${res.status}`);
  const data = await res.json();
  return JSON.parse(data.candidates[0].content.parts[0].text);
}

const hashKey = (s) => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) | 0; return (h >>> 0).toString(36); };

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "fr-FR";
  u.rate = 0.95;
  speechSynthesis.speak(u);
}

/** Mounted once in the shell: listens for taps and long-presses on [data-tr] text and shows the sheet. */
export function LookupLayer() {
  const [hit, setHit] = useState(null);
  const press = useRef(null);
  const suppressClick = useRef(false);

  useEffect(() => {
    const lookup = (el, x, y) => {
      const caret = caretAt(x, y);
      const text = el.textContent;
      const at = caret && el.contains(caret.node) ? textOffset(el, caret.node, caret.offset) : offsetByBoxes(el, x, y);
      const w = wordAt(text, at);
      if (!w) return false;
      const entry = findTranslation(el.dataset.tr);
      const sentence = entry ? sentenceAt(entry, text, w.start) : { fr: text, en: null };
      setHit({ key: el.dataset.tr, word: w.word, gloss: glossFor(entry, w.word), sentence, context: contextOf(el) });
      kvSet("lookupUsed", true);
      return true;
    };
    const onClick = (e) => {
      if (suppressClick.current) { suppressClick.current = false; e.preventDefault(); e.stopPropagation(); return; }
      const el = e.target.closest?.("[data-tr]");
      if (!el || e.target.closest("button, a, summary, .sheet")) return;
      lookup(el, e.clientX, e.clientY);
    };
    const onDown = (e) => {
      const el = e.target.closest?.("button [data-tr]");
      if (!el) return;
      const { clientX: x, clientY: y } = e;
      press.current = { x, y, timer: setTimeout(() => { if (lookup(el, x, y)) { suppressClick.current = true; navigator.vibrate?.(10); } }, LONG_PRESS_MS) };
    };
    const cancel = (e) => {
      const p = press.current;
      if (p && (e.type !== "pointermove" || Math.hypot(e.clientX - p.x, e.clientY - p.y) > 10)) { clearTimeout(p.timer); press.current = null; }
    };
    const noMenu = (e) => { if (e.target.closest?.("button [data-tr]")) e.preventDefault(); };
    document.addEventListener("click", onClick, true);
    document.addEventListener("pointerdown", onDown);
    ["pointerup", "pointercancel", "pointermove"].forEach((t) => document.addEventListener(t, cancel));
    document.addEventListener("contextmenu", noMenu);
    return () => {
      document.removeEventListener("click", onClick, true);
      document.removeEventListener("pointerdown", onDown);
      ["pointerup", "pointercancel", "pointermove"].forEach((t) => document.removeEventListener(t, cancel));
      document.removeEventListener("contextmenu", noMenu);
    };
  }, []);

  return hit ? html`<${LookupSheet} hit=${hit} onClose=${() => setHit(null)} />` : null;
}

function LookupSheet({ hit, onClose }) {
  const [ai, setAi] = useState({ state: "idle" }); // idle | loading | done | error
  const [settings, setSettings] = useState(null);
  const cacheKey = `ai:${hashKey(`${hit.word}|${hit.sentence.fr}|${hit.context?.answered ? 1 : 0}`)}`;
  useEffect(() => {
    aiSettings().then(setSettings);
    kvGet(cacheKey).then((v) => v && setAi({ state: "done", value: v, cached: true }));
  }, [hit.key, hit.word]);
  const ask = async () => {
    setAi({ state: "loading" });
    try {
      const value = await explainWithAI({ word: hit.word, sentence: hit.sentence.fr, context: hit.context }, settings);
      await kvSet(cacheKey, value);
      setAi({ state: "done", value });
    } catch (e) {
      setAi({ state: "error", message: e.message });
    }
  };
  const i = hit.sentence.fr.toLowerCase().indexOf(hit.word.toLowerCase());
  const fr = i < 0 ? hit.sentence.fr : html`${hit.sentence.fr.slice(0, i)}<mark>${hit.sentence.fr.slice(i, i + hit.word.length)}</mark>${hit.sentence.fr.slice(i + hit.word.length)}`;
  const canAsk = settings?.key && navigator.onLine;
  return html`<div class="sheet-backdrop" onClick=${onClose}>
    <section class="sheet" role="dialog" aria-label=${`Traduction : ${hit.word}`} onClick=${(e) => e.stopPropagation()}>
      <div class="sheet-grip" aria-hidden="true"></div>
      <div class="spread"><strong class="sheet-word">${hit.word}</strong>
        <button class="btn" onClick=${() => speak(hit.sentence.fr)} aria-label="Écouter la phrase">🔊</button></div>
      <p class="sheet-gloss">${hit.gloss ?? html`<span class="muted small">Pas de définition hors ligne pour ce mot${canAsk ? " : demandez à l'IA." : "."}</span>`}</p>
      <div class="sheet-sentence"><div class="small muted">Phrase</div><p>${fr}</p>
        ${hit.sentence.en ? html`<p class="sheet-en">${hit.sentence.en}</p>` : html`<p class="small muted">Traduction hors ligne pas encore disponible.</p>`}</div>
      ${ai.state === "done" ? html`<div class="sheet-ai">
          <div class="small muted">Explication IA${ai.cached ? " (enregistrée)" : ""}</div>
          <p><strong>${ai.value.lemma ?? ""}</strong> — ${ai.value.meaning ?? ""}</p>
          ${ai.value.note ? html`<p class="small">${ai.value.note}</p>` : null}
          ${ai.value.translation && !hit.sentence.en ? html`<p class="sheet-en">${ai.value.translation}</p>` : null}
        </div>`
        : ai.state === "loading" ? html`<p class="small muted" role="status">L'IA réfléchit…</p>`
        : ai.state === "error" ? html`<p class="small" style="color:var(--bad)">${ai.message}</p>` : null}
      <div class="row">
        ${canAsk && ai.state !== "done" && ai.state !== "loading" ? html`<button class="btn primary" onClick=${ask}>✨ Expliquer avec l'IA</button>` : null}
        ${!settings?.key ? html`<a class="small" href="#/settings" onClick=${onClose}>Ajouter une clé Gemini pour les explications IA</a>` : null}
        <button class="btn" onClick=${onClose}>Fermer</button>
      </div>
    </section>
  </div>`;
}

/** One-time hint shown in exercises until the first lookup. */
export function LookupTip() {
  const [show, setShow] = useState(false);
  useEffect(() => { kvGet("lookupUsed").then((v) => setShow(!v)); }, []);
  if (!show) return null;
  return html`<p class="lookup-tip small" onClick=${() => { setShow(false); kvSet("lookupUsed", true); }}>
    💡 Touchez un mot pour le traduire · appui long sur une réponse</p>`;
}
