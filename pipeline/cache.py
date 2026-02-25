"""
cache.py – Lightweight JSON cache that simulates fast NVMe-backed storage.

Records are stored under ``<cache_dir>/<namespace>.json``.  Each entry is a
dict with a ``_ts`` (Unix epoch) field added automatically so callers can
implement TTL-based invalidation.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

_DEFAULT_DIR = Path(os.environ.get("ESPX_CACHE_DIR", Path.home() / ".cache" / "espx"))


class Cache:
    """Persistent JSON cache backed by the local filesystem."""

    def __init__(self, namespace: str, cache_dir: Path | str = _DEFAULT_DIR, ttl: int = 3600) -> None:
        self.namespace = namespace
        self.cache_dir = Path(cache_dir)
        self.ttl       = ttl        # seconds; 0 = never expire
        self._path     = self.cache_dir / f"{namespace}.json"
        self._data: dict[str, Any] = {}
        self._load()

    # ── internal ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            try:
                with self._path.open() as fh:
                    self._data = json.load(fh)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save(self) -> None:
        with self._path.open("w") as fh:
            json.dump(self._data, fh, indent=2)

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, key: str) -> Any | None:
        entry = self._data.get(key)
        if entry is None:
            return None
        if self.ttl and time.time() - entry.get("_ts", 0) > self.ttl:
            del self._data[key]
            self._save()
            return None
        return entry

    def set(self, key: str, value: dict[str, Any]) -> None:
        self._data[key] = {**value, "_ts": time.time()}
        self._save()

    def invalidate(self, key: str) -> None:
        self._data.pop(key, None)
        self._save()

    def clear(self) -> None:
        self._data = {}
        self._save()

    def keys(self) -> list[str]:
        return list(self._data.keys())
