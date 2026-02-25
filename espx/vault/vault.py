"""Core ESPx Vault.

The Vault ties together:
  - AES-256-GCM encryption    (crypto.py)
  - Slot allocation            (slots.py)
  - Key rotation               (rotation.py)
  - RBAC access control        (access_control.py)
  - Tamper-evident audit log   (audit.py)
  - TOTP multi-factor auth     (mfa.py)

Persistence
-----------
The vault is persisted as a single encrypted JSON file.  The file is
entirely encrypted with the vault's master key so that no metadata leaks
to disk.  The master key itself is derived from the vault password via
PBKDF2 (see crypto.py).

Supported API-key services
---------------------------
  - huggingface   (Hugging Face inference / Hub)
  - esp-idf       (ESP-IDF cloud services)
  - robotics      (generic robotics platform APIs)
  - custom        (any user-defined service)

Quick start
-----------
>>> from espx import Vault
>>> vault = Vault.create("~/.espx/vault.enc", password="s3cr3t", owner="alice")
>>> vault.store("hf-token", "huggingface", "hf_MyTokenHere", actor="alice")
>>> key = vault.retrieve("hf-token", actor="alice")
"""

from __future__ import annotations

import json
import secrets
import time
from pathlib import Path
from typing import Any, Optional

from .access_control import AccessController, Role
from .audit import AuditLogger
from .crypto import (
    decrypt_with_password,
    encrypt_with_password,
    generate_vault_key,
)
from .mfa import MFAManager
from .rotation import KeyVersion, RotationManager, RotationPolicy, RotationStrategy
from .slots import Slot, SlotManager, SlotPolicy


class AuthenticationError(Exception):
    """Raised when authentication (password or MFA) fails."""


class AuthorizationError(Exception):
    """Raised when a principal lacks the required privilege."""


class RateLimitError(Exception):
    """Raised when a slot's rate limit is exceeded."""


