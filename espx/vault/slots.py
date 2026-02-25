"""Slot allocation with rate limiting for the ESPx vault.

A *slot* is a named container for one API key (plus metadata).  Slots support
per-slot rate limiting (max accesses per window) and a fixed total capacity
for the vault.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SlotPolicy:
    """Configuration for a single slot's rate-limit policy."""

    # Maximum number of read operations per *window_seconds*
    max_reads_per_window: int = 100
    window_seconds: float = 60.0
    # Slot can be marked read-only (no updates / rotation via API)
    read_only: bool = False


@dataclass
class Slot:
    """Metadata and rate-limit state for one API-key slot."""

    name: str
    service: str          # e.g. "huggingface", "esp-idf", "robotics"
    description: str = ""
    tags: list[str] = field(default_factory=list)
    policy: SlotPolicy = field(default_factory=SlotPolicy)
    created_at: float = field(default_factory=time.time)
    # Counters – not persisted to disk, reset on vault load
    _window_start: float = field(default_factory=time.time, repr=False)
    _read_count: int = field(default=0, repr=False)

    def check_rate_limit(self) -> bool:
        """Return True if this access is within the rate limit, else False."""
        now = time.time()
        if now - self._window_start >= self.policy.window_seconds:
            self._window_start = now
            self._read_count = 0
        self._read_count += 1
        return self._read_count <= self.policy.max_reads_per_window

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "service": self.service,
            "description": self.description,
            "tags": self.tags,
            "policy": {
                "max_reads_per_window": self.policy.max_reads_per_window,
                "window_seconds": self.policy.window_seconds,
                "read_only": self.policy.read_only,
            },
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Slot":
        policy_data = data.get("policy", {})
        policy = SlotPolicy(
            max_reads_per_window=policy_data.get("max_reads_per_window", 100),
            window_seconds=policy_data.get("window_seconds", 60.0),
            read_only=policy_data.get("read_only", False),
        )
        return cls(
            name=data["name"],
            service=data.get("service", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            policy=policy,
            created_at=data.get("created_at", time.time()),
        )


class SlotManager:
    """Manages slot allocation within a fixed capacity."""

    def __init__(self, capacity: int = 256) -> None:
        self._capacity = capacity
        self._slots: dict[str, Slot] = {}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def allocate(
        self,
        name: str,
        service: str,
        description: str = "",
        tags: Optional[list[str]] = None,
        policy: Optional[SlotPolicy] = None,
    ) -> Slot:
        """Allocate a new named slot.  Raises if capacity is exhausted."""
        if name in self._slots:
            raise ValueError(f"Slot {name!r} already exists")
        if len(self._slots) >= self._capacity:
            raise RuntimeError(
                f"Vault capacity exhausted ({self._capacity} slots maximum)"
            )
        slot = Slot(
            name=name,
            service=service,
            description=description or "",
            tags=tags or [],
            policy=policy or SlotPolicy(),
        )
        self._slots[name] = slot
        return slot

    def get(self, name: str) -> Slot:
        if name not in self._slots:
            raise KeyError(f"Slot {name!r} not found")
        return self._slots[name]

    def delete(self, name: str) -> None:
        if name not in self._slots:
            raise KeyError(f"Slot {name!r} not found")
        del self._slots[name]

    def list_slots(self) -> list[Slot]:
        return list(self._slots.values())

    def count(self) -> int:
        return len(self._slots)

    @property
    def capacity(self) -> int:
        return self._capacity

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "capacity": self._capacity,
            "slots": {name: slot.to_dict() for name, slot in self._slots.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SlotManager":
        sm = cls(capacity=data.get("capacity", 256))
        for slot_data in data.get("slots", {}).values():
            sm._slots[slot_data["name"]] = Slot.from_dict(slot_data)
        return sm
