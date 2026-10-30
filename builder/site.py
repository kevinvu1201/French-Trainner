"""Assemble the static PWA: app shell + data (+ encryption) + icons + service worker.

dist/      local site, plaintext data (python -m builder serve)
dist-enc/  publishable site, every data file encrypted except data/meta.json
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from . import crypto
from .config import Paths

APP_NAME = "Français B2 – Grammaire"
SHORT_NAME = "Français B2"
THEME_LIGHT = "#fbfaf7"
ACCENT = "#2b4c9b"
SHELL_EXCLUDE = {"tests"}
TEMPLATES = {"sw.js", "index.html"}  # files with build-time placeholders
PRELOAD_MARKER = "<!-- modulepreload: the builder lists every startup module here so they download in parallel -->"


@dataclass
class SiteResult:
    out: Path
    shell_files: int
    js_gzip: int  # bytes, JS loaded at startup (lazy views and KaTeX excluded)
    katex_gzip: int
    encrypted: bool
    encrypted_written: int = 0


_STATIC_IMPORT = re.compile(r'^\s*(?:import|export)\s[^;()]*?from\s+"([^"]+)"', re.M)


def startup_modules(app: Path, entry: str = "js/main.js") -> set[str]:
    """Modules reachable from `entry` through static imports (dynamic import() calls excluded)."""
    seen: set[str] = set()
    todo = [entry]
    while todo:
        rel = todo.pop()
        if rel in seen:
            continue
        seen.add(rel)
        text = (app / rel).read_text(encoding="utf-8")
        base = Path(rel).parent
        for spec in _STATIC_IMPORT.findall(text):
            if spec.startswith("."):
                todo.append((base / spec).as_posix().replace("/./", "/"))
    return {str(Path(m).as_posix()) for m in (_normalise(x) for x in seen)}


def _normalise(rel: str) -> str:
    parts: list[str] = []
    for part in rel.split("/"):
        if part == "..":
            parts.pop()
        elif part not in (".", ""):
            parts.append(part)
    return "/".join(parts)


def _shell_files(app: Path) -> list[Path]:
    return sorted(p for p in app.rglob("*") if p.is_file()
                  and not (set(p.relative_to(app).parts[:1]) & SHELL_EXCLUDE))


def _icon(size: int, maskable: bool = False) -> Image.Image:
    scale = 4  # draw large, downsample for smooth edges
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = 0 if maskable else s // 5
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=radius, fill=ACCENT)
    text = "B2"
    font_px = int(s * (0.36 if maskable else 0.44))
    try:
        font = ImageFont.truetype("arialbd.ttf", font_px)
    except OSError:
        font = ImageFont.load_default(size=font_px)
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((s - w) / 2 - box[0], (s - h) / 2 - box[1]), text, font=font, fill="#ffffff")
    return img.resize((size, size), Image.LANCZOS)


def _write_icons(out: Path) -> None:
    icons = out / "icons"
    icons.mkdir(parents=True, exist_ok=True)
    for name, size, maskable in [("icon-192.png", 192, False), ("icon-512.png", 512, False),
                                 ("maskable-512.png", 512, True), ("apple-touch-icon.png", 180, True)]:
        target = icons / name
        if not target.exists():
            _icon(size, maskable).save(target, optimize=True)


def _webmanifest() -> str:
    return json.dumps({
        "name": APP_NAME, "short_name": SHORT_NAME, "start_url": "./", "scope": "./",
        "display": "standalone", "background_color": THEME_LIGHT, "theme_color": ACCENT,
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }, indent=1)


def build_site(paths: Paths, out: Path, passphrase: str | None = None) -> SiteResult:
    """Copy the shell into `out` and write its data folder (plain or encrypted)."""
    app = paths.app
    out.mkdir(parents=True, exist_ok=True)
    shell: list[str] = []
    for f in _shell_files(app):
        rel = f.relative_to(app).as_posix()
        if rel in TEMPLATES:
            continue
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != f.read_bytes():
            shutil.copyfile(f, target)
        shell.append(rel)
    # index.html: preload the modules main.js imports statically (transitively), so they download in
    # parallel instead of as an import waterfall. Lazily imported views and KaTeX are left out.
    modules = sorted(startup_modules(app))
    preload = "\n".join(f'<link rel="modulepreload" href="{m}">' for m in modules)
    # The first data requests (meta.json, then the manifest) would otherwise start only after all
    # the JS has run: two serial round-trips on the critical path. Start them with the HTML.
    manifest_name = "manifest.json.enc" if passphrase is not None else "manifest.json"
    preload += ('\n<link rel="preload" href="data/meta.json" as="fetch" crossorigin>'
                f'\n<link rel="preload" href="data/{manifest_name}" as="fetch" crossorigin>')
    index = (app / "index.html").read_text(encoding="utf-8")
    assert PRELOAD_MARKER in index, "index.html lost its modulepreload marker"
    (out / "index.html").write_text(index.replace(PRELOAD_MARKER, preload), encoding="utf-8")
    shell.append("index.html")

    _write_icons(out)
    (out / "manifest.webmanifest").write_text(_webmanifest(), encoding="utf-8")
    shell += [f"icons/{p.name}" for p in sorted((out / "icons").iterdir())] + ["manifest.webmanifest"]

    # Data: plaintext lives in dist/data (written by compile); dist-enc gets ciphertext.
    written = 0
    if passphrase is None:
        crypto.write_meta(out / "data", crypto.meta(b"", 0, None))
    else:
        salt, iterations = crypto.kdf_params(paths.config)
        key = crypto.derive_key(passphrase, salt, iterations)
        written = crypto.encrypt_tree(paths.data, out / "data", key)
        crypto.write_meta(out / "data", crypto.meta(salt, iterations, key))

    # Service worker: precache the shell; version changes whenever any shell file does.
    digest = hashlib.sha1()
    for rel in sorted(shell):
        digest.update(rel.encode() + (out / rel).read_bytes())
    template = (app / "sw.js").read_text(encoding="utf-8")
    sw = (template.replace("__VERSION__", digest.hexdigest()[:12])
                  .replace("__PRECACHE__", json.dumps(["./"] + sorted(shell))))
    (out / "sw.js").write_text(sw, encoding="utf-8")

    def gz(files: list[str]) -> int:
        return sum(len(gzip.compress((out / f).read_bytes(), 9)) for f in files)

    js = modules  # startup JS only; lazily loaded views and KaTeX arrive later
    katex = [f for f in shell if "katex" in f and f.endswith((".js", ".css"))]
    return SiteResult(out, len(shell), gz(js), gz(katex), passphrase is not None, written)
