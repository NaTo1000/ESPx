"""Tests for the ESPx pipeline package."""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Cache tests ────────────────────────────────────────────────────────────

def test_cache_set_get(tmp_path):
    from pipeline.cache import Cache
    c = Cache("test", cache_dir=tmp_path, ttl=60)
    c.set("key1", {"value": "hello"})
    entry = c.get("key1")
    assert entry is not None
    assert entry["value"] == "hello"


def test_cache_ttl_expiry(tmp_path):
    from pipeline.cache import Cache
    c = Cache("test", cache_dir=tmp_path, ttl=1)
    c.set("key1", {"value": "hi"})
    # Manually backdate the timestamp
    c._data["key1"]["_ts"] = time.time() - 10
    c._save()
    result = c.get("key1")
    assert result is None


def test_cache_invalidate(tmp_path):
    from pipeline.cache import Cache
    c = Cache("test", cache_dir=tmp_path, ttl=60)
    c.set("k", {"v": 1})
    c.invalidate("k")
    assert c.get("k") is None


def test_cache_clear(tmp_path):
    from pipeline.cache import Cache
    c = Cache("test", cache_dir=tmp_path, ttl=60)
    c.set("a", {"x": 1})
    c.set("b", {"x": 2})
    c.clear()
    assert c.keys() == []


def test_cache_persistence(tmp_path):
    from pipeline.cache import Cache
    c1 = Cache("test", cache_dir=tmp_path, ttl=60)
    c1.set("persistent", {"data": [1, 2, 3]})
    # Re-open from disk
    c2 = Cache("test", cache_dir=tmp_path, ttl=60)
    entry = c2.get("persistent")
    assert entry is not None
    assert entry["data"] == [1, 2, 3]


# ── Feed registry tests ────────────────────────────────────────────────────

def test_default_registry_non_empty():
    from pipeline.feed import default_registry
    reg = default_registry()
    assert len(reg) > 0


def test_registry_by_tag():
    from pipeline.feed import default_registry
    reg  = default_registry()
    esp  = reg.by_tag("esp32")
    ai   = reg.by_tag("ai")
    assert len(esp) >= 1
    assert len(ai)  >= 1


def test_feed_fields():
    from pipeline.feed import Feed
    f = Feed(name="test", url="http://example.com", kind="json_api",
             description="desc", tags=["a", "b"])
    assert f.name == "test"
    assert "a" in f.tags


# ── Agent parsing tests (offline – no HTTP) ────────────────────────────────

def test_parse_github_release():
    from pipeline.agent import _parse_github_release
    data = [{"name": "v5.2.0", "tag_name": "v5.2.0",
             "html_url": "https://example.com/rel", "published_at": "2024-01-01T00:00:00Z",
             "body": "changelog"}]
    items = _parse_github_release(data)
    assert len(items) == 1
    assert items[0]["title"] == "v5.2.0"
    assert items[0]["url"]   == "https://example.com/rel"


def test_parse_github_commits():
    from pipeline.agent import _parse_github_commits
    data = [{"sha": "abc123def456", "html_url": "https://example.com/commit/abc123",
             "commit": {"message": "fix: some bug\n\nDetails here",
                        "author": {"date": "2024-01-02T12:00:00Z"}}}]
    items = _parse_github_commits(data)
    assert len(items) == 1
    assert items[0]["title"] == "fix: some bug"
    assert items[0]["sha"]   == "abc123de"


def test_parse_nvd():
    from pipeline.agent import _parse_nvd
    data = {"vulnerabilities": [{"cve": {
        "id": "CVE-2024-1234",
        "published": "2024-01-01T00:00:00Z",
        "descriptions": [{"lang": "en", "value": "A flaw in ESP32 firmware."}],
    }}]}
    items = _parse_nvd(data)
    assert len(items) == 1
    assert "CVE-2024-1234" in items[0]["title"]


def test_parse_hf_models():
    from pipeline.agent import _parse_hf_models
    data = [{"id": "meta-llama/Llama-2-7b", "lastModified": "2024-01-10T00:00:00Z",
             "pipeline_tag": "text-generation", "likes": 9000}]
    items = _parse_hf_models(data)
    assert len(items) == 1
    assert items[0]["likes"] == 9000


def test_fetch_feed_uses_cache_mock():
    """fetch_feed should return items for a known kind even with mocked HTTP."""
    from pipeline.feed  import Feed
    from pipeline.agent import fetch_feed
    feed = Feed(name="mock", url="http://mock", kind="github_release")
    mock_data = [{"name": "v1.0", "tag_name": "v1.0", "html_url": "http://h",
                  "published_at": "2024-01-01T00:00:00Z", "body": ""}]
    with patch("pipeline.agent._get", return_value=mock_data):
        items = fetch_feed(feed)
    assert len(items) == 1
    assert items[0]["title"] == "v1.0"


def test_fetch_all_parallel_mock():
    from pipeline.feed  import Feed
    from pipeline.agent import fetch_all_parallel
    feeds = [
        Feed(name="f1", url="u1", kind="github_release"),
        Feed(name="f2", url="u2", kind="github_release"),
    ]
    mock_item = [{"name": "v1", "tag_name": "v1", "html_url": "u",
                  "published_at": "", "body": ""}]
    with patch("pipeline.agent._get", return_value=mock_item):
        results = fetch_all_parallel(feeds)
    assert set(results.keys()) == {"f1", "f2"}
    assert results["f1"][0]["title"] == "v1"


def test_fetch_feed_returns_empty_on_error():
    from pipeline.feed  import Feed
    from pipeline.agent import fetch_feed
    feed = Feed(name="bad", url="http://bad", kind="github_release")
    with patch("pipeline.agent._get", return_value=None):
        items = fetch_feed(feed)
    assert items == []
