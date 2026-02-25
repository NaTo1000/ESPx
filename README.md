# ESPx — Comprehensive ESP32 Wireless Suite

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A full-featured ESP32 wireless scanning and mapping toolkit — come have a look,
add to it, make it next level 😄

---

## Features

| Feature | Description |
|---------|-------------|
| 📡 **WiFi Scanner** | Scan visible 802.11 networks (SSID, BSSID, RSSI, channel, band 2.4/5 GHz, encryption) |
| 🔵 **BLE Mapper** | Active BLE scan (device name, address, RSSI, manufacturer data, service UUID) |
| 🗄 **Persistent Logging** | All scan results saved to a local SQLite database (`~/.espx/scans.db`) |
| 🖥 **Desktop GUI** | Python/tkinter GUI — connect, scan, sort, view history, export CSV |
| 📤 **CSV Export** | One-click export of WiFi or BLE scan history |
| 🔌 **Multi-board** | Generic ESP32, LilyGo T-Display, ESP32-S3 — add your own board in minutes |
| 📱 **Phone-ready** | Wiring guide for Android (USB OTG) and iOS (Camera Adapter) connection to breadboard |
| 🐬 **Flipper Zero** | UART-bridge compatible; send scan commands from a Flipper app |
| 🍍 **WiFi Pineapple** | Use ESPx as a BLE extension for Pineapple setups |

---

## Quick Start

### 1 — Flash the firmware

```bash
cd firmware
pio run -e esp32dev --target upload   # or lilygo-t-display / esp32s3
pio device monitor                    # 115200 baud
```

### 2 — Run the desktop GUI

```bash
cd desktop
pip install -r requirements.txt
python espx_gui.py
```

Select your serial port, click **Connect**, then **📡 Scan WiFi** or **🔵 Scan BLE**.

### 3 — Run tests

```bash
python -m pytest tests/ -v
```

---

## Serial Protocol

Commands are plain ASCII lines, case-insensitive, terminated with `\n`.

| Command | Action |
|---------|--------|
| `SCAN_WIFI` | Scan WiFi networks → JSON |
| `SCAN_BLE [secs]` | BLE scan for N seconds (default 5) → JSON |
| `STATUS` | Firmware version, uptime, free heap |
| `HELP` | List commands |

---

## Project Layout

```
firmware/          ESP32 Arduino/PlatformIO firmware
  platformio.ini
  src/
    main.cpp
    wifi_scanner.{h,cpp}
    ble_scanner.{h,cpp}
    serial_protocol.{h,cpp}
desktop/           Python desktop GUI
  espx_gui.py
  scanner_db.py
  requirements.txt
tests/             Python unit tests (no hardware required)
  test_scanner_db.py
docs/
  getting_started.md
  device_compatibility.md
  cable_design.md
```

---

## Documentation

- [Getting Started](docs/getting_started.md)
- [Device Compatibility](docs/device_compatibility.md) — ESP32, LilyGo, Flipper Zero, WiFi Pineapple, Pager
- [Phone to Breadboard Cable Design](docs/cable_design.md)

---

## Contributing

PRs are welcome — add new board configs, new scan modes, GUI improvements,
or protocol extensions.  See [Getting Started](docs/getting_started.md) for
the development workflow.

## License

[Apache 2.0](LICENSE)

