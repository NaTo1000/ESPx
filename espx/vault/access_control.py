"""Role-Based Access Control (RBAC) for the ESPx vault.

Roles
-----
- ``admin``   – full access (CRUD on all slots, manage users/roles)
- ``operator``– read/write access to owned slots, can rotate own keys
- ``reader``  – read-only access to explicitly granted slots

Each *principal* (identified by a string name) is assigned a set of roles
and an optional per-slot allowlist.

This module is intentionally kept in-memory so it can be serialised into
the encrypted vault state without external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Role(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    READER = "reader"


# Privileges implied by each role (ordered from most to least privileged).
_ROLE_PRIVILEGES: dict[Role, frozenset[str]] = {
    Role.ADMIN: frozenset(
        {
            "slot.create",
            "slot.read",
            "slot.update",
            "slot.delete",
            "slot.rotate",
            "slot.list",
            "user.manage",
            "audit.read",
            "vault.export",
        }
    ),
    Role.OPERATOR: frozenset(
        {
            "slot.create",
            "slot.read",
            "slot.update",
            "slot.rotate",
            "slot.list",
        }
    ),
    Role.READER: frozenset({"slot.read", "slot.list"}),
}


@dataclass
class Principal:
    name: str
    roles: set[Role] = field(default_factory=lambda: {Role.READER})
    # Explicit per-slot allowlist; None means "all slots permitted by role"
    allowed_slots: Optional[set[str]] = None

    def has_privilege(self, privilege: str) -> bool:
        for role in self.roles:
            if privilege in _ROLE_PRIVILEGES.get(role, frozenset()):
                return True
        return False

    def can_access_slot(self, slot_name: str, privilege: str) -> bool:
        if not self.has_privilege(privilege):
            return False
        if self.allowed_slots is None:
            return True
        return slot_name in self.allowed_slots


class AccessController:
    """Manages principals, roles, and authorisation checks."""

    def __init__(self) -> None:
        self._principals: dict[str, Principal] = {}

    # ------------------------------------------------------------------
    # Principal management
    # ------------------------------------------------------------------

    def add_principal(
        self,
        name: str,
        roles: set[Role] | None = None,
        allowed_slots: set[str] | None = None,
    ) -> Principal:
        p = Principal(
            name=name,
            roles=roles or {Role.READER},
            allowed_slots=allowed_slots,
        )
        self._principals[name] = p
        return p

    def remove_principal(self, name: str) -> None:
        self._principals.pop(name, None)

    def get_principal(self, name: str) -> Principal | None:
        return self._principals.get(name)

    def assign_role(self, name: str, role: Role) -> None:
        p = self._require(name)
        p.roles.add(role)

    def revoke_role(self, name: str, role: Role) -> None:
        p = self._require(name)
        p.roles.discard(role)

    def grant_slot(self, name: str, slot_name: str) -> None:
        p = self._require(name)
        if p.allowed_slots is None:
            p.allowed_slots = set()
        p.allowed_slots.add(slot_name)

    def revoke_slot(self, name: str, slot_name: str) -> None:
        p = self._require(name)
        if p.allowed_slots is not None:
            p.allowed_slots.discard(slot_name)

    # ------------------------------------------------------------------
    # Authorisation
    # ------------------------------------------------------------------

    def authorize(self, name: str, slot_name: str, privilege: str) -> bool:
        """Return True iff *name* may perform *privilege* on *slot_name*."""
        p = self._principals.get(name)
        if p is None:
            return False
        return p.can_access_slot(slot_name, privilege)

    def authorize_global(self, name: str, privilege: str) -> bool:
        """Return True iff *name* has *privilege* globally (no slot check)."""
        p = self._principals.get(name)
        if p is None:
            return False
        return p.has_privilege(privilege)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            name: {
                "roles": [r.value for r in p.roles],
                "allowed_slots": list(p.allowed_slots) if p.allowed_slots is not None else None,
            }
            for name, p in self._principals.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AccessController":
        ac = cls()
        for name, info in data.items():
            roles = {Role(r) for r in info.get("roles", ["reader"])}
            raw_slots = info.get("allowed_slots")
            allowed = set(raw_slots) if raw_slots is not None else None
            ac.add_principal(name, roles=roles, allowed_slots=allowed)
        return ac

    # ------------------------------------------------------------------

    def _require(self, name: str) -> Principal:
        p = self._principals.get(name)
        if p is None:
            raise KeyError(f"Unknown principal: {name!r}")
        return p
