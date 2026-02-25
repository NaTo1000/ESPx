"""
ESPx API Vault

Secure storage for API keys, credentials, and secrets used across the
ESPx / ESPiritAi ecosystem.  Keys are stored in memory with optional
simple XOR-based obfuscation (not a substitute for a real KMS in
production, but keeps secrets out of plaintext logs).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _obfuscate(value: str, key: bytes) -> bytes:
    """XOR obfuscate a string with a repeating key."""
    encoded = value.encode()
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(encoded))


def _deobfuscate(data: bytes, key: bytes) -> str:
    """Reverse XOR obfuscation."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data)).decode()


# ---------------------------------------------------------------------------
# Secret entry
# ---------------------------------------------------------------------------

@dataclass
class SecretEntry:
    """An entry in the API vault."""

    name: str
    service: str                    # e.g. "huggingface", "aws", "openai"
    _obfuscated: bytes = field(repr=False, default=b"")
    created_at: float = field(default_factory=time.time)
    last_accessed: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        """Return a safe summary (no plaintext secret value)."""
        return {
            "name": self.name,
            "service": self.service,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "tags": self.tags,
        }


# ---------------------------------------------------------------------------
# API Vault
# ---------------------------------------------------------------------------

class APIVault:
    """
    Secure in-memory vault for API keys and credentials used by ESPiritAi
    and related ESPx components.

    Design decisions
    ----------------
    * Secrets are XOR-obfuscated in memory to prevent accidental leakage
      into string representations and logs.
    * Access attempts are audit-logged with timestamps.
    * The vault can be locked / unlocked with a master token.
    * In production, replace the obfuscation layer with an integration to
      HashiCorp Vault, AWS Secrets Manager, or equivalent KMS.
    """

    def __init__(self, master_token: Optional[str] = None) -> None:
        # Derive obfuscation key from master token (or random bytes)
        raw = (master_token or os.urandom(32).hex()).encode()
        self._obf_key: bytes = hashlib.sha256(raw).digest()
        self._store: Dict[str, SecretEntry] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._locked: bool = False
        self._master_hash: str = hashlib.sha256(raw).hexdigest()

    # -- Lock / unlock -----------------------------------------------------

    def lock(self) -> None:
        """Lock the vault (read operations will raise RuntimeError)."""
        self._locked = True
        self._audit("vault_lock", None, success=True)

    def unlock(self, master_token: str) -> bool:
        """Unlock the vault with the master token."""
        token_hash = hashlib.sha256(master_token.encode()).hexdigest()
        ok = hmac.compare_digest(token_hash, self._master_hash)
        if ok:
            self._locked = False
        self._audit("vault_unlock", None, success=ok)
        return ok

    # -- CRUD --------------------------------------------------------------

    def store(
        self,
        name: str,
        value: str,
        service: str = "generic",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store a secret in the vault."""
        if self._locked:
            raise RuntimeError("Vault is locked.")
        obf = _obfuscate(value, self._obf_key)
        entry = SecretEntry(
            name=name,
            service=service,
            _obfuscated=obf,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._store[name] = entry
        self._audit("store", name, success=True)

    def retrieve(self, name: str) -> str:
        """Retrieve a secret by name."""
        if self._locked:
            raise RuntimeError("Vault is locked.")
        entry = self._store.get(name)
        if entry is None:
            self._audit("retrieve", name, success=False)
            raise KeyError(f"No secret named '{name}' in vault.")
        entry.last_accessed = time.time()
        self._audit("retrieve", name, success=True)
        return _deobfuscate(entry._obfuscated, self._obf_key)

    def delete(self, name: str) -> bool:
        """Delete a secret.  Returns True if it existed."""
        if self._locked:
            raise RuntimeError("Vault is locked.")
        existed = name in self._store
        self._store.pop(name, None)
        self._audit("delete", name, success=existed)
        return existed

    def list_secrets(self, service: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return summaries of stored secrets (no plaintext values)."""
        entries = self._store.values()
        if service:
            entries = [e for e in entries if e.service == service]  # type: ignore[assignment]
        return [e.summary() for e in entries]

    def has(self, name: str) -> bool:
        return name in self._store

    # -- Audit log ---------------------------------------------------------

    def _audit(self, action: str, name: Optional[str], success: bool) -> None:
        self._audit_log.append({
            "action": action,
            "name": name,
            "success": success,
            "timestamp": time.time(),
        })

    def audit_log(self) -> List[Dict[str, Any]]:
        """Return the full audit log (read-only copy)."""
        return list(self._audit_log)

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        return {
            "locked": self._locked,
            "stored_secrets": len(self._store),
            "audit_entries": len(self._audit_log),
            "services": list({e.service for e in self._store.values()}),
        }
