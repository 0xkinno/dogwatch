"""Encrypted vault on the seafarer's machine. Default location ~/.dogwatch/vault/, never in the repository."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from . import crypto
from .placeholders import Registry


def default_root() -> Path:
    return Path(os.environ.get("DOGWATCH_VAULT_DIR", Path.home() / ".dogwatch" / "vault"))


class Vault:
    """documents.json, ledger.json, identifiers.json and original images, all encrypted at rest."""

    def __init__(self, root: Path, key: bytes):
        self.root = Path(root)
        self._key = key
        self.registry = Registry(self._get("identifiers", None))

    @classmethod
    def create(cls, root: Path, passphrase: str) -> "Vault":
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        salt_path = root / "vault.salt"
        if salt_path.exists():
            raise FileExistsError("vault already exists")
        salt = crypto.new_salt()
        salt_path.write_bytes(salt)
        key = crypto.derive_key(passphrase, salt)
        v = cls(root, key)
        v._put("identifiers", v.registry.export())
        return v

    @classmethod
    def open(cls, root: Path, passphrase: str) -> "Vault":
        root = Path(root)
        salt = (root / "vault.salt").read_bytes()
        key = crypto.derive_key(passphrase, salt)
        v = cls(root, key)
        v._get("identifiers", None)  # raises on a wrong passphrase
        return v

    def _path(self, name: str) -> Path:
        return self.root / f"{name}.enc"

    def _put(self, name: str, obj) -> None:
        tmp = self._path(name).with_suffix(".tmp")
        tmp.write_bytes(crypto.encrypt_json(self._key, obj))
        tmp.replace(self._path(name))

    def _get(self, name: str, default):
        p = self._path(name)
        if not p.exists():
            return default
        return crypto.decrypt_json(self._key, p.read_bytes())

    def save_registry(self) -> None:
        self._put("identifiers", self.registry.export())

    def documents(self) -> list[dict]:
        return self._get("documents", [])

    def put_documents(self, docs: list[dict]) -> None:
        self._put("documents", docs)

    def ledger(self) -> list[dict]:
        return self._get("ledger", [])

    def add_ledger_entry(self, entry: dict) -> list[dict]:
        led = self.ledger()
        led.append(entry)
        self._put("ledger", led)
        return led

    def state(self, name: str, default=None):
        return self._get("state_" + name, default)

    def put_state(self, name: str, obj) -> None:
        self._put("state_" + name, obj)

    def add_image(self, data: bytes, suffix: str = ".img") -> str:
        """Store an original image encrypted. Returns its content id."""
        cid = hashlib.sha256(data).hexdigest()[:16]
        (self.root / "images").mkdir(exist_ok=True)
        (self.root / "images" / f"{cid}{suffix}.enc").write_bytes(crypto.encrypt(self._key, data))
        return cid

    def read_image(self, cid: str, suffix: str = ".img") -> bytes:
        return crypto.decrypt(self._key, (self.root / "images" / f"{cid}{suffix}.enc").read_bytes())
