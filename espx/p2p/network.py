"""P2P distributed key-sharing for the ESPx vault.

Overview
--------
In collaborative environments (e.g. a team working with ESP-IDF, robotics
platforms, or Hugging Face pipelines), it can be useful to share a subset of
vault slots across trusted peers without a central key server.

Protocol (simplified)
---------------------
1. Each peer has an *identity key* (Ed25519 signing key) and an
   *encryption key* (X25519 ECDH key).
2. To share a key with a peer, the sender:
   a. Derives a shared ECDH secret with the peer's public key.
   b. Encrypts the slot payload (service + ciphertext token) with
      AES-256-GCM using the shared secret.
   c. Signs the encrypted bundle with its identity key.
3. The receiving peer verifies the signature, derives the same shared
   secret, and decrypts the bundle.
4. A simple in-process message bus (``P2PBroker``) simulates peer
   discovery and message passing; in production this would be replaced
   by a real transport (e.g. libp2p, ZeroMQ, or a custom TCP protocol).

Security properties
-------------------
- Forward secrecy is *not* provided by ECDH alone; ephemeral keys should
  be used in a full implementation.
- All bundles are authenticated (Ed25519 signature + GCM tag).
- This module never writes plaintext key material to disk.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE_BYTES = 12


# ---------------------------------------------------------------------------
# Key-pair helpers
# ---------------------------------------------------------------------------


@dataclass
class PeerIdentity:
    """Holds both the signing and encryption key pairs for one peer."""

    name: str
    sign_private: Ed25519PrivateKey
    dh_private: X25519PrivateKey

    @property
    def sign_public_bytes(self) -> bytes:
        return self.sign_private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @property
    def dh_public_bytes(self) -> bytes:
        return self.dh_private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    @classmethod
    def generate(cls, name: str) -> "PeerIdentity":
        return cls(
            name=name,
            sign_private=Ed25519PrivateKey.generate(),
            dh_private=X25519PrivateKey.generate(),
        )


@dataclass
class PeerPublicInfo:
    """The public portion of a peer's identity (shared with others)."""

    name: str
    sign_public_bytes: bytes
    dh_public_bytes: bytes


# ---------------------------------------------------------------------------
# Bundle (encrypted + signed payload)
# ---------------------------------------------------------------------------