class Vault:
    """Secure API key vault for the ESPx build system."""

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(
        self,
        vault_path: str | Path,
        password: str,
        *,
        capacity: int = 256,
        audit_path: Optional[str | Path] = None,
        require_mfa: bool = False,
    ) -> None:
        self._path = Path(vault_path).expanduser()
        self._password = password
        self._require_mfa = require_mfa

        # Derive a deterministic audit-chain key from the vault password so
        # the audit log can be verified independently.
        import hashlib

        _audit_key = hashlib.sha256(
            b"espx-audit:" + password.encode()
        ).digest()

        _audit_path = audit_path or self._path.parent / (self._path.stem + ".audit.jsonl")
        self._audit = AuditLogger(log_path=_audit_path, chain_key=_audit_key)

        self._acl = AccessController()
        self._slots = SlotManager(capacity=capacity)
        self._rotation = RotationManager()
        self._mfa = MFAManager()
        # slot_name -> encrypted key string (AES-256-GCM token)
        self._encrypted_keys: dict[str, str] = {}
        # slot_name -> RotationPolicy
        self._rotation_policies: dict[str, RotationPolicy] = {}

    # ------------------------------------------------------------------
    # Class-level factory methods
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        vault_path: str | Path,
        password: str,
        owner: str,
        *,
        capacity: int = 256,
        audit_path: Optional[str | Path] = None,
        require_mfa: bool = False,
    ) -> "Vault":
        """Create a new vault file and register *owner* as the first admin."""
        path = Path(vault_path).expanduser()
        if path.exists():
            raise FileExistsError(f"Vault already exists at {path}")
        vault = cls(
            vault_path=path,
            password=password,
            capacity=capacity,
            audit_path=audit_path,
            require_mfa=require_mfa,
        )
        vault._acl.add_principal(owner, roles={Role.ADMIN})
        vault._audit.log("vault.create", actor=owner, detail={"capacity": capacity})
        vault.save()
        return vault

    @classmethod
    def load(
        cls,
        vault_path: str | Path,
        password: str,
        *,
        audit_path: Optional[str | Path] = None,
        require_mfa: bool = False,
    ) -> "Vault":
        """Load and decrypt an existing vault file."""
        path = Path(vault_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Vault not found at {path}")
        token = path.read_text()
        try:
            plaintext = decrypt_with_password(token, password)
        except ValueError as exc:
            raise AuthenticationError("Wrong vault password") from exc
        state = json.loads(plaintext)
        vault = cls(
            vault_path=path,
            password=password,
            capacity=state.get("capacity", 256),
            audit_path=audit_path,
            require_mfa=require_mfa,
        )
        vault._load_state(state)
        return vault

    # ------------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Encrypt and persist vault state to disk."""
        state = self._dump_state()
        plaintext = json.dumps(state)
        token = encrypt_with_password(plaintext, self._password)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(token)

    # ------------------------------------------------------------------
    # Key management API
    # ------------------------------------------------------------------

    def store(
        self,
        slot_name: str,
        service: str,
        api_key: str,
        actor: str,
        *,
        description: str = "",
        tags: Optional[list[str]] = None,
        slot_policy: Optional[SlotPolicy] = None,
        rotation_policy: Optional[RotationPolicy] = None,
        mfa_code: Optional[str] = None,
        overwrite: bool = False,
    ) -> Slot:
        """Store a new API key in *slot_name*.

        Parameters
        ----------
        slot_name:
            Unique name for the slot (e.g. ``"hf-prod"``).
        service:
            Service identifier (e.g. ``"huggingface"``).
        api_key:
            The plaintext API key to encrypt and store.
        actor:
            Principal performing the operation.
        overwrite:
            If True and the slot exists, rotate the key in-place.
        """
        self._check_auth(actor, slot_name, "slot.create", mfa_code)
        if overwrite and slot_name in {s.name for s in self._slots.list_slots()}:
            return self._rotate_key(slot_name, api_key, actor)
        slot = self._slots.allocate(
            slot_name,
            service=service,
            description=description,
            tags=tags,
            policy=slot_policy,
        )
        self._encrypted_keys[slot_name] = encrypt_with_password(api_key, self._password)
        rp = rotation_policy or RotationPolicy()
        self._rotation_policies[slot_name] = rp
        self._rotation.register(slot_name)
        self._audit.log(
            "slot.create",
            actor=actor,
            target=slot_name,
            detail={"service": service},
        )
        self.save()
        return slot

    def retrieve(
        self,
        slot_name: str,
        actor: str,
        *,
        mfa_code: Optional[str] = None,
    ) -> str:
        """Retrieve the plaintext API key from *slot_name*."""
        self._check_auth(actor, slot_name, "slot.read", mfa_code)
        slot = self._slots.get(slot_name)
        if not slot.check_rate_limit():
            self._audit.log(
                "slot.rate_limit",
                actor=actor,
                target=slot_name,
            )
            raise RateLimitError(f"Rate limit exceeded for slot {slot_name!r}")

        # Auto-rotate if policy demands it
        rp = self._rotation_policies.get(slot_name, RotationPolicy())
        if self._rotation.should_rotate(slot_name, rp):
            self._audit.log(
                "slot.auto_rotate_pending",
                actor="system",
                target=slot_name,
                detail={"strategy": rp.strategy.value},
            )

        self._rotation.record_read(slot_name)
        token = self._encrypted_keys.get(slot_name)
        if token is None:
            raise KeyError(f"No encrypted key found for slot {slot_name!r}")
        try:
            key = decrypt_with_password(token, self._password)
        except ValueError as exc:
            self._audit.log("slot.decrypt_error", actor=actor, target=slot_name)
            raise AuthenticationError("Failed to decrypt key") from exc
        self._audit.log("slot.read", actor=actor, target=slot_name)
        return key

    def rotate(
        self,
        slot_name: str,
        new_key: str,
        actor: str,
        *,
        mfa_code: Optional[str] = None,
    ) -> KeyVersion:
        """Manually rotate the key in *slot_name* to *new_key*."""
        self._check_auth(actor, slot_name, "slot.rotate", mfa_code)
        return self._rotate_key(slot_name, new_key, actor)

    def delete(
        self,
        slot_name: str,
        actor: str,
        *,
        mfa_code: Optional[str] = None,
    ) -> None:
        """Delete *slot_name* and its stored key."""
        self._check_auth(actor, slot_name, "slot.delete", mfa_code)
        self._slots.delete(slot_name)
        self._encrypted_keys.pop(slot_name, None)
        self._rotation_policies.pop(slot_name, None)
        self._audit.log("slot.delete", actor=actor, target=slot_name)
        self.save()

    def list_slots(
        self, actor: str, *, mfa_code: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """List all slots visible to *actor* (no key material returned)."""
        self._check_global_auth(actor, "slot.list", mfa_code)
        return [s.to_dict() for s in self._slots.list_slots()]

    # ------------------------------------------------------------------
    # User / MFA management
    # ------------------------------------------------------------------

    def add_user(
        self,
        name: str,
        roles: Optional[set[Role]] = None,
        actor: str = "system",
    ) -> None:
        self._check_global_auth(actor, "user.manage")
        self._acl.add_principal(name, roles=roles)
        self._audit.log("user.add", actor=actor, target=name, detail={"roles": [r.value for r in (roles or {Role.READER})]})
        self.save()

    def enrol_mfa(self, principal: str, actor: str) -> dict:
        """Enrol *principal* in TOTP MFA.  Returns enrolment details."""
        if principal != actor:
            self._check_global_auth(actor, "user.manage")
        result = self._mfa.enrol(principal)
        self._audit.log("mfa.enrol", actor=actor, target=principal)
        self.save()
        return result

    def verify_mfa(self, principal: str, code: str) -> bool:
        return self._mfa.verify(principal, code)

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_tail(self, actor: str, n: int = 20) -> list[dict[str, Any]]:
        """Return the last *n* audit records (admin only)."""
        self._check_global_auth(actor, "audit.read")
        return self._audit.tail(n)

    def audit_verify(self) -> bool:
        """Verify the integrity of the audit chain."""
        return self._audit.verify_chain()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_auth(
        self,
        actor: str,
        slot_name: str,
        privilege: str,
        mfa_code: Optional[str],
    ) -> None:
        if not self._acl.authorize(actor, slot_name, privilege):
            p = self._acl.get_principal(actor)
            if p is None or not p.has_privilege(privilege):
                self._audit.log(
                    "authz.denied",
                    actor=actor,
                    target=slot_name,
                    detail={"privilege": privilege},
                )
                raise AuthorizationError(
                    f"{actor!r} lacks privilege {privilege!r} on slot {slot_name!r}"
                )
        self._verify_mfa_if_required(actor, mfa_code)

    def _check_global_auth(
        self,
        actor: str,
        privilege: str,
        mfa_code: Optional[str] = None,
    ) -> None:
        if not self._acl.authorize_global(actor, privilege):
            self._audit.log(
                "authz.denied",
                actor=actor,
                detail={"privilege": privilege},
            )
            raise AuthorizationError(f"{actor!r} lacks privilege {privilege!r}")
        self._verify_mfa_if_required(actor, mfa_code)

    def _verify_mfa_if_required(self, actor: str, mfa_code: Optional[str]) -> None:
        if not self._require_mfa:
            return
        if not self._mfa.is_enrolled(actor):
            return  # MFA not set up for this principal – skip
        if mfa_code is None or not self._mfa.verify(actor, mfa_code):
            self._audit.log("mfa.failed", actor=actor)
            raise AuthenticationError(f"MFA verification failed for {actor!r}")

    def _rotate_key(self, slot_name: str, new_key: str, actor: str) -> KeyVersion:
        version = self._rotation.rotate(slot_name)
        self._encrypted_keys[slot_name] = encrypt_with_password(new_key, self._password)
        self._audit.log(
            "slot.rotate",
            actor=actor,
            target=slot_name,
            detail={"version": version.version},
        )
        self.save()
        return version

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def _dump_state(self) -> dict:
        return {
            "capacity": self._slots.capacity,
            "slots": self._slots.to_dict(),
            "encrypted_keys": self._encrypted_keys,
            "rotation_policies": {
                name: rp.to_dict()
                for name, rp in self._rotation_policies.items()
            },
            "rotation_history": self._rotation.to_dict(),
            "acl": self._acl.to_dict(),
            "mfa": self._mfa.to_dict(),
        }

    def _load_state(self, state: dict) -> None:
        self._slots = SlotManager.from_dict(state.get("slots", {"capacity": 256, "slots": {}}))
        self._encrypted_keys = state.get("encrypted_keys", {})
        self._rotation_policies = {
            name: RotationPolicy.from_dict(rp)
            for name, rp in state.get("rotation_policies", {}).items()
        }
        self._rotation = RotationManager.from_dict(state.get("rotation_history", {}))
        self._acl = AccessController.from_dict(state.get("acl", {}))
        self._mfa = MFAManager.from_dict(state.get("mfa", {}))
