# Getting Started with ESPx

## Prerequisites

| Tool | Version |
|------|---------|
| [PlatformIO](https://platformio.org/) | ≥ 6.x |
| Python | ≥ 3.10 |
| pip | latest |

---

## 1 — Flash the Firmware

```bash
cd firmware

# Generic ESP32 dev board
pio run -e esp32dev --target upload

# LilyGo T-Display
pio run -e lilygo-t-display --target upload

# ESP32-S3 DevKit
pio run -e esp32s3 --target upload
```

Monitor the serial output (115200 baud):

```bash
pio device monitor
```

You should see:

```json
{"type":"boot","message":"ESPx starting..."}
{"type":"boot","message":"ESPx ready — send HELP for commands"}
```

---

## 2 — Serial Command Reference

Send plain-text commands over the serial port (or the PlatformIO monitor).
All commands are case-insensitive and terminated with a newline (`\n`).

| Command | Description |
|---------|-------------|
| `SCAN_WIFI` | Scan all visible 802.11 networks and return JSON |
| `SCAN_BLE [secs]` | Active BLE scan for *secs* seconds (default 5, max 30) |
| `STATUS` | Return firmware version, uptime and free heap |
| `HELP` | List available commands |

### Example WiFi scan response

```json
{
  "type": "wifi_scan",
  "timestamp": 12345,
  "networks": [
    {
      "ssid": "HomeNet",
      "bssid": "AA:BB:CC:DD:EE:FF",
      "rssi": -55,
      "channel": 6,
      "band": "2.4GHz",
      "frequency_mhz": 2437,
      "encryption": "WPA2"
    }
  ]
}
```

### Example BLE scan response

```json
{
  "type": "ble_scan",
  "timestamp": 23456,
  "duration": 5,
  "devices": [
    {
      "name": "MyHeadphones",
      "address": "11:22:33:44:55:66",
      "rssi": -62,
      "manufacturer_data": "4C000F05",
      "service_uuid": "0000180f-0000-1000-8000-00805f9b34fb"
    }
  ]
}
```

---

## 3 — Desktop GUI

```bash
cd desktop
pip install -r requirements.txt
python espx_gui.py
```

1. Select the serial port from the **Port** drop-down and click **Connect**.
2. Click **📡 Scan WiFi** or **🔵 Scan BLE** to trigger a scan.
3. Adjust the **BLE secs** spinner to change scan duration.
4. Switch to the **🗄 History** tab to see aggregated all-time results.
5. Export data via **File → Export WiFi / BLE CSV**.

Scan data is automatically saved to `~/.espx/scans.db` (SQLite).

---

## 4 — Running Tests

```bash
pip install pyserial   # only required for the GUI; tests run without a device
python -m pytest tests/ -v
```

---

## 5 — Project Layout

```
ESPx/
├── firmware/
│   ├── platformio.ini          # multi-board PlatformIO config
│   └── src/
│       ├── main.cpp            # setup() / loop()
│       ├── wifi_scanner.{h,cpp}
│       ├── ble_scanner.{h,cpp}
│       └── serial_protocol.{h,cpp}
├── desktop/
│   ├── espx_gui.py             # tkinter desktop GUI
│   ├── scanner_db.py           # SQLite persistence layer
│   └── requirements.txt
├── tests/
│   └── test_scanner_db.py
└── docs/
    ├── getting_started.md      ← you are here
    ├── device_compatibility.md
    └── cable_design.md
```
