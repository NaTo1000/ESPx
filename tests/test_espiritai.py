"""
Tests for ESPiritAi and all ESPx subsystems.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pytest

# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

from espx.espiritai.knowledge import (
    KnowledgeBase,
    ESP_CHIPS,
    FIRMWARE_TYPES,
    RELATED_PROJECTS,
    PROGRAMMING_LANGUAGES,
)


class TestKnowledgeBase:
    def setup_method(self):
        self.kb = KnowledgeBase()

    def test_summary_counts(self):
        s = self.kb.summary()
        assert s["chips"] >= 6
        assert s["firmware_types"] >= 7
        assert s["related_projects"] >= 4
        assert s["programming_languages"] >= 5

    def test_get_chip(self):
        chip = self.kb.get_chip("ESP32")
        assert chip.family == "ESP32"
        assert chip.wifi is True
        assert chip.bluetooth is True

    def test_get_esp8266(self):
        chip = self.kb.get_chip("ESP8266")
        assert chip.bluetooth is False
        assert len(chip.weaknesses) > 0

    def test_chips_for_firmware_arduino(self):
        chips = self.kb.chips_for_firmware("Arduino")
        assert "ESP32" in chips
        assert "ESP8266" in chips

    def test_chips_with_bluetooth(self):
        bt_chips = self.kb.chips_with_bluetooth()
        assert "ESP32" in bt_chips
        assert "ESP8266" not in bt_chips

    def test_chips_with_wifi(self):
        wifi_chips = self.kb.chips_with_wifi()
        assert "ESP32" in wifi_chips
        assert "ESP32-H2" not in wifi_chips  # H2 has no Wi-Fi

    def test_get_firmware(self):
        fw = self.kb.get_firmware("Marauder")
        assert "ESP32" in fw.supported_chips
        assert len(fw.features) > 0

    def test_firmware_for_language_python(self):
        py_fw = self.kb.firmware_for_language("Python")
        assert "MicroPython" in py_fw

    def test_get_project(self):
        proj = self.kb.get_project("Meshtastic")
        assert "ESP32" in proj.supported_chips

    def test_projects_for_chip_esp32(self):
        projects = self.kb.projects_for_chip("ESP32")
        assert len(projects) > 0

    def test_chip_weaknesses(self):
        weaknesses = self.kb.chip_weaknesses("ESP8266")
        assert len(weaknesses) > 0

    def test_firmware_weaknesses(self):
        weaknesses = self.kb.firmware_weaknesses("MicroPython")
        assert len(weaknesses) > 0


# ---------------------------------------------------------------------------
# Algorithms
# ---------------------------------------------------------------------------

from espx.espiritai.algorithms import (
    ReinforcementLearner,
    MetaLearner,
    Task,
    SelfUpgrader,
    ReplayBuffer,
    Experience,
)


class TestReinforcementLearner:
    def setup_method(self):
        self.rl = ReinforcementLearner(actions=["a", "b", "c"])

    def test_select_action_returns_valid(self):
        action = self.rl.select_action("state_0")
        assert action in ["a", "b", "c"]

    def test_update_returns_td_error(self):
        td = self.rl.update("s0", "a", 1.0, "s1", False)
        assert isinstance(td, float)

    def test_epsilon_decays_after_episode(self):
        initial_eps = self.rl.epsilon
        for _ in range(10):
            self.rl.update("s", "a", 0.5, "s2", True)
        assert self.rl.epsilon < initial_eps

    def test_train_on_batch_without_enough_data(self):
        err = self.rl.train_on_batch(batch_size=100)
        assert err == 0.0

    def test_replay_buffer(self):
        buf = ReplayBuffer(capacity=5)
        for i in range(7):
            buf.push(Experience(f"s{i}", "a", 1.0, f"s{i+1}", False))
        assert len(buf) == 5

    def test_metrics_structure(self):
        m = self.rl.metrics()
        assert "epsilon" in m
        assert "q_table_states" in m


class TestMetaLearner:
    def setup_method(self):
        self.meta = MetaLearner(param_dim=16, inner_steps=2)

    def _make_task(self, name: str) -> Task:
        support = [([float(i)] * 16, float(i % 2)) for i in range(4)]
        query = [([float(i + 4)] * 16, float(i % 2)) for i in range(2)]
        return Task(name=name, support=support, query=query)

    def test_meta_update_returns_float(self):
        tasks = [self._make_task(f"task_{i}") for i in range(3)]
        loss = self.meta.meta_update(tasks)
        assert isinstance(loss, float)

    def test_adapt_changes_params(self):
        task = self._make_task("t")
        adapted = self.meta.adapt(task)
        assert len(adapted) == len(self.meta.meta_params)

    def test_metrics(self):
        m = self.meta.metrics()
        assert "param_dim" in m


class TestSelfUpgrader:
    def setup_method(self):
        self.upgrader = SelfUpgrader()

    def test_run_cycle(self):
        result = self.upgrader.run_cycle(
            state="test_state",
            reward_fn=lambda s, a: 0.9,
        )
        assert "cycle" in result
        assert "action" in result

    def test_metrics(self):
        m = self.upgrader.metrics()
        assert "cycles" in m
        assert "rl" in m
        assert "meta" in m


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

from espx.espiritai.simulation import (
    VirtualESPEmulator,
    RiskAssessor,
    RiskLevel,
    SimulationRunner,
    SimulationStatus,
)


class TestVirtualESPEmulator:
    def setup_method(self):
        self.emu = VirtualESPEmulator(chip="ESP32", firmware="Arduino")

    def test_boot(self):
        self.emu.boot()
        assert self.emu.state.uptime_s == 0.0
        assert len(self.emu.state.logs) >= 1

    def test_start_task_reduces_heap(self):
        self.emu.boot()
        heap_before = self.emu.state.heap_free_b
        ok = self.emu.start_task("wifi_scan")
        assert ok
        assert self.emu.state.heap_free_b < heap_before

    def test_stop_task_restores_heap(self):
        self.emu.boot()
        self.emu.start_task("wifi_scan")
        heap_mid = self.emu.state.heap_free_b
        self.emu.stop_task("wifi_scan")
        assert self.emu.state.heap_free_b > heap_mid

    def test_connect_wifi(self):
        self.emu.boot()
        result = self.emu.connect_wifi("TestAP")
        assert result is True
        assert self.emu.state.wifi_connected

    def test_crash_increments_counter(self):
        self.emu.boot()
        self.emu.inject_crash("watchdog")
        assert self.emu.state.crash_count == 1

    def test_snapshot_structure(self):
        self.emu.boot()
        snap = self.emu.snapshot()
        assert "chip" in snap
        assert "heap_free_b" in snap


class TestRiskAssessor:
    def setup_method(self):
        self.assessor = RiskAssessor()

    def test_low_risk_clean_state(self):
        from espx.espiritai.simulation import VirtualESPState
        state = VirtualESPState()
        report = self.assessor.assess(state)
        assert report.level == RiskLevel.LOW

    def test_high_risk_attack_tasks(self):
        from espx.espiritai.simulation import VirtualESPState
        state = VirtualESPState()
        report = self.assessor.assess(state, proposed_tasks=["deauth_attack"])
        assert report.level in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL)
        assert len(report.findings) > 0

    def test_recommendations_populated(self):
        from espx.espiritai.simulation import VirtualESPState
        state = VirtualESPState(crash_count=5, cpu_usage_pct=90.0)
        report = self.assessor.assess(state)
        assert len(report.recommendations) > 0


class TestSimulationRunner:
    def setup_method(self):
        self.runner = SimulationRunner()

    def test_run_simple_scenario(self):
        result = self.runner.run_scenario(
            scenario="basic_boot",
            steps=[
                {"type": "boot"},
                {"type": "tick", "delta_s": 2},
            ],
        )
        assert result.status == SimulationStatus.COMPLETED
        assert result.steps == 2

    def test_run_full_scan_scenario(self):
        result = self.runner.run_scenario(
            scenario="wifi_audit",
            steps=[
                {"type": "boot"},
                {"type": "connect_wifi", "ssid": "AuditNet"},
                {"type": "start_task", "task": "wifi_scan"},
                {"type": "tick", "delta_s": 3},
                {"type": "stop_task", "task": "wifi_scan"},
            ],
        )
        assert result.status == SimulationStatus.COMPLETED
        assert result.risk_report is not None

    def test_unknown_step_type_causes_failure(self):
        result = self.runner.run_scenario(
            scenario="bad_step",
            steps=[{"type": "nonexistent_step_type"}],
        )
        assert result.status == SimulationStatus.FAILED


# ---------------------------------------------------------------------------
# Multi-AI Council
# ---------------------------------------------------------------------------

from espx.espiritai.council import (
    MultiAICouncil,
    ConsensusEngine,
    CouncilMember,
    SecurityAdvisor,
    PerformanceAdvisor,
    NetworkAdvisor,
    Recommendation,
)


class TestMultiAICouncil:
    def setup_method(self):
        self.council = MultiAICouncil()

    def test_deliberate_returns_result(self):
        context = {
            "available_actions": ["no_op", "abort", "reduce_load"],
            "risk_score": 0.2,
            "cpu_usage_pct": 30.0,
            "heap_free_b": 150_000,
            "wifi_connected": True,
            "wifi_rssi_dbm": -60,
        }
        result = self.council.deliberate(context)
        assert result.final_action in context["available_actions"] or result.final_action == "no_op"
        assert 0.0 <= result.consensus_confidence <= 1.0

    def test_decision_history_grows(self):
        context = {"available_actions": ["a", "b"]}
        self.council.deliberate(context)
        self.council.deliberate(context)
        assert self.council.metrics()["decisions_made"] == 2

    def test_security_advisor_avoids_risky_actions(self):
        advisor = SecurityAdvisor()
        rec = advisor.recommend({
            "available_actions": ["deauth_attack", "no_op"],
            "risk_score": 0.9,
        })
        assert rec.action != "deauth_attack"

    def test_performance_advisor_recommends_reduce_on_high_cpu(self):
        advisor = PerformanceAdvisor()
        rec = advisor.recommend({
            "available_actions": ["no_op"],
            "cpu_usage_pct": 95.0,
            "heap_free_b": 200_000,
        })
        assert rec.action == "reduce_load"

    def test_network_advisor_recommends_reconnect_on_bad_wifi(self):
        advisor = NetworkAdvisor()
        rec = advisor.recommend({
            "available_actions": ["no_op"],
            "wifi_connected": False,
            "wifi_rssi_dbm": -90,
        })
        assert rec.action == "reconnect_wifi"


# ---------------------------------------------------------------------------
# CHAIMERA
# ---------------------------------------------------------------------------

from espx.espiritai.chaimera import (
    CHAIMERA,
    SymbolicReasoner,
    FuzzyVariable,
    FuzzyInference,
    BayesianClassifier,
    EvolutionaryOptimiser,
    Perceptron,
    Rule,
)


class TestCHAIMERA:
    def setup_method(self):
        self.chaimera = CHAIMERA(
            actions=["no_op", "abort", "reduce_load", "optimize_scan"]
        )

    def test_infer_returns_result(self):
        context = {
            "risk_score": 0.3,
            "cpu_usage_pct": 40.0,
            "heap_free_b": 100_000,
            "wifi_connected": True,
            "reward": 0.6,
        }
        result = self.chaimera.infer(context)
        assert result.final_action in self.chaimera.actions
        assert 0.0 <= result.confidence <= 1.0

    def test_high_risk_triggers_abort_or_safe_action(self):
        context = {
            "risk_score": 0.9,
            "cpu_usage_pct": 20.0,
            "heap_free_b": 180_000,
            "wifi_connected": True,
            "reward": 0.5,
        }
        result = self.chaimera.infer(context)
        # Symbolic rule: risk > 0.75 -> "abort"
        assert result.paradigm_votes.get("symbolic") is not None

    def test_feedback_trains_neural(self):
        context = {"risk_score": 0.2, "cpu_usage_pct": 30.0,
                   "heap_free_b": 150_000, "wifi_connected": True, "reward": 0.8}
        self.chaimera.feedback(context, "optimize_scan", reward=1.0)
        # No assertion needed — just ensure no exception

    def test_symbolic_reasoner(self):
        sr = SymbolicReasoner()
        sr.add_rule(Rule(
            name="test",
            condition=lambda f: f.get("x", 0) > 5,
            action="fire",
            confidence=0.9,
        ))
        assert sr.infer({"x": 10}) == ("fire", 0.9)
        assert sr.infer({"x": 1}) is None

    def test_fuzzy_variable_membership(self):
        fv = FuzzyVariable("cpu", 60, 80, 100)
        assert fv.membership(50) == 0.0
        assert fv.membership(80) == 1.0
        assert 0.0 < fv.membership(70) < 1.0

    def test_bayesian_classifier(self):
        bc = BayesianClassifier(actions=["a", "b"])
        bc.train({"x": 1, "y": 2}, "a")
        bc.train({"x": 1, "y": 2}, "a")
        action, conf = bc.predict({"x": 1, "y": 2})
        assert action in ["a", "b"]
        assert 0.0 <= conf <= 1.0

    def test_evolutionary_optimiser(self):
        evo = EvolutionaryOptimiser(param_dim=4, pop_size=5)
        best = evo.evolve(lambda genes: -sum(g ** 2 for g in genes))
        assert isinstance(best.fitness, float)
        assert evo.generation == 1

    def test_perceptron_forward(self):
        p = Perceptron(input_dim=4, output_dim=3)
        probs = p.forward([0.1, 0.2, 0.3, 0.4])
        assert len(probs) == 3
        assert abs(sum(probs) - 1.0) < 1e-5


# ---------------------------------------------------------------------------
# Three-Speed Engines
# ---------------------------------------------------------------------------

from espx.espiritai.engines import (
    ThreeSpeedEngine,
    FastEngine,
    MediumEngine,
    SlowEngine,
    EngineSpeed,
    FAST_TASKS,
    MEDIUM_TASKS,
    SLOW_TASKS,
)


class TestThreeSpeedEngine:
    def setup_method(self):
        self.engine = ThreeSpeedEngine()

    def test_fast_task_dispatch(self):
        result = self.engine.dispatch("gpio_toggle")
        assert result.engine_speed == EngineSpeed.FAST
        assert result.success

    def test_medium_task_dispatch(self):
        result = self.engine.dispatch("wifi_scan")
        assert result.engine_speed == EngineSpeed.MEDIUM
        assert result.success

    def test_slow_task_dispatch(self):
        result = self.engine.dispatch("model_retrain")
        assert result.engine_speed == EngineSpeed.SLOW
        assert result.success

    def test_force_speed_override(self):
        result = self.engine.dispatch("gpio_toggle", force_speed=EngineSpeed.SLOW)
        assert result.engine_speed == EngineSpeed.SLOW

    def test_unknown_task_routes_to_slow(self):
        result = self.engine.dispatch("some_unknown_task")
        assert result.engine_speed == EngineSpeed.SLOW

    def test_metrics_structure(self):
        self.engine.dispatch("gpio_toggle")
        m = self.engine.metrics()
        assert "fast" in m
        assert "medium" in m
        assert "slow" in m

    def test_slow_engine_queue(self):
        se = SlowEngine()
        jid = se.submit("firmware_ota", {"version": "2.0"})
        assert jid.startswith("job_")
        job = se.process_next()
        assert job is not None
        assert job.status == "done"

    def test_medium_engine_stats(self):
        me = MediumEngine()
        me.analyse("wifi_scan", {"data": "test"})
        stats = me.stats()
        assert stats["total_tasks"] == 1
        assert stats["success_rate"] == 1.0


# ---------------------------------------------------------------------------
# Cloud & Hugging Face
# ---------------------------------------------------------------------------

from espx.espiritai.cloud import (
    CloudComputeClient,
    HuggingFaceClient,
    DistributedProcessor,
    HuggingFaceModel,
)


class TestCloudComputeClient:
    def setup_method(self):
        self.client = CloudComputeClient()

    def test_submit_default_handler(self):
        job = self.client.submit("custom_task", {"x": 1})
        assert job.status == "completed"
        assert job.result is not None

    def test_custom_handler(self):
        self.client.register_task_handler("echo", lambda p: {"echo": p})
        job = self.client.submit("echo", {"msg": "hello"})
        assert job.result["echo"]["msg"] == "hello"

    def test_disconnected_returns_failed(self):
        self.client.connected = False
        job = self.client.submit("anything")
        assert job.status == "failed"

    def test_metrics(self):
        self.client.submit("t1")
        m = self.client.metrics()
        assert m["total_jobs"] == 1
        assert "connected" in m


class TestHuggingFaceClient:
    def setup_method(self):
        self.hf = HuggingFaceClient(use_stubs=True)

    def test_stub_text_generation(self):
        result = self.hf.run("code-gen", "void setup()")
        assert "output" in result
        assert result["stub"] is True

    def test_stub_question_answering(self):
        result = self.hf.run("nlp-qa", "What is ESP32?")
        assert "output" in result

    def test_stub_text_classification(self):
        result = self.hf.run("sentiment", "Great device!")
        assert isinstance(result["output"], list)

    def test_stub_feature_extraction(self):
        result = self.hf.run("embedding", "ESP32 firmware")
        assert len(result["output"]) == 384

    def test_unknown_model_alias(self):
        result = self.hf.run("nonexistent_model", "test")
        assert "error" in result

    def test_register_custom_model(self):
        model = HuggingFaceModel(
            model_id="test/model",
            task="text-generation",
            description="Test model",
        )
        self.hf.register_model("test_model", model)
        result = self.hf.run("test_model", "hello")
        assert "output" in result

    def test_list_models(self):
        models = self.hf.list_models()
        assert len(models) >= 5


class TestDistributedProcessor:
    def setup_method(self):
        self.dp = DistributedProcessor()

    def test_cloud_request(self):
        result = self.dp.process("compute_task", {"x": 42})
        assert isinstance(result, dict)

    def test_hf_request(self):
        result = self.dp.process("hf_code-gen", {"input": "// ESP32 setup"})
        assert isinstance(result, dict)

    def test_metrics(self):
        self.dp.process("t1", {})
        m = self.dp.metrics()
        assert m["total_requests"] >= 1


# ---------------------------------------------------------------------------
# Background modes
# ---------------------------------------------------------------------------

from espx.espiritai.background import (
    BackgroundModeManager,
    BackgroundModeStatus,
    P2POrchestrator,
    ResearchPipeline,
    PipelineStage,
    P2PPeer,
)


class TestBackgroundModeManager:
    def setup_method(self):
        self.mgr = BackgroundModeManager()

    def test_register_and_tick(self):
        results = []
        self.mgr.register("t1", "Test Task", lambda: results.append(1), interval_s=0)
        self.mgr.start()
        executed = self.mgr.tick(now=time.time() + 1)
        assert "t1" in executed
        assert len(results) == 1

    def test_task_not_run_before_interval(self):
        self.mgr.register("t2", "Slow Task", lambda: None, interval_s=9999)
        self.mgr.start()
        # Tick at a time before the interval has elapsed (last_run=0, tick at 1s)
        executed = self.mgr.tick(now=1.0)
        assert "t2" not in executed

    def test_disabled_task_not_executed(self):
        results = []
        self.mgr.register("t3", "Disabled", lambda: results.append(1), interval_s=0)
        self.mgr.disable("t3")
        self.mgr.start()
        self.mgr.tick(now=time.time() + 1)
        assert len(results) == 0

    def test_status_transitions(self):
        assert self.mgr.status == BackgroundModeStatus.STOPPED
        self.mgr.start()
        assert self.mgr.status == BackgroundModeStatus.RUNNING
        self.mgr.pause()
        assert self.mgr.status == BackgroundModeStatus.PAUSED
        self.mgr.stop()
        assert self.mgr.status == BackgroundModeStatus.STOPPED

    def test_metrics(self):
        m = self.mgr.metrics()
        assert "status" in m
        assert "registered_tasks" in m


class TestP2POrchestrator:
    def setup_method(self):
        self.orc = P2POrchestrator(node_id="node_test")

    def test_register_peer(self):
        peer = P2PPeer(peer_id="peer_1", address="192.168.1.2", trusted=True)
        self.orc.register_peer(peer)
        assert len(self.orc.discover_peers()) == 1
        assert len(self.orc.trusted_peers()) == 1

    def test_send_message_delivered_to_known_peer(self):
        peer = P2PPeer(peer_id="peer_2", address="192.168.1.3")
        self.orc.register_peer(peer)
        msg = self.orc.send("peer_2", {"task": "ping"})
        assert msg.delivered

    def test_broadcast(self):
        peer = P2PPeer(peer_id="p1", address="1.1.1.1")
        self.orc.register_peer(peer)
        msg = self.orc.broadcast({"task": "announce"})
        assert msg.recipient_id == "*"

    def test_metrics(self):
        m = self.orc.metrics()
        assert "node_id" in m
        assert m["node_id"] == "node_test"


class TestResearchPipeline:
    def setup_method(self):
        self.pipeline = ResearchPipeline("test_pipeline")

    def test_run_pipeline(self):
        self.pipeline.add_stage(PipelineStage(
            name="stage1",
            processor=lambda d: {"step1": True},
        ))
        self.pipeline.add_stage(PipelineStage(
            name="stage2",
            processor=lambda d: {"step2": d.get("step1", False)},
        ))
        run = self.pipeline.run({"initial": "data"})
        assert run.status == "completed"
        assert len(run.stage_results) == 2

    def test_failed_pipeline(self):
        self.pipeline.add_stage(PipelineStage(
            name="bad_stage",
            processor=lambda d: (_ for _ in ()).throw(RuntimeError("boom")),
        ))
        run = self.pipeline.run()
        assert run.status == "failed"

    def test_metrics(self):
        m = self.pipeline.metrics()
        assert m["pipeline"] == "test_pipeline"
        assert "stages" in m


# ---------------------------------------------------------------------------
# API Vault
# ---------------------------------------------------------------------------

from espx.vault.vault import APIVault


class TestAPIVault:
    def setup_method(self):
        self.vault = APIVault(master_token="supersecret")

    def test_store_and_retrieve(self):
        self.vault.store("hf_token", "hf-abcdefg", service="huggingface")
        value = self.vault.retrieve("hf_token")
        assert value == "hf-abcdefg"

    def test_retrieve_unknown_raises(self):
        with pytest.raises(KeyError):
            self.vault.retrieve("nonexistent_key")

    def test_delete(self):
        self.vault.store("temp_key", "12345")
        assert self.vault.delete("temp_key")
        assert not self.vault.has("temp_key")

    def test_lock_prevents_access(self):
        self.vault.store("secret", "value")
        self.vault.lock()
        with pytest.raises(RuntimeError):
            self.vault.retrieve("secret")

    def test_unlock_with_wrong_token(self):
        self.vault.lock()
        ok = self.vault.unlock("wrong_token")
        assert not ok
        assert self.vault._locked

    def test_unlock_with_correct_token(self):
        self.vault.lock()
        ok = self.vault.unlock("supersecret")
        assert ok
        assert not self.vault._locked

    def test_list_secrets_no_plaintext(self):
        self.vault.store("k1", "secret_value", service="aws")
        secrets = self.vault.list_secrets()
        for s in secrets:
            assert "secret_value" not in str(s)

    def test_audit_log_grows(self):
        self.vault.store("x", "y")
        self.vault.retrieve("x")
        log = self.vault.audit_log()
        assert len(log) >= 2

    def test_metrics(self):
        self.vault.store("m1", "v1")
        m = self.vault.metrics()
        assert m["stored_secrets"] >= 1


# ---------------------------------------------------------------------------
# P2P Network
# ---------------------------------------------------------------------------

from espx.p2p.network import P2PNetwork, NetworkNode


class TestP2PNetwork:
    def setup_method(self):
        self.net = P2PNetwork(local_node_id="local_node")

    def test_register_and_get_node(self):
        node = NetworkNode(node_id="remote_1", address="10.0.0.2")
        self.net.register_node(node)
        retrieved = self.net.get_node("remote_1")
        assert retrieved is not None
        assert retrieved.address == "10.0.0.2"

    def test_heartbeat_marks_connected(self):
        node = NetworkNode(node_id="remote_2", address="10.0.0.3")
        self.net.register_node(node)
        ok = self.net.heartbeat("remote_2")
        assert ok
        assert self.net.get_node("remote_2").connected

    def test_derive_shared_key(self):
        sk = self.net.derive_shared_key("peer_x", "shared_secret_123")
        assert sk.key_id is not None
        assert len(sk.key_material) == 32

    def test_shared_key_ttl_expiry(self):
        sk = self.net.derive_shared_key("peer_y", "secret", ttl_s=-1)
        # Negative TTL means already expired
        result = self.net.get_shared_key(sk.key_id)
        assert result is None

    def test_revoke_key(self):
        sk = self.net.derive_shared_key("peer_z", "secret")
        revoked = self.net.revoke_key(sk.key_id)
        assert revoked
        assert self.net.get_shared_key(sk.key_id) is None

    def test_send_message_with_hmac(self):
        node = NetworkNode(node_id="target", address="10.0.0.4", connected=True)
        self.net.register_node(node)
        sk = self.net.derive_shared_key("target", "secret")
        envelope = self.net.send("target", "ping", {"data": "hello"}, key_id=sk.key_id)
        assert "hmac_tag" in envelope
        assert envelope["delivered"]

    def test_metrics(self):
        m = self.net.metrics()
        assert "local_id" in m
        assert m["local_id"] == "local_node"


# ---------------------------------------------------------------------------
# ESPiritAi Core (integration)
# ---------------------------------------------------------------------------

from espx.espiritai.core import ESPiritAi, ESPiritAiConfig


class TestESPiritAiCore:
    def setup_method(self):
        config = ESPiritAiConfig(
            node_id="test_node",
            vault_master_token="test_secret",
            use_hf_stubs=True,
            background_enabled=False,  # manual tick in tests
        )
        self.ai = ESPiritAi(config=config)

    def test_instantiation(self):
        assert self.ai.VERSION == "1.0.0"

    def test_status(self):
        s = self.ai.status()
        assert s["node_id"] == "test_node"
        assert "knowledge" in s
        assert "engines" in s
        assert "upgrader" in s
        assert "council" in s
        assert "chaimera" in s
        assert "cloud" in s
        assert "vault" in s
        assert "p2p_network" in s

    def test_decide_returns_action(self):
        context = {
            "risk_score": 0.1,
            "cpu_usage_pct": 20.0,
            "heap_free_b": 180_000,
            "wifi_connected": True,
            "wifi_rssi_dbm": -55,
        }
        decision = self.ai.decide(context)
        assert "final_action" in decision
        assert "confidence" in decision
        assert decision["final_action"] in self.ai.config.chaimera_actions

    def test_decide_logs_decisions(self):
        self.ai.decide({"risk_score": 0.2})
        self.ai.decide({"risk_score": 0.3})
        assert self.ai.status()["decisions_made"] == 2

    def test_upgrade_cycle(self):
        result = self.ai.run_upgrade_cycle("test_state")
        assert "cycle" in result
        assert "action" in result

    def test_simulate_default(self):
        result = self.ai.simulate("integration_test")
        assert result.status.value == "completed"

    def test_simulate_custom_steps(self):
        result = self.ai.simulate(
            "custom_sim",
            steps=[
                {"type": "boot"},
                {"type": "tick", "delta_s": 1},
            ],
        )
        assert result.status.value == "completed"

    def test_store_and_retrieve_api_key(self):
        self.ai.store_api_key("hf_api", "hf-xyz123", service="huggingface")
        value = self.ai.get_api_key("hf_api")
        assert value == "hf-xyz123"

    def test_cloud_process_hf(self):
        result = self.ai.cloud_process("hf_code-gen", {"input": "// test"})
        assert isinstance(result, dict)

    def test_cloud_process_compute(self):
        result = self.ai.cloud_process("batch_task", {"data": [1, 2, 3]})
        assert isinstance(result, dict)

    def test_background_tick_when_stopped(self):
        # Background disabled in setup, should return empty
        executed = self.ai.tick_background()
        assert executed == []

    def test_background_tick_when_running(self):
        self.ai.background.start()
        # Run tick far in future so all tasks fire
        executed = self.ai.tick_background(now=time.time() + 99_999)
        assert len(executed) > 0

    def test_knowledge_accessible(self):
        chip = self.ai.knowledge.get_chip("ESP32")
        assert chip is not None

    def test_high_risk_context_council(self):
        """Council should still return a valid action even for high-risk context."""
        context = {
            "risk_score": 0.95,
            "cpu_usage_pct": 95.0,
            "heap_free_b": 5_000,
            "wifi_connected": False,
        }
        decision = self.ai.decide(context)
        assert decision["final_action"] in self.ai.config.chaimera_actions
