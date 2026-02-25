"""
ESPiritAi Background Modes

Coordinated background orchestration across P2P networks, research
pipelines, and system components.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BackgroundModeStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


# ---------------------------------------------------------------------------
# P2P Orchestrator
# ---------------------------------------------------------------------------

@dataclass
class P2PPeer:
    """Represents a peer in the P2P orchestration network."""

    peer_id: str
    address: str
    capabilities: List[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)
    trusted: bool = False


@dataclass
class P2PMessage:
    """A message routed across the P2P network."""

    message_id: str
    sender_id: str
    recipient_id: str  # "*" for broadcast
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    delivered: bool = False


class P2POrchestrator:
    """
    Manages peer discovery, message routing, and coordinated task
    distribution across a P2P network of ESPx / ESPiritAi nodes.
    """

    def __init__(self, node_id: Optional[str] = None) -> None:
        self.node_id: str = node_id or f"node_{uuid.uuid4().hex[:8]}"
        self._peers: Dict[str, P2PPeer] = {}
        self._inbox: List[P2PMessage] = []
        self._sent: List[P2PMessage] = []
        self._task_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    # -- Peer management ---------------------------------------------------

    def register_peer(self, peer: P2PPeer) -> None:
        self._peers[peer.peer_id] = peer

    def remove_peer(self, peer_id: str) -> bool:
        return self._peers.pop(peer_id, None) is not None

    def discover_peers(self) -> List[P2PPeer]:
        """Return all currently known peers (simulated discovery)."""
        return list(self._peers.values())

    def trusted_peers(self) -> List[P2PPeer]:
        return [p for p in self._peers.values() if p.trusted]

    # -- Messaging ---------------------------------------------------------

    def send(
        self,
        recipient_id: str,
        payload: Dict[str, Any],
    ) -> P2PMessage:
        msg = P2PMessage(
            message_id=uuid.uuid4().hex[:12],
            sender_id=self.node_id,
            recipient_id=recipient_id,
            payload=payload,
        )
        self._sent.append(msg)
        # Simulate delivery for in-process peers
        if recipient_id == "*":
            for peer_id in self._peers:
                msg.delivered = True
        elif recipient_id in self._peers:
            msg.delivered = True
        return msg

    def broadcast(self, payload: Dict[str, Any]) -> P2PMessage:
        return self.send("*", payload)

    def receive(self, message: P2PMessage) -> None:
        """Deliver an incoming message to this node's inbox."""
        self._inbox.append(message)

    def process_inbox(self) -> List[Any]:
        """Process all queued inbox messages and return results."""
        results = []
        while self._inbox:
            msg = self._inbox.pop(0)
            task = msg.payload.get("task")
            handler = self._task_handlers.get(task)
            if handler:
                results.append(handler(msg.payload))
        return results

    def register_task_handler(
        self, task: str, handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        self._task_handlers[task] = handler

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "peers": len(self._peers),
            "trusted_peers": len(self.trusted_peers()),
            "messages_sent": len(self._sent),
            "inbox_pending": len(self._inbox),
        }


# ---------------------------------------------------------------------------
# Research Pipeline
# ---------------------------------------------------------------------------

@dataclass
class PipelineStage:
    """A single stage in a research pipeline."""

    name: str
    processor: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str = ""


@dataclass
class PipelineRun:
    """Record of a single pipeline execution."""

    run_id: str
    pipeline_name: str
    status: str  # "running" | "completed" | "failed"
    stage_results: List[Dict[str, Any]] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None


