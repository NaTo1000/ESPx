# ESPx

**Full ESP32 Wireless Suite** — a comprehensive C++ framework for ESP32 development covering WiFi, Bluetooth/BLE, networking, security, OTA updates, GPIO, and more. Come have a look, add to it, make it next level ;)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## Features

| Module | Description |
|--------|-------------|
| **Core** | Application lifecycle, configuration store, structured logging, event loop |
| **WiFi** | Station/AP mode management, network scanning, auto-reconnect |
| **Bluetooth** | BLE scanning, advertising, GATT server with custom services |
| **Network** | HTTP client/server, TCP/UDP sockets, DNS resolver |
| **Security** | Encrypted vault, SHA-256 crypto, HMAC, key store |
| **OTA** | Over-the-air firmware updates with verification |
| **GPIO** | Digital I/O, PWM, ADC, temperature/humidity sensors |
| **Utils** | Ring buffer, high-res timer, UUID generator, Base64 codec |

## Project Structure

```
ESPx/
├── CMakeLists.txt                  # Build system
├── include/espx/                   # Public headers
│   ├── espx.hpp                    # Single-include header
│   ├── core/                       # App, Config, Logger, EventLoop
│   ├── wifi/                       # WiFiManager, Scanner, APMode
│   ├── bluetooth/                  # BLEManager, Scanner, Advertiser, GATT
│   ├── network/                    # HttpClient, HttpServer, TCP, UDP, DNS
│   ├── security/                   # Vault, Crypto, KeyStore
│   ├── ota/                        # OTAUpdater
│   ├── gpio/                       # Pin, ADC, Sensor
│   └── utils/                      # RingBuffer, Timer, UUID, Base64
├── src/                            # Implementation files
│   ├── core/                       # Core implementations
│   ├── wifi/                       # WiFi implementations
│   ├── bluetooth/                  # BLE implementations
│   ├── network/                    # Network implementations
│   ├── security/                   # Security implementations (real SHA-256)
│   ├── ota/                        # OTA implementations
│   ├── gpio/                       # GPIO implementations
│   └── utils/                      # Utility implementations
├── tests/                          # Unit tests (12 test suites)
├── examples/                       # Example applications
│   ├── wifi_scan/                  # WiFi scanning demo
│   ├── ble_scan/                   # BLE scanning + GATT demo
│   ├── http_server/                # HTTP server + client demo
│   └── secure_vault/               # Vault, crypto, Base64, UUID demo
├── LICENSE                         # Apache 2.0
└── README.md
```

## Building

### Prerequisites

- CMake 3.14 or later
- C++17 compatible compiler (GCC 8+, Clang 7+, MSVC 2017+)

### Build Commands

```bash
# Configure
mkdir build && cd build
cmake ..

# Build everything (library + tests + examples)
make -j$(nproc)

# Run tests
ctest --output-on-failure

# Run examples
./examples/wifi_scan/example_wifi_scan
./examples/ble_scan/example_ble_scan
./examples/http_server/example_http_server
./examples/secure_vault/example_secure_vault
```

### Build Options

| Option | Default | Description |
|--------|---------|-------------|
| `ESPX_BUILD_TESTS` | `ON` | Build the unit test suite |
| `ESPX_BUILD_EXAMPLES` | `ON` | Build example applications |
| `ESPX_HOST_MODE` | `ON` | Build for host (desktop) testing |

```bash
# Build only the library
cmake .. -DESPX_BUILD_TESTS=OFF -DESPX_BUILD_EXAMPLES=OFF
```

## Quick Start

### Single Include

```cpp
#include <espx/espx.hpp>  // Include everything
```

### WiFi Scanning

```cpp
#include <espx/wifi/scanner.hpp>
#include <iostream>

int main() {
    espx::wifi::Scanner scanner;
    auto results = scanner.scan_sync();

    for (const auto& ap : results) {
        std::cout << ap.ssid << " (" << (int)ap.rssi << " dBm)" << std::endl;
    }
}
```

### BLE GATT Server

```cpp
#include <espx/bluetooth/ble_manager.hpp>
#include <espx/bluetooth/gatt_server.hpp>

int main() {
    espx::bluetooth::BLEManager ble;
    ble.init({.device_name = "ESPx-Device"});

    espx::bluetooth::GATTServer server;
    espx::bluetooth::GATTService svc;
    svc.uuid = "12345678-1234-1234-1234-123456789ABC";

    espx::bluetooth::GATTCharacteristic temp;
    temp.uuid = "12345678-1234-1234-1234-123456789ABD";
    temp.readable = true;
    temp.notify = true;
    svc.characteristics.push_back(temp);

    server.add_service(svc);
    server.start();
}
```

### Secure Vault

```cpp
#include <espx/security/vault.hpp>
#include <iostream>

int main() {
    espx::security::Vault vault;
    vault.init("my-32-byte-master-key-here!!");

    vault.store("api_key", "sk-secret123");
    std::cout << vault.retrieve_string("api_key") << std::endl;
}
```

### HTTP Server

```cpp
#include <espx/network/http_server.hpp>

int main() {
    espx::network::HttpServer server;

    server.get("/api/status", [](const auto& req, auto& res) {
        res.json(R"({"status": "ok"})");
    });

    server.start({.port = 8080});
}
```

## Testing

The project includes 12 comprehensive test suites covering all modules:

```
test_ring_buffer   — Ring buffer push/pop/overwrite/clear
test_base64        — Base64 encode/decode/URL-safe/validation
test_uuid          — UUID generation/parsing/comparison
test_timer         — Timer stopwatch and timing accuracy
test_crypto        — SHA-256/HMAC/hex encoding/random/secure compare
test_config        — Config get/set/JSON serialization
test_event_loop    — Event registration/dispatch/deferred
test_logger        — Log levels/message counting
test_vault         — Encrypted storage/retrieval
test_key_store     — Key generation/import/management
test_wifi          — WiFi manager/scanner/AP mode
test_gpio          — GPIO pins/ADC/sensors
```

## Architecture

ESPx uses a modular architecture with clean separation of concerns:

- **Pimpl Pattern**: All classes use pointer-to-implementation for ABI stability and fast compilation
- **Host Mode**: All modules work in simulated host mode for desktop development and testing
- **Event-Driven**: The `EventLoop` provides a centralized event bus with synchronous and deferred dispatch
- **Thread-Safe**: Logger and core components use mutex-based synchronization
- **Zero External Dependencies**: No third-party libraries required

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
