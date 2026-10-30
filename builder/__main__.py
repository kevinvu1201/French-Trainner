"""CLI: python -m builder <command>"""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from .config import ROOT, Paths


def _passphrase() -> str:
    """TRAINER_PASSPHRASE from the environment, else an interactive prompt."""
    env = os.environ.get("TRAINER_PASSPHRASE")
    if env:
        return env
    first = getpass.getpass("Site passphrase: ")
    if len(first) < 8:
        sys.exit("Use at least 8 characters.")
    if getpass.getpass("Repeat passphrase: ") != first:
        sys.exit("Passphrases don't match.")
    return first


def _build(paths: Paths, force: bool, encrypt: bool) -> int:
    from .incremental import book_files
    from .pipeline import build
    from .site import build_site

    if not paths.content.exists() or not book_files(paths):
        print(f"No source books (*.pdf or *.md) in {paths.content}", file=sys.stderr)
        return 2
    res = build(paths, force=force)
    s, inc = res.report["summary"], res.report["incremental"]
    print(f"Built data in {res.seconds:.1f}s: {s['readings']} readings, {s['modules']} modules, {s['los']} LOS, "
          f"{s['schweser_usable']}/{s['schweser_questions']} usable quiz questions, "
          f"{s['figures']} figures ({s['figures_with_image']} with original images)")
    print(f"  parsed: {', '.join(inc['reparsed']) or '-'} | cached: {', '.join(inc['cached']) or '-'}")
    print(f"  chunks written: {', '.join(inc['written']) or '-'} | unchanged: {', '.join(inc['unchanged']) or '-'}")
    print(f"  {s['errors']} errors, {s['warnings']} warnings -> {paths.dist / 'report.html'}")
    for topic in res.report.get("reviews", []):
        print(f"  review of generated content: {paths.dist / 'review' / (topic + '.html')}")
    if not res.report["weights_verified"]:
        print("  NOTE: exam weights are unverified (config/exam_weights.yaml)")

    site = build_site(paths, paths.dist)
    print(f"Site: {site.out} ({site.shell_files} shell files; startup JS {site.js_gzip / 1024:.1f} KB gz, "
          f"KaTeX {site.katex_gzip / 1024:.0f} KB gz loaded on demand)")
    if encrypt:
        enc = build_site(paths, paths.dist_enc, _passphrase())
        print(f"Encrypted site: {enc.out} ({enc.encrypted_written} data files re-encrypted)")
    return 0 if res.ok else 1


def _cmd_build(args: argparse.Namespace) -> int:
    return _build(Paths(args.root), args.force, args.encrypt)


def _cmd_serve(args: argparse.Namespace) -> int:
    from .serve import serve

    paths = Paths(args.root)
    if not args.no_build:
        code = _build(paths, False, args.encrypted)
        if code == 2:
            return code
    serve(paths.dist_enc if args.encrypted else paths.dist, args.host, args.port)
    return 0


def _cmd_deploy(args: argparse.Namespace) -> int:
    from .deploy import DeployError, deploy_settings, publish

    paths = Paths(args.root)
    settings = deploy_settings(paths)
    remote = args.remote or settings["remote"]
    if not remote and not args.no_push:
        print("No remote set. Put your GitHub repository URL in config/deploy.yaml (or pass --remote).", file=sys.stderr)
        return 2
    code = _build(paths, False, encrypt=settings["encrypt"])
    if code == 2:
        return code
    if code != 0:
        print("Build has errors; fix them (see dist/report.html) before deploying.", file=sys.stderr)
        return code
    try:
        commit = publish(paths, remote, settings["branch"], push=not args.no_push, encrypted=settings["encrypt"])
    except DeployError as e:
        print(e, file=sys.stderr)
        return 1
    if args.no_push:
        print(f"Committed {commit[:10]} in .cache/deploy (not pushed: --no-push).")
    else:
        print(f"Pushed {commit[:10]} to {remote} ({settings['branch']}).")
        print("If this is the first deploy: repository Settings → Pages → Deploy from a branch → "
              f"{settings['branch']} / (root). The site updates a minute or two after each push.")
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    from .audit import audit
    from .browser import find_browser

    paths = Paths(args.root)
    site = paths.dist_enc if args.encrypted else paths.dist
    if not (site / "index.html").exists():
        print(f"{site} isn't built yet; run `python -m builder build{' --encrypt' if args.encrypted else ''}` first.", file=sys.stderr)
        return 2
    if not find_browser():
        print("The audit needs Chrome or Edge installed.", file=sys.stderr)
        return 2
    res = audit(site)
    print(f"Audit of {site}:")
    for c in res.checks:
        print(f"  {'PASS' if c.ok else 'FAIL'}  {c.name}: {c.detail}")
    if res.lighthouse:
        print("  Lighthouse: " + ", ".join(f"{k} {v}" for k, v in res.lighthouse.items()))
    else:
        print("  Lighthouse: not run (needs Node.js for `npx lighthouse`; install Node LTS from nodejs.org to add it).")
    return 0 if res.ok else 1


def _cmd_vocab(args: argparse.Namespace) -> int:
    from .incremental import build_vocab

    path = build_vocab(Paths(args.root))
    print(f"Vocabulary rebuilt: {path}. The next build re-parses every Markdown book.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m builder", description="French B2 trainer builder")
    parser.add_argument("--root", default=ROOT, type=Path, help="project root")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build", help="parse content, compile data, validate, assemble dist/")
    p.add_argument("--force", action="store_true", help="ignore the parse cache")
    p.add_argument("--encrypt", action="store_true",
                   help="also build dist-enc/ (encrypted data; passphrase from TRAINER_PASSPHRASE or a prompt)")
    p.set_defaults(func=_cmd_build)

    p = sub.add_parser("serve", help="build, then serve the app locally")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1", help="0.0.0.0 to reach it from other devices on your network")
    p.add_argument("--encrypted", action="store_true", help="serve dist-enc/ to test the passphrase flow")
    p.add_argument("--no-build", action="store_true", help="serve what is already built")
    p.set_defaults(func=_cmd_serve)

    p = sub.add_parser("deploy", help="build the site (encrypted unless config/deploy.yaml says otherwise) and push it to GitHub Pages")
    p.add_argument("--remote", help="git remote URL (overrides config/deploy.yaml)")
    p.add_argument("--no-push", action="store_true", help="commit locally in .cache/deploy without pushing")
    p.set_defaults(func=_cmd_deploy)

    p = sub.add_parser("audit", help="performance / offline / installability / accessibility checks (Lighthouse if Node is installed)")
    p.add_argument("--encrypted", action="store_true", help="audit dist-enc/ instead of dist/")
    p.set_defaults(func=_cmd_audit)

    p = sub.add_parser("vocab", help="rebuild the ligature-repair vocabulary (Markdown sources only)")
    p.set_defaults(func=_cmd_vocab)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
