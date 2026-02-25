"""
ESPiritAi Multi-AI Council

Ensemble of models for collaborative decision-making via consensus.
Each council member provides a recommendation; the consensus engine
aggregates them into a final decision.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Council member interface
# ---------------------------------------------------------------------------

@dataclass
class Recommendation:
    """A recommendation produced by a council member."""

    member_id: str
    action: str
    confidence: float  # 0.0 – 1.0
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class CouncilMember:
    """
    Base class for an AI council member.

    Subclass and override ``recommend`` to implement custom logic.
    The default implementation is a configurable stub.
    """

    def __init__(
        self,
        member_id: str,
        specialty: str = "general",
        weight: float = 1.0,
    ) -> None:
        self.member_id = member_id
        self.specialty = specialty
        self.weight = weight  # influence weight in consensus

    def recommend(self, context: Dict[str, Any]) -> Recommendation:
        """
        Produce a recommendation given a context dict.

        The default implementation picks the first available action with
        random confidence — override in subclasses for real logic.
        """
        actions: List[str] = context.get("available_actions", ["no_op"])
        action = actions[0] if actions else "no_op"
        confidence = round(random.uniform(0.5, 1.0), 3)
        return Recommendation(
            member_id=self.member_id,
            action=action,
            confidence=confidence,
            rationale=f"{self.specialty} heuristic",
        )


# ---------------------------------------------------------------------------
# Specialised council members
# ---------------------------------------------------------------------------

class SecurityAdvisor(CouncilMember):
    """Council member specialising in security risk assessment."""

    _RISKY = {"deauth_attack", "packet_capture", "evil_portal", "beacon_spam"}

    def __init__(self) -> None:
        super().__init__("security_advisor", specialty="security", weight=1.5)

    def recommend(self, context: Dict[str, Any]) -> Recommendation:
        available: List[str] = context.get("available_actions", [])
        risk_score: float = context.get("risk_score", 0.0)

        # Filter out risky actions if risk is high
        safe = [a for a in available if a not in self._RISKY] or available
        if risk_score > 0.6:
            action = safe[0] if safe else "abort"
            confidence = 0.9
            rationale = f"High risk ({risk_score:.2f}); recommending safe action."
        else:
            action = available[0] if available else "no_op"
            confidence = 0.7
            rationale = "Risk acceptable; proceeding with primary action."
        return Recommendation(
            member_id=self.member_id,
            action=action,
            confidence=confidence,
            rationale=rationale,
        )


class PerformanceAdvisor(CouncilMember):
    """Council member specialising in system performance."""

    def __init__(self) -> None:
        super().__init__("performance_advisor", specialty="performance", weight=1.2)

    def recommend(self, context: Dict[str, Any]) -> Recommendation:
        available: List[str] = context.get("available_actions", [])
        cpu: float = context.get("cpu_usage_pct", 0.0)
        heap: int = context.get("heap_free_b", 200_000)

        if cpu > 80 or heap < 30_000:
            action = "reduce_load"
            confidence = 0.85
            rationale = (
                f"System under pressure (CPU={cpu:.0f}%, heap={heap}B). "
                "Recommending load reduction."
            )
        else:
            action = available[0] if available else "no_op"
            confidence = 0.75
            rationale = "System resources adequate."
        return Recommendation(
            member_id=self.member_id,
            action=action,
            confidence=confidence,
            rationale=rationale,
        )


class NetworkAdvisor(CouncilMember):
    """Council member specialising in network operations."""

    def __init__(self) -> None:
        super().__init__("network_advisor", specialty="network", weight=1.0)

    def recommend(self, context: Dict[str, Any]) -> Recommendation:
        available: List[str] = context.get("available_actions", [])
        wifi_ok: bool = context.get("wifi_connected", False)
        rssi: int = context.get("wifi_rssi_dbm", -100)

        if not wifi_ok or rssi < -80:
            action = "reconnect_wifi"
            confidence = 0.88
            rationale = "Poor / no Wi-Fi connection; reconnect recommended."
        else:
            action = available[0] if available else "no_op"
            confidence = 0.72
            rationale = "Network conditions acceptable."
        return Recommendation(
            member_id=self.member_id,
            action=action,
            confidence=confidence,
            rationale=rationale,
        )


# ---------------------------------------------------------------------------
# Consensus Engine
# ---------------------------------------------------------------------------

@dataclass
class ConsensusResult:
    """Aggregated outcome from the council."""

    final_action: str
    consensus_confidence: float
    votes: Dict[str, int]          # action -> vote count
    weighted_scores: Dict[str, float]  # action -> weighted confidence sum
    recommendations: List[Recommendation]
    dissent: List[str] = field(default_factory=list)  # minority opinions


class ConsensusEngine:
    """
    Aggregates recommendations from council members via weighted voting.

    The action with the highest weighted confidence score wins.
    If the winning margin is below *min_margin*, the result is flagged as
    low-confidence and a fallback action is used.
    """

    def __init__(self, min_margin: float = 0.1, fallback_action: str = "no_op") -> None:
        self.min_margin = min_margin
        self.fallback_action = fallback_action

    def aggregate(
        self,
        recommendations: List[Recommendation],
    ) -> ConsensusResult:
        if not recommendations:
            return ConsensusResult(
                final_action=self.fallback_action,
                consensus_confidence=0.0,
                votes={},
                weighted_scores={},
                recommendations=[],
            )

        # Gather member weights (default 1.0 if not set)
        votes: Dict[str, int] = {}
        weighted: Dict[str, float] = {}

        for rec in recommendations:
            votes[rec.action] = votes.get(rec.action, 0) + 1
            score = rec.confidence * getattr(rec, "_weight", 1.0)
            weighted[rec.action] = weighted.get(rec.action, 0.0) + score

        # Determine winner
        winner = max(weighted, key=lambda a: weighted[a])
        total_score = sum(weighted.values())
        winner_score = weighted[winner]
        confidence = winner_score / total_score if total_score > 0 else 0.0

        # Check margin
        sorted_scores = sorted(weighted.values(), reverse=True)
        margin = (
            (sorted_scores[0] - sorted_scores[1]) / total_score
            if len(sorted_scores) > 1
            else 1.0
        )
        final_action = winner if margin >= self.min_margin else self.fallback_action

        # Identify dissenting recommendations
        dissent = [r.member_id for r in recommendations if r.action != winner]

        return ConsensusResult(
            final_action=final_action,
            consensus_confidence=round(confidence, 4),
            votes=votes,
            weighted_scores={k: round(v, 4) for k, v in weighted.items()},
            recommendations=recommendations,
            dissent=dissent,
        )


# ---------------------------------------------------------------------------
# Multi-AI Council
# ---------------------------------------------------------------------------

class MultiAICouncil:
    """
    Orchestrates a panel of specialised AI council members to reach
    consensus on ESPiritAi orchestration decisions.
    """

    def __init__(
        self,
        members: Optional[List[CouncilMember]] = None,
        consensus_engine: Optional[ConsensusEngine] = None,
    ) -> None:
        self.members: List[CouncilMember] = members or [
            SecurityAdvisor(),
            PerformanceAdvisor(),
            NetworkAdvisor(),
        ]
        self.engine = consensus_engine or ConsensusEngine()
        self.decision_history: List[ConsensusResult] = []

    def add_member(self, member: CouncilMember) -> None:
        self.members.append(member)

    def deliberate(self, context: Dict[str, Any]) -> ConsensusResult:
        """
        Ask every council member for a recommendation, then run the
        consensus engine and store the result.
        """
        recommendations: List[Recommendation] = []
        for member in self.members:
            rec = member.recommend(context)
            # Attach member weight for consensus scoring
            rec._weight = member.weight  # type: ignore[attr-defined]
            recommendations.append(rec)

        result = self.engine.aggregate(recommendations)
        self.decision_history.append(result)
        return result

    def metrics(self) -> Dict[str, Any]:
        return {
            "member_count": len(self.members),
            "decisions_made": len(self.decision_history),
            "members": [
                {"id": m.member_id, "specialty": m.specialty, "weight": m.weight}
                for m in self.members
            ],
        }
