"""Tests for espx.vault.audit."""
import json
import tempfile
from pathlib import Path
import pytest
from espx.vault.audit import AuditLogger


def _make_logger(tmp_path: Path) -> AuditLogger:
    key = b"test-chain-key-32bytes-padding000"
    return AuditLogger(log_path=tmp_path / "audit.jsonl", chain_key=key)


def test_log_creates_records(tmp_path):
    al = _make_logger(tmp_path)
    r = al.log("slot.read", actor="alice", target="hf-prod")
    assert r["event"] == "slot.read"
    assert r["actor"] == "alice"
    assert r["seq"] == 0
    assert "hash" in r


def test_chain_increments(tmp_path):
    al = _make_logger(tmp_path)
    r0 = al.log("e1", actor="a")
    r1 = al.log("e2", actor="b")
    assert r1["seq"] == 1
    assert r1["prev_hash"] == r0["hash"]


def test_verify_chain_valid(tmp_path):
    al = _make_logger(tmp_path)
    al.log("e1", actor="a")
    al.log("e2", actor="b")
    assert al.verify_chain() is True


def test_verify_chain_tampered(tmp_path):
    al = _make_logger(tmp_path)
    al.log("e1", actor="a")
    log_file = tmp_path / "audit.jsonl"
    content = log_file.read_text()
    # Corrupt the actor field
    tampered = content.replace('"actor": "a"', '"actor": "hacker"')
    log_file.write_text(tampered)
    assert al.verify_chain() is False


def test_tail(tmp_path):
    al = _make_logger(tmp_path)
    for i in range(25):
        al.log(f"event-{i}", actor="user")
    tail = al.tail(10)
    assert len(tail) == 10
    assert tail[-1]["event"] == "event-24"


def test_resume_from_existing_log(tmp_path):
    al = _make_logger(tmp_path)
    al.log("e1", actor="a")
    al.log("e2", actor="b")
    # Create a new logger on the same file – it should resume
    key = b"test-chain-key-32bytes-padding000"
    al2 = AuditLogger(log_path=tmp_path / "audit.jsonl", chain_key=key)
    r = al2.log("e3", actor="c")
    assert r["seq"] == 2
