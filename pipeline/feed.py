"""
feed.py – Modular feed definitions for the ESPx pipeline.

Each feed is a plain dataclass describing a remote source (URL, kind, and
optional parse hints).  ``FeedRegistry`` holds all active feeds and supports
dynamic registration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Feed:
    """A single remote data source."""

    name:        str
    url:         str
    kind:        str   # "github_release" | "github_commits" | "rss" | "json_api"
    description: str   = ""
    tags:        list[str] = field(default_factory=list)


class FeedRegistry:
    """Collection of all active feeds, indexed by name."""

    def __init__(self) -> None:
        self._feeds: dict[str, Feed] = {}

    def register(self, feed: Feed) -> None:
        self._feeds[feed.name] = feed

    def all(self) -> list[Feed]:
        return list(self._feeds.values())

    def by_tag(self, tag: str) -> list[Feed]:
        return [f for f in self._feeds.values() if tag in f.tags]

    def __len__(self) -> int:
        return len(self._feeds)


# ── Default feed catalogue ─────────────────────────────────────────────────

def default_registry() -> FeedRegistry:
    """Return a pre-populated registry covering ESP32, AI models, and security."""
    reg = FeedRegistry()

    # ESP32 / ESP-IDF firmware
    reg.register(Feed(
        name="esp-idf-releases",
        url="https://api.github.com/repos/espressif/esp-idf/releases?per_page=5",
        kind="github_release",
        description="Latest ESP-IDF framework releases",
        tags=["esp32", "firmware"],
    ))
    reg.register(Feed(
        name="esp-idf-commits",
        url="https://api.github.com/repos/espressif/esp-idf/commits?per_page=5",
        kind="github_commits",
        description="Recent ESP-IDF commits",
        tags=["esp32", "firmware"],
    ))
    reg.register(Feed(
        name="arduino-esp32-releases",
        url="https://api.github.com/repos/espressif/arduino-esp32/releases?per_page=5",
        kind="github_release",
        description="Arduino-ESP32 board support releases",
        tags=["esp32", "arduino"],
    ))

    # Security / CVE
    reg.register(Feed(
        name="nvd-esp32-cve",
        url="https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=ESP32&resultsPerPage=5",
        kind="json_api",
        description="NIST NVD – recent ESP32 CVEs",
        tags=["security", "esp32"],
    ))

    # AI / Hugging Face models
    reg.register(Feed(
        name="hf-trending-models",
        url="https://huggingface.co/api/models?sort=trending&limit=5",
        kind="json_api",
        description="Trending Hugging Face models",
        tags=["ai", "hf"],
    ))

    # Robotics
    reg.register(Feed(
        name="ros2-releases",
        url="https://api.github.com/repos/ros2/rclpy/releases?per_page=5",
        kind="github_release",
        description="ROS 2 rclpy releases",
        tags=["robotics"],
    ))

    return reg
