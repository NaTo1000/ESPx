"""
ESPiritAi Three-Speed AI Engines

Three tiers of processing speed for different operational requirements:
  - FastEngine:   Real-time device control (microsecond to millisecond latency)
  - MediumEngine: Analysis and monitoring (sub-second latency)
  - SlowEngine:   Deep learning and batch optimisation (seconds to minutes)
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Engine speed tiers
# ---------------------------------------------------------------------------

class EngineSpeed(str, Enum):
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"


# ---------------------------------------------------------------------------
# Task types per engine
# ---------------------------------------------------------------------------

FAST_TASKS = {
    "gpio_toggle",
    "pwm_update",
    "interrupt_handle",
    "motor_command",
    "servo_position",
    "sensor_sample",
    "pid_tick",
    "watchdog_feed",
}

MEDIUM_TASKS = {
    "wifi_scan",
    "telemetry_aggregate",
    "anomaly_detect",
    "dashboard_update",
    "log_analysis",
    "threshold_check",
    "mqtt_publish",
    "ble_scan",
}

SLOW_TASKS = {
    "model_retrain",
    "meta_learning_update",
    "firmware_ota",
    "knowledge_base_update",
    "council_retrain",
    "simulation_run",
    "cloud_sync",
    "batch_analysis",
}


# ---------------------------------------------------------------------------
# Engine result
# ---------------------------------------------------------------------------

@dataclass
class EngineResult:
    """Result returned by any engine tier."""

    engine_speed: EngineSpeed
    task: str
    output: Any
    latency_ms: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Fast Engine
# ---------------------------------------------------------------------------

class FastEngine:
    """
    Real-time engine for time-critical control tasks.

    Designed to respond in under 1 ms (simulated).  Uses a pre-compiled
    lookup table of handlers and avoids dynamic dispatch overhead.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._register_defaults()
        self.metrics: Dict[str, Any] = {
            "tasks_handled": 0,
            "total_latency_ms": 0.0,
        }

    def _register_defaults(self) -> None:
        for task in FAST_TASKS:
            self._handlers[task] = self._default_fast_handler

    def _default_fast_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "executed", "params": params}

    def register_handler(
        self, task: str, handler: Callable[[Dict[str, Any]], Any]
    ) -> None:
        self._handlers[task] = handler

    def execute(self, task: str, params: Optional[Dict[str, Any]] = None) -> EngineResult:
        params = params or {}
        t0 = time.monotonic()
        handler = self._handlers.get(task)
        if handler is None:
            return EngineResult(
                engine_speed=EngineSpeed.FAST,
                task=task,
                output=None,
                latency_ms=0.0,
                success=False,
                metadata={"error": f"Unknown task: {task}"},
            )
        output = handler(params)
        latency = (time.monotonic() - t0) * 1000
        self.metrics["tasks_handled"] += 1
        self.metrics["total_latency_ms"] += latency
        return EngineResult(
            engine_speed=EngineSpeed.FAST,
            task=task,
            output=output,
            latency_ms=round(latency, 4),
            success=True,
        )

    def avg_latency_ms(self) -> float:
        n = self.metrics["tasks_handled"]
        return self.metrics["total_latency_ms"] / n if n else 0.0


# ---------------------------------------------------------------------------
# Medium Engine
# ---------------------------------------------------------------------------

class MediumEngine:
    """
    Analysis engine for monitoring, aggregation, and diagnostic tasks.

    Operates in the sub-second range.  Supports pluggable analyser
    functions and maintains a rolling results buffer.
    """

    BUFFER_SIZE = 500

    def __init__(self) -> None:
        self._analysers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._results: List[EngineResult] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        for task in MEDIUM_TASKS:
            self._analysers[task] = self._default_analyser

    def _default_analyser(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"analysed": True, "keys": list(data.keys()), "summary": str(data)[:120]}

    def register_analyser(
        self, task: str, analyser: Callable[[Dict[str, Any]], Any]
    ) -> None:
        self._analysers[task] = analyser

    def analyse(self, task: str, data: Optional[Dict[str, Any]] = None) -> EngineResult:
        data = data or {}
        t0 = time.monotonic()
        analyser = self._analysers.get(task)
        if analyser is None:
            return EngineResult(
                engine_speed=EngineSpeed.MEDIUM,
                task=task,
                output=None,
                latency_ms=0.0,
                success=False,
                metadata={"error": f"Unknown task: {task}"},
            )
        output = analyser(data)
        latency = (time.monotonic() - t0) * 1000
        result = EngineResult(
            engine_speed=EngineSpeed.MEDIUM,
            task=task,
            output=output,
            latency_ms=round(latency, 4),
            success=True,
        )
        # Rolling buffer
        self._results.append(result)
        if len(self._results) > self.BUFFER_SIZE:
            self._results.pop(0)
        return result

    def recent_results(self, n: int = 10) -> List[EngineResult]:
        return self._results[-n:]

    def stats(self) -> Dict[str, Any]:
        total = len(self._results)
        success = sum(1 for r in self._results if r.success)
        avg_lat = (
            sum(r.latency_ms for r in self._results) / total if total else 0.0
        )
        return {
            "total_tasks": total,
            "success_rate": round(success / total, 4) if total else 0.0,
            "avg_latency_ms": round(avg_lat, 4),
        }


