# Phone to Breadboard Adapter Cable Design

This document describes the minimal wiring to connect an Android or iOS phone
directly to an ESP32 on a breadboard for serial debugging and control.

---

## Android (USB OTG) → ESP32 UART

```
Phone USB-C / micro-USB
        │
  USB OTG adapter  (female-A → host mode)
        │
  CP2102 / CH340 / FT232 USB-to-UART dongle
        │
  ┌─────┴──────────────────────────────────┐
  │  USB-UART dongle                        │
  │   GND  ──────────────────  GND  (ESP32) │
  │   TX   ──────────────────  RX   (GPIO3) │
  │   RX   ──────────────────  TX   (GPIO1) │
  │   3V3  ──(optional power)─  3V3  (ESP32)│
  └────────────────────────────────────────┘
```

> ⚠️ Do **not** connect the 5 V pin from the phone to the ESP32 3V3 rail.
> Power the ESP32 from its own USB connection or a 3V3 regulator.

### Recommended dongles

| Chip | Notes |
|------|-------|
| CP2102 | Reliable, widely supported on Android |
| CH340G | Budget option; install drivers on Windows |
| FT232RL | Best compatibility; supports 921600 baud for fast flashing |

---

## iOS (Lightning / USB-C) → ESP32 UART

iOS requires the **Apple Camera Connection Kit** (USB3 camera adapter) to
expose a USB host port:

```
iPhone/iPad
     │
  Apple USB3 Camera Adapter (Lightning or USB-C)
     │ USB-A port
  CP2102 / FT232 USB-to-UART dongle
     │
  ESP32 UART (same wiring as Android above)
```

> Note: not all third-party USB-to-UART chips are recognised by iOS.
> CP2102 and FT232RL have the best track record.

---

## Direct UART (3.3 V logic) — Breadboard Jumpers

If your phone exposes a UART through a custom cable (e.g., some older Android
devices with UART on the headphone jack), you can connect directly:

```
Phone UART TX  ──  ESP32 RX (GPIO3)
Phone UART RX  ──  ESP32 TX (GPIO1)
Phone GND      ──  ESP32 GND
```

Ensure both sides use 3.3 V logic levels.  Use a level-shifter if the phone
outputs 5 V.

---

## Baud Rate

ESPx defaults to **115200 baud**, 8N1.  Most serial terminal apps on Android
(e.g. Serial USB Terminal) and iOS (e.g. Bluetooth Serial) support this rate.
