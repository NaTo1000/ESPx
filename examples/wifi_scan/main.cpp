// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include <cstdint>
#include <iostream>
#include <string>

#include "espx/core/logger.hpp"
#include "espx/wifi/scanner.hpp"
#include "espx/wifi/wifi_manager.hpp"

static const char* TAG = "WiFiScan";

using espx::core::LogLevel;

static void log_info(const std::string& msg) {
    espx::core::Logger::instance().log(LogLevel::Info, TAG, __FILE__, __LINE__, msg);
}

static const char* auth_mode_str(espx::wifi::WiFiAuthMode mode) {
    switch (mode) {
        case espx::wifi::WiFiAuthMode::Open:           return "Open";
        case espx::wifi::WiFiAuthMode::WEP:            return "WEP";
        case espx::wifi::WiFiAuthMode::WPA_PSK:        return "WPA-PSK";
        case espx::wifi::WiFiAuthMode::WPA2_PSK:       return "WPA2-PSK";
        case espx::wifi::WiFiAuthMode::WPA_WPA2_PSK:   return "WPA/WPA2-PSK";
        case espx::wifi::WiFiAuthMode::WPA3_PSK:       return "WPA3-PSK";
        case espx::wifi::WiFiAuthMode::WPA2_Enterprise: return "WPA2-Enterprise";
        case espx::wifi::WiFiAuthMode::Unknown:         return "Unknown";
    }
    return "Unknown";
}

int main() {
    // Configure logger
    auto& logger = espx::core::Logger::instance();
    logger.set_level(LogLevel::Info);

    log_info("=== ESPx WiFi Scan Example ===");

    // Initialize WiFi in Station mode
    espx::wifi::WiFiManager wifi;
    if (!wifi.init(espx::wifi::WiFiMode::Station)) {
        logger.log(LogLevel::Error, TAG, __FILE__, __LINE__, "Failed to initialize WiFi");
        return 1;
    }
    log_info("WiFi initialized in Station mode");

    // Perform a synchronous scan
    espx::wifi::Scanner scanner;
    log_info("Starting WiFi scan...");

    auto results = scanner.scan_sync();
    log_info("Scan complete. Found " + std::to_string(results.size()) + " networks:");

    std::cout << "\n";
    std::cout << "  # | SSID                             | RSSI | Ch | Auth\n";
    std::cout << "----+----------------------------------+------+----+----------------\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& ap = results[i];
        std::string ssid = ap.ssid.empty() ? "(hidden)" : ap.ssid;
        if (ssid.size() < 32) {
            ssid.resize(32, ' ');
        }
        std::cout << "  " << (i + 1) << " | " << ssid << " | "
                  << static_cast<int>(ap.rssi) << " | "
                  << static_cast<int>(ap.channel) << "  | "
                  << auth_mode_str(ap.auth) << "\n";
    }
    std::cout << "\n";

    // Connect to a network
    espx::wifi::WiFiConfig cfg;
    cfg.ssid = "MyNetwork";
    cfg.password = "MyPassword123";

    wifi.on_connected([](const espx::wifi::WiFiNetworkInfo& info) {
        std::cout << "  Connected callback: IP=" << info.ip_address << "\n";
    });

    log_info("Connecting to \"" + cfg.ssid + "\"...");
    if (!wifi.connect(cfg)) {
        logger.log(LogLevel::Warn, TAG, __FILE__, __LINE__,
                   "Connection initiation failed (expected in host mode)");
    }

    // Print connection info
    auto info = wifi.network_info();
    log_info("Connection info:");
    std::cout << "  IP:      " << wifi.ip_address() << "\n";
    std::cout << "  MAC:     " << wifi.mac_address() << "\n";
    std::cout << "  RSSI:    " << static_cast<int>(wifi.rssi()) << " dBm\n";

    wifi.disconnect();
    log_info("WiFi scan example complete.");

    return 0;
}
