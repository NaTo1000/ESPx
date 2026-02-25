"""
ESPx P2P Network

Peer-to-peer key sharing and coordinated network communication between
ESPx / ESPiritAi nodes.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Key exchange
# ---------------------------------------------------------------------------

@dataclass
class SharedKey:
    """A symmetric key shared between two peers."""

    key_id: str
    peer_a: str
    peer_b: str
    key_material: bytes
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


# ---------------------------------------------------------------------------
# Network node
# ---------------------------------------------------------------------------

@dataclass
class NetworkNode:
    """A node participating in the P2P network."""

    node_id: str
    address: str
    public_info: Dict[str, Any] = field(default_factory=dict)
    connected: bool = False
    last_heartbeat: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# P2P Network
# ---------------------------------------------------------------------------

class P2PNetwork:
    """
    Peer-to-peer network manager for the ESPx ecosystem.

    Handles node registration, secure key sharing via HMAC-derived
    session keys, message routing, and basic topology management.
    """

    def __init__(self, local_node_id: Optional[str] = None) -> None:
        self.local_id: str = local_node_id or f"node_{uuid.uuid4().hex[:8]}"
        self._nodes: Dict[str, NetworkNode] = {}
        self._shared_keys: Dict[str, SharedKey] = {}  # key_id -> SharedKey
        self._message_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._message_log: List[Dict[str, Any]] = []

    # -- Node management ---------------------------------------------------

    def register_node(self, node: NetworkNode) -> None:
        """Register a remote node."""
        self._nodes[node.node_id] = node

    def deregister_node(self, node_id: str) -> bool:
        return self._nodes.pop(node_id, None) is not None

    def get_node(self, node_id: str) -> Optional[NetworkNode]:
        return self._nodes.get(node_id)

    def online_nodes(self) -> List[NetworkNode]:
        return [n for n in self._nodes.values() if n.connected]

    def heartbeat(self, node_id: str) -> bool:
        """Update a node's last-seen timestamp."""
        node = self._nodes.get(node_id)
        if node is None:
            return False
        node.last_heartbeat = time.time()
        node.connected = True
        return True

    # -- Key sharing -------------------------------------------------------

    def derive_shared_key(
        self,
        peer_id: str,
        shared_secret: str,
        ttl_s: Optional[float] = None,
    ) -> SharedKey:
        """
        Derive a session key between this node and *peer_id* using HMAC-SHA256
        over a shared secret.
        """
        material = hmac.new(
            shared_secret.encode(),
            msg=f"{self.local_id}:{peer_id}".encode(),
            digestmod=hashlib.sha256,
        ).digest()
        key_id = hashlib.sha256(material).hexdigest()[:16]
        expires = time.time() + ttl_s if ttl_s else None
        sk = SharedKey(
            key_id=key_id,
            peer_a=self.local_id,
            peer_b=peer_id,
            key_material=material,
            expires_at=expires,
        )
        self._shared_keys[key_id] = sk
        return sk

    def get_shared_key(self, key_id: str) -> Optional[SharedKey]:
        sk = self._shared_keys.get(key_id)
        if sk and sk.expired:
            del self._shared_keys[key_id]
            return None
        return sk

    def revoke_key(self, key_id: str) -> bool:
        return self._shared_keys.pop(key_id, None) is not None

    def active_keys(self) -> List[SharedKey]:
        return [sk for sk in self._shared_keys.values() if not sk.expired]

    # -- Messaging ---------------------------------------------------------

    def register_handler(
        self, message_type: str, handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        self._message_handlers[message_type] = handler

    def send(
        self,
        recipient_id: str,
        message_type: str,
        payload: Dict[str, Any],
        key_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message to a peer.  Optionally sign the payload with a
        shared key (HMAC tag added to envelope).
        """
        envelope: Dict[str, Any] = {
            "message_id": uuid.uuid4().hex[:12],
            "sender": self.local_id,
            "recipient": recipient_id,
            "type": message_type,
            "payload": payload,
            "timestamp": time.time(),
        }
        if key_id:
            sk = self.get_shared_key(key_id)
            if sk:
                tag = hmac.new(
                    sk.key_material,
                    msg=str(payload).encode(),
                    digestmod=hashlib.sha256,
                ).hexdigest()
                envelope["hmac_tag"] = tag

        # Simulate delivery within process
        delivered = recipient_id in self._nodes
        envelope["delivered"] = delivered
        self._message_log.append(envelope)
        return envelope

    def receive(self, envelope: Dict[str, Any]) -> Any:
        """Process an incoming message envelope."""
        msg_type = envelope.get("type", "unknown")
        handler = self._message_handlers.get(msg_type)
        if handler:
            return handler(envelope.get("payload", {}))
        return None

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        return {
            "local_id": self.local_id,
            "registered_nodes": len(self._nodes),
            "online_nodes": len(self.online_nodes()),
            "active_keys": len(self.active_keys()),
            "messages_sent": len(self._message_log),
        }
