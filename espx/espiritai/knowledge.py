"""
ESPiritAi Knowledge Base

Comprehensive knowledge on firmware types, programming languages, operational
values, weaknesses, and secrets for ESP32/ESP8266 variants, robotics
dashboards, and related projects (Marauder, Meshtastic, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ChipVariant:
    """Describes a specific ESP chip variant."""

    name: str
    family: str  # "ESP32" | "ESP8266"
    cpu: str
    flash_kb: int
    ram_kb: int
    wifi: bool
    bluetooth: bool
    firmware_support: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    operational_values: Dict[str, Any] = field(default_factory=dict)
    weaknesses: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)


@dataclass
class FirmwareType:
    """Describes a firmware / framework."""

    name: str
    language: str
    supported_chips: List[str] = field(default_factory=list)
    description: str = ""
    features: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)


@dataclass
class RelatedProject:
    """Describes a related project in the ESPx ecosystem."""

    name: str
    description: str
    supported_chips: List[str] = field(default_factory=list)
    firmware_base: str = ""
    features: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Chip variants
# ---------------------------------------------------------------------------

ESP_CHIPS: Dict[str, ChipVariant] = {
    "ESP32": ChipVariant(
        name="ESP32",
        family="ESP32",
        cpu="Xtensa LX6 dual-core 240 MHz",
        flash_kb=4096,
        ram_kb=520,
        wifi=True,
        bluetooth=True,
        firmware_support=[
            "Arduino", "ESP-IDF", "MicroPython", "Tasmota",
            "ESPHome", "Marauder", "Meshtastic",
        ],
        languages=["C", "C++", "Python", "Lua", "JavaScript"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 240,
            "current_sleep_ua": 10,
            "temp_range_c": (-40, 85),
            "wifi_standards": ["802.11b", "802.11g", "802.11n"],
            "bt_version": "4.2 BR/EDR + BLE",
        },
        weaknesses=[
            "Higher power consumption vs ESP8266",
            "More complex toolchain setup",
            "Larger binary size for ESP-IDF builds",
            "Susceptible to Wi-Fi deauthentication attacks",
        ],
        capabilities=[
            "Dual-core processing",
            "Bluetooth Classic + BLE",
            "Hardware encryption (AES, RSA, SHA)",
            "Touch sensors",
            "Hall sensor",
            "CAN bus interface",
            "SD/SDIO/MMC host",
        ],
    ),
    "ESP32-S2": ChipVariant(
        name="ESP32-S2",
        family="ESP32",
        cpu="Xtensa LX7 single-core 240 MHz",
        flash_kb=4096,
        ram_kb=320,
        wifi=True,
        bluetooth=False,
        firmware_support=["Arduino", "ESP-IDF", "MicroPython", "CircuitPython"],
        languages=["C", "C++", "Python"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 150,
            "current_sleep_ua": 22,
            "temp_range_c": (-40, 85),
            "wifi_standards": ["802.11b", "802.11g", "802.11n"],
            "usb_otg": True,
        },
        weaknesses=[
            "No Bluetooth",
            "Single core limits parallel workloads",
        ],
        capabilities=[
            "Native USB OTG",
            "Ultra-low-power coprocessor",
            "LCD interface",
            "Hardware security (Digital Signature, HMAC)",
        ],
    ),
    "ESP32-S3": ChipVariant(
        name="ESP32-S3",
        family="ESP32",
        cpu="Xtensa LX7 dual-core 240 MHz",
        flash_kb=8192,
        ram_kb=512,
        wifi=True,
        bluetooth=True,
        firmware_support=[
            "Arduino", "ESP-IDF", "MicroPython", "Tasmota", "ESPHome",
        ],
        languages=["C", "C++", "Python"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 260,
            "current_sleep_ua": 14,
            "temp_range_c": (-40, 85),
            "wifi_standards": ["802.11b", "802.11g", "802.11n"],
            "bt_version": "BLE 5.0",
            "usb_otg": True,
            "ai_acceleration": True,
        },
        weaknesses=[
            "Higher power draw than S2",
            "BLE 5.0 only (no Bluetooth Classic)",
        ],
        capabilities=[
            "Vector instructions for AI/ML",
            "Native USB OTG",
            "PSRAM support",
            "Advanced power management",
        ],
    ),
    "ESP32-C3": ChipVariant(
        name="ESP32-C3",
        family="ESP32",
        cpu="RISC-V single-core 160 MHz",
        flash_kb=4096,
        ram_kb=400,
        wifi=True,
        bluetooth=True,
        firmware_support=["Arduino", "ESP-IDF", "MicroPython", "ESPHome"],
        languages=["C", "C++", "Python", "Rust"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 120,
            "current_sleep_ua": 5,
            "temp_range_c": (-40, 105),
            "wifi_standards": ["802.11b", "802.11g", "802.11n"],
            "bt_version": "BLE 5.0",
        },
        weaknesses=[
            "Single core RISC-V",
            "No Bluetooth Classic",
            "Fewer GPIO pins",
        ],
        capabilities=[
            "RISC-V architecture (good Rust support)",
            "IEEE 802.15.4 (Thread/Zigbee) variant available",
            "Low power consumption",
            "Hardware security boot",
        ],
    ),
    "ESP32-H2": ChipVariant(
        name="ESP32-H2",
        family="ESP32",
        cpu="RISC-V single-core 96 MHz",
        flash_kb=4096,
        ram_kb=320,
        wifi=False,
        bluetooth=True,
        firmware_support=["ESP-IDF", "Arduino", "Zephyr"],
        languages=["C", "C++", "Rust"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 50,
            "current_sleep_ua": 8,
            "temp_range_c": (-40, 85),
            "ieee802154": True,
            "bt_version": "BLE 5.2",
        },
        weaknesses=[
            "No Wi-Fi",
            "Limited library ecosystem",
            "96 MHz limits compute-heavy tasks",
        ],
        capabilities=[
            "IEEE 802.15.4 (Thread + Zigbee)",
            "BLE 5.2",
            "Matter protocol support",
            "Ultra-low-power coprocessor",
        ],
    ),
    "ESP8266": ChipVariant(
        name="ESP8266",
        family="ESP8266",
        cpu="Xtensa L106 single-core 80-160 MHz",
        flash_kb=4096,
        ram_kb=160,
        wifi=True,
        bluetooth=False,
        firmware_support=[
            "Arduino", "MicroPython", "NodeMCU (Lua)", "Tasmota", "ESPHome",
        ],
        languages=["C", "C++", "Python", "Lua", "JavaScript"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 170,
            "current_sleep_ua": 20,
            "temp_range_c": (-40, 125),
            "wifi_standards": ["802.11b", "802.11g", "802.11n"],
        },
        weaknesses=[
            "No Bluetooth",
            "Limited RAM (160 KB)",
            "Single core only",
            "Susceptible to Wi-Fi deauthentication attacks",
            "No hardware encryption acceleration",
            "Unstable deep-sleep GPIO state",
        ],
        capabilities=[
            "Mature ecosystem",
            "Cheap and widely available",
            "Low power sleep modes",
            "AT command firmware available",
        ],
    ),
    "ESP-01": ChipVariant(
        name="ESP-01",
        family="ESP8266",
        cpu="Xtensa L106 single-core 80 MHz",
        flash_kb=1024,
        ram_kb=96,
        wifi=True,
        bluetooth=False,
        firmware_support=["AT Firmware", "Arduino (limited)", "Custom"],
        languages=["C", "C++"],
        operational_values={
            "voltage_min": 3.0,
            "voltage_max": 3.6,
            "current_active_ma": 215,
            "gpio_count": 2,
        },
        weaknesses=[
            "Only 2 GPIO pins",
            "Very limited flash/RAM",
            "No USB serial (requires external adapter)",
        ],
        capabilities=[
            "Minimal footprint",
            "AT command Wi-Fi modem use case",
        ],
    ),
}


# ---------------------------------------------------------------------------
# Firmware types
# ---------------------------------------------------------------------------

FIRMWARE_TYPES: Dict[str, FirmwareType] = {
    "Arduino": FirmwareType(
        name="Arduino",
        language="C/C++",
        supported_chips=list(ESP_CHIPS.keys()),
        description="Popular microcontroller framework with large library ecosystem.",
        features=[
            "Extensive library ecosystem",
            "Simple setup() / loop() model",
            "Arduino IDE + PlatformIO support",
            "OTA updates",
        ],
        weaknesses=[
            "Abstraction overhead vs bare-metal ESP-IDF",
            "Single-threaded by default (though FreeRTOS tasks available)",
        ],
    ),
    "ESP-IDF": FirmwareType(
        name="ESP-IDF",
        language="C/C++",
        supported_chips=["ESP32", "ESP32-S2", "ESP32-S3", "ESP32-C3", "ESP32-H2"],
        description="Espressif's official IoT Development Framework.",
        features=[
            "Full FreeRTOS multi-tasking",
            "Component-based architecture",
            "Advanced power management APIs",
            "Secure boot + flash encryption",
            "Over-the-air (OTA) update support",
        ],
        weaknesses=[
            "Steeper learning curve",
            "Verbose boilerplate",
            "Longer compile times",
        ],
    ),
    "MicroPython": FirmwareType(
        name="MicroPython",
        language="Python",
        supported_chips=["ESP32", "ESP32-S2", "ESP32-S3", "ESP32-C3", "ESP8266"],
        description="Python 3 implementation for microcontrollers.",
        features=[
            "Interactive REPL",
            "uasyncio for async programming",
            "Large built-in module set",
            "Rapid prototyping",
        ],
        weaknesses=[
            "Slower than C/C++ (interpreted)",
            "Higher memory footprint",
            "GC pauses can affect real-time tasks",
        ],
    ),
    "Tasmota": FirmwareType(
        name="Tasmota",
        language="C++",
        supported_chips=["ESP32", "ESP32-S2", "ESP32-S3", "ESP8266"],
        description="Open-source firmware for ESP-based IoT devices.",
        features=[
            "MQTT integration",
            "Web UI + REST API",
            "Hundreds of supported sensors/devices",
            "Home automation friendly",
        ],
        weaknesses=[
            "Limited custom code extensibility",
            "Scripting language is basic",
        ],
    ),
    "ESPHome": FirmwareType(
        name="ESPHome",
        language="YAML/C++",
        supported_chips=["ESP32", "ESP32-S2", "ESP32-S3", "ESP32-C3", "ESP8266"],
        description="YAML-configured firmware builder for Home Assistant.",
        features=[
            "YAML-driven configuration",
            "Native Home Assistant integration",
            "OTA + web server",
            "Hundreds of components",
        ],
        weaknesses=[
            "Tightly coupled to Home Assistant ecosystem",
            "Limited arbitrary code injection",
        ],
    ),
    "Marauder": FirmwareType(
        name="Marauder",
        language="C++",
        supported_chips=["ESP32", "ESP8266"],
        description=(
            "Wi-Fi and Bluetooth security auditing firmware for ESP hardware."
        ),
        features=[
            "Wi-Fi scanning, sniffing, and deauth attacks",
            "Bluetooth scanning and BLE spam",
            "Evil portal / captive portal",
            "Packet monitor",
            "GPS integration",
            "SD card logging",
        ],
        weaknesses=[
            "Requires physical access or flashed device",
            "Legal / ethical constraints on use",
            "Limited range without external antenna",
        ],
    ),
    "Meshtastic": FirmwareType(
        name="Meshtastic",
        language="C++",
        supported_chips=["ESP32", "ESP32-S3"],
        description="Long-range LoRa mesh networking firmware.",
        features=[
            "LoRa mesh networking",
            "GPS position sharing",
            "Encrypted messaging",
            "Python / Android / iOS apps",
            "MQTT bridge",
        ],
        weaknesses=[
            "Requires LoRa radio module (not built into ESP)",
            "Lower throughput than Wi-Fi",
            "Mesh latency increases with hops",
        ],
    ),
    "NodeMCU": FirmwareType(
        name="NodeMCU",
        language="Lua",
        supported_chips=["ESP8266"],
        description="Lua-based firmware for ESP8266.",
        features=[
            "Lua scripting on-device",
            "Event-driven programming model",
            "Built-in Wi-Fi APIs",
        ],
        weaknesses=[
            "ESP8266-only",
            "Lua ecosystem smaller than Python/C++",
            "Development less active",
        ],
    ),
}


# ---------------------------------------------------------------------------
# Related projects
# ---------------------------------------------------------------------------

RELATED_PROJECTS: Dict[str, RelatedProject] = {
    "Marauder": RelatedProject(
        name="Marauder",
        description="ESP32/ESP8266 Wi-Fi and Bluetooth security auditing tool.",
        supported_chips=["ESP32", "ESP8266"],
        firmware_base="Marauder",
        features=[
            "Deauthentication attacks",
            "Beacon spam",
            "Probe flood",
            "Evil portal",
            "BLE spam (Apple, Samsung, Windows)",
            "Bluetooth classic scanning",
        ],
        use_cases=[
            "Penetration testing",
            "Security research",
            "CTF challenges",
            "Network auditing",
        ],
    ),
    "Meshtastic": RelatedProject(
        name="Meshtastic",
        description="Off-grid LoRa mesh messaging and position sharing.",
        supported_chips=["ESP32", "ESP32-S3"],
        firmware_base="Meshtastic",
        features=[
            "Long-range LoRa mesh (up to 100+ km line-of-sight)",
            "AES-256 encrypted channels",
            "Position sharing via GPS",
            "Store-and-forward messages",
            "MQTT cloud bridge",
        ],
        use_cases=[
            "Off-grid communication",
            "Disaster relief",
            "Hiking / outdoor adventures",
            "Community mesh networks",
        ],
    ),
    "RoboticsDashboard": RelatedProject(
        name="RoboticsDashboard",
        description=(
            "Web-based telemetry and control dashboard for ESP32-powered robots."
        ),
        supported_chips=["ESP32", "ESP32-S3"],
        firmware_base="Arduino",
        features=[
            "Real-time sensor telemetry (WebSocket)",
            "Motor / servo control panel",
            "PID tuning interface",
            "Camera stream (ESP32-CAM)",
            "OTA firmware update",
            "Data logging to SD / cloud",
        ],
        use_cases=[
            "Robot telemetry monitoring",
            "Remote control",
            "Autonomous robot supervision",
            "Educational robotics",
        ],
    ),
    "FlipperZeroCompanion": RelatedProject(
        name="FlipperZeroCompanion",
        description="ESP32 Wi-Fi companion module for Flipper Zero.",
        supported_chips=["ESP32", "ESP32-S2"],
        firmware_base="Marauder",
        features=[
            "Extends Flipper Zero with Wi-Fi capabilities",
            "Marauder firmware integration",
            "UART bridge to Flipper",
        ],
        use_cases=["Security research", "CTF", "Wi-Fi auditing"],
    ),
    "ESPHome": RelatedProject(
        name="ESPHome",
        description="ESP-based home automation firmware builder.",
        supported_chips=["ESP32", "ESP32-S2", "ESP32-S3", "ESP32-C3", "ESP8266"],
        firmware_base="ESPHome",
        features=["Home Assistant native integration", "300+ components"],
        use_cases=["Smart home automation", "IoT sensors", "Custom devices"],
    ),
}


# ---------------------------------------------------------------------------
# Programming languages knowledge
# ---------------------------------------------------------------------------

PROGRAMMING_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "C": {
        "paradigm": "Procedural",
        "use_cases": ["Bare-metal firmware", "HAL drivers", "RTOS tasks"],
        "performance": "Highest",
        "memory_overhead": "Lowest",
    },
    "C++": {
        "paradigm": "Object-oriented / Procedural",
        "use_cases": ["Arduino sketches", "ESP-IDF components", "Marauder", "Meshtastic"],
        "performance": "High",
        "memory_overhead": "Low-Medium",
    },
    "Python": {
        "paradigm": "Multi-paradigm",
        "use_cases": ["MicroPython on-device", "PC-side tooling", "ESPiritAi AI layer"],
        "performance": "Moderate (interpreted)",
        "memory_overhead": "Medium-High",
    },
    "Lua": {
        "paradigm": "Multi-paradigm (lightweight scripting)",
        "use_cases": ["NodeMCU scripting"],
        "performance": "Moderate",
        "memory_overhead": "Low",
    },
    "JavaScript": {
        "paradigm": "Event-driven / Prototype-based",
        "use_cases": ["Espruino", "Web dashboards (Node.js backend)"],
        "performance": "Moderate",
        "memory_overhead": "Medium",
    },
    "Rust": {
        "paradigm": "Systems / Functional",
        "use_cases": ["ESP32-C3 bare metal", "Embassy async firmware"],
        "performance": "High",
        "memory_overhead": "Low",
    },
}


# ---------------------------------------------------------------------------
# KnowledgeBase class
# ---------------------------------------------------------------------------

class KnowledgeBase:
    """
    Central knowledge repository for ESPiritAi.

    Provides query methods for chip variants, firmware types, related projects,
    and programming language metadata.
    """

    def __init__(self) -> None:
        self.chips: Dict[str, ChipVariant] = ESP_CHIPS
        self.firmware: Dict[str, FirmwareType] = FIRMWARE_TYPES
        self.projects: Dict[str, RelatedProject] = RELATED_PROJECTS
        self.languages: Dict[str, Dict[str, Any]] = PROGRAMMING_LANGUAGES

    # -- Chip queries -------------------------------------------------------

    def get_chip(self, name: str) -> ChipVariant:
        """Return chip variant by name (raises KeyError if not found)."""
        return self.chips[name]

    def chips_for_firmware(self, firmware_name: str) -> List[str]:
        """Return all chip names that support the given firmware."""
        return [
            chip_name
            for chip_name, chip in self.chips.items()
            if firmware_name in chip.firmware_support
        ]

    def chips_with_bluetooth(self) -> List[str]:
        """Return chip names that include Bluetooth."""
        return [n for n, c in self.chips.items() if c.bluetooth]

    def chips_with_wifi(self) -> List[str]:
        """Return chip names that include Wi-Fi."""
        return [n for n, c in self.chips.items() if c.wifi]

    # -- Firmware queries ---------------------------------------------------

    def get_firmware(self, name: str) -> FirmwareType:
        """Return firmware type by name."""
        return self.firmware[name]

    def firmware_for_language(self, language: str) -> List[str]:
        """Return firmware names whose primary language matches."""
        return [
            fw_name
            for fw_name, fw in self.firmware.items()
            if language.lower() in fw.language.lower()
        ]

    # -- Project queries ----------------------------------------------------

    def get_project(self, name: str) -> RelatedProject:
        """Return related project by name."""
        return self.projects[name]

    def projects_for_chip(self, chip_name: str) -> List[str]:
        """Return project names that support the given chip."""
        return [
            proj_name
            for proj_name, proj in self.projects.items()
            if chip_name in proj.supported_chips
        ]

    # -- Weakness / capability analysis ------------------------------------

    def chip_weaknesses(self, chip_name: str) -> List[str]:
        """Return known weaknesses for a chip variant."""
        return self.chips[chip_name].weaknesses

    def firmware_weaknesses(self, firmware_name: str) -> List[str]:
        """Return known weaknesses for a firmware type."""
        return self.firmware[firmware_name].weaknesses

    # -- Summary -----------------------------------------------------------

    def summary(self) -> Dict[str, int]:
        """Return a count summary of all knowledge domains."""
        return {
            "chips": len(self.chips),
            "firmware_types": len(self.firmware),
            "related_projects": len(self.projects),
            "programming_languages": len(self.languages),
        }