@dataclass
class KeyBundle:
    """An encrypted, signed key-sharing bundle."""

    sender: str
    nonce: bytes
    ciphertext: bytes   # AES-256-GCM (tag appended)
    signature: bytes    # Ed25519 over (sender||nonce||ciphertext)

    def to_dict(self) -> dict:
        import base64

        return {
            "sender": self.sender,
            "nonce": base64.b64encode(self.nonce).decode(),
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "signature": base64.b64encode(self.signature).decode(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KeyBundle":
        import base64

        return cls(
            sender=data["sender"],
            nonce=base64.b64decode(data["nonce"]),
            ciphertext=base64.b64decode(data["ciphertext"]),
            signature=base64.b64decode(data["signature"]),
        )


# ---------------------------------------------------------------------------
# P2P Node
# ---------------------------------------------------------------------------


class P2PNode:
    """One participant in the P2P key-sharing mesh."""

    def __init__(self, identity: PeerIdentity) -> None:
        self._id = identity
        self._peers: dict[str, PeerPublicInfo] = {}  # name -> public info
        self._received: list[dict[str, Any]] = []
        self._handlers: list[Callable[[str, dict[str, Any]], None]] = []

    @property
    def name(self) -> str:
        return self._id.name

    @property
    def public_info(self) -> PeerPublicInfo:
        return PeerPublicInfo(
            name=self._id.name,
            sign_public_bytes=self._id.sign_public_bytes,
            dh_public_bytes=self._id.dh_public_bytes,
        )

    def register_peer(self, peer_info: PeerPublicInfo) -> None:
        self._peers[peer_info.name] = peer_info

    def on_message(self, handler: Callable[[str, dict[str, Any]], None]) -> None:
        """Register a callback invoked when a verified key bundle is received."""
        self._handlers.append(handler)

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    def send_key(self, recipient: str, slot_name: str, encrypted_token: str) -> KeyBundle:
        """Encrypt and sign a key bundle for *recipient*."""
        peer = self._peers.get(recipient)
        if peer is None:
            raise ValueError(f"Unknown peer {recipient!r}")
        shared = self._derive_shared(peer.dh_public_bytes)
        payload = json.dumps(
            {"slot": slot_name, "token": encrypted_token}
        ).encode()
        nonce = os.urandom(_NONCE_BYTES)
        aesgcm = AESGCM(shared)
        ciphertext = aesgcm.encrypt(nonce, payload, None)
        signed_data = self._id.name.encode() + nonce + ciphertext
        signature = self._id.sign_private.sign(signed_data)
        return KeyBundle(
            sender=self._id.name,
            nonce=nonce,
            ciphertext=ciphertext,
            signature=signature,
        )

    # ------------------------------------------------------------------
    # Receiving
    # ------------------------------------------------------------------

    def receive_bundle(self, bundle: KeyBundle) -> dict[str, Any]:
        """Verify and decrypt a key bundle from a peer."""
        peer = self._peers.get(bundle.sender)
        if peer is None:
            raise ValueError(f"Unknown sender {bundle.sender!r}")
        # Verify signature
        signed_data = bundle.sender.encode() + bundle.nonce + bundle.ciphertext
        sign_pub = Ed25519PublicKey.from_public_bytes(peer.sign_public_bytes)
        try:
            sign_pub.verify(bundle.signature, signed_data)
        except Exception as exc:
            raise ValueError("Bundle signature verification failed") from exc
        # Decrypt
        shared = self._derive_shared(peer.dh_public_bytes)
        aesgcm = AESGCM(shared)
        try:
            plaintext = aesgcm.decrypt(bundle.nonce, bundle.ciphertext, None)
        except Exception as exc:
            raise ValueError("Bundle decryption failed") from exc
        payload = json.loads(plaintext)
        for handler in self._handlers:
            handler(bundle.sender, payload)
        self._received.append({"from": bundle.sender, "payload": payload})
        return payload

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _derive_shared(self, peer_dh_public_bytes: bytes) -> bytes:
        """ECDH key exchange → HKDF-derived 32-byte AES key."""
        peer_dh_pub = X25519PublicKey.from_public_bytes(peer_dh_public_bytes)
        raw_shared = self._id.dh_private.exchange(peer_dh_pub)
        # Simple HKDF-like derivation with SHA-256
        return hashlib.sha256(b"espx-p2p:" + raw_shared).digest()


# ---------------------------------------------------------------------------
# P2P Broker (in-process peer discovery / routing)
# ---------------------------------------------------------------------------


class P2PBroker:
    """Simple in-process message broker that connects P2PNode instances.

    In a real deployment this would be replaced by a network transport
    (TCP/UDP sockets, libp2p, ZeroMQ, etc.).
    """

    def __init__(self) -> None:
        self._nodes: dict[str, P2PNode] = {}
        self._lock = threading.Lock()

    def register(self, node: P2PNode) -> None:
        with self._lock:
            self._nodes[node.name] = node
            # Exchange public info with every existing node
            for existing_name, existing_node in self._nodes.items():
                if existing_name != node.name:
                    existing_node.register_peer(node.public_info)
                    node.register_peer(existing_node.public_info)

    def route(self, bundle: KeyBundle, recipient: str) -> dict[str, Any]:
        """Deliver *bundle* to *recipient* and return the decrypted payload."""
        with self._lock:
            node = self._nodes.get(recipient)
        if node is None:
            raise ValueError(f"Recipient {recipient!r} not registered")
        return node.receive_bundle(bundle)


# ---------------------------------------------------------------------------
# High-level P2PNetwork facade
# ---------------------------------------------------------------------------


class P2PNetwork:
    """Facade that integrates P2P key sharing with the ESPx vault.

    Usage::

        net = P2PNetwork()
        net.join("alice")
        net.join("bob")

        # alice sends a vault-encrypted token to bob
        bundle = net.share_key("alice", "bob", "hf-prod", encrypted_token)
        payload = net.receive_key("bob", bundle)
        # payload == {"slot": "hf-prod", "token": encrypted_token}
    """

    def __init__(self) -> None:
        self._broker = P2PBroker()
        self._nodes: dict[str, P2PNode] = {}

    def join(self, peer_name: str) -> P2PNode:
        """Create and register a new P2P node for *peer_name*."""
        identity = PeerIdentity.generate(peer_name)
        node = P2PNode(identity)
        self._broker.register(node)
        self._nodes[peer_name] = node
        return node

    def share_key(
        self,
        sender: str,
        recipient: str,
        slot_name: str,
        encrypted_token: str,
    ) -> KeyBundle:
        """Have *sender* encrypt and sign a key bundle for *recipient*."""
        node = self._nodes.get(sender)
        if node is None:
            raise ValueError(f"Sender {sender!r} not joined")
        return node.send_key(recipient, slot_name, encrypted_token)

    def receive_key(self, recipient: str, bundle: KeyBundle) -> dict[str, Any]:
        """Deliver and decrypt a bundle to *recipient*."""
        return self._broker.route(bundle, recipient)

    def peers(self) -> list[str]:
        return list(self._nodes.keys())
