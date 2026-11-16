// Flux: an endless full-screen feed, one card per screen, scrolled like a video app.
// Swipe: the same stream as a deck of cards thrown right (yes / I know) or left (no / again).
// Both log ordinary answer and review events, so they feed mastery, spaced repetition and XP.

import { getChunk, manifest } from "../core/data.js";
import { getEvents, logEvent, useEvents } from "../core/events.js";
import { CHEST_NEED, createFeed, rollChest, tfSentence } from "../core/feed.js";
import { confetti, feedback, floatXP, frenchVoice, fxPrefs, reducedMotion, speak } from "../core/fx.js";
import { gameState, xpFor } from "../core/game.js";
import { buildModel } from "../core/mastery.js";
import { questionMeta } from "../core/select.js";
import { settingsFrom } from "../core/settings.js";
import { html, useEffect, useMemo, useRef, useState } from "../lib.js";
import { CardBack, ErrorBox, Loading, Md, useAsync } from "../ui.js";

const LETTERS = ["A", "B", "C"];
const ADVANCE_MS = 950; // pause on a right answer before the next card slides in
const SWIPE_X = 80; // px a card must travel sideways to count
const SWIPE_UP = 100;

/** The stream for this visit: every topic's questions and cards, ordered by what needs work. */
function useFeed(opts) {
  return useAsync(async () => {
    const m = manifest();
    const topics = m.topics.filter((t) => t.counts.questions || t.counts.formulas);
    const [events, ...loaded] = await Promise.all([getEvents(), ...topics.map((t) => getChunk(t.id))]);
    const settings = settingsFrom(events);
    return createFeed({
      chunks: new Map(topics.map((t, i) => [t.id, loaded[i]])), events,
      model: buildModel(events, m, Date.now(), { target: settings.target ?? undefined }),
      names: new Map(m.topics.map((t) => [t.id, t.name])),
      retention: m.scoring.spaced_repetition.desired_retention, newPerDay: settings.new_cards, ...opts,
    });
  }, []);
}

/** Running totals for this visit, plus the sound, vibration and "+XP" that go with each answer. */
function useSession() {
  const [s, setS] = useState({ answered: 0, right: 0, combo: 0, xp: 0, sinceChest: 0 });
  const ref = useRef(s);
  const set = (next) => { ref.current = next; setS(next); };
  return {
    s,
    record(correct, xp, anchor) {
      const p = ref.current;
      const combo = correct ? p.combo + 1 : 0;
      set({ answered: p.answered + 1, right: p.right + (correct ? 1 : 0), combo, xp: p.xp + xp, sinceChest: p.sinceChest + 1 });
      feedback(correct ? (combo >= 3 ? "combo" : "right") : "wrong", combo);
      floatXP(anchor, correct && combo >= 3 ? `+${xp} XP · ×${combo}` : `+${xp} XP`);
    },
    bonus(xp) { set({ ...ref.current, xp: ref.current.xp + xp, sinceChest: 0 }); },
  };
}

function logAnswer(item, correct, ms, mode, choice, tf) {
  const { los, module } = questionMeta(item.q, item.chunk);
  // A sentence judged right or wrong is half luck: it counts as a guess (confidence 1).
  return logEvent("answer", { qid: item.q.id, los, topic: item.topic, module, correct, ms: Math.round(ms),
                              confidence: tf ? 1 : 2, mode, choice, ...(tf ? { tf: true } : {}) });
}
const logReview = (item, grade, ms, src) =>
  logEvent("review", { card: item.card.id, topic: item.topic, los: item.card.los, grade, ms: Math.round(ms), src });
const answerXP = (mode, correct, tf) => xpFor({ type: "answer", payload: { mode, correct, confidence: tf ? 1 : 2, tf } });
const reviewXP = (grade) => xpFor({ type: "review", payload: { grade } });

/** The time the card came on screen (for the answer's duration). */
function useShownAt(active) {
  const t = useRef(null);
  if (active && t.current == null) t.current = Date.now();
  return () => Date.now() - (t.current ?? Date.now());
}

