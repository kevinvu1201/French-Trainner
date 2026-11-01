"""End-to-end tests of the PWA in headless Chrome/Edge (skipped when neither is installed).

A throwaway project is built from the synthetic fixture book with the real app/, then
served on a random port and driven through the DevTools protocol at phone size.
"""

import json
import shutil
import threading
import time
from pathlib import Path

import pytest

from builder.config import Paths
from builder.pipeline import build
from builder.serve import make_server
from builder.site import build_site

from .browser import Browser, find_browser
from .conftest import FIXTURE_WEIGHTS

REPO = Path(__file__).parent.parent
PASSPHRASE = "fixture-passphrase"

pytestmark = pytest.mark.skipif(find_browser() is None, reason="no Chrome/Edge available")


@pytest.fixture(scope="module")
def sites(tmp_path_factory):
    root = tmp_path_factory.mktemp("proj")
    shutil.copytree(REPO / "config", root / "config", ignore=shutil.ignore_patterns("crypto.yaml"))
    shutil.copytree(REPO / "app", root / "app")
    (root / "content").mkdir()
    shutil.copy(REPO / "tests" / "fixtures" / "sample_book.md", root / "content" / "Book 9.md")
    (root / "config" / "topics.yaml").write_text(
        "topics:\n  - {id: quant, name: Quant, readings: [1, 1]}\n  - {id: economics, name: Econ, readings: [2, 2]}\n",
        encoding="utf-8")
    (root / "config" / "exam_weights.yaml").write_text(FIXTURE_WEIGHTS, encoding="utf-8")
    paths = Paths(root)
    assert build(paths).ok
    build_site(paths, paths.dist)
    build_site(paths, paths.dist_enc, PASSPHRASE)
    servers = {}
    for name, folder in (("plain", paths.dist), ("enc", paths.dist_enc)):
        srv = make_server(folder, port=0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        servers[name] = f"http://127.0.0.1:{srv.server_address[1]}/"
    yield {"paths": paths, **servers}
    # daemon threads end with the test session


@pytest.fixture
def browser():
    with Browser() as b:
        b.phone()
        yield b


def test_home_and_study_render(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.list')")
    text = browser.eval("document.body.innerText", False)
    assert "Quant" in text and "Econ" in text and "ne sont pas encore validés" not in text  # the weights are marked verified
    browser.goto(sites["plain"] + "#/study/quant", wait_for="document.querySelector('.list a')")
    assert "Regression Basics and Assumptions" in browser.eval("document.body.innerText", False)
    assert browser.console == []


def test_module_reader(sites, browser):
    browser.goto(sites["plain"] + "#/m/m01.2", wait_for="document.querySelector('.los-card')")
    page = browser.eval("""({
        cards: [...document.querySelectorAll('.los-card .id')].map(e => e.innerText),
        example: document.querySelector('.example .ex-title b')?.innerText,
        index: document.querySelectorAll('.los-index li').length,
        next: document.querySelector('.pager .next')?.getAttribute('href'),
        overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    })""", False)
    assert page["cards"] == ["OBJECTIF 01.C"]  # shown in capitals by CSS
    assert page["example"] == "Calculating adjusted R2"
    assert page["index"] == 2  # 1.c and the inferred 1.d
    assert page["next"] == "#/m/m02.1"
    assert not page["overflow"]
    # Deep link to an LOS scrolls it to the top (or as far as a short page allows).
    browser.goto(sites["plain"] + "#/m/m01.1/los.01.b", wait_for="document.getElementById('los.01.b')")
    browser.wait("""(() => {
        const top = document.getElementById('los.01.b').getBoundingClientRect().top;
        const max = document.documentElement.scrollHeight - innerHeight;
        return Math.abs(top) < 120 || (max > 0 && Math.abs(scrollY - max) < 2);
    })()""")


def test_dark_mode_and_theme_setting(sites, browser):
    browser.phone(dark=True)
    browser.goto(sites["plain"] + "#/settings", wait_for="document.querySelector('.seg')")
    bg = lambda: browser.eval("getComputedStyle(document.body).backgroundColor", False)
    assert bg() == "rgb(21, 21, 20)"
    browser.eval("[...document.querySelectorAll('.seg button')].find(b => b.innerText.trim() === 'Clair').click()", False)
    browser.wait("getComputedStyle(document.body).backgroundColor === 'rgb(251, 250, 247)'")


def test_inline_markdown_is_escaped(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.list')")
    out = browser.eval("""import('./js/core/md.js').then(({ inline }) => [
        inline('<img src=x onerror=alert(1)> **b** _i_ R<sup>2</sup>'),
        inline('cost \\\\(x_1 + **y**\\\\) is $5 and $6'),
    ])""")
    assert out[0] == "&lt;img src=x onerror=alert(1)&gt; <strong>b</strong> <em>i</em> R<sup>2</sup>"
    assert 'data-tex="x_1 + **y**"' in out[1] and "$5 and $6" in out[1]


def test_offline_after_first_visit(sites, browser):
    url = sites["plain"] + "#/m/m01.1"
    browser.goto(url, wait_for="document.querySelector('.los-card')")
    browser.wait("navigator.serviceWorker.controller !== null", 20)
    browser.eval("caches.keys().then(k => Promise.all(k.map(n => caches.open(n).then(c => c.keys())))).then(() => true)")
    browser.goto(url, wait_for="document.querySelector('.los-card')")  # now served via the SW, chunk cached
    browser.send("Network.enable")
    browser.send("Network.emulateNetworkConditions", offline=True, latency=0, downloadThroughput=-1, uploadThroughput=-1)
    browser.goto("about:blank")
    browser.goto(url, wait_for="document.querySelector('.los-card')", timeout=20)
    assert "Regression Basics" in browser.eval("document.querySelector('h1').innerText", False)


def test_encrypted_site_unlock(sites, browser):
    data = sites["paths"].dist_enc / "data"
    assert json.loads((data / "meta.json").read_text())["encrypted"] is True
    assert not [p for p in data.rglob("*") if p.is_file() and p.suffix != ".enc" and p.name != "meta.json"]
    assert not any(b"Sample Regression" in p.read_bytes() for p in data.rglob("*.enc"))

    submit = "document.querySelector('#pp').value = %s; document.querySelector('form').requestSubmit()"
    browser.goto(sites["enc"] + "#/m/m01.2", wait_for="document.querySelector('#pp')")
    browser.eval(submit % json.dumps("not it"), False)
    browser.wait("document.querySelector('[role=alert]')")
    assert "?" not in browser.eval("location.href", False)  # passphrase never lands in the URL
    browser.eval(submit % json.dumps(PASSPHRASE), False)
    browser.wait("document.querySelector('.los-card')")
    # The key is remembered on the device: a fresh load opens without the form.
    browser.goto("about:blank")
    browser.goto(sites["enc"] + "#/m/m02.1", wait_for="document.querySelector('.los-card')")
    assert browser.console == []


def test_analytics_and_selection_functions(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.list')")
    out = browser.eval("""Promise.all([import('./js/core/analytics.js'), import('./js/core/select.js')]).then(([a, s]) => {
      const day = 86400000, now = Date.UTC(2026, 9, 28, 12);
      const ev = (qid, correct, conf, ts, los = ['los.01.a'], extra = {}) => ({ type: 'answer', ts,
        payload: { qid, los, topic: 'quant', module: 'm01.1', correct, ms: 120000, confidence: conf, mode: 'drill', choice: 'A', ...extra } });
      const events = [ev('q1', true, 3, now - 2 * day), ev('q2', false, 3, now - day), ev('q3', true, 1, now),
                      ev('q4', false, 2, now, ['los.01.a', 'los.01.b']), ev('q5', true, 2, now),
                      { type: 'study', ts: now, payload: { module: 'm01.2' } }];
      const ans = a.answers(events);
      const byLos = Object.fromEntries(a.groupStats(ans, (e) => e.payload.los).map((g) => [g.key, [g.n, g.correct, g.enough]]));
      const cal = a.calibration(ans);
      const days = a.daily(ans, 3, now);
      const pool = ['q1', 'q2', 'q9'].map((id) => ({ id }));
      return {
        byLos, median: a.median([3, 1, 2, 10]),
        cal: cal.levels.map((l) => [l.n, l.acc]), sureWrong: cal.sureWrong.length, lucky: cal.luckyRight.length,
        days: days.map((d) => d.n), rolling: a.rollingAccuracy(days, 7).map((r) => r.acc),
        coverage: [...a.coverage(['m01.1', 'm01.2', 'm01.3'], events)],
        picked: s.pickQuestions(pool, ans, 3, () => 0).map((q) => q.id),
        set: s.pickItemSet([{ id: 'S1' }, { id: 'S2' }], [ev('x', true, 1, now, undefined, { set: 'S1' })], () => 0).id,
        fmt: [a.formatMs(185000), a.pct(0.666)],
      };
    })""")
    assert out["byLos"] == {"los.01.a": [5, 3, True], "los.01.b": [1, 0, False]}  # multi-LOS answer counts for each
    assert out["median"] == 2.5
    assert out["cal"] == [[1, 1.0], [2, 0.5], [2, 0.5]]
    assert (out["sureWrong"], out["lucky"]) == (1, 1)
    assert out["days"] == [1, 1, 3]
    assert out["rolling"] == [None, None, 0.6]  # needs MIN_N = 5 answers in the window
    assert out["coverage"] == [["m01.1", "practised"], ["m01.2", "studied"], ["m01.3", "untouched"]]
    assert out["picked"] == ["q9", "q2", "q1"]  # unseen, then wrong, then right
    assert out["set"] == "S2"  # unattempted set first
    assert out["fmt"] == ["3:05", "67%"]


def test_drill_answer_is_logged_and_persists(sites, browser):
    browser.goto(sites["plain"] + "#/practice/drill/quant", wait_for="document.querySelector('.option')")
    submit = browser.eval("document.querySelector('.sticky-actions .btn').disabled", False)
    assert submit is True  # nothing chosen yet
    browser.eval("document.querySelectorAll('.option')[0].click()", False)
    browser.wait("document.querySelector('.option[aria-checked=\"true\"]')")
    # Choosing a confidence after an answer submits at once (no separate "Valider" tap)
    browser.eval("[...document.querySelectorAll('.confidence button')].find((b) => b.innerText.trim() === 'Hésitant').click()", False)
    browser.wait("document.querySelector('.feedback')")
    browser.eval("document.querySelector('.sticky-actions .btn').click()", False)  # a stray tap now means "next", not a second answer
    browser.goto("about:blank")
    browser.goto(sites["plain"] + "#/stats", wait_for="document.querySelector('.tiles')")
    events = browser.eval("import('./js/core/events.js').then((m) => m.getEvents())")
    answers = [e for e in events if e["type"] == "answer"]
    assert len(answers) == 1
    p = answers[-1]["payload"]
    assert p["topic"] == "quant" and p["mode"] == "drill" and p["confidence"] == 2 and p["choice"] == "A"
    assert p["los"] and p["module"].startswith("m01.") and isinstance(p["correct"], bool)
    assert answers[-1]["id"][14] == "7"  # UUIDv7
    assert browser.eval("document.querySelector('.tile .v').innerText", False) == str(len(answers))
    assert browser.console == []


SCORING_JS = """Promise.all(['stats-math', 'fsrs', 'mastery', 'smart', 'settings', 'plan', 'data']
  .map((n) => import(`./js/core/${n}.js`))).then(async ([sm, fsrs, mastery, smart, settings, plan, data]) => {
  const DAY = 86400000, now = Date.UTC(2026, 9, 28, 12);
  const manifest = data.manifest();
  const ans = (qid, los, correct, conf, ago) => ({ type: 'answer', ts: now - ago * DAY, payload: { qid, los: [los], topic: 'quant',
    module: 'm01.1', correct, ms: 90000, confidence: conf, mode: 'drill', choice: 'A' } });
  const out = {};
  out.beta = [sm.betaQuantile(0.5, 2, 3), sm.betaCdf(0.3, 2, 5), sm.betaQuantile(0.05, 1, 1), ...sm.betaInterval(6.4, 1.6, 0.9)];
  const c1 = fsrs.review(null, 3, now);
  const good = fsrs.review(c1, 3, now + c1.s * DAY);
  const again = fsrs.review(c1, 1, now + c1.s * DAY);
  out.fsrs = [c1.s, c1.d, good.s, good.d, again.s, fsrs.intervalDays(c1.s, 0.9), fsrs.retrievability(c1.s, c1.s),
              fsrs.cardStatus(c1, now + 2 * c1.s * DAY).overdueDays > 0];
  const sr = manifest.scoring.spaced_repetition;
  out.grades = [[false, 3], [true, 1], [true, 2], [true, 3]].map(([correct, confidence]) => fsrs.gradeAnswer({ correct, confidence }, sr));

  // 4 right + 1 wrong today on 01.b; one answer on 01.c 21 days ago (half weight)
  const events = [ans('sq.01.2.1', 'los.01.c', true, 3, 21), ...[1, 2, 3, 4].map((i) => ans('qb' + i, 'los.01.b', true, 3, 0)),
                  ans('qb5', 'los.01.b', false, 3, 0)];
  const model = mastery.buildModel(events, manifest, now);
  const L = (id) => model.los.get(id);
  out.mastery = { b: [L('los.01.b').n, L('los.01.b').mean], a: [L('los.01.a').n, L('los.01.a').mean, L('los.01.a').forgetting],
                  b_band: L('los.01.b').lo < L('los.01.b').mean && L('los.01.b').mean < L('los.01.b').hi };
  out.order = [...model.los.values()].filter((l) => l.topic === 'quant').sort((x, y) => y.priority - x.priority).map((l) => l.id);
  out.readiness = [model.topics.get('quant').coverage, model.overall.mean > 0 && model.overall.mean < 1];
  const losList = [...model.los.values()];
  const naive = losList.reduce((x, l) => x + (l.hi - l.lo), 0) / losList.length;
  out.band = [model.overall.lo < model.overall.mean && model.overall.mean < model.overall.hi, model.overall.hi - model.overall.lo, naive];

  out.split = [smart.splitMix(10, manifest.scoring.smart_session.mix), smart.sessionSize(15, manifest.scoring)];
  const old = [ans('sq.01.1.1', 'los.01.b', false, 2, 10)];
  const intents = smart.planSession(mastery.buildModel(old, manifest, now), manifest, old, 30);
  out.intents = intents.map((i) => [i.kind, i.reason.split(':')[0]]);
  const items = await smart.resolveSession(intents, old, data.getChunk);
  out.resolved = items.map((i) => [i.kind, Boolean(i.q.stem), [i.q.los].flat().includes(intents.find((x) => x.reason === i.reason).los ?? [i.q.los].flat()[0])]);

  out.settings = settings.settingsFrom([{ type: 'setting', ts: 1, payload: { key: 'daily_minutes', value: 15 } },
    { type: 'setting', ts: 2, payload: { key: 'daily_minutes', value: 60 } }]).daily_minutes;
  const exam = new Date(now + 30 * DAY).toISOString().slice(0, 10);
  const p = plan.dailyPlan(manifest, [], { exam_date: exam }, now);
  out.plan = [p.daysLeft, p.newDays, p.remaining, p.schedule.length, p.schedule.flatMap((d) => d.modules).length];
  // Ten one-LOS modules over Mon..Sun with weekends at 2x: weekend days take the larger share
  const week = Array.from({ length: 7 }, (_, k) => new Date(2026, 10, 2 + k).getTime())
    .map((date) => ({ date, weight: plan.isWeekend(date) ? 2 : 1 }));
  out.spread = plan.spread(Array.from({ length: 10 }, (_, k) => ({ id: `m${k}`, load: 1 })), week).map((d) => d.modules.length);
  // Exam 17 days out: 3 days of new material from today, 4 from yesterday (when the plan was set)
  const exam2 = new Date(now + 17 * DAY).toISOString().slice(0, 10);
  const opts = { exam_date: exam2 };
  const setting = (key, value, ts) => ({ type: 'setting', ts, payload: { key, value } });
  const study = (module, ts, extra = {}) => ({ type: 'study', ts, payload: { module, topic: 'quant', auto: false, ...extra } });
  const ids = (list) => list.map((m) => m.id);
  const run = (evts, at = now) => plan.dailyPlan(manifest, evts.sort((x, y) => x.ts - y.ts), opts, at);
  const set = [setting('exam_date', exam2, now - DAY)];
  const yest = run([...set], now - DAY);
  const first = yest.today[0].id;
  out.carry = {
    yesterday: ids(yest.today),
    today: run([...set]).today.map((m) => [m.id, m.carried]),
    // viewing it for a minute or practising it doesn't finish it
    viewed: ids(run([...set, study(first, now - DAY + 1000, { auto: true }),
      { type: 'answer', ts: now - DAY + 2000, payload: { module: first } }]).today),
    finished: ids(run([...set, study(first, now - DAY + 1000)]).today),
    undone: ids(run([...set, study(first, now - DAY + 1000), study(first, now - DAY + 2000, { finished: false })]).today),
    tickedToday: run([...set, study(first, now)]).today.map((m) => [m.id, m.done]),
  };
  // A new exam date never brings back a finished module
  const moved = run([...set, study(first, now - DAY + 1000), setting('exam_date', exam2, now)]);
  out.dateChange = { scheduled: moved.schedule.flatMap((d) => ids(d.modules)), carried: moved.carried, remaining: moved.remaining };
  // Studying ahead: finish today's list and tomorrow's first module today
  const fresh = [setting('exam_date', exam2, now)];
  const p0 = run([...fresh]);
  const nextDay = p0.schedule.findIndex((d, k) => k > 0 && d.modules.length);
  const ahead = run([...fresh, ...p0.today.map((m) => study(m.id, now)), study(p0.schedule[nextDay].modules[0].id, now)]);
  out.ahead = { aheadDays: ahead.aheadDays, todayIds: ids(ahead.today), before: p0.schedule[nextDay].modules.length,
                after: ahead.schedule[nextDay].modules.length, onTrack: p0.aheadDays };
  // Behind, then rebalanced: nothing is carried once the plan is laid out again from today
  const behind = run([...set]);
  const rebalanced = run([...set, setting('plan_reset', 'x', now)]);
  out.rebalance = { behind: behind.aheadDays, carriedBefore: behind.carried, carriedAfter: rebalanced.carried, after: rebalanced.aheadDays };
  out.streak = mastery.streak([0, 1, 3].map((d) => ({ type: 'answer', ts: now - d * DAY, payload: {} })), now);
  return out;
})"""


def test_scoring_logic(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.tiles')")
    o = browser.eval(SCORING_JS)
    # Beta quantiles/CDF against SciPy reference values
    for got, want in zip(o["beta"], [0.385727568, 0.579825, 0.05, 0.542740903, 0.969372874]):
        assert abs(got - want) < 1e-6, (got, want)
    # FSRS-4.5 against the published formulas (reference computed independently in Python)
    s0, d0, s_good, d_good, s_again, interval, r_at_s, overdue = o["fsrs"]
    assert s0 == pytest.approx(3.7145) and d0 == pytest.approx(5.1618)
    assert s_good == pytest.approx(14.094985, rel=1e-6) and d_good == pytest.approx(5.1618)
    assert s_again == pytest.approx(1.418525, rel=1e-6)
    assert interval == pytest.approx(s0) and r_at_s == pytest.approx(0.9) and overdue is True
    assert o["grades"] == [1, 2, 3, 4]
    # Mastery: 01.b has 4/5 right today; topic accuracy (decayed) is the prior centre
    n_b, mean_b = o["mastery"]["b"]
    assert n_b == 5 and 0.75 < mean_b < 0.85 and o["mastery"]["b_band"]
    assert o["mastery"]["a"] == [0, pytest.approx(1 / 3, abs=1e-3), 1]  # untouched: guessing prior, full forgetting
    # Untouched LOS (full forgetting, max uncertainty) outrank practised ones. Among the practised,
    # 01.b (mastery ≈ 0.80) outranks 01.c (≈ 0.84): both sit at the forgetting floor, and 01.c's
    # larger uncertainty bonus (n = 1) doesn't offset its higher mastery.
    assert set(o["order"][:2]) == {"los.01.a", "los.01.d"}
    assert o["order"][2:] == ["los.01.b", "los.01.c"]
    assert o["readiness"] == [0.5, True]  # 2 of 4 quant LOS practised
    ordered, width, naive = o["band"]
    assert ordered and 0 < width < naive / 2  # averaging LOS narrows the readiness band
    assert o["split"] == [{"priority": 5, "review": 3, "maintenance": 2}, 15]  # one minute per question
    kinds = [k for k, _ in o["intents"]]
    assert "review" in kinds  # the wrong answer from 10 days ago is due
    assert all(r in ("Priorité", "Révision", "Découverte", "Entretien") for _, r in o["intents"])
    assert o["resolved"] and all(has_stem for _, has_stem, _ in o["resolved"])
    assert o["settings"] == 60  # last write wins
    assert o["plan"][:4] == [30, 16, 3, 16] and o["plan"][4] == 3  # every module scheduled exactly once
    spread = o["spread"]  # Mon..Sun
    assert sum(spread) == 10 and min(spread[5:]) >= max(spread[:5]) and sum(spread[5:]) > 2 * sum(spread[:5]) / 5
    c = o["carry"]
    assert c["yesterday"] == ["m01.1"]
    assert c["today"] == [["m01.1", True], ["m01.2", False]]  # unfinished work first, then today's share
    assert c["viewed"] == ["m01.1", "m01.2"]  # an automatic view or a practice answer doesn't finish it
    assert c["finished"] == ["m01.2"] and c["undone"] == ["m01.1", "m01.2"]
    assert c["tickedToday"] == [["m01.1", True], ["m01.2", False]]  # ticked off today, list unchanged
    assert o["dateChange"] == {"scheduled": ["m01.2", "m02.1"], "carried": 0, "remaining": 2}
    a = o["ahead"]
    assert a["onTrack"] == 0 and a["aheadDays"] > 0 and a["before"] == 1 and a["after"] == 0
    r = o["rebalance"]
    assert r["behind"] < 0 and r["carriedBefore"] == 1 and r["carriedAfter"] == 0 and r["after"] == 0
    assert o["streak"] == 2


PHASE7_JS = """Promise.all(['mock', 'graph', 'events', 'sync'].map((n) => import(`./js/core/${n}.js`)))
  .then(async ([mock, graph, events, sync]) => {
  const out = {};
  let seed = 7;
  const rng = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const set = (topic, i) => ({ id: `${topic}.${i}`, topic, questions: [1, 2, 3, 4].map((k) => ({ id: `${topic}.${i}.${k}`, answer: 'A' })) });
  const sets = new Map([['eq', Array.from({ length: 10 }, (_, i) => set('eq', i))], ['fi', Array.from({ length: 10 }, (_, i) => set('fi', i))]]);
  const built = mock.buildMock(sets, [{ id: 'eq', weight: 2 }, { id: 'fi', weight: 1 }], { questions: 24, sessions: 2, rng });
  const all = built.sessions.flat();
  out.mock = { plan: built.plan, sessions: built.sessions.map((s) => s.length), unique: new Set(all.map((s) => s.id)).size === all.length };
  const scored = mock.scoreSession([set('eq', 0), set('fi', 0)], { 'eq.0.1': { choice: 'A' }, 'eq.0.2': { choice: 'B' }, 'fi.0.1': { choice: 'A' } });
  out.score = [scored.n, scored.correct, scored.perTopic.map((t) => [t.topic, t.correct])];
  const q = (id, vignette, source = 'schweser') => ({ id, module: 'm01.1', vignette, source, options: ['x', 'y', 'z'], answer: 'A' });
  const cases = mock.itemSetsFor({ topic: 'quant', item_sets: [],
    questions: [q('a', 'Case 1'), q('b', 'Case 1'), q('c', 'Case 1'), q('d', 'Case 2'), q('e', 'Case 3', 'generated'), q('f', 'Case 3', 'generated')] });
  out.cases = cases.map((s) => [s.id, s.vignette, s.questions.length, s.questions.every((x) => x.vignette === null)]);

  // a builds on b and d; b builds on c. c and d are equally weak: the deeper one (c) is the root gap.
  const g = { edges: [{ from: 'a', to: 'b', type: 'requires' }, { from: 'b', to: 'c', type: 'requires' },
                      { from: 'a', to: 'd', type: 'requires' }, { from: 'c', to: 'a', type: 'contrasts_with' }] };
  out.pre = Object.fromEntries(graph.prerequisites(g, 'a'));
  const means = { a: 0.9, b: 0.6, c: 0.3, d: 0.3 };
  const model = { los: new Map(Object.entries(means).map(([m, mean]) => [`los.${m}`, { mean, n: 1 }])) };
  const man = { topics: [{ readings: [{ modules: Object.keys(means).map((m) => ({ id: m, los: [`los.${m}`] })) }] }] };
  out.gap = graph.rootGap(g, model, man, 'a');
  out.noGap = graph.rootGap(g, model, man, 'd');

  // uuidv7 has random bits, so each event is created once and reused
  const ev = [0, 1, 2, 3, 4].map((i) => ({ id: events.uuidv7(1_700_000_000_000 + i), v: 1, device: 'other', ts: 1_700_000_000_000 + i,
    type: 'answer', payload: { qid: `q${i}`, los: ['los.01.a'], topic: 'quant', correct: true, ms: 1000, confidence: 2, mode: 'drill' } }));
  const incoming = [ev[1], ev[2], ev[3], { id: 'junk' }];
  const first = await events.importEvents(incoming);
  const again = await events.importEvents(incoming);
  out.imports = [[first.fresh.length, first.duplicates, first.invalid], [again.fresh.length, again.duplicates, again.invalid]];

  out.parse = ['{', '{"format": "other", "events": []}', '{"format": "fr-b2-progress", "version": 2, "events": []}']
    .map((t) => { try { sync.parseProgress(t); return 'ok'; } catch (e) { return e.message; } });

  // Gist sync against a stubbed GitHub API: pull one new event, push the union back.
  const remote = { format: sync.FORMAT, version: 1, events: [ev[4], ev[1]] };
  const calls = [];
  const realFetch = window.fetch;
  window.fetch = async (url, init = {}) => {
    calls.push([init.method ?? 'GET', url.replace('https://api.github.com', ''), init.headers?.Authorization, init.body ? JSON.parse(init.body) : null]);
    const body = (init.method ?? 'GET') === 'GET' ? { files: { 'fr-b2-progress.json': { content: JSON.stringify(remote) } } } : { id: 'g123' };
    return new Response(JSON.stringify(body), { status: 200 });
  };
  try {
    const r = await sync.syncGist({ token: 'tok', id: 'g123', lastSync: null });
    out.sync = { result: r, calls: calls.map(([m, u, auth, body]) => [m, u, auth, body && JSON.parse(body.files['fr-b2-progress.json'].content).events.length]),
                 saved: await sync.gistSettings() };
  } finally {
    window.fetch = realFetch;
  }
  return out;
})"""


def test_phase7_logic(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.tiles')")
    o = browser.eval(PHASE7_JS)
    # Mock: 24 questions split 2:1 by weight, whole item sets, no set used twice, two sessions
    assert o["mock"]["plan"] == [{"topic": "eq", "target": 16, "got": 16}, {"topic": "fi", "target": 8, "got": 8}]
    assert o["mock"]["sessions"] == [3, 3] and o["mock"]["unique"]
    assert o["score"] == [8, 2, [["eq", 1], ["fi", 1]]]
    # Schweser questions sharing a vignette become one case; singletons and generated ones don't
    assert o["cases"] == [["case.m01.1.1", "Case 1", 3, True]]
    assert o["pre"] == {"b": 1, "d": 1, "c": 2}  # "contrasts_with" isn't a dependency
    assert o["gap"] == {"module": "c", "mean": 0.3, "practised": True, "depth": 2}
    assert o["noGap"] is None
    # Importing the same file twice adds nothing the second time; malformed events are counted
    assert o["imports"] == [[3, 0, 1], [0, 3, 1]]
    assert o["parse"][0] == "Ce fichier n'est pas un JSON valide."
    assert "sauvegarde de progrès Français B2" in o["parse"][1] and "plus récente" in o["parse"][2]
    s = o["sync"]
    assert s["result"] == {"pulled": 1, "pushed": 4, "id": "g123"}
    assert s["calls"] == [["GET", "/gists/g123", "Bearer tok", None], ["PATCH", "/gists/g123", "Bearer tok", 4]]
    assert s["saved"]["id"] == "g123" and s["saved"]["lastSync"] > 0
    # The merged log survives a reload (it is in IndexedDB, not just memory)
    browser.goto("about:blank")
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.tiles')")
    assert browser.eval("import('./js/core/events.js').then((m) => m.getEvents()).then((l) => l.length)") == 4


SYNC_JS = """Promise.all(['events', 'sync'].map((n) => import(`./js/core/${n}.js`))).then(async ([events, sync]) => {
  const out = {};
  out.flagValid = events.isEvent({ id: 'x', v: 1, device: 'd', ts: 1, type: 'flag', payload: { qid: 'q.01.a.001', note: 'key?' } });
  const local = await events.getEvents();
  const calls = [];
  const realFetch = window.fetch;
  window.fetch = async (url, init = {}) => {
    calls.push(init.method ?? 'GET');
    const remote = { format: sync.FORMAT, version: 1, events: local };
    const body = (init.method ?? 'GET') === 'GET' ? { files: { 'fr-b2-progress.json': { content: JSON.stringify(remote) } } } : { id: 'g9' };
    return new Response(JSON.stringify(body), { status: 200 });
  };
  try {
    // The Gist already holds every local event: pull only, no rewrite
    out.same = await sync.syncGist({ token: 'tok', id: 'g9' });
    out.sameCalls = calls.splice(0);
    // Auto-sync never creates a Gist: without an id it makes no request
    await sync.saveGistSettings({ token: 'tok', id: '', lastSync: null });
    await sync.autoSync();
    out.noIdCalls = calls.splice(0);
    // With an id it syncs, and a failure is recorded instead of thrown
    await sync.saveGistSettings({ token: 'tok', id: 'g9', lastSync: null });
    window.fetch = async () => new Response('{}', { status: 401 });
    await sync.autoSync();
    out.failed = (await sync.gistSettings()).lastError;
  } finally {
    window.fetch = realFetch;
    await sync.saveGistSettings({ token: '', id: '', lastSync: null });
  }
  return out;
})"""


def test_sync_and_flags(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.tiles')")
    o = browser.eval(SYNC_JS)
    assert o["flagValid"] is True
    assert o["sameCalls"] == ["GET"] and o["same"]["pulled"] == 0
    assert o["noIdCalls"] == []
    assert o["failed"] == "GitHub 401 (vérifiez le jeton)"
    # Analytics lists a reported question
    browser.eval("import('./js/core/events.js').then((m) => m.logEvent('flag', { qid: 'q.test.1', module: null, note: 'Key looks wrong' }))")
    browser.goto(sites["plain"] + "#/stats", wait_for="document.querySelector('main h1')")
    browser.wait("document.body.textContent.includes('Questions signalées')")
    assert "Key looks wrong" in browser.eval("document.body.innerText", False)


def test_phase7_views_render(sites, browser):
    browser.goto(sites["plain"] + "#/practice/mock", wait_for="document.querySelector('h1')")
    browser.wait("document.querySelector('h1').innerText === 'Examen blanc'")
    assert "Examen complet · 40 questions" in browser.eval("document.body.innerText", False)
    browser.goto(sites["plain"] + "#/map", wait_for="document.querySelector('main h1, main svg')")
    browser.goto(sites["plain"] + "#/settings", wait_for="document.querySelector('details')")
    text = browser.eval("document.body.innerText", False)
    assert "Exporter mes progrès" in text and "Importer des progrès" in text and "Gist" in text
    assert not browser.console, browser.console


CARDS_JS = """import('./js/views/practice.js').then(({ cardQueue }) => {
  const DAY = 86400000, now = Date.UTC(2026, 9, 28, 12);
  const cards = ['a', 'b', 'c', 'd', 'e'].map((id) => ({ id }));
  const rev = (card, grade, ago) => ({ type: 'review', ts: now - ago * DAY, payload: { card, grade } });
  // a: reviewed 30 days ago (due, lowest recall); b: 5 days ago (due); c: yesterday (not due yet); d, e: never seen
  const ev = [rev('a', 3, 30), rev('b', 3, 5), rev('c', 3, 1), { type: 'review', ts: now, payload: { card: 'other-deck', grade: 3 } }];
  const q = cardQueue(cards, ev, now, { newPerDay: 1 });
  const more = cardQueue(cards, ev, now, { newPerDay: 1, extraNew: 10 });
  const started = cardQueue(cards, [...ev, rev('d', 3, 0)], now, { newPerDay: 1 });
  return { queue: q.queue.map((c) => c.id), due: q.due, fresh: q.fresh, more: more.queue.map((c) => c.id),
           started: started.queue.map((c) => c.id), newToday: started.newToday };
})"""


def test_card_queue(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.tiles')")
    o = browser.eval(CARDS_JS)
    assert o["queue"] == ["a", "b", "d"]  # due cards, lowest recall first, then today's new-card allowance
    assert (o["due"], o["fresh"]) == (2, 2)
    assert o["more"] == ["a", "b", "d", "e"]  # "10 nouvelles cartes de plus" raises the allowance
    assert o["started"] == ["a", "b"] and o["newToday"] == 1  # a card first seen today uses the allowance; other decks don't


@pytest.fixture(scope="module")
def real_site(tmp_path_factory):
    """The real French content (content/ + generated/ + config/) built and served."""
    root = tmp_path_factory.mktemp("real")
    for name in ("config", "app", "content", "generated"):
        shutil.copytree(REPO / name, root / name, ignore=shutil.ignore_patterns("crypto.yaml"))
    paths = Paths(root)
    assert build(paths).ok
    build_site(paths, paths.dist)
    srv = make_server(paths.dist, port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/"


@pytest.mark.skipif(not (REPO / "generated").exists(), reason="real content not present")
def test_french_content_lesson_cards_and_drill(real_site, browser):
    browser.goto(real_site + "#/m/m51.1", wait_for="document.querySelector('.los-card')")
    assert "Il faut que" in browser.eval("document.querySelector('h1').innerText", False)
    assert "L'essentiel en 4 étapes" in browser.eval("document.body.innerText", False)
    # Vocabulary deck: a new card, flip, grade "Bien", and the review is logged
    browser.goto(real_site + "#/practice/cards/vocabulaire", wait_for="document.querySelector('.flashcard')")
    browser.eval("[...document.querySelectorAll('.sticky-actions .btn')].find((b) => b.innerText.includes('Voir la réponse')).click()", False)
    browser.wait("[...document.querySelectorAll('.sticky-actions .btn')].some((b) => b.innerText.trim() === 'Bien')")
    browser.eval("[...document.querySelectorAll('.sticky-actions .btn')].find((b) => b.innerText.trim() === 'Bien').click()", False)
    browser.wait("import('./js/core/events.js').then((m) => m.getEvents()).then((l) => l.some((e) => e.type === 'review'))", 10)
    # A grammar drill question shows French feedback
    browser.goto(real_site + "#/practice/drill/subjonctif", wait_for="document.querySelector('.option')")
    browser.eval("document.querySelectorAll('.option')[0].click()", False)
    browser.eval("[...document.querySelectorAll('.confidence button')].find((b) => b.innerText.trim() === 'Sûr').click()", False)
    browser.wait("document.querySelector('.feedback')")
    assert any(w in browser.eval("document.querySelector('.feedback').innerText", False) for w in ("Correct", "Faux"))
    assert not browser.console, browser.console


@pytest.fixture(scope="module")
def listening_site(tmp_path_factory):
    """The fixture book plus one listening set with a real (silent, 1 s) WAV, built encrypted."""
    import wave
    from .test_build import _listening_set
    root = tmp_path_factory.mktemp("listen")
    shutil.copytree(REPO / "config", root / "config", ignore=shutil.ignore_patterns("crypto.yaml"))
    shutil.copytree(REPO / "app", root / "app")
    (root / "content").mkdir()
    shutil.copy(REPO / "tests" / "fixtures" / "sample_book.md", root / "content" / "Book 9.md")
    (root / "config" / "topics.yaml").write_text(
        "topics:\n  - {id: quant, name: Quant, readings: [1, 1]}\n  - {id: economics, name: Econ, readings: [2, 2]}\n",
        encoding="utf-8")
    (root / "config" / "exam_weights.yaml").write_text(FIXTURE_WEIGHTS, encoding="utf-8")
    audio = root / "audio-src"
    audio.mkdir()
    with wave.open(str(audio / "track.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b"\0\0" * 8000)
    (root / "config" / "audio.yaml").write_text(f"source: '{audio.as_posix()}'\n", encoding="utf-8")
    paths = Paths(root)
    build(paths)  # learns the module hash
    chunk = json.loads(next((paths.data / "chunks").glob("quant.*.json")).read_text(encoding="utf-8"))
    mod_hash = next(m for m in chunk["modules"] if m["id"] == "m01.2")["hash"]
    learning = {"logic_chain": [{"stage": s, "md": "x"} for s in ("assumption", "mechanism", "result")],
                "why_it_matters": "x", "exam_approach": {"look_first": ["x"], "traps": ["x"], "distractors": ["x"]}}
    doc = {"module": "m01.2", "source_hash": mod_hash, "learning": learning, "connections": [], "questions": [],
           "item_sets": [_listening_set(3)], "formulas": []}
    (root / "generated" / "quant").mkdir(parents=True)
    (root / "generated" / "quant" / "m01.2.json").write_text(json.dumps(doc), encoding="utf-8")
    assert build(paths).ok
    build_site(paths, paths.dist_enc, PASSPHRASE)
    srv = make_server(paths.dist_enc, port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/"


def test_listening_set_encrypted_audio_exam_mode_and_transcript(listening_site, browser):
    submit = "document.querySelector('#pp').value = %s; document.querySelector('form').requestSubmit()"
    browser.goto(listening_site + "#/practice/set/quant/m01.2", wait_for="document.querySelector('#pp')")
    browser.eval(submit % json.dumps(PASSPHRASE), False)
    browser.wait("document.querySelector('.audio-player button.play:not([disabled])')", 20)
    assert browser.eval("document.querySelector('audio').src", False).startswith("blob:")  # decrypted in the browser
    play = "document.querySelector('.audio-player button.play').click()"
    for n in (1, 2):  # exam mode: two listens, each from the start
        browser.eval(play, False)
        browser.wait(f"document.querySelector('.audio-player').dataset.used === '{n}'")
        browser.wait("document.querySelector('audio').ended", 10)
    browser.wait("document.querySelector('.audio-player button.play').disabled")
    assert "Écoutes terminées" in browser.eval("document.querySelector('.audio-player button.play').innerText", False)
    # Practice mode lifts the limit
    browser.eval("document.querySelector('.audio-player input[type=checkbox]').click()", False)
    browser.wait("!document.querySelector('.audio-player button.play').disabled")
    # Answer and submit: the transcript appears and answers are logged as listening
    browser.eval("document.querySelectorAll('.qcard').forEach((c) => c.querySelectorAll('.option')[1].click())", False)
    browser.eval("document.querySelectorAll('.qcard').forEach((c) => [...c.querySelectorAll('.confidence button')].find((b) => b.innerText.trim() === 'Sûr').click())", False)
    browser.wait("!document.querySelector('.sticky-actions .btn').disabled")
    browser.eval("document.querySelector('.sticky-actions .btn').click()", False)
    browser.wait("document.querySelector('.transcript')")
    assert "Au revoir" in browser.eval("document.querySelector('.transcript').innerText", False)
    count = "import('./js/core/events.js').then((m) => m.getEvents()).then((l) => l.filter((e) => e.type === 'answer').length)"
    for _ in range(50):  # the answers are saved one by one after submitting
        if browser.eval(count) == 3:
            break
        time.sleep(0.1)
    events = browser.eval("import('./js/core/events.js').then((m) => m.getEvents())")
    modes = [e["payload"]["mode"] for e in events if e["type"] == "answer"]
    assert modes == ["listening"] * 3
    assert not browser.console, browser.console


GAME_JS = """import('./js/core/game.js').then((g) => {
  const DAY = 86400000, now = new Date(2026, 10, 1, 15).getTime();
  const ans = (correct, ts, extra = {}) => ({ type: 'answer', ts, payload: { correct, confidence: 2, mode: 'drill', ...extra } });
  const out = {};
  out.xp = [g.xpFor(ans(true, 0)), g.xpFor(ans(true, 0, { confidence: 3 })), g.xpFor(ans(false, 0)),
            g.xpFor(ans(true, 0, { mode: 'listening' })), g.xpFor({ type: 'review', payload: { grade: 3 } }),
            g.xpFor({ type: 'review', payload: { grade: 1 } }), g.xpFor({ type: 'study', payload: { auto: true } }),
            g.xpFor({ type: 'study', payload: {} }), g.xpFor({ type: 'setting', payload: {} })];
  out.levels = [0, 99, 100, 249, 250].map((x) => [g.levelFor(x).level, g.levelFor(x).into]);
  out.title = g.levelFor(0).title;
  // yesterday: 10 right in a row, then a wrong one; today: a perfect 3-question set (one attempt)
  const ev = [];
  for (let k = 0; k < 10; k++) ev.push(ans(true, now - DAY + k * 1000));
  ev.push(ans(false, now - DAY + 20000));
  for (let k = 1; k <= 3; k++) ev.push(ans(true, now - 3600000 + k, { set: 'S1', mode: 'item_set' }));
  const s = g.gameState(ev, { daily_xp: 30 }, now);
  out.state = { today: s.today, goalDone: s.goalDone, streak: s.streak, bestCombo: s.bestCombo,
                badges: [...s.earned.keys()].sort(), week: s.week.map((d) => d.xp) };
  return out;
})"""


def test_game_rules(sites, browser):
    browser.goto(sites["plain"] + "#/", wait_for="document.querySelector('.hero-card')")
    o = browser.eval(GAME_JS)
    assert o["xp"] == [10, 12, 2, 15, 5, 2, 0, 20, 0]  # effort always earns something; right and sure earns most
    assert o["levels"] == [[1, 0], [1, 99], [2, 0], [2, 149], [3, 0]] and o["title"] == "Touriste"
    st = o["state"]
    assert st["today"] == 30 and st["goalDone"] and st["streak"] == 2 and st["bestCombo"] == 10  # the wrong answer resets the run
    assert st["badges"] == ["combo10", "first", "perfect"]
    assert st["week"][-1] == 30 and st["week"][-2] == 102
