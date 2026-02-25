"""Tests for espx.vault.mfa."""
import pytest
import pyotp
from espx.vault.mfa import MFAManager


def test_enrol_returns_secret_and_uri():
    mgr = MFAManager()
    result = mgr.enrol("alice")
    assert "secret" in result
    assert result["uri"].startswith("otpauth://totp/")


def test_verify_valid_code():
    mgr = MFAManager()
    result = mgr.enrol("alice")
    secret = result["secret"]
    code = pyotp.TOTP(secret).now()
    assert mgr.verify("alice", code) is True


def test_verify_invalid_code():
    mgr = MFAManager()
    mgr.enrol("alice")
    assert mgr.verify("alice", "000000") is False


def test_verify_unenrolled():
    mgr = MFAManager()
    assert mgr.verify("nobody", "123456") is False


def test_is_enrolled():
    mgr = MFAManager()
    assert not mgr.is_enrolled("alice")
    mgr.enrol("alice")
    assert mgr.is_enrolled("alice")


def test_remove():
    mgr = MFAManager()
    mgr.enrol("alice")
    mgr.remove("alice")
    assert not mgr.is_enrolled("alice")


def test_serialisation_roundtrip():
    mgr = MFAManager()
    result = mgr.enrol("alice")
    secret = result["secret"]
    data = mgr.to_dict()
    mgr2 = MFAManager.from_dict(data)
    code = pyotp.TOTP(secret).now()
    assert mgr2.verify("alice", code) is True
