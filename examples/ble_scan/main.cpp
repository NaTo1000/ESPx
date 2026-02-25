// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include <cstdint>
#include <iostream>
#include <string>

#include "espx/bluetooth/ble_advertiser.hpp"
#include "espx/bluetooth/ble_manager.hpp"
#include "espx/bluetooth/ble_scanner.hpp"
#include "espx/bluetooth/gatt_server.hpp"
#include "espx/core/logger.hpp"

static const char* TAG = "BLEScan";

using espx::core::LogLevel;

static void log_info(const std::string& msg) {
    espx::core::Logger::instance().log(LogLevel::Info, TAG, __FILE__, __LINE__, msg);
}

int main() {
    auto& logger = espx::core::Logger::instance();
    logger.set_level(LogLevel::Info);

    log_info("=== ESPx BLE Scan Example ===");

    // Initialize BLE
    espx::bluetooth::BLEManager ble;
    espx::bluetooth::BLEConfig ble_cfg;
    ble_cfg.device_name = "ESPx-Demo";
    ble_cfg.mtu = 512;

    if (!ble.init(ble_cfg)) {
        logger.log(LogLevel::Error, TAG, __FILE__, __LINE__, "Failed to initialize BLE");
        return 1;
    }
    log_info("BLE initialized. Address: " + ble.address());

    // Create scanner with device-found callback
    espx::bluetooth::BLEScanner scanner;
    scanner.on_device_found([](const espx::bluetooth::BLEDeviceInfo& dev) {
        std::string name = dev.name.empty() ? "(unknown)" : dev.name;
        std::cout << "  [FOUND] " << name
                  << " addr=" << dev.address
                  << " rssi=" << static_cast<int>(dev.rssi)
                  << (dev.connectable ? " (connectable)" : "") << "\n";
    });

    scanner.on_scan_complete([](const std::vector<espx::bluetooth::BLEDeviceInfo>& devs) {
        std::cout << "\n  Scan finished. Total devices: " << devs.size() << "\n";
    });

    // Start scanning for 5 seconds
    espx::bluetooth::BLEScanConfig scan_cfg;
    scan_cfg.duration_ms = 5000;
    scan_cfg.active_scan = true;
    scan_cfg.filter_duplicates = true;

    log_info("Starting BLE scan for 5 seconds...");
    if (!scanner.start(scan_cfg)) {
        logger.log(LogLevel::Warn, TAG, __FILE__, __LINE__,
                   "Scanner start returned false (expected in host mode)");
    }

    // Print discovered devices
    auto devices = scanner.results();
    log_info("Discovered " + std::to_string(devices.size()) + " device(s)");

    for (const auto& dev : devices) {
        std::string name = dev.name.empty() ? "(unknown)" : dev.name;
        std::cout << "  - " << name << " [" << dev.address << "] "
                  << static_cast<int>(dev.rssi) << " dBm";
        for (const auto& uuid : dev.service_uuids) {
            std::cout << " svc:" << uuid;
        }
        std::cout << "\n";
    }

    // Create a GATT server with a custom service
    log_info("Setting up GATT server...");
    espx::bluetooth::GATTServer gatt;

    espx::bluetooth::GATTService svc;
    svc.uuid = "12345678-1234-1234-1234-123456789ABC";
    svc.description = "ESPx Demo Service";
    svc.primary = true;

    espx::bluetooth::GATTCharacteristic temp_char;
    temp_char.uuid = "12345678-1234-1234-1234-123456789ABD";
    temp_char.description = "Temperature";
    temp_char.readable = true;
    temp_char.notify = true;
    temp_char.value = {0x19, 0x00};  // 25°C as uint16

    svc.characteristics.push_back(temp_char);

    if (!gatt.add_service(svc)) {
        logger.log(LogLevel::Warn, TAG, __FILE__, __LINE__, "Failed to add GATT service");
    }

    if (!gatt.start()) {
        logger.log(LogLevel::Warn, TAG, __FILE__, __LINE__,
                   "GATT server start returned false (expected in host mode)");
    }
    log_info("GATT server running: " + std::string(gatt.is_running() ? "yes" : "no")
             + ", services: " + std::to_string(gatt.service_count()));

    // Start advertising
    espx::bluetooth::BLEAdvertiser advertiser;
    espx::bluetooth::AdvertiseConfig adv_cfg;
    adv_cfg.device_name = "ESPx-Demo";
    adv_cfg.connectable = true;
    adv_cfg.service_uuids = {svc.uuid};

    log_info("Starting BLE advertising...");
    if (!advertiser.start(adv_cfg)) {
        logger.log(LogLevel::Warn, TAG, __FILE__, __LINE__,
                   "Advertising start returned false (expected in host mode)");
    }
    log_info("Advertising: " + std::string(advertiser.is_advertising() ? "yes" : "no"));

    // Cleanup
    advertiser.stop();
    gatt.stop();
    ble.deinit();

    log_info("BLE scan example complete.");
    return 0;
}
