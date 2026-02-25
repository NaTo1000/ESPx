"""Tests for espx.vault.rotation."""
import time
import pytest
from espx.vault.rotation import (
    KeyVersion,
    RotationManager,
    RotationPolicy,
    RotationStrategy,
    generate_key_material,
)


def test_register_creates_version_1():
    rm = RotationManager()
    v = rm.register("slot-a")
    assert v.version == 1
    assert v.is_active


def test_current_version_auto_registers():
    rm = RotationManager()
    v = rm.current_version("new-slot")
    assert v.version == 1


def test_rotate_increments_version():
    rm = RotationManager()
    rm.register("slot-a")
    v2 = rm.rotate("slot-a")
    assert v2.version == 2
    assert v2.is_active


def test_rotate_retires_previous():
    rm = RotationManager()
    rm.register("slot-a")
    rm.rotate("slot-a")
    history = rm.history("slot-a")
    assert history[0].retired_at is not None
    assert history[1].is_active


def test_should_rotate_time():
    rm = RotationManager()
    v = rm.register("slot-b")
    # artificially age the version
    v.created_at = time.time() - 100
    policy = RotationPolicy(strategy=RotationStrategy.TIME, rotate_after_seconds=50)
    assert rm.should_rotate("slot-b", policy) is True


def test_should_not_rotate_time():
    rm = RotationManager()
    rm.register("slot-b")
    policy = RotationPolicy(strategy=RotationStrategy.TIME, rotate_after_seconds=3600)
    assert rm.should_rotate("slot-b", policy) is False


def test_should_rotate_usage():
    rm = RotationManager()
    rm.register("slot-c")
    policy = RotationPolicy(strategy=RotationStrategy.USAGE, rotate_after_reads=3)
    for _ in range(3):
        rm.record_read("slot-c")
    assert rm.should_rotate("slot-c", policy) is True


def test_no_rotation_strategy():
    rm = RotationManager()
    rm.register("slot-d")
    policy = RotationPolicy(strategy=RotationStrategy.NONE)
    assert rm.should_rotate("slot-d", policy) is False


def test_serialisation_roundtrip():
    rm = RotationManager()
    rm.register("s")
    rm.record_read("s")
    rm.rotate("s")
    data = rm.to_dict()
    rm2 = RotationManager.from_dict(data)
    assert rm2.current_version("s").version == 2


def test_generate_key_material():
    k = generate_key_material()
    assert len(k) == 64  # 32 bytes hex
