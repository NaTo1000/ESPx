"""Tests for espx.vault.slots."""
import pytest
from espx.vault.slots import Slot, SlotManager, SlotPolicy


def test_allocate_and_get():
    sm = SlotManager()
    sm.allocate("hf-prod", "huggingface", description="HF production token")
    slot = sm.get("hf-prod")
    assert slot.name == "hf-prod"
    assert slot.service == "huggingface"


def test_duplicate_slot_raises():
    sm = SlotManager()
    sm.allocate("hf-prod", "huggingface")
    with pytest.raises(ValueError, match="already exists"):
        sm.allocate("hf-prod", "huggingface")


def test_capacity_exhausted():
    sm = SlotManager(capacity=2)
    sm.allocate("a", "svc")
    sm.allocate("b", "svc")
    with pytest.raises(RuntimeError, match="capacity exhausted"):
        sm.allocate("c", "svc")


def test_delete():
    sm = SlotManager()
    sm.allocate("temp", "svc")
    sm.delete("temp")
    assert sm.count() == 0
    with pytest.raises(KeyError):
        sm.get("temp")


def test_list_slots():
    sm = SlotManager()
    sm.allocate("s1", "svc")
    sm.allocate("s2", "svc")
    assert len(sm.list_slots()) == 2


def test_rate_limit():
    policy = SlotPolicy(max_reads_per_window=3, window_seconds=60.0)
    sm = SlotManager()
    sm.allocate("rls", "svc", policy=policy)
    slot = sm.get("rls")
    assert slot.check_rate_limit() is True
    assert slot.check_rate_limit() is True
    assert slot.check_rate_limit() is True
    assert slot.check_rate_limit() is False  # 4th access exceeds limit


def test_serialisation_roundtrip():
    sm = SlotManager(capacity=10)
    sm.allocate("x", "esp-idf", tags=["prod"])
    data = sm.to_dict()
    sm2 = SlotManager.from_dict(data)
    assert sm2.capacity == 10
    assert sm2.get("x").service == "esp-idf"
    assert sm2.get("x").tags == ["prod"]
