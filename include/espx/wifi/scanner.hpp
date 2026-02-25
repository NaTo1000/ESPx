// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

#include "espx/wifi/wifi_manager.hpp"

namespace espx {
namespace wifi {

/**
 * @struct ScanResult
 * @brief Information about a discovered WiFi network.
 */
struct ScanResult {
    std::string ssid;          ///< Network SSID
    std::string bssid;         ///< BSSID (MAC) of the access point
    int8_t rssi = 0;           ///< Signal strength in dBm
    uint8_t channel = 0;       ///< Channel number
    WiFiAuthMode auth = WiFiAuthMode::Unknown;  ///< Authentication mode
    bool hidden = false;       ///< Whether the network is hidden

    /// Compare by signal strength (strongest first)
    bool operator<(const ScanResult& other) const { return rssi > other.rssi; }
};

/**
 * @struct ScanConfig
 * @brief Configuration for WiFi scanning.
 */
struct ScanConfig {
    bool show_hidden = false;      ///< Include hidden networks
    bool active_scan = true;       ///< Active scan (sends probe requests)
    uint32_t scan_time_ms = 1500;  ///< Max scan time per channel in ms
    uint8_t channel = 0;           ///< Specific channel (0 = scan all)
    std::string target_ssid;       ///< Scan for a specific SSID (empty = all)
};

/**
 * @class Scanner
 * @brief WiFi network scanner.
 *
 * Scans for available WiFi networks and reports results
 * via callbacks or synchronous polling.
 *
 * Example:
 * @code
 *   espx::wifi::Scanner scanner;
 *   auto results = scanner.scan_sync();
 *   for (const auto& ap : results) {
 *       std::cout << ap.ssid << " (" << (int)ap.rssi << " dBm)" << std::endl;
 *   }
 * @endcode
 */
class Scanner {
public:
    Scanner();
    ~Scanner();

    Scanner(const Scanner&) = delete;
    Scanner& operator=(const Scanner&) = delete;

    /**
     * @brief Start an asynchronous WiFi scan.
     * @param config Scan configuration
     * @return true if the scan was started
     */
    bool scan_async(const ScanConfig& config = {});

    /**
     * @brief Perform a synchronous (blocking) WiFi scan.
     * @param config Scan configuration
     * @return Vector of scan results sorted by signal strength
     */
    [[nodiscard]] std::vector<ScanResult> scan_sync(const ScanConfig& config = {});

    /**
     * @brief Check if a scan is currently in progress.
     * @return true if scanning
     */
    [[nodiscard]] bool is_scanning() const;

    /**
     * @brief Get results from the last completed scan.
     * @return Vector of scan results
     */
    [[nodiscard]] std::vector<ScanResult> results() const;

    /**
     * @brief Get the number of results from the last scan.
     * @return Count of discovered networks
     */
    [[nodiscard]] size_t result_count() const;

    /// Register callback for scan completion
    void on_scan_done(std::function<void(const std::vector<ScanResult>&)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace wifi
}  // namespace espx
