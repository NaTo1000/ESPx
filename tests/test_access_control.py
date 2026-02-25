"""Tests for espx.vault.access_control."""
import pytest
from espx.vault.access_control import AccessController, Role


def test_add_and_get_principal():
    ac = AccessController()
    p = ac.add_principal("alice", roles={Role.ADMIN})
    assert p.name == "alice"
    assert Role.ADMIN in p.roles


def test_default_role_is_reader():
    ac = AccessController()
    p = ac.add_principal("bob")
    assert Role.READER in p.roles


def test_admin_has_all_privileges():
    ac = AccessController()
    ac.add_principal("alice", roles={Role.ADMIN})
    for priv in ("slot.create", "slot.read", "slot.delete", "user.manage", "audit.read"):
        assert ac.authorize_global("alice", priv)


def test_reader_cannot_create():
    ac = AccessController()
    ac.add_principal("carol", roles={Role.READER})
    assert not ac.authorize_global("carol", "slot.create")


def test_slot_allowlist():
    ac = AccessController()
    ac.add_principal("dave", roles={Role.OPERATOR}, allowed_slots={"hf-prod"})
    assert ac.authorize("dave", "hf-prod", "slot.read")
    assert not ac.authorize("dave", "other-slot", "slot.read")


def test_authorize_unknown_principal():
    ac = AccessController()
    assert not ac.authorize_global("unknown", "slot.read")


def test_assign_and_revoke_role():
    ac = AccessController()
    ac.add_principal("eve", roles={Role.READER})
    ac.assign_role("eve", Role.OPERATOR)
    assert ac.authorize_global("eve", "slot.create")
    ac.revoke_role("eve", Role.OPERATOR)
    assert not ac.authorize_global("eve", "slot.create")


def test_grant_and_revoke_slot():
    ac = AccessController()
    ac.add_principal("frank", roles={Role.READER}, allowed_slots=set())
    assert not ac.authorize("frank", "hf-prod", "slot.read")
    ac.grant_slot("frank", "hf-prod")
    assert ac.authorize("frank", "hf-prod", "slot.read")
    ac.revoke_slot("frank", "hf-prod")
    assert not ac.authorize("frank", "hf-prod", "slot.read")


def test_serialisation_roundtrip():
    ac = AccessController()
    ac.add_principal("grace", roles={Role.ADMIN})
    ac.add_principal("henry", roles={Role.READER}, allowed_slots={"s1"})
    data = ac.to_dict()
    ac2 = AccessController.from_dict(data)
    assert ac2.authorize_global("grace", "audit.read")
    assert ac2.authorize("henry", "s1", "slot.read")
    assert not ac2.authorize("henry", "s2", "slot.read")
