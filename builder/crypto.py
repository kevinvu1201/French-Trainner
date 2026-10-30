"""Passphrase encryption of the published data (the public site holds only ciphertext).

Format of every `<file>.enc`:  IV (12 bytes) || AES-256-GCM(ciphertext || tag)
  * JSON files are gzipped before encryption; images (already compressed) are not.
  * key = PBKDF2-HMAC-SHA256(passphrase, salt, iterations); salt and iterations
    live in config/crypto.yaml so the key (and devices' stored keys) survive rebuilds.
  * IV = HMAC-SHA256(key, plaintext)[:12]. Deterministic: the same file always
    encrypts to the same bytes, so browsers and the service worker keep their
    caches across deploys. An IV only repeats for identical plaintext, which
    reveals nothing beyond "these two files are equal".

The browser side (app/js/core/crypto.js) mirrors this with WebCrypto.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ITERATIONS = 600_000
CHECK_PLAINTEXT = b"cfa-l2-unlock-v1"
GZIP_SUFFIXES = (".json",)


def derive_key(passphrase: str, salt: bytes, iterations: int = ITERATIONS) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt(key: bytes, data: bytes) -> bytes:
    iv = hmac.new(key, data, hashlib.sha256).digest()[:12]
    return iv + AESGCM(key).encrypt(iv, data, None)


def decrypt(key: bytes, blob: bytes) -> bytes:
    return AESGCM(key).decrypt(blob[:12], blob[12:], None)


def kdf_params(config_dir: Path) -> tuple[bytes, int]:
    """Salt + iterations from config/crypto.yaml, created on first use."""
    path = config_dir / "crypto.yaml"
    if path.exists():
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return base64.b64decode(cfg["salt"]), int(cfg.get("iterations", ITERATIONS))
    salt = os.urandom(16)
    path.write_text(
        "# Key-derivation parameters for the encrypted site. Not secret; commit this file.\n"
        "# Changing either value changes the key, and every device must re-enter the passphrase.\n"
        f"salt: {base64.b64encode(salt).decode()}\niterations: {ITERATIONS}\n",
        encoding="utf-8",
    )
    return salt, ITERATIONS


def meta(salt: bytes, iterations: int, key: bytes | None) -> dict[str, Any]:
    """data/meta.json: the only plaintext data file. Tells the app how to unlock."""
    if key is None:
        return {"encrypted": False}
    return {
        "encrypted": True,
        "kdf": {"name": "PBKDF2", "hash": "SHA-256", "iterations": iterations,
                "salt": base64.b64encode(salt).decode()},
        "check": base64.b64encode(encrypt(key, CHECK_PLAINTEXT)).decode(),
    }


def encrypt_tree(src: Path, dst: Path, key: bytes) -> int:
    """Encrypt every file under src into dst as <name>.enc. Returns the number of files written.

    Unchanged files are skipped (encryption is deterministic, so equal names mean equal bytes
    for the content-hashed chunks and images); stale .enc files are removed.
    """
    written = 0
    wanted: set[Path] = set()
    for f in sorted(p for p in src.rglob("*") if p.is_file() and p.name != "meta.json"):
        rel = f.relative_to(src)
        target = dst / (str(rel) + ".enc")
        wanted.add(target)
        data = f.read_bytes()
        if f.suffix in GZIP_SUFFIXES:
            data = gzip.compress(data, compresslevel=9, mtime=0)
        blob = encrypt(key, data)
        if target.exists() and target.read_bytes() == blob:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        written += 1
    for old in dst.rglob("*.enc"):
        if old not in wanted:
            old.unlink()
    return written


def write_meta(data_dir: Path, info: dict[str, Any]) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "meta.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
