"""AES-256-GCM encryption helpers for the ESPx vault.

Keys are derived from a master password (or a randomly generated vault key)
using PBKDF2-HMAC-SHA256.  Every ciphertext carries its own salt, IV/nonce,
and GCM authentication tag so the representation is self-contained.

Wire format (all base64url-encoded JSON-safe string):
    <base64(salt)>.<base64(nonce)>.<base64(tag+ciphertext)>
"""

from __future__ import annotations

import base64
import os
import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_SALT_BYTES = 32
_NONCE_BYTES = 12  # 96-bit nonce required by GCM
_KEY_BYTES = 32    # AES-256
_PBKDF2_ITERATIONS = 390_000  # OWASP 2023 recommendation


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode()


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s.encode())


def derive_key(password: str | bytes, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from *password* and *salt*."""
    if isinstance(password, str):
        password = password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_BYTES,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
    )
    return kdf.derive(password)


def generate_vault_key() -> bytes:
    """Generate a cryptographically random 256-bit vault key."""
    return secrets.token_bytes(_KEY_BYTES)


def encrypt(plaintext: str | bytes, key: bytes) -> str:
    """Encrypt *plaintext* under *key* (32 bytes) using AES-256-GCM.

    Returns a compact string ``salt.nonce.ciphertext`` where every part is
    base64url-encoded.  A fresh salt and nonce are generated for every call.
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode()
    salt = os.urandom(_SALT_BYTES)
    nonce = os.urandom(_NONCE_BYTES)
    derived = derive_key(key, salt)
    aesgcm = AESGCM(derived)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)  # tag appended
    return f"{_b64(salt)}.{_b64(nonce)}.{_b64(ciphertext)}"


def decrypt(token: str, key: bytes) -> str:
    """Decrypt a token produced by :func:`encrypt`.

    Raises :class:`ValueError` on any integrity / decryption failure.
    """
    try:
        salt_b64, nonce_b64, ct_b64 = token.split(".")
        salt = _unb64(salt_b64)
        nonce = _unb64(nonce_b64)
        ciphertext = _unb64(ct_b64)
    except Exception as exc:
        raise ValueError("Malformed ciphertext token") from exc
    derived = derive_key(key, salt)
    aesgcm = AESGCM(derived)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed – wrong key or tampered data") from exc
    return plaintext.decode()


def encrypt_with_password(plaintext: str | bytes, password: str) -> str:
    """Convenience wrapper: derive a key from *password*, then encrypt."""
    if isinstance(plaintext, str):
        plaintext = plaintext.encode()
    salt = os.urandom(_SALT_BYTES)
    key = derive_key(password, salt)
    nonce = os.urandom(_NONCE_BYTES)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return f"{_b64(salt)}.{_b64(nonce)}.{_b64(ciphertext)}"


def decrypt_with_password(token: str, password: str) -> str:
    """Convenience wrapper: derive a key from *password*, then decrypt."""
    try:
        salt_b64, nonce_b64, ct_b64 = token.split(".")
        salt = _unb64(salt_b64)
        nonce = _unb64(nonce_b64)
        ciphertext = _unb64(ct_b64)
    except Exception as exc:
        raise ValueError("Malformed ciphertext token") from exc
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed – wrong password or tampered data") from exc
    return plaintext.decode()
