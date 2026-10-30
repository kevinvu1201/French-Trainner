// Mirrors builder/crypto.py. Each .enc file is IV (12 bytes) || AES-256-GCM ciphertext+tag;
// JSON was gzipped before encryption. The key is derived once per device with PBKDF2 and
// kept as a non-extractable CryptoKey in IndexedDB: scripts can use it but never read it.

const CHECK = "cfa-l2-unlock-v1";

export const fromB64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

export async function deriveKey(passphrase, kdf) {
  const base = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(passphrase), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "PBKDF2", hash: kdf.hash, salt: fromB64(kdf.salt), iterations: kdf.iterations },
    base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
}

export async function decrypt(key, buffer) {
  const bytes = new Uint8Array(buffer);
  const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: bytes.subarray(0, 12) }, key, bytes.subarray(12));
  return new Uint8Array(plain);
}

export async function gunzip(bytes) {
  const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

export async function checkKey(key, meta) {
  try {
    return new TextDecoder().decode(await decrypt(key, fromB64(meta.check))) === CHECK;
  } catch {
    return false;
  }
}
