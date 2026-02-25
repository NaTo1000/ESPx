# ESPx
Full ESP32 wireless suite — come have a look, add to it, make it next level 😄

---

## 🚀 Innovations Engine

The **Innovations Engine** is a firmware-mapping search tool.  
Describe what you want your ESP32 to *do* in plain English, and it
returns the most relevant ESP32 firmware capabilities, libraries, and
starter code snippets — ranked by relevance.

### Features

| Feature | Description |
|---|---|
| 🔍 **Intent search** | Natural-language query mapped to firmware capabilities |
| 📚 **Vast knowledge base** | 30+ ESP32 domains: WiFi, BLE, MQTT, OTA, sensors, displays, motors, ML, LoRa, and more |
| 🏷️ **Tag browser** | Browse capabilities by topic tag (95 unique tags) |
| 📋 **Starter snippets** | Every result includes a minimal code sketch for Arduino or ESP-IDF |
| 🛠️ **Extensible** | Supply your own `knowledge_base` list to customise or extend |

---

### Quick Start

```bash
# One-shot query
python -m innovations_engine "send temperature over MQTT to Home Assistant"

# Show up to 8 results
python -m innovations_engine "BLE sensor notify phone" --top 8

# Interactive REPL (describe, refine, explore)
python -m innovations_engine

# List all topic tags
python -m innovations_engine --tags

# Browse a specific tag
python -m innovations_engine --tag wifi
```

### Example Output

```
  Found 3 relevant firmware capability(s) for:
  "send temperature over MQTT to Home Assistant"

  ── Result 1 ──────────────────────────────────────────
  [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░]  62.3%
  Home Assistant Integration (ESPHome / MQTT Discovery)
  ID: home_assistant_esphome  │  Framework: both
  ...
  Starter code snippet
  ────────────────────
  # ESPHome YAML
  sensor:
    - platform: dht
      pin: GPIO4
      model: DHT22
      temperature:
        name: "Room Temperature"
```

---

### Python API

```python
from innovations_engine import InnovationsEngine

engine = InnovationsEngine()

# Search by intent description
results = engine.search("battery powered sensor sends data every minute", top_n=5)
for r in results:
    print(f"{r.score*100:.0f}%  {r.title}")
    print(f"  Snippet:\n{r.snippet}")

# Browse tags
print(engine.list_tags())

# Get a specific entry
entry = engine.get_entry("mqtt_client")
```

---

### Knowledge Base Coverage

| Domain | Capabilities |
|---|---|
| **Wireless** | WiFi STA, WiFi AP, SmartConfig, ESP-NOW, LoRa/LoRaWAN, WiFi Mesh |
| **Bluetooth** | BLE GATT Server, BLE Scanner / iBeacon |
| **Protocols** | MQTT, HTTP Server, HTTPS Client, I²C, SPI, UART |
| **Sensors** | Temperature/Humidity, IMU/Motion, Distance/ToF, ADC/Analog |
| **Display** | OLED (SSD1306), TFT/LCD (ILI9341/ST7789) |
| **Actuators** | DC Motor PWM, Servo, Stepper (CNC) |
| **Media** | Camera (ESP32-CAM), Audio I²S |
| **Power** | Deep Sleep, ULP, GPIO/Touch wake |
| **Storage** | NVS/Preferences, SD Card, Partition Tables |
| **Connectivity** | OTA Updates, NTP/RTC |
| **RTOS** | FreeRTOS multi-tasking, core pinning |
| **Security** | Secure Boot V2, Flash Encryption |
| **Automation** | Home Assistant / ESPHome integration |
| **Edge AI** | TensorFlow Lite Micro, Edge Impulse |

---

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
