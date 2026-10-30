"""Minimal Chrome/Edge DevTools-protocol driver (end-to-end tests, screenshots, `builder audit`).

Real phone emulation (viewport, DPR, touch, prefers-color-scheme) and the ability to
wait for async content, which plain `--headless --screenshot` can't do.
"""

from __future__ import annotations

import base64
import itertools
import json
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

import websocket

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def find_browser() -> str | None:
    for c in CANDIDATES:
        if Path(c).exists() or shutil.which(c):
            return c
    return None


class Browser:
    def __init__(self, executable: str | None = None):
        exe = executable or find_browser()
        if not exe:
            raise RuntimeError("No Chrome/Edge found")
        self.profile = Path(tempfile.mkdtemp(prefix="cfa-cdp-"))
        self.proc = subprocess.Popen(
            [exe, "--headless=new", "--disable-gpu", "--autoplay-policy=no-user-gesture-required", "--no-first-run", "--no-default-browser-check",
             "--remote-debugging-port=0", f"--user-data-dir={self.profile}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = self.profile / "DevToolsActivePort"
        for _ in range(100):
            if port_file.exists() and port_file.read_text().strip():
                break
            time.sleep(0.1)
        port = int(port_file.read_text().split()[0])
        pages = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list"))
        ws_url = next(p["webSocketDebuggerUrl"] for p in pages if p["type"] == "page")
        self.ws = websocket.create_connection(ws_url, timeout=60, suppress_origin=True)
        self.ids = itertools.count(1)
        self.console: list[str] = []
        self.send("Runtime.enable")
        self.send("Page.enable")

    def send(self, method: str, **params: Any) -> dict[str, Any]:
        msg_id = next(self.ids)
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("method") == "Runtime.exceptionThrown":
                self.console.append(msg["params"]["exceptionDetails"].get("text", "") + " " +
                                    str(msg["params"]["exceptionDetails"].get("exception", {}).get("description", "")))
            elif msg.get("method") == "Runtime.consoleAPICalled" and msg["params"]["type"] in ("error", "warning"):
                self.console.append(" ".join(str(a.get("value", a.get("description", ""))) for a in msg["params"]["args"]))
            if msg.get("id") == msg_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def phone(self, width: int = 390, height: int = 844, dark: bool = False) -> None:
        self.send("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=2, mobile=True)
        self.send("Emulation.setTouchEmulationEnabled", enabled=True)
        self.send("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])

    def desktop(self, width: int = 1280, height: int = 900, dark: bool = False) -> None:
        self.send("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=False)
        self.send("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])

    def eval(self, expression: str, await_promise: bool = True) -> Any:
        res = self.send("Runtime.evaluate", expression=expression, awaitPromise=await_promise, returnByValue=True)
        if "exceptionDetails" in res:
            raise RuntimeError(res["exceptionDetails"].get("exception", {}).get("description", res["exceptionDetails"]))
        return res["result"].get("value")

    def goto(self, url: str, wait_for: str | None = None, timeout: float = 20) -> None:
        self.send("Page.navigate", url=url)
        if wait_for:
            self.wait(wait_for, timeout)

    def wait(self, js_condition: str, timeout: float = 20) -> None:
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.eval(f"Boolean({js_condition})", await_promise=False):
                    return
            except RuntimeError:
                pass
            time.sleep(0.1)
        raise TimeoutError(f"timed out waiting for: {js_condition}; console: {self.console[-5:]}")

    def screenshot(self, path: Path, full_page: bool = False) -> Path:
        params: dict[str, Any] = {"format": "png"}
        if full_page:
            params["captureBeyondViewport"] = True
            h = self.eval("document.documentElement.scrollHeight", await_promise=False)
            w = self.eval("document.documentElement.clientWidth", await_promise=False)
            params["clip"] = {"x": 0, "y": 0, "width": w, "height": min(h, 6000), "scale": 1}
        path.write_bytes(base64.b64decode(self.send("Page.captureScreenshot", **params)["data"]))
        return path

    def close(self) -> None:
        try:
            self.ws.close()
        finally:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            shutil.rmtree(self.profile, ignore_errors=True)

    def __enter__(self) -> "Browser":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