function Hud({ s, other }) {
  const events = useEvents();
  const game = useMemo(() => (events ? gameState(events, settingsFrom(events)) : null), [events?.length]);
  return html`<div class="hud">
    <span class="hud-pill" title="Jours d'affilée">🔥 ${game?.streak ?? 0}</span>
    <div class="hud-goal" title="Objectif du jour">
      <div class="hud-bar"><span style=${`width:${game ? Math.min(100, (100 * game.today) / game.goal) : 0}%`}></span></div>
      <span class="hud-xp">${game ? `${game.today} / ${game.goal} XP` : ""}${game?.goalDone ? " ✓" : ""}</span>
    </div>
    ${s.combo >= 2 ? html`<span class="hud-pill hud-combo" key=${s.combo}>×${s.combo}</span>` : null}
    <a class="hud-pill" href=${other.href}>${other.label}</a>
  </div>`;
}

const explain = (q, letter) => q.explanations?.[letter] ?? (letter === q.answer ? q.explanation : null);

// ---------------------------------------------------------------- Flux slides

function QuestionSlide({ item, active, session, onDone }) {
  const [choice, setChoice] = useState(null);
  const elapsed = useShownAt(active);
  const { q, chunk } = item;
  const pick = (letter, e) => {
    if (choice) return;
    const correct = letter === q.answer;
    setChoice(letter);
    session.record(correct, answerXP("feed", correct), e.currentTarget);
    logAnswer(item, correct, elapsed(), "feed", letter);
    onDone(item, correct);
  };
  return html`<section class="slide slide-question" data-uid=${item.uid}><div class="slide-in">
    <div class="slide-tag"><b>Question</b><span>${item.tag}</span>${item.why ? html`<span class="why">${item.why}</span>` : null}</div>
    <div class="stem"><${Md} tag="p" text=${q.stem} chunk=${chunk} tr=${`${q.id}|stem`} /></div>
    <div class="fopts">${q.options.map((opt, i) => {
      const l = LETTERS[i];
      const state = !choice ? "" : l === q.answer ? "right" : l === choice ? "wrong" : "dim";
      return html`<button class=${`fopt ${state}`} disabled=${!!choice} onClick=${(e) => pick(l, e)}>
        <${Md} text=${opt} chunk=${chunk} tr=${`${q.id}|${l}`} /></button>`;
    })}</div>
    ${choice ? html`<div class=${`verdict ${choice === q.answer ? "ok" : "bad"}`} role="status">
      <strong>${choice === q.answer ? "✓ Bien joué" : "✗ Raté : elle reviendra dans quelques cartes"}</strong>
      ${choice !== q.answer && explain(q, choice) ? html`<p><${Md} text=${explain(q, choice)} chunk=${chunk} tr=${`${q.id}|x${choice}`} /></p>` : null}
      ${explain(q, q.answer) ? html`<p><${Md} text=${explain(q, q.answer)} chunk=${chunk} tr=${`${q.id}|x${q.answer}`} /></p>` : null}
    </div><${Next} />` : null}
  </div></section>`;
}

function Truth({ item }) {
  const { q, chunk } = item;
  return html`<p><b>${item.truth ? "La phrase est juste." : "La phrase est fausse."}</b></p>
    ${explain(q, item.letter) ? html`<p><${Md} text=${explain(q, item.letter)} chunk=${chunk} tr=${`${q.id}|x${item.letter}`} /></p>` : null}
    ${!item.truth ? html`<p>→ <${Md} text=${tfSentence(q, q.answer)} chunk=${chunk} /></p>` : null}`;
}

