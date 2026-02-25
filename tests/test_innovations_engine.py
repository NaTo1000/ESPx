"""
Tests for the ESPx Innovations Engine.
"""
import pytest
from innovations_engine import InnovationsEngine, FIRMWARE_KNOWLEDGE_BASE
from innovations_engine.engine import _tokenise, FirmwareMatch


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

class TestTokenise:
    def test_lowercases(self):
        assert "hello" in _tokenise("Hello")

    def test_removes_punctuation(self):
        tokens = _tokenise("Wi-Fi, BLE!")
        assert "wi" in tokens or "wifi" in tokens or "ble" in tokens

    def test_removes_stop_words(self):
        tokens = _tokenise("I want to make a sensor")
        assert "i" not in tokens
        assert "want" not in tokens
        assert "to" not in tokens
        assert "a" not in tokens

    def test_empty_string(self):
        assert _tokenise("") == []


# ---------------------------------------------------------------------------
# Knowledge base integrity
# ---------------------------------------------------------------------------

class TestKnowledgeBase:
    def test_is_not_empty(self):
        assert len(FIRMWARE_KNOWLEDGE_BASE) > 0

    def test_required_fields(self):
        required = {"id", "title", "keywords", "description", "firmware", "tags"}
        for entry in FIRMWARE_KNOWLEDGE_BASE:
            missing = required - entry.keys()
            assert not missing, f"Entry '{entry.get('id', '?')}' missing: {missing}"

    def test_firmware_fields(self):
        for entry in FIRMWARE_KNOWLEDGE_BASE:
            fw = entry["firmware"]
            assert "framework" in fw, f"'{entry['id']}' firmware missing 'framework'"
            assert "components" in fw, f"'{entry['id']}' firmware missing 'components'"
            assert "snippet" in fw, f"'{entry['id']}' firmware missing 'snippet'"

    def test_unique_ids(self):
        ids = [e["id"] for e in FIRMWARE_KNOWLEDGE_BASE]
        assert len(ids) == len(set(ids)), "Duplicate IDs found in knowledge base"

    def test_keywords_are_non_empty_list(self):
        for entry in FIRMWARE_KNOWLEDGE_BASE:
            assert isinstance(entry["keywords"], list), f"'{entry['id']}' keywords not a list"
            assert len(entry["keywords"]) > 0, f"'{entry['id']}' has no keywords"


# ---------------------------------------------------------------------------
# Engine search
# ---------------------------------------------------------------------------

class TestEngineSearch:
    def setup_method(self):
        self.engine = InnovationsEngine()

    def test_returns_list(self):
        results = self.engine.search("wifi internet")
        assert isinstance(results, list)

    def test_results_are_firmware_match(self):
        results = self.engine.search("temperature sensor")
        for r in results:
            assert isinstance(r, FirmwareMatch)

    def test_wifi_query_returns_wifi_entry(self):
        results = self.engine.search("connect to wifi and send data to the cloud")
        ids = [r.id for r in results]
        assert any("wifi" in i for i in ids), f"Expected wifi entry, got: {ids}"

    def test_ble_query(self):
        results = self.engine.search("bluetooth low energy sensor notify mobile app")
        ids = [r.id for r in results]
        assert "ble_server" in ids, f"Expected ble_server, got: {ids}"

    def test_mqtt_query(self):
        results = self.engine.search("publish sensor readings to mqtt broker")
        ids = [r.id for r in results]
        assert "mqtt_client" in ids, f"Expected mqtt_client, got: {ids}"

    def test_deep_sleep_query(self):
        results = self.engine.search("battery powered low power deep sleep wake up timer")
        ids = [r.id for r in results]
        assert "deep_sleep" in ids, f"Expected deep_sleep, got: {ids}"

    def test_ota_query(self):
        results = self.engine.search("over the air firmware update remote deploy")
        ids = [r.id for r in results]
        assert "ota_update" in ids, f"Expected ota_update, got: {ids}"

    def test_results_ordered_by_score(self):
        results = self.engine.search("temperature humidity sensor dht22")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_n_respected(self):
        results = self.engine.search("sensor", top_n=3)
        assert len(results) <= 3

    def test_no_results_for_gibberish(self):
        results = self.engine.search("xyzzy quux frob nitz", min_score=0.3)
        assert results == []

    def test_scores_between_0_and_1(self):
        results = self.engine.search("wifi mqtt sensor camera")
        for r in results:
            assert 0.0 <= r.score <= 1.0, f"Score out of range: {r.score}"

    def test_matched_keywords_subset_of_entry_keywords(self):
        results = self.engine.search("wifi station connect internet")
        for r in results:
            entry = self.engine.get_entry(r.id)
            all_kw = entry["keywords"] if entry else []
            for mk in r.matched_keywords:
                assert mk in all_kw, f"Matched keyword '{mk}' not in entry keywords"

    def test_camera_query(self):
        results = self.engine.search("take photo video stream surveillance camera")
        ids = [r.id for r in results]
        assert "camera_vision" in ids, f"Expected camera_vision, got: {ids}"

    def test_lora_query(self):
        results = self.engine.search("long range lorawan low power wide area network")
        ids = [r.id for r in results]
        assert "lora_wan" in ids, f"Expected lora_wan, got: {ids}"

    def test_espnow_query(self):
        results = self.engine.search("esp-now peer to peer direct mesh no router")
        ids = [r.id for r in results]
        assert "espnow" in ids, f"Expected espnow, got: {ids}"

    def test_freertos_query(self):
        results = self.engine.search("multitask concurrent freertos task priority")
        ids = [r.id for r in results]
        assert "freertos_tasks" in ids, f"Expected freertos_tasks, got: {ids}"


# ---------------------------------------------------------------------------
# Engine utility methods
# ---------------------------------------------------------------------------

class TestEngineUtilities:
    def setup_method(self):
        self.engine = InnovationsEngine()

    def test_list_tags_returns_sorted_list(self):
        tags = self.engine.list_tags()
        assert isinstance(tags, list)
        assert tags == sorted(tags)
        assert len(tags) > 0

    def test_list_by_tag_wifi(self):
        entries = self.engine.list_by_tag("wifi")
        assert len(entries) > 0
        for e in entries:
            assert "wifi" in e["tags"]

    def test_list_by_tag_nonexistent(self):
        entries = self.engine.list_by_tag("doesnotexist")
        assert entries == []

    def test_get_entry_by_id(self):
        entry = self.engine.get_entry("wifi_sta")
        assert entry is not None
        assert entry["id"] == "wifi_sta"

    def test_get_entry_missing(self):
        assert self.engine.get_entry("does_not_exist") is None

    def test_custom_knowledge_base(self):
        custom_kb = [
            {
                "id": "custom_entry",
                "title": "Custom Capability",
                "keywords": ["custom", "test"],
                "description": "A custom test entry.",
                "use_cases": ["Testing"],
                "firmware": {
                    "framework": "arduino",
                    "components": ["none"],
                    "snippet": "// custom",
                },
                "tags": ["custom"],
            }
        ]
        engine = InnovationsEngine(knowledge_base=custom_kb)
        results = engine.search("custom test capability")
        assert len(results) == 1
        assert results[0].id == "custom_entry"


# ---------------------------------------------------------------------------
# FirmwareMatch string representation
# ---------------------------------------------------------------------------

class TestFirmwareMatchStr:
    def test_str_contains_title(self):
        engine = InnovationsEngine()
        results = engine.search("wifi connect internet")
        assert len(results) > 0
        text = str(results[0])
        assert results[0].title in text
