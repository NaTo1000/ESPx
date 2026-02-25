// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

#include "espx/bluetooth/ble_manager.hpp"

namespace espx {
namespace bluetooth {

/**
 * @struct BLEScanConfig
 * @brief Configuration for BLE scanning.
 */
struct BLEScanConfig {
    uint32_t duration_ms = 5000;       ///< Scan duration in milliseconds (0 = continuous)
    bool active_scan = true;           ///< Send scan request for scan response data
    uint16_t interval = 0x50;          ///< Scan interval (in units of 0.625ms)
    uint16_t window = 0x30;            ///< Scan window (in units of 0.625ms)
    bool filter_duplicates = true;     ///< Filter duplicate advertisements
    int8_t rssi_threshold = -127;      ///< Minimum RSSI to report
    std::string filter_name;           ///< Filter by device name (empty = all)
    std::string filter_service_uuid;   ///< Filter by service UUID (empty = all)
};

/**
 * @class BLEScanner
 * @brief BLE device scanner.
 *
 * Scans for nearby BLE devices and reports discovered peripherals
 * via callbacks.
 *
 * Example:
 * @code
 *   espx::bluetooth::BLEScanner scanner;
 *   scanner.on_device_found([](const BLEDeviceInfo& dev) {
 *       std::cout << dev.name << " (" << dev.address
 *                 << ") RSSI: " << (int)dev.rssi << std::endl;
 *   });
 *
 *   BLEScanConfig cfg;
 *   cfg.duration_ms = 10000;
 *   scanner.start(cfg);
 * @endcode
 */
class BLEScanner {
public:
    BLEScanner();
    ~BLEScanner();

    BLEScanner(const BLEScanner&) = delete;
    BLEScanner& operator=(const BLEScanner&) = delete;

    /**
     * @brief Start BLE scanning.
     * @param config Scan configuration
     * @return true if scanning started successfully
     */
    bool start(const BLEScanConfig& config = {});

    /**
     * @brief Stop BLE scanning.
     */
    void stop();

    /**
     * @brief Check if scanning is currently active.
     * @return true if scanning
     */
    [[nodiscard]] bool is_scanning() const;

    /**
     * @brief Get all devices found in the current/last scan.
     * @return Vector of discovered devices
     */
    [[nodiscard]] std::vector<BLEDeviceInfo> results() const;

    /**
     * @brief Get the number of discovered devices.
     * @return Device count
     */
    [[nodiscard]] size_t result_count() const;

    /**
     * @brief Clear all scan results.
     */
    void clear_results();

    /// Register callback for each device found
    void on_device_found(std::function<void(const BLEDeviceInfo&)> callback);

    /// Register callback for scan completion
    void on_scan_complete(std::function<void(const std::vector<BLEDeviceInfo>&)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace bluetooth
}  // namespace espx
