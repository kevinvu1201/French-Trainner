"""Deploy: the safety check and publishing to a git branch (a local bare repo, never GitHub)."""

import shutil
import subprocess
from pathlib import Path

import pytest

from builder.config import Paths
from builder.deploy import DeployError, check_site, deploy_settings, publish
from builder.pipeline import build
from builder.site import build_site

REPO = Path(__file__).parent.parent

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def built(project: Path) -> Paths:
    shutil.copytree(REPO / "app", project / "app")
    paths = Paths(project)
    assert build(paths).ok
    build_site(paths, paths.dist)
    build_site(paths, paths.dist_enc, "fixture-passphrase")
    return paths


def test_check_site_blocks_plaintext(built: Paths):
    assert check_site(built.dist_enc) == []
    problems = check_site(built.dist)  # the local, unencrypted site
    assert any("not marked encrypted" in p for p in problems)
    assert any("plaintext data file" in p and "manifest.json" in p for p in problems)
    assert any("report.html" in p for p in problems)


def test_publish_to_bare_repo(built: Paths, tmp_path: Path):
    remote = tmp_path / "remote.git"
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    first = publish(built, str(remote), "gh-pages")
    assert _git(remote, "rev-parse", "gh-pages") == first
    files = _git(remote, "ls-tree", "-r", "--name-only", "gh-pages").splitlines()
    assert "index.html" in files and ".nojekyll" in files and "data/meta.json" in files
    data = [f for f in files if f.startswith("data/") and f != "data/meta.json"]
    assert data and all(f.endswith(".enc") for f in data)
    assert not any(f.startswith(("review/", "report.")) for f in files)

    # A second deploy replaces the branch: the published history is only ever the current site.
    (built.dist_enc / "extra.txt").write_text("x", encoding="utf-8")
    second = publish(built, str(remote), "gh-pages")
    assert second != first
    assert _git(remote, "rev-list", "--count", "gh-pages") == "1"
    assert "extra.txt" in _git(remote, "ls-tree", "-r", "--name-only", "gh-pages").splitlines()


def test_publish_refuses_unsafe_site_and_missing_remote(built: Paths):
    (built.dist_enc / "data" / "leak.json").write_text("{}", encoding="utf-8")
    with pytest.raises(DeployError, match="leak.json"):
        publish(built, "unused", push=False)
    (built.dist_enc / "data" / "leak.json").unlink()
    with pytest.raises(DeployError, match="No remote"):
        publish(built, "", push=True)
    assert len(publish(built, "", push=False)) == 40  # --no-push commits locally only


def test_publish_plaintext_site_leaves_out_local_pages(built: Paths, tmp_path: Path):
    # encrypt: false publishes dist/ as is, minus the local build report and review pages.
    assert check_site(built.dist, encrypted=False) == []
    remote = tmp_path / "plain.git"
    _git(tmp_path, "init", "-q", "--bare", str(remote))
    publish(built, str(remote), "gh-pages", encrypted=False)
    files = _git(remote, "ls-tree", "-r", "--name-only", "gh-pages").splitlines()
    assert "index.html" in files and "data/meta.json" in files and "data/manifest.json" in files
    assert any(f.startswith("data/chunks/") and f.endswith(".json") for f in files)
    assert not any(f.startswith(("review/", "report.")) for f in files)


def test_deploy_settings_defaults(tmp_path: Path):
    (tmp_path / "config").mkdir()
    assert deploy_settings(Paths(tmp_path)) == {"remote": "", "branch": "gh-pages", "encrypt": True}
    (tmp_path / "config" / "deploy.yaml").write_text("remote: git@example.com:me/site.git\nencrypt: false\n", encoding="utf-8")
    assert deploy_settings(Paths(tmp_path)) == {"remote": "git@example.com:me/site.git", "branch": "gh-pages", "encrypt": False}
