"""
main.py – ESPx pipeline entry-point.

Usage:
    python -m pipeline            # run all feeds, print rich summary
    python -m pipeline --tag esp32
    python -m pipeline --no-cache
    python -m pipeline --list-feeds
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

try:
    from rich.console import Console
    from rich.table   import Table
    from rich.panel   import Panel
    from rich.text    import Text
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

from .agent  import fetch_all_parallel
from .cache  import Cache
from .feed   import Feed, default_registry

console = Console() if _HAS_RICH else None
logger  = logging.getLogger(__name__)


# ── helpers ───────────────────────────────────────────────────────────────

def _print(msg: str, style: str = "") -> None:
    if console:
        console.print(msg, style=style)
    else:
        print(msg)


def _banner() -> None:
    if _HAS_RICH:
        title = Text("iNFINITEAi2025  ∞  ESPx Pipeline", style="bold gold1")
        console.print(Panel(title, subtitle="[dim]research · feeds · cache[/dim]",
                             border_style="gold3", padding=(0, 2)))
    else:
        print("=" * 60)
        print("  iNFINITEAi2025  ∞  ESPx Pipeline")
        print("=" * 60)


# ── core logic ────────────────────────────────────────────────────────────

def run(tag: str | None = None, use_cache: bool = True, ttl: int = 3600) -> None:
    """Fetch all (or tag-filtered) feeds, update cache, and display results."""
    _banner()

    registry = default_registry()
    feeds    = registry.by_tag(tag) if tag else registry.all()

    if not feeds:
        _print(f"[yellow]No feeds found for tag '{tag}'.[/yellow]" if _HAS_RICH else
               f"No feeds found for tag '{tag}'.")
        return

    _print(f"\n[bold]Checking {len(feeds)} feed(s)…[/bold]\n" if _HAS_RICH else
           f"\nChecking {len(feeds)} feed(s)…\n")

    cache        = Cache("pipeline", ttl=ttl)
    results_all  : dict[str, list[dict]] = {}
    stale_feeds  : list[Feed] = []

    # ── cache hit / miss split ────────────────────────────────────────
    for feed in feeds:
        cached = cache.get(feed.name) if use_cache else None
        if cached:
            results_all[feed.name] = cached.get("items", [])
        else:
            stale_feeds.append(feed)

    # ── parallel fetch for stale feeds ────────────────────────────────
    if stale_feeds:
        t0      = time.perf_counter()
        fetched = fetch_all_parallel(stale_feeds)
        elapsed = time.perf_counter() - t0
        _print(f"[dim]Fetched {len(stale_feeds)} feed(s) in {elapsed:.2f}s[/dim]\n"
               if _HAS_RICH else
               f"Fetched {len(stale_feeds)} feed(s) in {elapsed:.2f}s\n")
        for feed in stale_feeds:
            items = fetched.get(feed.name, [])
            results_all[feed.name] = items
            cache.set(feed.name, {"items": items})

    # ── display ───────────────────────────────────────────────────────
    total_items = 0
    for feed in feeds:
        items = results_all.get(feed.name, [])
        total_items += len(items)

        if _HAS_RICH:
            tbl = Table(title=f"[bold gold1]{feed.name}[/bold gold1]  [dim]– {feed.description}[/dim]",
                        show_lines=True, border_style="dim")
            tbl.add_column("Title",     style="cyan",   no_wrap=False, max_width=60)
            tbl.add_column("Published", style="green",  no_wrap=True,  width=22)
            tbl.add_column("URL",       style="blue",   no_wrap=False, max_width=50)
            for item in items:
                tbl.add_row(item.get("title", ""),
                            item.get("published", "")[:19],
                            item.get("url", ""))
            if not items:
                tbl.add_row("[dim]no data[/dim]", "", "")
            console.print(tbl)
        else:
            print(f"\n── {feed.name}: {feed.description} ──")
            for item in items:
                print(f"  • {item.get('title','')}  [{item.get('published','')[:10]}]")
                print(f"    {item.get('url','')}")
            if not items:
                print("  (no data)")

    _print(f"\n[bold green]Done.[/bold green]  {total_items} item(s) across {len(feeds)} feed(s).  "
           f"Cache: [cyan]{cache._path}[/cyan]"
           if _HAS_RICH else
           f"\nDone. {total_items} item(s) across {len(feeds)} feed(s).  Cache: {cache._path}")


# ── CLI ───────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m pipeline",
        description="ESPx content-upgrade pipeline – fetch, cache, and display feed data.",
    )
    parser.add_argument("--tag",        help="Filter feeds by tag (e.g. esp32, ai, security)")
    parser.add_argument("--no-cache",   action="store_true", help="Bypass the local cache")
    parser.add_argument("--ttl",        type=int, default=3600, metavar="SECONDS",
                        help="Cache TTL in seconds (default: 3600)")
    parser.add_argument("--list-feeds", action="store_true", help="List all registered feeds and exit")
    args = parser.parse_args(argv)

    if args.list_feeds:
        reg = default_registry()
        if _HAS_RICH:
            tbl = Table(title="Registered Feeds", border_style="gold3")
            tbl.add_column("Name",        style="cyan")
            tbl.add_column("Kind",        style="yellow")
            tbl.add_column("Tags",        style="green")
            tbl.add_column("Description", style="white")
            for f in reg.all():
                tbl.add_row(f.name, f.kind, ", ".join(f.tags), f.description)
            console.print(tbl)
        else:
            for f in reg.all():
                print(f"{f.name:35s}  [{f.kind}]  tags={f.tags}  {f.description}")
        sys.exit(0)

    run(tag=args.tag, use_cache=not args.no_cache, ttl=args.ttl)


if __name__ == "__main__":
    main()
