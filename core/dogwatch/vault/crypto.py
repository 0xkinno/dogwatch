"""Encryption at rest for the vault: scrypt-derived key, NaCl secretbox, one random nonce per blob."""
from __future__ import annotations

import hashlib
import json
import os

from nacl import secret, utils

MAGIC = b"DWV1"
SALT_LEN = 16


def derive_key(passphrase: str, salt: bytes) -> bytes:
    if not passphrase:
        raise ValueError("a vault passphrase is required")
    return hashlib.scrypt(passphrase.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=secret.SecretBox.KEY_SIZE)


def new_salt() -> bytes:
    return os.urandom(SALT_LEN)


def encrypt(key: bytes, plaintext: bytes) -> bytes:
    box = secret.SecretBox(key)
    return MAGIC + box.encrypt(plaintext, utils.random(secret.SecretBox.NONCE_SIZE))


def decrypt(key: bytes, blob: bytes) -> bytes:
    if not blob.startswith(MAGIC):
        raise ValueError("not a Dogwatch vault blob")
    return secret.SecretBox(key).decrypt(blob[len(MAGIC):])


def encrypt_json(key: bytes, obj) -> bytes:
    return encrypt(key, json.dumps(obj, sort_keys=True).encode("utf-8"))


def decrypt_json(key: bytes, blob: bytes):
    return json.loads(decrypt(key, blob).decode("utf-8"))
