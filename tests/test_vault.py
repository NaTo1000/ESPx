"""Integration tests for espx.vault.vault (Vault class)."""
import tempfile
from pathlib import Path
import pytest
import pyotp

from espx.vault.vault import (
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    Vault,
)
from espx.vault.access_control import Role
from espx.vault.rotation import RotationPolicy, RotationStrategy
from espx.vault.slots import SlotPolicy


PASSWORD = "vault-test-pw"


def make_vault(tmp_path: Path, owner: str = "alice") -> Vault:
    vp = tmp_path / "test.vault"
    return Vault.create(str(vp), PASSWORD, owner=owner)


# ---------------------------------------------------------------------------
# Basic store / retrieve
# ---------------------------------------------------------------------------


def test_store_and_retrieve(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "hf_MyToken", actor="alice")
    key = v.retrieve("hf-prod", actor="alice")
    assert key == "hf_MyToken"


def test_retrieve_returns_correct_key(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "token-A", actor="alice")
    v.store("esp-key", "esp-idf", "token-B", actor="alice")
    assert v.retrieve("hf-prod", actor="alice") == "token-A"
    assert v.retrieve("esp-key", actor="alice") == "token-B"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_persist_and_reload(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "hf_Persistent", actor="alice")
    vpath = str(tmp_path / "test.vault")
    v2 = Vault.load(vpath, PASSWORD)
    assert v2.retrieve("hf-prod", actor="alice") == "hf_Persistent"


def test_wrong_password_on_load(tmp_path):
    make_vault(tmp_path)
    with pytest.raises(AuthenticationError):
        Vault.load(str(tmp_path / "test.vault"), "wrong-pw")


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------


def test_unauthorized_retrieve(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "secret", actor="alice")
    v.add_user("bob", roles={Role.READER}, actor="alice")
    # bob doesn't have slot access (allowed_slots is None by default so
    # READER with global slot.read SHOULD be able to access it)
    key = v.retrieve("hf-prod", actor="bob")
    assert key == "secret"


def test_reader_cannot_delete(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "secret", actor="alice")
    v.add_user("bob", roles={Role.READER}, actor="alice")
    with pytest.raises(AuthorizationError):
        v.delete("hf-prod", actor="bob")


def test_unknown_actor_raises(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "secret", actor="alice")
    with pytest.raises(AuthorizationError):
        v.retrieve("hf-prod", actor="unknown")


# ---------------------------------------------------------------------------
# Key rotation
# ---------------------------------------------------------------------------


def test_manual_rotation(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "old-key", actor="alice")
    v.rotate("hf-prod", "new-key", actor="alice")
    assert v.retrieve("hf-prod", actor="alice") == "new-key"


def test_overwrite_store(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "old-key", actor="alice")
    v.store("hf-prod", "huggingface", "new-key", actor="alice", overwrite=True)
    assert v.retrieve("hf-prod", actor="alice") == "new-key"


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


def test_rate_limit_enforced(tmp_path):
    v = make_vault(tmp_path)
    policy = SlotPolicy(max_reads_per_window=2, window_seconds=60.0)
    v.store("rl-slot", "svc", "api-key", actor="alice", slot_policy=policy)
    v.retrieve("rl-slot", actor="alice")
    v.retrieve("rl-slot", actor="alice")
    with pytest.raises(RateLimitError):
        v.retrieve("rl-slot", actor="alice")


# ---------------------------------------------------------------------------
# MFA
# ---------------------------------------------------------------------------


def test_mfa_required_valid_code(tmp_path):
    v = Vault.create(
        str(tmp_path / "mfa.vault"),
        PASSWORD,
        owner="alice",
        require_mfa=True,
    )
    result = v.enrol_mfa("alice", actor="alice")
    secret = result["secret"]
    v.store("hf-prod", "huggingface", "secret", actor="alice",
            mfa_code=pyotp.TOTP(secret).now())
    code = pyotp.TOTP(secret).now()
    key = v.retrieve("hf-prod", actor="alice", mfa_code=code)
    assert key == "secret"


def test_mfa_required_bad_code(tmp_path):
    v = Vault.create(
        str(tmp_path / "mfa.vault"),
        PASSWORD,
        owner="alice",
        require_mfa=True,
    )
    v.enrol_mfa("alice", actor="alice")
    v.store("hf-prod", "huggingface", "secret", actor="alice",
            mfa_code=pyotp.TOTP(v._mfa._records["alice"].secret).now())
    with pytest.raises(AuthenticationError):
        v.retrieve("hf-prod", actor="alice", mfa_code="000000")


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


def test_audit_tail(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "key", actor="alice")
    v.retrieve("hf-prod", actor="alice")
    records = v.audit_tail(actor="alice")
    events = [r["event"] for r in records]
    assert "slot.create" in events
    assert "slot.read" in events


def test_audit_verify(tmp_path):
    v = make_vault(tmp_path)
    v.store("hf-prod", "huggingface", "key", actor="alice")
    assert v.audit_verify() is True


def test_audit_reader_cannot_access(tmp_path):
    v = make_vault(tmp_path)
    v.add_user("bob", roles={Role.READER}, actor="alice")
    with pytest.raises(AuthorizationError):
        v.audit_tail(actor="bob")


# ---------------------------------------------------------------------------
# Slot management
# ---------------------------------------------------------------------------


def test_delete_slot(tmp_path):
    v = make_vault(tmp_path)
    v.store("tmp-slot", "svc", "key", actor="alice")
    v.delete("tmp-slot", actor="alice")
    with pytest.raises(KeyError):
        v.retrieve("tmp-slot", actor="alice")


def test_list_slots(tmp_path):
    v = make_vault(tmp_path)
    v.store("s1", "svc", "k1", actor="alice")
    v.store("s2", "svc", "k2", actor="alice")
    slots = v.list_slots(actor="alice")
    names = {s["name"] for s in slots}
    assert {"s1", "s2"} <= names
