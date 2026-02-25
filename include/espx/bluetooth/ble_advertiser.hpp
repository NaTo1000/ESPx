// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace bluetooth {

/**
 * @struct AdvertiseConfig
 * @brief Configuration for BLE advertising.
 */
struct AdvertiseConfig {
    std::string device_name;                    ///< Device name to advertise
    uint16_t interval_min_ms = 100;             ///< Minimum advertising interval (ms)
    uint16_t interval_max_ms = 200;             ///< Maximum advertising interval (ms)
    bool connectable = true;                    ///< Allow connections
    bool scannable = true;                      ///< Allow scan requests
    std::vector<std::string> service_uuids;     ///< Service UUIDs to advertise
    std::vector<uint8_t> manufacturer_data;     ///< Custom manufacturer data
    int8_t tx_power = 3;                        ///< Transmit power (0-7)
    uint16_t appearance = 0;                    ///< GAP appearance value
};

/**
 * @class BLEAdvertiser
 * @brief BLE advertisement manager.
 *
 * Controls BLE advertising, allowing the device to be discoverable
 * by other BLE devices. Supports custom advertisement data,
 * service UUIDs, and manufacturer-specific data.
 *
 * Example:
 * @code
 *   espx::bluetooth::BLEAdvertiser adv;
 *   espx::bluetooth::AdvertiseConfig cfg;
 *   cfg.device_name = "ESPx-Sensor";
 *   cfg.service_uuids = {"180D"};  // Heart Rate Service
 *   cfg.connectable = true;
 *   adv.start(cfg);
 * @endcode
 */
class BLEAdvertiser {
public:
    BLEAdvertiser();
    ~BLEAdvertiser();

    BLEAdvertiser(const BLEAdvertiser&) = delete;
    BLEAdvertiser& operator=(const BLEAdvertiser&) = delete;

    /**
     * @brief Start advertising.
     * @param config Advertising configuration
     * @return true if advertising started
     */
    bool start(const AdvertiseConfig& config);

    /**
     * @brief Stop advertising.
     */
    void stop();

    /**
     * @brief Check if advertising is active.
     * @return true if advertising
     */
    [[nodiscard]] bool is_advertising() const;

    /**
     * @brief Update the advertising data without restarting.
     * @param manufacturer_data New manufacturer-specific data
     */
    void update_manufacturer_data(const std::vector<uint8_t>& manufacturer_data);

    /**
     * @brief Set the advertising interval.
     * @param min_ms Minimum interval in milliseconds
     * @param max_ms Maximum interval in milliseconds
     */
    void set_interval(uint16_t min_ms, uint16_t max_ms);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace bluetooth
}  // namespace espx