class ResearchPipeline:
    """
    Sequential processing pipeline for ESPiritAi research and analysis
    workflows (e.g., firmware analysis, threat research, model evaluation).
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.stages: List[PipelineStage] = []
        self._runs: List[PipelineRun] = []

    def add_stage(self, stage: PipelineStage) -> None:
        self.stages.append(stage)

    def run(self, initial_data: Optional[Dict[str, Any]] = None) -> PipelineRun:
        """Execute all pipeline stages sequentially."""
        run = PipelineRun(
            run_id=uuid.uuid4().hex[:10],
            pipeline_name=self.name,
            status="running",
        )
        self._runs.append(run)
        data = initial_data or {}
        try:
            for stage in self.stages:
                result = stage.processor(data)
                run.stage_results.append(
                    {"stage": stage.name, "output": result}
                )
                data = {**data, **result}
            run.status = "completed"
        except Exception as exc:  # pylint: disable=broad-except
            run.status = "failed"
            run.stage_results.append({"stage": "error", "output": str(exc)})
        run.finished_at = time.time()
        return run

    def history(self) -> List[PipelineRun]:
        return list(self._runs)

    def metrics(self) -> Dict[str, Any]:
        total = len(self._runs)
        success = sum(1 for r in self._runs if r.status == "completed")
        return {
            "pipeline": self.name,
            "stages": len(self.stages),
            "total_runs": total,
            "success_rate": round(success / total, 4) if total else 0.0,
        }


# ---------------------------------------------------------------------------
# Background Mode Manager
# ---------------------------------------------------------------------------

@dataclass
class BackgroundTask:
    """A periodic background task."""

    task_id: str
    name: str
    handler: Callable[[], Any]
    interval_s: float
    last_run: float = 0.0
    run_count: int = 0
    enabled: bool = True


class BackgroundModeManager:
    """
    Manages background operational modes for ESPiritAi:
      - Periodic orchestration tasks
      - P2P heartbeat / discovery
      - Research pipeline scheduling
      - System component health checks

    The manager maintains a registry of BackgroundTasks and provides a
    ``tick`` method that fires any task whose interval has elapsed.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, BackgroundTask] = {}
        self.status: BackgroundModeStatus = BackgroundModeStatus.STOPPED
        self._tick_count: int = 0
        self._run_log: List[Dict[str, Any]] = []

    # -- Task registration -------------------------------------------------

    def register(
        self,
        task_id: str,
        name: str,
        handler: Callable[[], Any],
        interval_s: float = 60.0,
    ) -> None:
        self._tasks[task_id] = BackgroundTask(
            task_id=task_id,
            name=name,
            handler=handler,
            interval_s=interval_s,
        )

    def enable(self, task_id: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].enabled = True

    def disable(self, task_id: str) -> None:
        if task_id in self._tasks:
            self._tasks[task_id].enabled = False

    # -- Lifecycle ---------------------------------------------------------

    def start(self) -> None:
        self.status = BackgroundModeStatus.RUNNING

    def pause(self) -> None:
        self.status = BackgroundModeStatus.PAUSED

    def stop(self) -> None:
        self.status = BackgroundModeStatus.STOPPED

    # -- Execution ---------------------------------------------------------

    def tick(self, now: Optional[float] = None) -> List[str]:
        """
        Check all registered tasks and run those whose interval has
        elapsed.  Returns the list of task IDs that were executed.
        """
        if self.status != BackgroundModeStatus.RUNNING:
            return []
        now = now or time.time()
        self._tick_count += 1
        executed: List[str] = []
        for task in self._tasks.values():
            if not task.enabled:
                continue
            if now - task.last_run >= task.interval_s:
                try:
                    result = task.handler()
                    task.run_count += 1
                    task.last_run = now
                    self._run_log.append(
                        {"task_id": task.task_id, "tick": self._tick_count,
                         "success": True}
                    )
                    executed.append(task.task_id)
                except Exception as exc:  # pylint: disable=broad-except
                    self._run_log.append(
                        {"task_id": task.task_id, "tick": self._tick_count,
                         "success": False, "error": str(exc)}
                    )
        return executed

    # -- Metrics -----------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "registered_tasks": len(self._tasks),
            "tick_count": self._tick_count,
            "run_log_entries": len(self._run_log),
            "tasks": [
                {
                    "id": t.task_id,
                    "name": t.name,
                    "interval_s": t.interval_s,
                    "run_count": t.run_count,
                    "enabled": t.enabled,
                }
                for t in self._tasks.values()
            ],
        }
