"""
agent.py – Research agents that fetch, parse, and normalise feed data.

Each agent handles one ``Feed.kind`` and returns a list of normalised
``Item`` dicts with at least ``title``, ``url``, and ``published`` keys.
Fetching is done via :mod:`requests` with a short timeout; on failure the
agent returns an empty list so the rest of the pipeline continues.
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

from .feed import Feed

logger = logging.getLogger(__name__)

_TIMEOUT    = 10   # seconds per HTTP request
_USER_AGENT = "ESPx-Research-Bot/1.0 (+https://github.com/NaTo1000/ESPx)"
_HEADERS    = {"User-Agent": _USER_AGENT, "Accept": "application/vnd.github+json"}


def _get(url: str) -> Any | None:
    """Perform a GET request and return parsed JSON, or *None* on failure."""
    if not _HAS_REQUESTS:
        logger.warning("requests library not installed – skipping %s", url)
        return None
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.debug("fetch failed for %s: %s", url, exc)
        return None


# ── Kind-specific parsers ─────────────────────────────────────────────────

def _parse_github_release(data: Any) -> list[dict]:
    items = []
    if not isinstance(data, list):
        return items
    for rel in data:
        items.append({
            "title":     rel.get("name") or rel.get("tag_name", ""),
            "url":       rel.get("html_url", ""),
            "published": rel.get("published_at", ""),
            "body":      (rel.get("body") or "")[:300],
        })
    return items


def _parse_github_commits(data: Any) -> list[dict]:
    items = []
    if not isinstance(data, list):
        return items
    for commit in data:
        c = commit.get("commit", {})
        items.append({
            "title":     c.get("message", "").split("\n", 1)[0],
            "url":       commit.get("html_url", ""),
            "published": c.get("author", {}).get("date", ""),
            "sha":       commit.get("sha", "")[:8],
        })
    return items


def _parse_nvd(data: Any) -> list[dict]:
    items = []
    if not isinstance(data, dict):
        return items
    for vuln in data.get("vulnerabilities", []):
        cve  = vuln.get("cve", {})
        desc = next(
            (d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"),
            "",
        )
        items.append({
            "title":     cve.get("id", ""),
            "url":       f"https://nvd.nist.gov/vuln/detail/{cve.get('id','')}",
            "published": cve.get("published", ""),
            "body":      desc[:300],
        })
    return items


def _parse_hf_models(data: Any) -> list[dict]:
    items = []
    if not isinstance(data, list):
        return items
    for m in data:
        items.append({
            "title":     m.get("id", ""),
            "url":       f"https://huggingface.co/{m.get('id','')}",
            "published": m.get("lastModified", ""),
            "pipeline":  m.get("pipeline_tag", ""),
            "likes":     m.get("likes", 0),
        })
    return items


_PARSERS = {
    "github_release":  _parse_github_release,
    "github_commits":  _parse_github_commits,
    "json_api":        lambda d: (
        _parse_nvd(d)       if "vulnerabilities" in (d or {}) else
        _parse_hf_models(d) if isinstance(d, list)             else []
    ),
}


def fetch_feed(feed: Feed) -> list[dict]:
    """Fetch a single feed and return a list of normalised items."""
    data = _get(feed.url)
    if data is None:
        return []
    parser = _PARSERS.get(feed.kind)
    if parser is None:
        logger.warning("No parser for feed kind '%s' (feed: %s)", feed.kind, feed.name)
        return []
    return parser(data)


def fetch_all_parallel(feeds: list[Feed], max_workers: int = 8) -> dict[str, list[dict]]:
    """Fetch all feeds in parallel using a thread pool.

    Returns a dict mapping ``feed.name`` → list of items.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results: dict[str, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(fetch_feed, f): f for f in feeds}
        for future in as_completed(future_map):
            feed = future_map[future]
            try:
                results[feed.name] = future.result()
            except Exception as exc:  # noqa: BLE001
                logger.error("Agent error for %s: %s", feed.name, exc)
                results[feed.name] = []
    return results