function TfSlide({ item, active, session, onDone }) {
  const [said, setSaid] = useState(null);
  const elapsed = useShownAt(active);
  const judge = (says, e) => {
    if (said != null) return;
    const correct = says === item.truth;
    setSaid(says);
    session.record(correct, answerXP("feed", correct, true), e.currentTarget);
    logAnswer(item, correct, elapsed(), "feed", item.letter, true);
    onDone(item, correct);
  };
  const state = (says) => (said == null ? "" : says === item.truth ? "right" : says === said ? "wrong" : "dim");
  return html`<section class="slide slide-tf" data-uid=${item.uid}><div class="slide-in">
    <div class="slide-tag"><b>Juste ou faux ?</b><span>${item.tag}</span>${item.retry ? html`<span class="why">Revanche</span>` : null}</div>
    <div class="stem"><${Md} tag="p" text=${item.text} chunk=${item.chunk} tr=${`${item.q.id}|stem`} /></div>
    <div class="tf-row">
      <button class=${`fopt tf-no ${state(false)}`} disabled=${said != null} onClick=${(e) => judge(false, e)}>✗ Faux</button>
      <button class=${`fopt tf-yes ${state(true)}`} disabled=${said != null} onClick=${(e) => judge(true, e)}>✓ Juste</button>
    </div>
    ${said != null ? html`<div class=${`verdict ${said === item.truth ? "ok" : "bad"}`} role="status">
      <strong>${said === item.truth ? "✓ Bien vu" : "✗ Raté"}</strong><${Truth} item=${item} /></div><${Next} />` : null}
  </div></section>`;
}

const speakable = (card) => card.front.length <= 40;

function WordSlide({ item, active, session, onDone }) {
  const { card } = item;
  const canSpeak = fxPrefs().speak && "speechSynthesis" in window;
  const mode = item.mode === "listen" && !(canSpeak && frenchVoice()) ? "mcq" : item.mode;
  const [shown, setShown] = useState(false);
  const [picked, setPicked] = useState(null);
  const [graded, setGraded] = useState(null);
  const elapsed = useShownAt(active);
  useEffect(() => { if (active && graded == null && canSpeak && speakable(card)) speak(card.front); }, [active]);

  const grade = (g, e) => {
    if (graded != null) return;
    setGraded(g);
    session.record(g >= 3, reviewXP(g), e.currentTarget);
    logReview(item, g, elapsed(), "feed");
    onDone(item, g >= 3, mode === "flip" || g >= 3); // a self-graded card has nothing more to read
  };
  const pick = (i, e) => { if (picked == null) { setPicked(i); grade(item.options[i].right ? 3 : 1, e); } };
  const hidden = mode === "listen" && picked == null;
  return html`<section class=${`slide slide-word ${speakable(card) ? "" : "slide-rule"}`} data-uid=${item.uid}><div class="slide-in">
    <div class="slide-tag"><b>${mode === "listen" ? "Écoute" : speakable(card) ? "Mot" : "Règle"}</b><span>${item.tag}</span>
      ${item.retry ? html`<span class="why">Revanche</span>` : item.isNew ? html`<span class="why">Nouveau</span>` : null}</div>
    ${hidden ? html`<button class="listen-btn" onClick=${() => speak(card.front)} aria-label="Réécouter">🔊</button>
        <p class="center">Écoutez, puis choisissez le sens.</p>`
      : html`<div class=${speakable(card) ? "word-big" : "stem"}><${Md} tag="p" text=${card.front} /></div>
        ${canSpeak && speakable(card) ? html`<button class="say" onClick=${() => speak(card.front)} aria-label="Écouter">🔊</button>` : null}`}
    ${mode === "flip" ? (shown
        ? html`<div class="word-back"><${CardBack} card=${card} /></div>
          ${graded == null ? html`<div class="tf-row">
            <button class="fopt tf-no" onClick=${(e) => grade(1, e)}>À revoir</button>
            <button class="fopt tf-yes" onClick=${(e) => grade(3, e)}>Je savais</button>
            <button class="fopt tf-easy" onClick=${(e) => grade(4, e)}>Facile</button></div>` : html`<${Next} />`}`
        : html`<button class="fopt reveal" onClick=${() => { feedback("flip"); setShown(true); }}>Voir la réponse</button>`)
      : html`<div class="fopts">${item.options.map((o, i) => html`<button disabled=${picked != null} onClick=${(e) => pick(i, e)}
            class=${`fopt ${picked == null ? "" : o.right ? "right" : i === picked ? "wrong" : "dim"}`}><${Md} text=${o.text} /></button>`)}</div>
          ${picked != null ? html`<${Next} />` : null}`}
  </div></section>`;
}

