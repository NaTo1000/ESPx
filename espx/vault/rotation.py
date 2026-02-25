"""Key rotation algorithms for the ESPx vault.

Supports:
- Time-based rotation  : rotate after N seconds
- Usage-based rotation : rotate after N accesses
- Manual rotation      : triggered explicitly by an operator/admin

A *RotationPolicy* is attached to each slot.  The vault checks whether
rotation is due before returning a key to the caller.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RotationStrategy(str, Enum):
    NONE = "none"
    TIME = "time"
    USAGE = "usage"
    MANUAL = "manual"


@dataclass
class RotationPolicy:
    """Describes *when* and *how* a slot key should be rotated."""

    strategy: RotationStrategy = RotationStrategy.NONE
    # For TIME strategy: rotate after this many seconds (e.g. 86400 = 1 day)
    rotate_after_seconds: float = 86400.0
    # For USAGE strategy: rotate after this many reads
    rotate_after_reads: int = 1000
    # Callback name (informational, the vault dispatches the actual call)
    on_rotate: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy.value,
            "rotate_after_seconds": self.rotate_after_seconds,
            "rotate_after_reads": self.rotate_after_reads,
            "on_rotate": self.on_rotate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RotationPolicy":
        return cls(
            strategy=RotationStrategy(data.get("strategy", "none")),
            rotate_after_seconds=data.get("rotate_after_seconds", 86400.0),
            rotate_after_reads=data.get("rotate_after_reads", 1000),
            on_rotate=data.get("on_rotate"),
        )


@dataclass
class KeyVersion:
    """Represents one version of a (possibly rotated) API key."""

    version: int
    created_at: float = field(default_factory=time.time)
    read_count: int = 0
    retired_at: Optional[float] = None

    @property
    def is_active(self) -> bool:
        return self.retired_at is None

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "read_count": self.read_count,
            "retired_at": self.retired_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KeyVersion":
        obj = cls(
            version=data["version"],
            created_at=data.get("created_at", time.time()),
        )
        obj.read_count = data.get("read_count", 0)
        obj.retired_at = data.get("retired_at")
        return obj


class RotationManager:
    """Tracks key versions and decides when to rotate."""

    def __init__(self) -> None:
        # slot_name -> list[KeyVersion] (index 0 is oldest)
        self._history: dict[str, list[KeyVersion]] = {}

    def register(self, slot_name: str) -> KeyVersion:
        """Create the initial version record for *slot_name*."""
        v = KeyVersion(version=1)
        self._history[slot_name] = [v]
        return v

    def current_version(self, slot_name: str) -> KeyVersion:
        versions = self._history.get(slot_name)
        if not versions:
            return self.register(slot_name)
        active = [v for v in versions if v.is_active]
        if not active:
            raise RuntimeError(f"No active key version for slot {slot_name!r}")
        return active[-1]

    def record_read(self, slot_name: str) -> None:
        try:
            v = self.current_version(slot_name)
            v.read_count += 1
        except RuntimeError:
            pass

    def should_rotate(self, slot_name: str, policy: RotationPolicy) -> bool:
        """Return True if the current version has exceeded the policy limit."""
        if policy.strategy == RotationStrategy.NONE:
            return False
        try:
            v = self.current_version(slot_name)
        except RuntimeError:
            return False
        if policy.strategy == RotationStrategy.TIME:
            return (time.time() - v.created_at) >= policy.rotate_after_seconds
        if policy.strategy == RotationStrategy.USAGE:
            return v.read_count >= policy.rotate_after_reads
        return False  # MANUAL – never auto-triggered

    def rotate(self, slot_name: str) -> KeyVersion:
        """Retire the current version and create the next one."""
        versions = self._history.get(slot_name, [])
        for v in versions:
            if v.is_active:
                v.retired_at = time.time()
        next_version = (versions[-1].version + 1) if versions else 1
        new_v = KeyVersion(version=next_version)
        if slot_name not in self._history:
            self._history[slot_name] = []
        self._history[slot_name].append(new_v)
        return new_v

    def history(self, slot_name: str) -> list[KeyVersion]:
        return list(self._history.get(slot_name, []))

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            slot: [v.to_dict() for v in versions]
            for slot, versions in self._history.items()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RotationManager":
        rm = cls()
        for slot, versions in data.items():
            rm._history[slot] = [KeyVersion.from_dict(v) for v in versions]
        return rm


def generate_key_material() -> str:
    """Generate a cryptographically-random placeholder key (32 hex bytes)."""
    return secrets.token_hex(32)