# ---------------------------------------------------------------------------
# Slow Engine
# ---------------------------------------------------------------------------

@dataclass
class SlowJob:
    """A long-running job managed by the slow engine."""

    job_id: str
    task: str
    params: Dict[str, Any]
    status: str = "queued"  # queued | running | done | failed
    result: Any = None
    queued_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None


class SlowEngine:
    """
    Deep-learning / batch-processing engine for long-running operations.

    Jobs are queued and processed synchronously on demand (``process_next``).
    In production, this would be backed by a thread pool or async scheduler.
    """

    def __init__(self) -> None:
        self._queue: List[SlowJob] = []
        self._completed: List[SlowJob] = []
        self._processors: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._job_counter: int = 0
        self._register_defaults()

    def _register_defaults(self) -> None:
        for task in SLOW_TASKS:
            self._processors[task] = self._default_processor

    def _default_processor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate work (no real sleep in tests)
        return {"processed": True, "params_received": list(params.keys())}

    def register_processor(
        self, task: str, processor: Callable[[Dict[str, Any]], Any]
    ) -> None:
        self._processors[task] = processor

    def submit(self, task: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Enqueue a job and return its job_id."""
        self._job_counter += 1
        job_id = f"job_{self._job_counter:05d}"
        job = SlowJob(job_id=job_id, task=task, params=params or {})
        self._queue.append(job)
        return job_id

    def process_next(self) -> Optional[SlowJob]:
        """Process the next queued job and return it."""
        if not self._queue:
            return None
        job = self._queue.pop(0)
        job.status = "running"
        job.started_at = time.time()
        try:
            processor = self._processors.get(job.task, self._default_processor)
            job.result = processor(job.params)
            job.status = "done"
        except Exception as exc:  # pylint: disable=broad-except
            job.result = {"error": str(exc)}
            job.status = "failed"
        job.finished_at = time.time()
        self._completed.append(job)
        return job

    def process_all(self) -> List[SlowJob]:
        """Drain the entire queue and return completed jobs."""
        done = []
        while self._queue:
            job = self.process_next()
            if job:
                done.append(job)
        return done

    def queue_depth(self) -> int:
        return len(self._queue)

    def stats(self) -> Dict[str, Any]:
        total = len(self._completed)
        success = sum(1 for j in self._completed if j.status == "done")
        return {
            "queued": len(self._queue),
            "completed": total,
            "success_rate": round(success / total, 4) if total else 0.0,
        }


# ---------------------------------------------------------------------------
# Three-Speed Engine (unified facade)
# ---------------------------------------------------------------------------

class ThreeSpeedEngine:
    """
    Unified facade for all three engine tiers.

    Routes tasks to the appropriate tier and provides aggregate metrics.
    """

    def __init__(self) -> None:
        self.fast = FastEngine()
        self.medium = MediumEngine()
        self.slow = SlowEngine()

    def dispatch(
        self,
        task: str,
        params: Optional[Dict[str, Any]] = None,
        force_speed: Optional[EngineSpeed] = None,
    ) -> EngineResult:
        """
        Automatically route *task* to the correct engine tier, or use
        *force_speed* to override the routing decision.
        """
        speed = force_speed or self._classify(task)

        if speed == EngineSpeed.FAST:
            return self.fast.execute(task, params)
        if speed == EngineSpeed.MEDIUM:
            return self.medium.analyse(task, params)
        # SLOW — submit and immediately process for synchronous callers
        job_id = self.slow.submit(task, params)
        job = self.slow.process_next()
        return EngineResult(
            engine_speed=EngineSpeed.SLOW,
            task=task,
            output=job.result if job else None,
            latency_ms=0.0,
            success=job.status == "done" if job else False,
            metadata={"job_id": job_id},
        )

    @staticmethod
    def _classify(task: str) -> EngineSpeed:
        if task in FAST_TASKS:
            return EngineSpeed.FAST
        if task in MEDIUM_TASKS:
            return EngineSpeed.MEDIUM
        return EngineSpeed.SLOW

    def metrics(self) -> Dict[str, Any]:
        return {
            "fast": {
                "tasks_handled": self.fast.metrics["tasks_handled"],
                "avg_latency_ms": round(self.fast.avg_latency_ms(), 4),
            },
            "medium": self.medium.stats(),
            "slow": self.slow.stats(),
        }