function ChestSlide({ item, session }) {
  const [xp, setXp] = useState(null);
  const el = useRef(null);
  const left = Math.max(0, CHEST_NEED - session.s.sinceChest);
  const { answered, right } = session.s;
  const open = () => {
    const won = rollChest();
    setXp(won);
    session.bonus(won);
    logEvent("bonus", { xp: won, source: "chest" });
    feedback("chest", won);
    floatXP(el.current, `+${won} XP`);
    if (won >= 20) confetti({ pieces: won >= 50 ? 180 : 70 });
  };
  return html`<section class="slide slide-chest" data-uid=${item.uid}><div class="slide-in center">
    <div class="slide-tag"><b>Coffre</b>${answered ? html`<span>${answered} cartes · ${Math.round((100 * right) / answered)} % de réussite</span>` : null}</div>
    <div class=${`chest ${xp != null ? "open" : left ? "locked" : "ready"}`} ref=${el} aria-hidden="true">${xp != null ? "✨" : "🎁"}</div>
    ${xp != null ? html`<div class="chest-xp">+${xp} XP</div><p>${xp >= 100 ? "JACKPOT !" : xp >= 50 ? "Gros lot !" : "C'est dans la poche."} Le prochain coffre n'est pas loin.</p><${Next} />`
      : left ? html`<p>Encore <b>${left}</b> réponse${left > 1 ? "s" : ""} pour ouvrir ce coffre. Continuez, puis revenez.</p><${Next} />`
      : html`<button class="fopt reveal" onClick=${open}>Ouvrir le coffre</button>`}
  </div></section>`;
}

const Next = () => html`<div class="next-hint" aria-hidden="true">⌃<span>Glissez vers le haut</span></div>`;

const SLIDES = { question: QuestionSlide, tf: TfSlide, word: WordSlide, chest: ChestSlide };

export function Flux() {
  const { value: feed, error } = useFeed({ wordModes: ["flip", "mcq", "mcq", "listen"] });
  const [items, setItems] = useState(null);
  const [active, setActive] = useState(0);
  const scroller = useRef(null);
  const session = useSession();
  const activeRef = useRef(0);

  useEffect(() => { if (feed) setItems(feed.next(6)); }, [feed]);
  // Keep a few cards ready below the one on screen.
  useEffect(() => { if (feed && items && items.length - active <= 3) setItems((list) => [...list, ...feed.next(5)]); }, [active, feed]);

  if (error) return html`<div class="pad"><${ErrorBox} error=${error} retry=${() => location.reload()} /></div>`;
  if (!items) return html`<div class="pad"><${Loading} label="Préparation du flux…" /></div>`;
  if (!items.length) return html`<div class="pad stack"><h1>Flux</h1><p>Pas encore de questions ni de cartes à faire défiler.</p></div>`;

  const onScroll = (e) => {
    const i = Math.round(e.currentTarget.scrollTop / e.currentTarget.clientHeight);
    if (i !== activeRef.current) { activeRef.current = i; setActive(i); }
  };
  const onDone = (item, correct, advance = correct) => {
    if (!correct) feed.retry(item);
    if (!advance) return;
    const at = activeRef.current;
    setTimeout(() => {
      if (activeRef.current !== at) return; // already scrolled on
      scroller.current?.querySelector(`[data-uid="${item.uid}"]`)?.nextElementSibling
        ?.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
    }, ADVANCE_MS);
  };
  return html`<div class="flux">
    <${Hud} s=${session.s} other=${{ href: "#/swipe", label: "Swipe ⇄" }} />
    <div class="feed" ref=${scroller} onScroll=${onScroll}>
      ${items.map((item, i) => html`<${SLIDES[item.kind]} key=${item.uid} item=${item} active=${i === active} session=${session} onDone=${onDone} />`)}
    </div>
  </div>`;
}

// ---------------------------------------------------------------- Swipe

const clamp01 = (x) => Math.max(0, Math.min(1, x));

export function Swipe() {
  const { value: feed, error } = useFeed({ kinds: ["tf", "word"], wordModes: ["flip"], chests: false });
  const [deck, setDeck] = useState(null);
  const [flipped, setFlipped] = useState(false);
  const [last, setLast] = useState(null);
  const session = useSession();
  const top = useRef(null);
  const stage = useRef(null);
  const drag = useRef(null);
  const busy = useRef(false);
  const shownAt = useRef(Date.now());
  const item = deck?.[0];
  const canSpeak = fxPrefs().speak && "speechSynthesis" in window;

  useEffect(() => { if (feed) setDeck(feed.next(4)); }, [feed]);
  useEffect(() => {
    shownAt.current = Date.now();
    if (item?.kind === "word" && canSpeak && speakable(item.card)) speak(item.card.front);
  }, [item?.uid]);

  const commit = (dir) => {
    const ms = Date.now() - shownAt.current;
    let correct;
    if (item.kind === "tf") {
      correct = (dir === "right") === item.truth;
      session.record(correct, answerXP("swipe", correct, true), stage.current);
      logAnswer(item, correct, ms, "swipe", item.letter, true);
    } else {
      const g = dir === "up" ? 4 : dir === "right" ? 3 : 1;
      correct = g >= 3;
      session.record(correct, reviewXP(g), stage.current);
      logReview(item, g, ms, "swipe");
    }
    if (!correct) feed.retry(item);
    setLast({ item, correct });
    setFlipped(false);
    const rest = deck.slice(1);
    setDeck(rest.length < 3 ? [...rest, ...feed.next(4)] : rest);
    busy.current = false;
  };
  const decide = (dir) => {
    if (!item || busy.current || (dir === "up" && item.kind !== "word")) return;
    busy.current = true;
    feedback("swipe");
    const el = top.current;
    el.style.transition = "transform .2s ease-in, opacity .2s";
    el.style.opacity = "0";
    el.style.transform = dir === "up" ? "translateY(-110vh)" : `translate(${dir === "right" ? 120 : -120}vw, 30px) rotate(${dir === "right" ? 24 : -24}deg)`;
    setTimeout(() => commit(dir), reducedMotion() ? 0 : 190);
  };
  const flip = () => { if (item?.kind === "word" && !flipped) { feedback("flip"); setFlipped(true); } };

  const place = (dx, dy) => {
    const el = top.current;
    el.style.transform = dx || dy ? `translate(${dx}px, ${dy}px) rotate(${dx / 18}deg)` : "";
    el.style.setProperty("--yes", clamp01(dx / SWIPE_X));
    el.style.setProperty("--no", clamp01(-dx / SWIPE_X));
    el.style.setProperty("--up", item.kind === "word" && Math.abs(dx) < 40 ? clamp01(-dy / SWIPE_UP) : 0);
  };
  const onDown = (e) => { if (!busy.current) drag.current = { x: e.clientX, y: e.clientY, dx: 0, dy: 0, moved: false }; };
  const onMove = (e) => {
    const d = drag.current;
    if (!d) return;
    d.dx = e.clientX - d.x; d.dy = e.clientY - d.y;
    if (!d.moved && Math.hypot(d.dx, d.dy) < 8) return;
    // Capture only once it's a drag, so a plain tap still reaches the word under the finger.
    if (!d.moved) { d.moved = true; top.current.setPointerCapture?.(e.pointerId); top.current.style.transition = "none"; }
    place(d.dx, d.dy);
  };
  const onUp = () => {
    const d = drag.current;
    drag.current = null;
    if (!d) return;
    if (!d.moved) return flip();
    if (Math.abs(d.dx) > SWIPE_X) return decide(d.dx > 0 ? "right" : "left");
    if (d.dy < -SWIPE_UP && item.kind === "word") return decide("up");
    top.current.style.transition = "transform .3s cubic-bezier(.2, 1.4, .4, 1)";
    place(0, 0);
  };
  useEffect(() => {
    const onKey = (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey || e.target.closest?.("input, textarea")) return;
      const dir = { ArrowRight: "right", ArrowLeft: "left", ArrowUp: "up" }[e.key];
      if (dir) decide(dir); else if (e.key === " " || e.key === "Enter") flip(); else return;
      e.preventDefault();
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  });

  if (error) return html`<div class="pad"><${ErrorBox} error=${error} retry=${() => location.reload()} /></div>`;
  if (!deck) return html`<div class="pad"><${Loading} label="On bat les cartes…" /></div>`;
  if (!item) return html`<div class="pad stack"><h1>Swipe</h1><p>Pas encore de cartes à swiper.</p></div>`;

  const word = item.kind === "word";
  const labels = word ? { no: "À revoir", yes: "Je sais", up: "Facile" } : { no: "Faux", yes: "Juste" };
  return html`<div class="flux swipe">
    <${Hud} s=${session.s} other=${{ href: "#/flux", label: "Flux ⇅" }} />
    <div class="deck" ref=${stage}>
      ${deck[1] ? html`<div class=${`scard under slide-${deck[1].kind}`} key=${deck[1].uid} aria-hidden="true"></div>` : null}
      <article class=${`scard slide slide-${item.kind} ${word && !speakable(item.card) ? "slide-rule" : ""}`} key=${item.uid} ref=${top} data-uid=${item.uid}
          onPointerDown=${onDown} onPointerMove=${onMove} onPointerUp=${onUp} onPointerCancel=${onUp}>
        <span class="stamp stamp-yes">${labels.yes}</span><span class="stamp stamp-no">${labels.no}</span>
        ${word ? html`<span class="stamp stamp-up">${labels.up}</span>` : null}
        <div class="slide-tag"><b>${word ? (speakable(item.card) ? "Mot" : "Règle") : "Juste ou faux ?"}</b><span>${item.tag}</span>
          ${item.retry ? html`<span class="why">Revanche</span>` : item.isNew ? html`<span class="why">Nouveau</span>` : null}</div>
        ${word ? html`<div class=${speakable(item.card) ? "word-big" : "stem"}><${Md} tag="p" text=${item.card.front} /></div>
            ${flipped ? html`<div class="word-back"><${CardBack} card=${item.card} /></div>`
                      : html`<p class="tap-hint">Touchez pour voir la réponse</p>`}`
          : html`<div class="stem"><${Md} tag="p" text=${item.text} chunk=${item.chunk} tr=${`${item.q.id}|stem`} /></div>
            <p class="tap-hint">Cette phrase est-elle juste ?</p>`}
      </article>
    </div>
    <div class="swipe-actions">
      <button class="round no" onClick=${() => decide("left")} aria-label=${labels.no}>✗<span>${labels.no}</span></button>
      ${word ? html`<button class="round up" onClick=${() => decide("up")} aria-label=${labels.up}>★<span>${labels.up}</span></button>` : null}
      <button class="round yes" onClick=${() => decide("right")} aria-label=${labels.yes}>✓<span>${labels.yes}</span></button>
    </div>
    <div class=${`swipe-last ${last ? (last.correct ? "ok" : "bad") : ""}`} role="status">
      ${!last ? html`<span>→ ${labels.yes} · ← ${labels.no}${word ? ` · ↑ ${labels.up}` : ""}</span>`
        : last.item.kind === "word" ? html`<span><b><${Md} text=${last.item.card.front} /></b> = <${Md} text=${last.item.card.back} /></span>`
        : html`<div class="verdict-line"><strong>${last.correct ? "✓ Bien vu" : "✗ Raté"}</strong> <${Truth} item=${last.item} /></div>`}
    </div>
  </div>`;
}
