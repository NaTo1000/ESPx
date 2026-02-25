"""Audit logging for the ESPx vault.

Every sensitive vault operation (key creation, access, rotation, deletion,
failed authentication, …) is written to an append-only, tamper-evident log.

Each log record is a JSON line.  Records are chained via HMAC-SHA256 so that
any post-hoc modification of an earlier record is detectable.

Log format (JSON, newline-delimited):
    {
      "seq":      <int>,
      "ts":       <ISO-8601 UTC>,
      "event":    <str>,
      "actor":    <str>,
      "target":   <str | null>,
      "detail":   <dict | null>,
      "prev_hash": <hex>,
      "hash":     <hex>    // HMAC-SHA256(record_without_hash, chain_key)
    }
"""

from __future__ import annotations

import hashlib
import hmac
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLogger:
    """Thread-safe, tamper-evident audit log for vault operations."""

    def __init__(self, log_path: str | Path, chain_key: bytes) -> None:
        self._path = Path(log_path)
        self._chain_key = chain_key
        self._lock = threading.Lock()
        self._seq = 0
        self._prev_hash = "0" * 64
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Resume chain state from existing log
        self._resume()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(
        self,
        event: str,
        actor: str,
        target: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append one record to the log and return it."""
        with self._lock:
            record = self._build_record(event, actor, target, detail)
            self._append(record)
            self._seq = record["seq"] + 1
            self._prev_hash = record["hash"]
            return record

    def verify_chain(self) -> bool:
        """Return True if all records form an unbroken HMAC chain."""
        if not self._path.exists():
            return True
        prev = "0" * 64
        with self._path.open("r") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                expected_hash = record.get("hash", "")
                payload = self._payload_bytes(record)
                actual_hash = self._hmac(payload)
                if not hmac.compare_digest(expected_hash, actual_hash):
                    return False
                if record["prev_hash"] != prev:
                    return False
                prev = expected_hash
        return True

    def tail(self, n: int = 20) -> list[dict[str, Any]]:
        """Return the last *n* log records."""
        records: list[dict[str, Any]] = []
        if not self._path.exists():
            return records
        with self._path.open("r") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records[-n:]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resume(self) -> None:
        if not self._path.exists():
            return
        last: dict[str, Any] | None = None
        with self._path.open("r") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    last = json.loads(line)
        if last:
            self._seq = last["seq"] + 1
            self._prev_hash = last["hash"]

    def _build_record(
        self,
        event: str,
        actor: str,
        target: str | None,
        detail: dict[str, Any] | None,
    ) -> dict[str, Any]:
        record: dict[str, Any] = {
            "seq": self._seq,
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "actor": actor,
            "target": target,
            "detail": detail,
            "prev_hash": self._prev_hash,
        }
        record["hash"] = self._hmac(self._payload_bytes(record))
        return record

    @staticmethod
    def _payload_bytes(record: dict[str, Any]) -> bytes:
        """Canonical bytes for HMAC: JSON-sorted record without 'hash' key."""
        payload = {k: v for k, v in record.items() if k != "hash"}
        return json.dumps(payload, sort_keys=True).encode()

    def _hmac(self, data: bytes) -> str:
        return hmac.new(self._chain_key, data, hashlib.sha256).hexdigest()

    def _append(self, record: dict[str, Any]) -> None:
        with self._path.open("a") as fh:
            fh.write(json.dumps(record) + "\n")
