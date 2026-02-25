"""
ESPiritAi - Central Orchestration Engine

The 'brains' of the ESPx environment, binding all subsystems together:
  - Knowledge Base      (chip/firmware/project intelligence)
  - Self-Upgrading Algorithms (RL + meta-learning)
  - Simulation Runners  (virtual ESP emulation + risk assessment)
  - Multi-AI Council    (ensemble consensus decision-making)
  - CHAIMERA            (custom hybrid AI framework)
  - Three-Speed Engines (fast/medium/slow AI processing)
  - Cloud Compute       (distributed processing + Hugging Face)
  - Background Modes    (P2P orchestration, research pipelines)
  - API Vault           (secure credential management)
  - P2P Network         (peer coordination)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from espx.espiritai.algorithms import SelfUpgrader, Task as MetaTask
from espx.espiritai.background import (
    BackgroundModeManager,
    BackgroundModeStatus,
    P2POrchestrator,
    PipelineStage,
    ResearchPipeline,
)
from espx.espiritai.chaimera import CHAIMERA
from espx.espiritai.cloud import CloudComputeClient, DistributedProcessor, HuggingFaceClient
from espx.espiritai.council import MultiAICouncil
from espx.espiritai.engines import EngineResult, EngineSpeed, ThreeSpeedEngine
from espx.espiritai.knowledge import KnowledgeBase
from espx.espiritai.simulation import RiskLevel, SimulationResult, SimulationRunner
from espx.p2p.network import P2PNetwork
from espx.vault.vault import APIVault


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class ESPiritAiConfig:
    """Runtime configuration for ESPiritAi."""

    node_id: str = "espiritai_primary"
    vault_master_token: Optional[str] = None
    use_hf_stubs: bool = True          # True = no internet required
    background_enabled: bool = True
    simulation_chip: str = "ESP32"
    simulation_firmware: str = "Arduino"
    chaimera_actions: List[str] = field(default_factory=lambda: [
        "no_op",
        "abort",
        "reduce_load",
        "optimize_scan",
        "switch_engine_speed",
        "redistribute_tasks",
        "update_knowledge",
        "retrain_council",
        "reconnect_wifi",
        "run_simulation",
    ])
    rl_actions: Optional[List[str]] = None  # defaults to chaimera_actions


# ---------------------------------------------------------------------------
# ESPiritAi
# ---------------------------------------------------------------------------

class ESPiritAi:
    """
    ESPiritAi – Advanced Orchestration Model for the ESPx Environment.

    Acts as the central 'brains', coordinating:
    * Comprehensive ESP32/ESP8266 knowledge base
    * Continuous self-improvement via RL and meta-learning
    * Safe simulation and risk assessment
    * Collaborative multi-AI council decisions
    * CHAIMERA hybrid AI inference
    * Three-speed AI engine dispatch
    * Cloud compute and Hugging Face model integration
    * Background P2P orchestration and research pipelines
    * Secure API vault integration
    * P2P network coordination
    """

    VERSION = "1.0.0"

    def __init__(self, config: Optional[ESPiritAiConfig] = None) -> None:
        self.config = config or ESPiritAiConfig()
        self._boot_time = time.time()

        # -- Core subsystems ------------------------------------------------
        self.knowledge = KnowledgeBase()

        self.vault = APIVault(master_token=self.config.vault_master_token)

        self.p2p_network = P2PNetwork(local_node_id=self.config.node_id)

        actions = self.config.rl_actions or self.config.chaimera_actions
        self.upgrader = SelfUpgrader(rl_actions=actions)

        self.simulation = SimulationRunner()

        self.council = MultiAICouncil()

        self.chaimera = CHAIMERA(actions=self.config.chaimera_actions)

        self.engines = ThreeSpeedEngine()

        cloud_client = CloudComputeClient()
        hf_client = HuggingFaceClient(use_stubs=self.config.use_hf_stubs)
        self.cloud = DistributedProcessor(cloud=cloud_client, hf=hf_client)

        self.p2p_orchestrator = P2POrchestrator(node_id=self.config.node_id)

        self.background = BackgroundModeManager()
        self._setup_background_tasks()

        if self.config.background_enabled:
            self.background.start()

        self._decision_log: List[Dict[str, Any]] = []

    # -- Background setup --------------------------------------------------

    def _setup_background_tasks(self) -> None:
        """Register default background orchestration tasks."""
        self.background.register(
            "heartbeat",
            "P2P Heartbeat",
            lambda: self.p2p_network.metrics(),
            interval_s=30.0,
        )
        self.background.register(
            "knowledge_refresh",
            "Knowledge Base Refresh",
            lambda: self.knowledge.summary(),
            interval_s=3600.0,
        )
        self.background.register(
            "council_retrain",
            "Council Re-deliberation",
            lambda: self.council.metrics(),
            interval_s=300.0,
        )
        self.background.register(
            "upgrader_cycle",
            "Self-Upgrade Cycle",
            lambda: self.upgrader.metrics(),
            interval_s=120.0,
        )

    # -- Decision making ---------------------------------------------------

    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full ESPiritAi decision pipeline for a given context:

        1. Council deliberation (ensemble consensus)
        2. CHAIMERA blended inference
        3. Engine dispatch for the chosen action
        4. Log and return the decision

        The context dict may contain any of:
          available_actions, risk_score, cpu_usage_pct, heap_free_b,
          wifi_connected, wifi_rssi_dbm, reward, ...
        """
        # Merge chaimera actions into context if missing
        if "available_actions" not in context:
            context = {**context, "available_actions": self.config.chaimera_actions}

        # 1. Council
        council_result = self.council.deliberate(context)

        # 2. CHAIMERA
        chaimera_result = self.chaimera.infer(context)

        # 3. Final action selection (prefer CHAIMERA if both agree, else council)
        if council_result.final_action == chaimera_result.final_action:
            final_action = council_result.final_action
            confidence = (
                council_result.consensus_confidence + chaimera_result.confidence
            ) / 2
        else:
            # Weighted tiebreak: CHAIMERA wins on confidence
            if chaimera_result.confidence >= council_result.consensus_confidence:
                final_action = chaimera_result.final_action
                confidence = chaimera_result.confidence
            else:
                final_action = council_result.final_action
                confidence = council_result.consensus_confidence

        # 4. Dispatch to engine
        engine_result = self.engines.dispatch(final_action)

        decision = {
            "final_action": final_action,
            "confidence": round(confidence, 4),
            "council": {
                "action": council_result.final_action,
                "confidence": council_result.consensus_confidence,
            },
            "chaimera": {
                "action": chaimera_result.final_action,
                "confidence": chaimera_result.confidence,
            },
            "engine": {
                "speed": engine_result.engine_speed,
                "latency_ms": engine_result.latency_ms,
                "success": engine_result.success,
            },
            "timestamp": time.time(),
        }
        self._decision_log.append(decision)
        return decision

    # -- Self-upgrade cycle ------------------------------------------------

    def run_upgrade_cycle(
        self,
        state: str = "default",
        meta_tasks: Optional[List[MetaTask]] = None,
    ) -> Dict[str, Any]:
        """
        Run one self-upgrade cycle.

        The reward function is a simple heuristic based on recent decision
        confidence.
        """
        def reward_fn(s: str, action: str) -> float:
            recent = self._decision_log[-5:] if self._decision_log else []
            avg_conf = (
                sum(d["confidence"] for d in recent) / len(recent)
                if recent else 0.5
            )
            bonus = 0.1 if action != "no_op" else 0.0
            return round(avg_conf + bonus, 4)

        return self.upgrader.run_cycle(state, reward_fn, meta_tasks)

    # -- Simulation --------------------------------------------------------

    def simulate(
        self,
        scenario: str,
        steps: Optional[List[Dict[str, Any]]] = None,
        chip: Optional[str] = None,
        firmware: Optional[str] = None,
    ) -> SimulationResult:
        """Run a simulation scenario, defaulting to a standard boot+scan sequence."""
        default_steps = [
            {"type": "boot"},
            {"type": "connect_wifi", "ssid": "TestAP"},
            {"type": "start_task", "task": "wifi_scan"},
            {"type": "tick", "delta_s": 5},
            {"type": "stop_task", "task": "wifi_scan"},
        ]
        return self.simulation.run_scenario(
            scenario=scenario,
            steps=steps or default_steps,
            chip=chip or self.config.simulation_chip,
            firmware=firmware or self.config.simulation_firmware,
        )

    # -- Cloud / HF access -------------------------------------------------

    def cloud_process(
        self,
        request_type: str,
        payload: Dict[str, Any],
        model_alias: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch a request to the distributed cloud / HF processor."""
        return self.cloud.process(request_type, payload, model_alias)

    # -- Vault helpers -----------------------------------------------------

    def store_api_key(
        self, name: str, value: str, service: str = "generic"
    ) -> None:
        """Store an API key in the secure vault."""
        self.vault.store(name, value, service=service)

    def get_api_key(self, name: str) -> str:
        """Retrieve an API key from the vault."""
        return self.vault.retrieve(name)

    # -- Background tick ---------------------------------------------------

    def tick_background(self, now: Optional[float] = None) -> List[str]:
        """Manually advance the background task scheduler."""
        return self.background.tick(now)

    # -- Status / metrics --------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return a full system status report."""
        uptime = time.time() - self._boot_time
        return {
            "version": self.VERSION,
            "node_id": self.config.node_id,
            "uptime_s": round(uptime, 2),
            "background_status": self.background.status,
            "decisions_made": len(self._decision_log),
            "knowledge": self.knowledge.summary(),
            "engines": self.engines.metrics(),
            "upgrader": self.upgrader.metrics(),
            "council": self.council.metrics(),
            "chaimera": self.chaimera.metrics(),
            "cloud": self.cloud.metrics(),
            "vault": self.vault.metrics(),
            "p2p_network": self.p2p_network.metrics(),
            "background": self.background.metrics(),
        }
