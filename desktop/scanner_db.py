"""
ESPx Scanner Database
=====================
Manages a local SQLite database that logs every WiFi and BLE scan performed
by the ESPx desktop GUI.  The database is stored in ``~/.espx/scans.db``.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / ".espx" / "scans.db"


def get_connection() -> sqlite3.Connection:
    """Return an open connection to the ESPx database, creating it if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables and indexes if they do not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_sessions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_type TEXT    NOT NULL,
                timestamp TEXT    NOT NULL,
                device_id TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wifi_networks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER REFERENCES scan_sessions(id),
                ssid       TEXT,
                bssid      TEXT,
                rssi       INTEGER,
                channel    INTEGER,
                encryption TEXT,
                band       TEXT,
                frequency  INTEGER,
                timestamp  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ble_devices (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id        INTEGER REFERENCES scan_sessions(id),
                name              TEXT,
                address           TEXT,
                rssi              INTEGER,
                manufacturer_data TEXT,
                service_uuid      TEXT,
                timestamp         TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_wifi_bssid    ON wifi_networks(bssid)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ble_address   ON ble_devices(address)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_wifi_session  ON wifi_networks(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ble_session   ON ble_devices(session_id)")
        conn.commit()


def store_wifi_scan(networks: list, device_id: str = None) -> int:
    """
    Persist a list of WiFi network dicts.  Returns the new session id.

    Each network dict may contain: ssid, bssid, rssi, channel, encryption,
    band, frequency_mhz.
    """
    ts = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO scan_sessions (scan_type, timestamp, device_id) VALUES (?, ?, ?)",
            ("wifi", ts, device_id),
        )
        session_id = cur.lastrowid
        for net in networks:
            conn.execute(
                """INSERT INTO wifi_networks
                       (session_id, ssid, bssid, rssi, channel,
                        encryption, band, frequency, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    net.get("ssid", ""),
                    net.get("bssid", ""),
                    net.get("rssi"),
                    net.get("channel"),
                    net.get("encryption", ""),
                    net.get("band", ""),
                    net.get("frequency_mhz"),
                    ts,
                ),
            )
        conn.commit()
    return session_id


def store_ble_scan(devices: list, device_id: str = None) -> int:
    """
    Persist a list of BLE device dicts.  Returns the new session id.

    Each device dict may contain: name, address, rssi,
    manufacturer_data, service_uuid.
    """
    ts = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO scan_sessions (scan_type, timestamp, device_id) VALUES (?, ?, ?)",
            ("ble", ts, device_id),
        )
        session_id = cur.lastrowid
        for dev in devices:
            conn.execute(
                """INSERT INTO ble_devices
                       (session_id, name, address, rssi,
                        manufacturer_data, service_uuid, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    dev.get("name", ""),
                    dev.get("address", ""),
                    dev.get("rssi"),
                    dev.get("manufacturer_data", ""),
                    dev.get("service_uuid", ""),
                    ts,
                ),
            )
        conn.commit()
    return session_id


def get_wifi_history(limit: int = 200) -> list:
    """Return the most recent *limit* WiFi network rows, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT w.*, s.timestamp AS session_time
               FROM   wifi_networks w
               JOIN   scan_sessions  s ON w.session_id = s.id
               ORDER BY w.id DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_ble_history(limit: int = 200) -> list:
    """Return the most recent *limit* BLE device rows, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT b.*, s.timestamp AS session_time
               FROM   ble_devices   b
               JOIN   scan_sessions s ON b.session_id = s.id
               ORDER BY b.id DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_unique_networks() -> dict:
    """
    Return aggregated statistics for all known networks.

    Returns a dict with keys ``"wifi"`` and ``"ble"``, each a list of rows
    containing aggregated RSSI stats, seen count, and last-seen timestamp.
    """
    with get_connection() as conn:
        wifi = conn.execute(
            """SELECT bssid, ssid,
                      MAX(rssi)   AS best_rssi,
                      MIN(rssi)   AS worst_rssi,
                      COUNT(*)    AS seen_count,
                      MAX(timestamp) AS last_seen,
                      band, channel
               FROM   wifi_networks
               GROUP  BY bssid
               ORDER  BY seen_count DESC""",
        ).fetchall()
        ble = conn.execute(
            """SELECT address, name,
                      MAX(rssi)   AS best_rssi,
                      MIN(rssi)   AS worst_rssi,
                      COUNT(*)    AS seen_count,
                      MAX(timestamp) AS last_seen
               FROM   ble_devices
               GROUP  BY address
               ORDER  BY seen_count DESC""",
        ).fetchall()
    return {
        "wifi": [dict(r) for r in wifi],
        "ble":  [dict(r) for r in ble],
    }
