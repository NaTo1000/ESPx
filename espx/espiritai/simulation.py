"""
ESPiritAi Simulation Runners

Virtual ESP hardware emulation and risk assessment for testing in
sensitive environments without requiring physical hardware.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SimulationStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Virtual ESP Hardware State
# ---------------------------------------------------------------------------

@dataclass
class VirtualESPState:
    """Mutable state for a virtual ESP device."""

    chip: str = "ESP32"
    firmware: str = "Arduino"
    uptime_s: float = 0.0
    cpu_usage_pct: float = 0.0
    heap_free_b: int = 200_000
    wifi_connected: bool = False
    wifi_rssi_dbm: int = -70
    gpio_states: Dict[int, bool] = field(default_factory=dict)
    running_tasks: List[str] = field(default_factory=list)
    crash_count: int = 0
    ota_in_progress: bool = False
    logs: List[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        entry = f"[t={self.uptime_s:.2f}s] {message}"
        self.logs.append(entry)


# ---------------------------------------------------------------------------
# Virtual ESP Emulator
# ---------------------------------------------------------------------------

class VirtualESPEmulator:
    """
    Emulates an ESP32/ESP8266 device in software for safe simulation of
    firmware behaviour, network interactions, and failure modes.
    """

    # Simulated heap reduction per task (bytes)
    _TASK_HEAP_COST: Dict[str, int] = {
        "wifi_scan": 8_000,
        "ble_scan": 6_000,
        "deauth_attack": 10_000,
        "packet_capture": 12_000,
        "ota_update": 40_000,
        "meshtastic_mesh": 15_000,
        "sensor_read": 1_000,
        "web_server": 20_000,
    }

    def __init__(self, chip: str = "ESP32", firmware: str = "Arduino") -> None:
        self.state = VirtualESPState(chip=chip, firmware=firmware)
        self._tick_rate_hz: float = 1.0  # simulated ticks per second

    # -- Lifecycle ---------------------------------------------------------

    def boot(self) -> None:
        """Simulate device boot sequence."""
        self.state.uptime_s = 0.0
        self.state.cpu_usage_pct = random.uniform(5.0, 15.0)
        self.state.heap_free_b = 200_000
        self.state.wifi_connected = False
        self.state.running_tasks.clear()
        self.state.logs.clear()
        self.state.log(f"Boot: {self.state.chip} running {self.state.firmware}")

    def tick(self, delta_s: float = 1.0) -> None:
        """Advance simulation time by *delta_s* seconds."""
        self.state.uptime_s += delta_s
        # Simulate slight CPU drift
        self.state.cpu_usage_pct = min(
            100.0,
            self.state.cpu_usage_pct + random.gauss(0, 1.0),
        )
        self.state.cpu_usage_pct = max(0.0, self.state.cpu_usage_pct)

    # -- Task simulation ---------------------------------------------------

    def start_task(self, task_name: str) -> bool:
        """
        Start a named task.  Returns False if heap is insufficient.
        """
        cost = self._TASK_HEAP_COST.get(task_name, 2_000)
        if self.state.heap_free_b < cost:
            self.state.log(f"WARN: Not enough heap for task '{task_name}'")
            return False
        self.state.heap_free_b -= cost
        self.state.cpu_usage_pct = min(100.0, self.state.cpu_usage_pct + 10.0)
        self.state.running_tasks.append(task_name)
        self.state.log(f"Task started: {task_name}")
        return True

    def stop_task(self, task_name: str) -> bool:
        """Stop a running task and reclaim heap."""
        if task_name not in self.state.running_tasks:
            return False
        cost = self._TASK_HEAP_COST.get(task_name, 2_000)
        self.state.heap_free_b += cost
        self.state.cpu_usage_pct = max(0.0, self.state.cpu_usage_pct - 10.0)
        self.state.running_tasks.remove(task_name)
        self.state.log(f"Task stopped: {task_name}")
        return True

    # -- Network simulation ------------------------------------------------

    def connect_wifi(self, ssid: str = "TestAP") -> bool:
        """Simulate Wi-Fi association."""
        self.state.wifi_connected = True
        self.state.wifi_rssi_dbm = random.randint(-80, -40)
        self.state.log(f"Wi-Fi connected: {ssid} RSSI={self.state.wifi_rssi_dbm} dBm")
        return True

    def disconnect_wifi(self) -> None:
        self.state.wifi_connected = False
        self.state.log("Wi-Fi disconnected")

    # -- Crash simulation --------------------------------------------------

    def inject_crash(self, reason: str = "panic") -> None:
        """Simulate a firmware crash and auto-reboot."""
        self.state.crash_count += 1
        self.state.log(f"CRASH: {reason} (count={self.state.crash_count})")
        self.boot()

    # -- Snapshot ----------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        return {
            "chip": self.state.chip,
            "firmware": self.state.firmware,
            "uptime_s": round(self.state.uptime_s, 2),
            "cpu_usage_pct": round(self.state.cpu_usage_pct, 1),
            "heap_free_b": self.state.heap_free_b,
            "wifi_connected": self.state.wifi_connected,
            "wifi_rssi_dbm": self.state.wifi_rssi_dbm,
            "running_tasks": list(self.state.running_tasks),
            "crash_count": self.state.crash_count,
            "log_lines": len(self.state.logs),
        }


# ---------------------------------------------------------------------------
# Risk Assessor
# ---------------------------------------------------------------------------

@dataclass
class RiskReport:
    """Result of a risk assessment."""

    level: RiskLevel
    score: float  # 0.0 – 1.0
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class RiskAssessor:
    """
    Evaluates operational risk for proposed actions or configurations in
    the ESPx environment.
    """

    # Risk weights per factor
    _WEIGHTS: Dict[str, float] = {
        "heap_low": 0.25,
        "cpu_high": 0.20,
        "wifi_open": 0.15,
        "attack_tasks": 0.30,
        "crash_history": 0.10,
    }

    _ATTACK_TASKS = {"deauth_attack", "packet_capture", "evil_portal", "beacon_spam"}

    def assess(
        self,
        state: VirtualESPState,
        proposed_tasks: Optional[List[str]] = None,
    ) -> RiskReport:
        """Compute a risk report for the current/proposed state."""
        proposed_tasks = proposed_tasks or []
        score = 0.0
        findings: List[str] = []
        recommendations: List[str] = []

        # Heap pressure
        heap_ratio = 1.0 - (state.heap_free_b / 200_000)
        if heap_ratio > 0.7:
            score += self._WEIGHTS["heap_low"] * heap_ratio
            findings.append(
                f"Low heap: {state.heap_free_b} bytes free ({heap_ratio*100:.0f}% used)"
            )
            recommendations.append("Reduce active tasks or increase PSRAM usage.")

        # CPU pressure
        if state.cpu_usage_pct > 80:
            cpu_factor = (state.cpu_usage_pct - 80) / 20
            score += self._WEIGHTS["cpu_high"] * cpu_factor
            findings.append(f"High CPU usage: {state.cpu_usage_pct:.1f}%")
            recommendations.append("Offload tasks or reduce polling frequency.")

        # Open Wi-Fi (no encryption indicator — RSSI too strong = broadcast env)
        if state.wifi_connected and state.wifi_rssi_dbm > -50:
            score += self._WEIGHTS["wifi_open"] * 0.5
            findings.append("Strong open Wi-Fi signal detected.")
            recommendations.append("Verify network encryption (WPA2/WPA3).")

        # Attack tasks
        attack_present = [t for t in proposed_tasks if t in self._ATTACK_TASKS]
        if attack_present:
            score += self._WEIGHTS["attack_tasks"]
            findings.append(
                f"Potentially sensitive tasks proposed: {attack_present}"
            )
            recommendations.append(
                "Ensure proper authorisation before running attack/audit tasks."
            )

        # Crash history
        if state.crash_count > 3:
            crash_factor = min(1.0, state.crash_count / 10)
            score += self._WEIGHTS["crash_history"] * crash_factor
            findings.append(f"Elevated crash count: {state.crash_count}")
            recommendations.append("Investigate crash logs before proceeding.")

        score = min(1.0, score)
        level = self._score_to_level(score)
        return RiskReport(level=level, score=round(score, 3), findings=findings,
                          recommendations=recommendations)

    @staticmethod
    def _score_to_level(score: float) -> RiskLevel:
        if score < 0.25:
            return RiskLevel.LOW
        if score < 0.5:
            return RiskLevel.MEDIUM
        if score < 0.75:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL


# ---------------------------------------------------------------------------
# Simulation Runner
# ---------------------------------------------------------------------------

@dataclass
class SimulationResult:
    """Result of a simulation run."""

    scenario: str
    status: SimulationStatus
    steps: int
    duration_s: float
    final_snapshot: Dict[str, Any]
    risk_report: Optional[RiskReport]
    logs: List[str] = field(default_factory=list)


class SimulationRunner:
    """
    Orchestrates multi-step simulation scenarios on a VirtualESPEmulator
    with optional risk assessment at each step.
    """

    def __init__(self) -> None:
        self.emulator = VirtualESPEmulator()
        self.risk_assessor = RiskAssessor()
        self.results: List[SimulationResult] = []

    def run_scenario(
        self,
        scenario: str,
        steps: List[Dict[str, Any]],
        chip: str = "ESP32",
        firmware: str = "Arduino",
        assess_risk: bool = True,
    ) -> SimulationResult:
        """
        Execute a named scenario as a list of step dicts.

        Each step is a dict with a 'type' key and optional params:
          {"type": "boot"}
          {"type": "tick", "delta_s": 5}
          {"type": "start_task", "task": "wifi_scan"}
          {"type": "stop_task", "task": "wifi_scan"}
          {"type": "connect_wifi", "ssid": "MyAP"}
          {"type": "disconnect_wifi"}
          {"type": "inject_crash", "reason": "watchdog"}
        """
        start = time.monotonic()
        self.emulator = VirtualESPEmulator(chip=chip, firmware=firmware)
        status = SimulationStatus.RUNNING

        try:
            for step in steps:
                self._execute_step(step)
            status = SimulationStatus.COMPLETED
        except Exception as exc:  # pylint: disable=broad-except
            self.emulator.state.log(f"Simulation error: {exc}")
            status = SimulationStatus.FAILED

        duration = time.monotonic() - start
        snapshot = self.emulator.snapshot()
        risk = (
            self.risk_assessor.assess(self.emulator.state)
            if assess_risk
            else None
        )

        result = SimulationResult(
            scenario=scenario,
            status=status,
            steps=len(steps),
            duration_s=round(duration, 4),
            final_snapshot=snapshot,
            risk_report=risk,
            logs=list(self.emulator.state.logs),
        )
        self.results.append(result)
        return result

    def _execute_step(self, step: Dict[str, Any]) -> None:
        step_type = step.get("type", "")
        if step_type == "boot":
            self.emulator.boot()
        elif step_type == "tick":
            self.emulator.tick(step.get("delta_s", 1.0))
        elif step_type == "start_task":
            self.emulator.start_task(step["task"])
        elif step_type == "stop_task":
            self.emulator.stop_task(step["task"])
        elif step_type == "connect_wifi":
            self.emulator.connect_wifi(step.get("ssid", "TestAP"))
        elif step_type == "disconnect_wifi":
            self.emulator.disconnect_wifi()
        elif step_type == "inject_crash":
            self.emulator.inject_crash(step.get("reason", "panic"))
        else:
            raise ValueError(f"Unknown simulation step type: '{step_type}'")
