"""Tests for espx.vault.crypto."""
import pytest
from espx.vault.crypto import (
    decrypt,
    decrypt_with_password,
    encrypt,
    encrypt_with_password,
    generate_vault_key,
)


def test_roundtrip_with_key():
    key = generate_vault_key()
    plaintext = "hf_SuperSecretToken123"
    token = encrypt(plaintext, key)
    assert decrypt(token, key) == plaintext


def test_roundtrip_with_password():
    pw = "correct-horse-battery-staple"
    plaintext = "sk-robotics-api-key-xyz"
    token = encrypt_with_password(plaintext, pw)
    assert decrypt_with_password(token, pw) == plaintext


def test_wrong_key_raises():
    key = generate_vault_key()
    wrong_key = generate_vault_key()
    token = encrypt("secret", key)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, wrong_key)


def test_wrong_password_raises():
    token = encrypt_with_password("secret", "right-password")
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_with_password(token, "wrong-password")


def test_tampered_ciphertext_raises():
    key = generate_vault_key()
    token = encrypt("sensitive-data", key)
    # Corrupt the last byte of the ciphertext segment
    parts = token.split(".")
    tampered = parts[2][:-2] + "AA"
    bad_token = ".".join(parts[:2] + [tampered])
    with pytest.raises(ValueError):
        decrypt(bad_token, key)


def test_bytes_plaintext():
    key = generate_vault_key()
    token = encrypt(b"binary payload", key)
    assert decrypt(token, key) == "binary payload"


def test_each_encrypt_unique():
    key = generate_vault_key()
    t1 = encrypt("same", key)
    t2 = encrypt("same", key)
    assert t1 != t2  # different nonces
