"""
ESPx Innovations Engine – Command-Line Interface
================================================
Usage
-----
  # Interactive mode (REPL):
  python -m innovations_engine

  # One-shot query:
  python -m innovations_engine "send temperature over MQTT"

  # Show top N results:
  python -m innovations_engine "BLE sensor" --top 8

  # List all available tags:
  python -m innovations_engine --tags

  # Browse all entries for a tag:
  python -m innovations_engine --tag wifi
"""

import argparse
import sys

from .engine import InnovationsEngine


BANNER = r"""
  _____ ____  ____        ___                              _    _
 | ____/ ___||  _ \__  __/ _ \ _ __ __  ___  ___  __ _   | |  | |
 |  _| \___ \| |_) \ \/ / | | | '_ \_ \/ _ \/ _ \/ _` | | |  | |
 | |___ ___) |  __/ >  <| |_| | | | | |  __/  __/ (_| | |_|  |_|
 |_____|____/|_|   /_/\_\\___/|_| |_| |_|\___|\___|\__,_| (_) (_)

  ESPx Innovations Engine  ·  Describe your outcome, discover the firmware.
"""


def _render_result(index: int, match) -> None:
    bar_filled = int(match.score * 30)
    bar = "▓" * bar_filled + "░" * (30 - bar_filled)
    print(f"\n  ── Result {index} ─────────────────────────────────────────")
    print(f"  [{bar}] {match.score*100:5.1f}%")
    print(f"  {match.title}")
    print(f"  ID: {match.id}  │  Framework: {match.framework}")
    print()
    print(f"  Description")
    print(f"  {match.description}")
    if match.matched_keywords:
        print()
        print(f"  Matched intent keywords")
        print(f"  {', '.join(match.matched_keywords)}")
    if match.use_cases:
        print()
        print(f"  Common use cases")
        for uc in match.use_cases:
            print(f"    • {uc}")
    print()
    print(f"  Components / Libraries")
    for comp in match.components:
        print(f"    · {comp}")
    print()
    print(f"  Starter code snippet")
    print("  " + "─" * 50)
    for line in match.snippet.splitlines():
        print(f"  {line}")
    print("  " + "─" * 50)


def run_search(query: str, top_n: int) -> None:
    engine = InnovationsEngine()
    results = engine.search(query, top_n=top_n)
    if not results:
        print("\n  No matching firmware capabilities found for that description.")
        print("  Try different words describing what the device should *do*.")
        return
    print(f"\n  Found {len(results)} relevant firmware capability(s) for:")
    print(f"  \"{query}\"")
    for i, match in enumerate(results, 1):
        _render_result(i, match)


def interactive_mode() -> None:
    engine = InnovationsEngine()
    print(BANNER)
    print("  Describe what you want your ESP32 firmware to DO in plain English.")
    print("  Type  'tags'   to list available topic tags.")
    print("  Type  'tag <name>' to browse entries by tag.")
    print("  Type  'quit'   or press Ctrl-C to exit.")
    print()

    while True:
        try:
            raw = input("  > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye!")
            break

        if not raw:
            continue

        if raw.lower() in ("quit", "exit", "q"):
            print("  Goodbye!")
            break

        if raw.lower() == "tags":
            tags = engine.list_tags()
            print(f"\n  Available tags ({len(tags)}):")
            print("  " + "  ".join(f"[{t}]" for t in tags))
            print()
            continue

        if raw.lower().startswith("tag "):
            tag_name = raw[4:].strip()
            entries = engine.list_by_tag(tag_name)
            if not entries:
                print(f"  No entries found for tag '{tag_name}'.")
            else:
                print(f"\n  Entries tagged [{tag_name}]:")
                for e in entries:
                    print(f"    • {e['id']:30s}  {e['title']}")
            print()
            continue

        results = engine.search(raw, top_n=5)
        if not results:
            print("\n  No matches found. Try other words describing the outcome.\n")
            continue
        print(f"\n  Top {len(results)} match(es) for: \"{raw}\"")
        for i, match in enumerate(results, 1):
            _render_result(i, match)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="innovations_engine",
        description="ESPx Innovations Engine – map firmware intent to ESP32 capabilities",
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Plain-English description of the intended firmware outcome",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Number of results to show (default: 5)",
    )
    parser.add_argument(
        "--tags",
        action="store_true",
        help="List all available topic tags and exit",
    )
    parser.add_argument(
        "--tag",
        metavar="TAG",
        help="List all knowledge-base entries for a specific tag",
    )

    args = parser.parse_args(argv)

    engine = InnovationsEngine()

    if args.tags:
        tags = engine.list_tags()
        print(f"Available tags ({len(tags)}):")
        for t in tags:
            print(f"  [{t}]")
        return

    if args.tag:
        entries = engine.list_by_tag(args.tag)
        if not entries:
            print(f"No entries for tag '{args.tag}'.")
        else:
            print(f"Entries tagged [{args.tag}]:")
            for e in entries:
                print(f"  {e['id']:30s}  {e['title']}")
        return

    if args.query:
        run_search(args.query, args.top)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
