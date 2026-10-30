import gzip
import json

import pytest
from cryptography.exceptions import InvalidTag

from builder import crypto


@pytest.fixture(scope="module")
def key() -> bytes:
    return crypto.derive_key("correct horse", b"0123456789abcdef", 1000)


def test_round_trip_and_determinism(key):
    blob = crypto.encrypt(key, b"hello")
    assert crypto.decrypt(key, blob) == b"hello"
    assert crypto.encrypt(key, b"hello") == blob  # same plaintext -> same bytes (cache-friendly)
    assert crypto.encrypt(key, b"hellp")[:12] != blob[:12]  # different plaintext -> different IV


def test_wrong_key_and_tampering_fail(key):
    blob = crypto.encrypt(key, b"secret")
    with pytest.raises(InvalidTag):
        crypto.decrypt(crypto.derive_key("wrong", b"0123456789abcdef", 1000), blob)
    with pytest.raises(InvalidTag):
        crypto.decrypt(key, blob[:-1] + bytes([blob[-1] ^ 1]))


def test_kdf_params_are_created_once_and_stable(tmp_path):
    salt, iters = crypto.kdf_params(tmp_path)
    assert len(salt) == 16 and iters == crypto.ITERATIONS
    assert crypto.kdf_params(tmp_path) == (salt, iters)


def test_encrypt_tree(tmp_path, key):
    src, dst = tmp_path / "src", tmp_path / "dst"
    (src / "chunks").mkdir(parents=True)
    (src / "manifest.json").write_text('{"a": 1}')
    (src / "chunks" / "t.json").write_text('{"b": 2}')
    (src / "meta.json").write_text("{}")
    assert crypto.encrypt_tree(src, dst, key) == 2
    assert not (dst / "meta.json.enc").exists()  # meta stays plaintext, written separately
    plain = gzip.decompress(crypto.decrypt(key, (dst / "manifest.json.enc").read_bytes()))
    assert json.loads(plain) == {"a": 1}
    assert crypto.encrypt_tree(src, dst, key) == 0  # unchanged -> nothing rewritten
    (src / "chunks" / "t.json").unlink()
    crypto.encrypt_tree(src, dst, key)
    assert not (dst / "chunks" / "t.json.enc").exists()  # stale file removed


def test_meta_check_value(key):
    meta = crypto.meta(b"0123456789abcdef", 1000, key)
    import base64
    assert crypto.decrypt(key, base64.b64decode(meta["check"])) == crypto.CHECK_PLAINTEXT
    assert crypto.meta(b"", 0, None) == {"encrypted": False}
