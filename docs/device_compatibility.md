# Device Compatibility

ESPx firmware is built with PlatformIO and the ESP32 Arduino core.  The serial
protocol and desktop GUI work with any board that provides a USB-to-serial
interface at 115200 baud.

---

## Supported ESP32 Boards

| Board | PlatformIO env | Notes |
|-------|---------------|-------|
| Generic ESP32 Dev Module | `esp32dev` | Breadboard-friendly; most common |
| LilyGo T-Display (ESP32) | `lilygo-t-display` | Integrated 1.14″ TFT; useful for stand-alone display |
| ESP32-S3 DevKitC-1 | `esp32s3` | Dual-core Xtensa LX7; USB-OTG support |
| Any ESP32 variant | custom env | Add a new `[env:xxx]` block in `firmware/platformio.ini` |

---

## Flipper Zero

The Flipper Zero can communicate with an ESPx device in two ways:

1. **UART bridge** — wire the Flipper's UART TX/RX pins to the ESP32 GPIO
   (default 115200 baud).  A Flipper app can send `SCAN_WIFI` / `SCAN_BLE`
   commands and parse the JSON responses.
2. **Serial-over-USB** — connect the ESP32 via USB and use the Flipper's
   USB-UART bridge application.

---

## LilyGo Devices

| Model | Status |
|-------|--------|
| T-Display (ESP32) | ✅ Supported — dedicated `lilygo-t-display` env |
| T-Display S3 | ✅ Use `esp32s3` env |
| T-Pico C3 | ⚙️ Use `esp32dev` env; adjust `board` field |

---

## WiFi Pineapple

An ESPx device can augment a WiFi Pineapple setup by providing BLE scanning
(which the Pineapple does not do natively).  Connect the ESP32 over serial to
the Pineapple's UART or USB port and parse the JSON output from the Pineapple's
scripting environment.

---

## Pager / LoRa modules

The serial protocol is designed to be relay-friendly.  Any device that can
forward newline-terminated ASCII strings can act as a transport layer between
the ESPx and a host.

---

## Phone to Breadboard Cable

See [`cable_design.md`](cable_design.md) for the recommended USB OTG /
UART adapter pinout.
