"""
Innovations Engine – Core Search & Mapping
==========================================
Matches a plain-English description of intended firmware outcomes to the
most relevant ESP32 capabilities in the knowledge base.

Algorithm
---------
For each knowledge-base entry the engine scores the user query by:
  1. Keyword overlap  – tokens in the query that appear in ``entry["keywords"]``
  2. Title overlap    – tokens shared with the entry title
  3. Tag overlap      – tokens shared with the entry tags
  4. Description hits – query tokens found inside the long description text

Scores are weighted, normalised, and the top-N entries are returned ranked
by relevance, each annotated with matched keywords and a confidence score.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .knowledge_base import FIRMWARE_KNOWLEDGE_BASE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset(
    "a an the and or but in on at to for of with is are was were be been "
    "i want need make build create add use my get have do can".split()
)


def _tokenise(text: str) -> List[str]:
    """Lowercase, strip punctuation, split on whitespace, remove stop words."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return [t for t in text.split() if t not in _STOP_WORDS and len(t) > 1]


def _tokens_set(tokens: List[str]) -> set:
    return set(tokens)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class FirmwareMatch:
    """A single knowledge-base entry matched to the user query."""
    id: str
    title: str
    description: str
    score: float                  # 0.0 – 1.0
    matched_keywords: List[str]
    use_cases: List[str]
    framework: str
    components: List[str]
    snippet: str
    tags: List[str]

    def __str__(self) -> str:  # pragma: no cover
        bar = "█" * int(self.score * 20)
        lines = [
            f"  [{bar:<20}] {self.score*100:5.1f}%  {self.title}",
            f"    {self.description}",
        ]
        if self.matched_keywords:
            lines.append(f"    Matched keywords : {', '.join(self.matched_keywords)}")
        if self.use_cases:
            lines.append("    Use cases:")
            for uc in self.use_cases:
                lines.append(f"      • {uc}")
        lines.append(f"    Framework : {self.framework}")
        lines.append(f"    Components: {', '.join(self.components)}")
        lines.append("    Code hint:")
        for code_line in self.snippet.splitlines():
            lines.append(f"      {code_line}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class InnovationsEngine:
    """
    Search the ESP32 firmware knowledge base by describing your intended
    outcome in plain English.

    Parameters
    ----------
    knowledge_base : list, optional
        Override the default knowledge base with a custom list of entries.
        Useful for testing or extending the catalogue.

    Examples
    --------
    >>> engine = InnovationsEngine()
    >>> results = engine.search("I want to send temperature data to the cloud")
    >>> for r in results:
    ...     print(r.title, r.score)
    """

    # Scoring weights (must sum to 1.0 for normalisation sanity)
    _W_KEYWORD     = 0.50
    _W_TITLE       = 0.20
    _W_TAG         = 0.15
    _W_DESCRIPTION = 0.15

    def __init__(self, knowledge_base: Optional[list] = None) -> None:
        self._kb = knowledge_base if knowledge_base is not None else FIRMWARE_KNOWLEDGE_BASE

    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_n: int = 5,
        min_score: float = 0.05,
    ) -> List[FirmwareMatch]:
        """
        Search for firmware capabilities matching *query*.

        Parameters
        ----------
        query :
            Plain-English description of the intended firmware outcome.
        top_n :
            Maximum number of results to return (default 5).
        min_score :
            Minimum relevance score threshold – entries below this are dropped.

        Returns
        -------
        list[FirmwareMatch]
            Results ordered from most to least relevant.
        """
        query_tokens = _tokenise(query)
        query_set = _tokens_set(query_tokens)
        query_text = query.lower()

        scored: List[tuple] = []

        for entry in self._kb:
            score, matched_kw = self._score_entry(entry, query_tokens, query_set, query_text)
            if score >= min_score:
                fm = FirmwareMatch(
                    id=entry["id"],
                    title=entry["title"],
                    description=entry["description"],
                    score=round(score, 4),
                    matched_keywords=matched_kw,
                    use_cases=entry.get("use_cases", []),
                    framework=entry["firmware"]["framework"],
                    components=entry["firmware"]["components"],
                    snippet=entry["firmware"]["snippet"],
                    tags=entry.get("tags", []),
                )
                scored.append((score, fm))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [fm for _, fm in scored[:top_n]]

    # ------------------------------------------------------------------

    def _score_entry(
        self,
        entry: dict,
        query_tokens: List[str],
        query_set: set,
        query_text: str,
    ) -> tuple:
        """Return (float_score, matched_keyword_list) for *entry*."""

        # --- keyword overlap -------------------------------------------
        kw_tokens: List[List[str]] = [_tokenise(kw) for kw in entry["keywords"]]
        matched_kw: List[str] = []
        kw_score = 0.0
        for phrase_tokens, original_kw in zip(kw_tokens, entry["keywords"]):
            phrase_set = set(phrase_tokens)
            if not phrase_set:
                continue
            overlap = len(query_set & phrase_set) / len(phrase_set)
            if overlap > 0:
                matched_kw.append(original_kw)
                kw_score += overlap
        if kw_tokens:
            kw_score = min(kw_score / len(kw_tokens) * 3, 1.0)  # scale + cap

        # Also give a bonus for full multi-word keyword phrase match in raw text
        for kw in entry["keywords"]:
            if kw.lower() in query_text:
                kw_score = min(kw_score + 0.2, 1.0)

        # --- title overlap ---------------------------------------------
        title_tokens = set(_tokenise(entry["title"]))
        title_score = (
            len(query_set & title_tokens) / len(title_tokens)
            if title_tokens else 0.0
        )

        # --- tag overlap -----------------------------------------------
        tag_tokens = set(" ".join(entry.get("tags", [])).replace("-", " ").split())
        tag_score = (
            len(query_set & tag_tokens) / len(tag_tokens)
            if tag_tokens else 0.0
        )

        # --- description text hits ------------------------------------
        desc_tokens = set(_tokenise(entry["description"]))
        desc_score = (
            len(query_set & desc_tokens) / max(len(query_set), 1)
        )

        total = (
            self._W_KEYWORD     * kw_score
            + self._W_TITLE     * title_score
            + self._W_TAG       * tag_score
            + self._W_DESCRIPTION * desc_score
        )

        return total, matched_kw

    # ------------------------------------------------------------------

    def list_tags(self) -> List[str]:
        """Return a sorted list of all unique tags in the knowledge base."""
        tags: set = set()
        for entry in self._kb:
            tags.update(entry.get("tags", []))
        return sorted(tags)

    def list_by_tag(self, tag: str) -> List[dict]:
        """Return all knowledge-base entries that have *tag*."""
        return [e for e in self._kb if tag in e.get("tags", [])]

    def get_entry(self, entry_id: str) -> Optional[dict]:
        """Look up a knowledge-base entry by its ``id`` field."""
        for entry in self._kb:
            if entry["id"] == entry_id:
                return entry
        return None
