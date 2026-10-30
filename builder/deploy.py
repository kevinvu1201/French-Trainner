"""Publish the site to a git branch, typically GitHub Pages.

With `encrypt: true` in config/deploy.yaml the encrypted dist-enc/ is published; with
`encrypt: false`, the plaintext dist/ (for content that may be public). The site is committed
in its own working copy (.cache/deploy) on an orphan branch and force-pushed, so the published
history is just "the current site". The local review/report pages are never published.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import Paths

# Files that may legitimately be plaintext under data/ (everything else must be .enc).
PLAINTEXT_DATA = {"meta.json"}
FORBIDDEN_TOP = {"report.html", "report.json", "review"}


class DeployError(RuntimeError):
    pass


def deploy_settings(paths: Paths) -> dict:
    path = paths.config / "deploy.yaml"
    cfg = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    cfg = cfg or {}
    return {"remote": cfg.get("remote") or "", "branch": cfg.get("branch") or "gh-pages",
            "encrypt": bool(cfg.get("encrypt", True))}


def check_site(site: Path, encrypted: bool = True) -> list[str]:
    """Problems that must block publishing. Empty list = safe."""
    problems = []
    data = site / "data"
    meta = data / "meta.json"
    if not meta.exists():
        problems.append("data/meta.json is missing")
    elif encrypted and '"encrypted": true' not in meta.read_text(encoding="utf-8"):
        problems.append("data/meta.json is not marked encrypted (build with --encrypt)")
    if encrypted:
        for f in data.rglob("*") if data.exists() else []:
            if f.is_file() and f.suffix != ".enc" and f.name not in PLAINTEXT_DATA:
                problems.append(f"plaintext data file would be published: {f.relative_to(site)}")
        for name in FORBIDDEN_TOP:
            if (site / name).exists():
                problems.append(f"local-only file would be published: {name}")
    if not (site / "index.html").exists():
        problems.append("index.html missing")
    return problems


def _git(cwd: Path, *args: str) -> str:
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise DeployError(f"git {' '.join(args)} failed: {res.stderr.strip() or res.stdout.strip()}")
    return res.stdout.strip()


def publish(paths: Paths, remote: str, branch: str = "gh-pages", push: bool = True, label: str = "",
            encrypted: bool = True) -> str:
    """Commit the site (dist-enc/, or dist/ when not encrypted) to `branch` and push it to `remote`.
    Returns the commit id."""
    site = paths.dist_enc if encrypted else paths.dist
    problems = check_site(site, encrypted)
    if problems:
        raise DeployError("Refusing to publish:\n  - " + "\n  - ".join(problems))
    work = paths.cache / "deploy"
    if not (work / ".git").exists():
        work.mkdir(parents=True, exist_ok=True)
        _git(work, "init", "-q")
    _git(work, "checkout", "-q", "--orphan", f"deploy-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    for child in work.iterdir():
        if child.name == ".git":
            continue
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    # dist/ also holds the local build report and review pages; they never leave this machine.
    shutil.copytree(site, work, dirs_exist_ok=True, ignore=lambda d, names: FORBIDDEN_TOP & set(names) if Path(d) == site else set())
    (work / ".nojekyll").write_text("", encoding="utf-8")  # serve files as-is (no Jekyll processing)
    _git(work, "add", "-A")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    _git(work, "-c", "user.name=french-trainer-builder", "-c", "user.email=builder@localhost",
         "commit", "-q", "-m", f"Deploy site {label} ({stamp})".replace("  ", " "))
    _git(work, "branch", "-M", branch)
    commit = _git(work, "rev-parse", "HEAD")
    if push:
        if not remote:
            raise DeployError("No remote configured: set `remote` in config/deploy.yaml (or pass --remote).")
        _git(work, "push", "--force", remote, f"{branch}:{branch}")
    return commit
