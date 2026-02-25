"""Tests for espx.p2p.network (P2P key sharing)."""
import pytest
from espx.p2p.network import P2PNetwork


def test_join_and_peers():
    net = P2PNetwork()
    net.join("alice")
    net.join("bob")
    assert set(net.peers()) == {"alice", "bob"}


def test_share_and_receive_key():
    net = P2PNetwork()
    net.join("alice")
    net.join("bob")
    encrypted_token = "SALT.NONCE.CIPHERTEXT"
    bundle = net.share_key("alice", "bob", "hf-prod", encrypted_token)
    payload = net.receive_key("bob", bundle)
    assert payload["slot"] == "hf-prod"
    assert payload["token"] == encrypted_token


def test_tampered_signature_rejected():
    net = P2PNetwork()
    net.join("alice")
    net.join("bob")
    bundle = net.share_key("alice", "bob", "hf-prod", "TOKEN")
    # Corrupt the signature
    bad_sig = bytes([b ^ 0xFF for b in bundle.signature])
    bundle.signature = bad_sig
    with pytest.raises(ValueError, match="signature"):
        net.receive_key("bob", bundle)


def test_unknown_sender_rejected():
    net = P2PNetwork()
    net.join("alice")
    net.join("bob")
    bundle = net.share_key("alice", "bob", "slot", "TOKEN")
    bundle.sender = "mallory"
    with pytest.raises(ValueError):
        net.receive_key("bob", bundle)


def test_bundle_serialisation():
    net = P2PNetwork()
    net.join("alice")
    net.join("bob")
    bundle = net.share_key("alice", "bob", "slot", "TOKEN")
    restored = type(bundle).from_dict(bundle.to_dict())
    payload = net.receive_key("bob", restored)
    assert payload["token"] == "TOKEN"
