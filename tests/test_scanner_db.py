"""
Unit tests for desktop/scanner_db.py
=====================================
Run with:  python -m pytest tests/ -v
       or: python -m unittest discover tests
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

# Make desktop/ importable without installing anything
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "desktop"))

import scanner_db  # noqa: E402  (imported after path manipulation)


class TestScannerDb(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp  = tempfile.TemporaryDirectory()
        self._db   = Path(self._tmp.name) / "test_scans.db"
        self._patcher = patch.object(scanner_db, "DB_PATH", self._db)
        self._patcher.start()
        scanner_db.init_db()

    def tearDown(self) -> None:
        self._patcher.stop()
        self._tmp.cleanup()

    # ── Schema ────────────────────────────────────────────────────────────────
    def test_init_db_creates_tables(self) -> None:
        with scanner_db.get_connection() as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        self.assertIn("scan_sessions", tables)
        self.assertIn("wifi_networks", tables)
        self.assertIn("ble_devices",   tables)

    def test_init_db_is_idempotent(self) -> None:
        """Calling init_db twice must not raise or duplicate schema objects."""
        scanner_db.init_db()  # second call
        self.test_init_db_creates_tables()

    # ── WiFi storage ──────────────────────────────────────────────────────────
    def test_store_wifi_returns_session_id(self) -> None:
        sid = scanner_db.store_wifi_scan([])
        self.assertIsInstance(sid, int)
        self.assertGreater(sid, 0)

    def test_store_and_retrieve_wifi(self) -> None:
        networks = [
            {
                "ssid": "HomeNet", "bssid": "AA:BB:CC:DD:EE:FF",
                "rssi": -55, "channel": 6, "encryption": "WPA2",
                "band": "2.4GHz", "frequency_mhz": 2437,
            },
            {
                "ssid": "OfficeNet", "bssid": "11:22:33:44:55:66",
                "rssi": -70, "channel": 36, "encryption": "WPA2",
                "band": "5GHz",
            },
        ]
        scanner_db.store_wifi_scan(networks)
        rows = scanner_db.get_wifi_history()
        self.assertEqual(len(rows), 2)
        ssids = {r["ssid"] for r in rows}
        self.assertIn("HomeNet",   ssids)
        self.assertIn("OfficeNet", ssids)

    def test_wifi_frequency_stored(self) -> None:
        scanner_db.store_wifi_scan([
            {"ssid": "X", "bssid": "00:00:00:00:00:01",
             "rssi": -60, "channel": 1, "band": "2.4GHz", "frequency_mhz": 2412}
        ])
        rows = scanner_db.get_wifi_history()
        self.assertEqual(rows[0]["frequency"], 2412)

    def test_empty_wifi_scan_stored(self) -> None:
        sid = scanner_db.store_wifi_scan([])
        self.assertGreater(sid, 0)
        self.assertEqual(len(scanner_db.get_wifi_history()), 0)

    # ── BLE storage ───────────────────────────────────────────────────────────
    def test_store_ble_returns_session_id(self) -> None:
        sid = scanner_db.store_ble_scan([])
        self.assertIsInstance(sid, int)
        self.assertGreater(sid, 0)

    def test_store_and_retrieve_ble(self) -> None:
        devices = [
            {
                "name": "Headphones", "address": "AA:BB:CC:DD:EE:01",
                "rssi": -60, "manufacturer_data": "4C00", "service_uuid": "",
            },
            {
                "name": "", "address": "AA:BB:CC:DD:EE:02",
                "rssi": -80, "manufacturer_data": "", "service_uuid": "",
            },
        ]
        scanner_db.store_ble_scan(devices)
        rows = scanner_db.get_ble_history()
        self.assertEqual(len(rows), 2)
        addresses = {r["address"] for r in rows}
        self.assertIn("AA:BB:CC:DD:EE:01", addresses)
        self.assertIn("AA:BB:CC:DD:EE:02", addresses)

    def test_empty_ble_scan_stored(self) -> None:
        sid = scanner_db.store_ble_scan([])
        self.assertGreater(sid, 0)
        self.assertEqual(len(scanner_db.get_ble_history()), 0)

    # ── Aggregation ───────────────────────────────────────────────────────────
    def test_wifi_seen_count_increments(self) -> None:
        net = [{"ssid": "TestNet", "bssid": "DE:AD:BE:EF:00:01",
                "rssi": -50, "channel": 1, "encryption": "WPA2", "band": "2.4GHz"}]
        scanner_db.store_wifi_scan(net)
        scanner_db.store_wifi_scan(net)
        unique = scanner_db.get_unique_networks()
        entry = next(
            (r for r in unique["wifi"] if r["bssid"] == "DE:AD:BE:EF:00:01"), None
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry["seen_count"], 2)

    def test_wifi_best_rssi_tracked(self) -> None:
        bssid = "CA:FE:BA:BE:00:01"
        scanner_db.store_wifi_scan([{"bssid": bssid, "ssid": "R", "rssi": -80,
                                     "channel": 6, "band": "2.4GHz"}])
        scanner_db.store_wifi_scan([{"bssid": bssid, "ssid": "R", "rssi": -40,
                                     "channel": 6, "band": "2.4GHz"}])
        unique = scanner_db.get_unique_networks()
        entry  = next(r for r in unique["wifi"] if r["bssid"] == bssid)
        self.assertEqual(entry["best_rssi"],  -40)
        self.assertEqual(entry["worst_rssi"], -80)

    def test_ble_seen_count_increments(self) -> None:
        dev = [{"address": "11:22:33:44:55:66", "name": "Tag",
                "rssi": -65, "manufacturer_data": "", "service_uuid": ""}]
        scanner_db.store_ble_scan(dev)
        scanner_db.store_ble_scan(dev)
        unique = scanner_db.get_unique_networks()
        entry  = next(
            (r for r in unique["ble"] if r["address"] == "11:22:33:44:55:66"), None
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry["seen_count"], 2)

    # ── History limit ─────────────────────────────────────────────────────────
    def test_get_wifi_history_limit(self) -> None:
        for i in range(10):
            scanner_db.store_wifi_scan([
                {"ssid": f"Net{i}", "bssid": f"00:00:00:00:00:{i:02X}",
                 "rssi": -60, "channel": 1, "band": "2.4GHz"}
            ])
        rows = scanner_db.get_wifi_history(limit=5)
        self.assertEqual(len(rows), 5)

    def test_get_ble_history_limit(self) -> None:
        for i in range(8):
            scanner_db.store_ble_scan([
                {"address": f"00:00:00:00:00:{i:02X}", "name": f"Dev{i}",
                 "rssi": -70, "manufacturer_data": "", "service_uuid": ""}
            ])
        rows = scanner_db.get_ble_history(limit=3)
        self.assertEqual(len(rows), 3)

    # ── Device id tagging ─────────────────────────────────────────────────────
    def test_device_id_stored_with_session(self) -> None:
        scanner_db.store_wifi_scan([], device_id="ESP32-DEMO")
        with scanner_db.get_connection() as conn:
            row = conn.execute(
                "SELECT device_id FROM scan_sessions ORDER BY id DESC LIMIT 1"
            ).fetchone()
        self.assertEqual(row["device_id"], "ESP32-DEMO")


if __name__ == "__main__":
    unittest.main()
