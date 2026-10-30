"""Performance / PWA / accessibility audit of a built site.

Runs Lighthouse (`npx lighthouse`) when Node is installed. Otherwise it performs its own
checks through the DevTools protocol: Chrome's installability verdict, cold-load timings
under mobile throttling, transferred bytes, offline reload and a few accessibility basics.
"""

from __future__ import annotations

import gzip
import json
import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from .browser import Browser, find_browser
from .serve import make_server

TARGET_LOAD_MS = 1500
TARGET_SWITCH_MS = 100
TARGET_JS_KB = 150


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


@dataclass
class AuditResult:
    checks: list[Check] = field(default_factory=list)
    lighthouse: dict[str, float] | None = None

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


def _js_gzip_kb(site: Path) -> float:
    """Startup JS: the modules index.html preloads (lazy views and KaTeX load later)."""
    mods = re.findall(r'<link rel="modulepreload" href="([^"]+)"', (site / "index.html").read_text(encoding="utf-8"))
    return sum(len(gzip.compress((site / m).read_bytes(), 9)) for m in mods) / 1024


def lighthouse(url: str) -> dict[str, float] | None:
    npx = shutil.which("npx")
    browser = find_browser()
    if not npx or not browser:
        return None
    res = subprocess.run([npx, "--yes", "lighthouse", url, "--output=json", "--quiet", "--form-factor=mobile",
                          "--only-categories=performance,accessibility,best-practices",
                          "--chrome-flags=--headless=new"], capture_output=True, text=True,
                         env={**__import__("os").environ, "CHROME_PATH": browser}, timeout=600)
    if res.returncode != 0:
        return None
    report = json.loads(res.stdout)
    return {k: round(v["score"] * 100) for k, v in report["categories"].items() if v.get("score") is not None}


def audit(site: Path, start_route: str = "#/") -> AuditResult:
    result = AuditResult()
    server = make_server(site, port=0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        js_kb = _js_gzip_kb(site)
        result.checks.append(Check("Startup JavaScript (gzip, lazy views excluded)", js_kb < TARGET_JS_KB, f"{js_kb:.1f} KB (target < {TARGET_JS_KB} KB)"))
        encrypted = '"encrypted": true' in (site / "data" / "meta.json").read_text(encoding="utf-8")

        with Browser() as b:
            b.phone()
            b.goto(url + start_route, wait_for="document.querySelector('main, #pp')", timeout=30)
            b.wait("navigator.serviceWorker.controller !== null", 30)
            errors = b.send("Page.getInstallabilityErrors").get("installabilityErrors", [])
            result.checks.append(Check("Installable as an app (Chrome's verdict)", not errors,
                                       "no errors" if not errors else "; ".join(e.get("errorId", "?") for e in errors)))

        # Loads on a simulated mid-range phone (4x CPU, 150 ms RTT, 9 Mbps). "First visit" uses a
        # fresh browser profile each run (empty caches, no service worker); "repeat visit" reloads in
        # the same profile once the service worker has the shell, the everyday case on a phone.
        ready = "document.querySelector('#pp')" if encrypted else "document.querySelector('.tiles')"
        what = "unlock screen" if encrypted else "dashboard"

        # Record the moment the ready element appears (polling for it would add up to ~0.5 s of
        # detection delay on a throttled CPU).
        mark = ("new MutationObserver((_, o) => { if (" + ready + ") { window.__ready = performance.now(); o.disconnect(); } })"
                ".observe(document, {subtree: true, childList: true});")

        def throttle(b: Browser) -> None:
            b.send("Page.addScriptToEvaluateOnNewDocument", source=mark)
            b.send("Network.enable")
            b.send("Network.emulateNetworkConditions", offline=False, latency=150,
                   downloadThroughput=9_000_000 / 8, uploadThroughput=1_500_000 / 8)
            b.send("Emulation.setCPUThrottlingRate", rate=4)

        def timed(b: Browser) -> tuple[float, float, float]:
            b.goto("about:blank")
            b.goto(url + start_route, wait_for=ready, timeout=60)
            fcp = b.eval("performance.getEntriesByName('first-contentful-paint')[0]?.startTime ?? 0", False)
            # decodedBodySize: what was loaded, uncompressed (transferSize reads 0 when the
            # service worker answers, so it can't be used here).
            kb = b.eval("performance.getEntriesByType('resource').reduce((s, r) => s + (r.decodedBodySize || 0), 0)", False) / 1024
            return b.eval("window.__ready", False), fcp, kb

        first = []
        for _ in range(3):
            with Browser() as b:
                b.phone()
                throttle(b)
                first.append(timed(b))
        first.sort()
        med, fcp, kb = first[len(first) // 2]
        result.checks.append(Check(f"First visit to usable {what} (4x CPU, 4G)", med < TARGET_LOAD_MS,
                                   f"median {med:.0f} ms (target < {TARGET_LOAD_MS} ms); first paint {fcp:.0f} ms; {kb:.0f} KB loaded (uncompressed)"))

        with Browser() as b:
            b.phone()
            b.goto(url + start_route, wait_for="document.querySelector('main, #pp')", timeout=30)
            b.wait("navigator.serviceWorker.controller !== null", 30)
            throttle(b)
            repeat = sorted(timed(b) for _ in range(3))
        med, fcp, _ = repeat[len(repeat) // 2]
        result.checks.append(Check(f"Repeat visit to usable {what} (4x CPU, 4G)", med < TARGET_LOAD_MS,
                                   f"median {med:.0f} ms (target < {TARGET_LOAD_MS} ms); first paint {fcp:.0f} ms"))

        # Offline: once the service worker has the shell, a reload with no network still works.
        with Browser() as b:
            b.phone()
            b.goto(url + start_route, wait_for="document.querySelector('main, #pp')", timeout=30)
            b.wait("navigator.serviceWorker.controller !== null", 30)
            b.goto(url + start_route, wait_for="document.querySelector('main, #pp')", timeout=30)
            b.send("Network.enable")
            b.send("Network.emulateNetworkConditions", offline=True, latency=0, downloadThroughput=-1, uploadThroughput=-1)
            b.goto("about:blank")
            ok = True
            try:
                b.goto(url + start_route, wait_for="document.querySelector('main, #pp')", timeout=20)
            except TimeoutError:
                ok = False
            result.checks.append(Check("Works offline after first visit", ok, "app shell loads with the network off" if ok else "failed to load offline"))

            # Accessibility basics on the loaded page.
            a11y = b.eval("""(() => ({
              lang: !!document.documentElement.lang,
              imgs: [...document.images].filter((i) => !i.hasAttribute('alt')).length,
              unlabeled: [...document.querySelectorAll('button, a, input')].filter((el) =>
                !(el.innerText || '').trim() && !el.getAttribute('aria-label') && !el.labels?.length && el.type !== 'hidden').length,
              viewport: !!document.querySelector('meta[name=viewport]'),
            }))()""", False)
            problems = [k for k, bad in [("missing lang", not a11y["lang"]), (f"{a11y['imgs']} images without alt", a11y["imgs"]),
                                          (f"{a11y['unlabeled']} unlabeled controls", a11y["unlabeled"]), ("no viewport meta", not a11y["viewport"])] if bad]
            result.checks.append(Check("Accessibility basics", not problems, "; ".join(problems) or "lang, alt text, control labels, viewport"))
        result.lighthouse = lighthouse(url + start_route)
    finally:
        server.shutdown()
    return result
