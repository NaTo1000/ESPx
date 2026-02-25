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
 * @enum BLEState
 * @brief State of the BLE subsystem.
 */
enum class BLEState {
    Off,
    Initializing,
    Ready,
    Scanning,
    Advertising,
    Connected,
    Error
};

/**
 * @struct BLEConfig
 * @brief Configuration for the BLE subsystem.
 */
struct BLEConfig {
    std::string device_name = "ESPx";  ///< BLE device name
    uint16_t mtu = 512;                ///< Maximum transmission unit
    bool enable_bonding = true;        ///< Enable secure bonding
    uint8_t tx_power = 3;              ///< Transmit power level (0-7)
};

/**
 * @struct BLEDeviceInfo
 * @brief Information about a BLE device.
 */
struct BLEDeviceInfo {
    std::string name;              ///< Device name (may be empty)
    std::string address;           ///< BLE address
    int8_t rssi = 0;               ///< Signal strength in dBm
    uint16_t appearance = 0;       ///< GAP appearance value
    bool connectable = false;      ///< Whether the device is connectable
    std::vector<std::string> service_uuids;  ///< Advertised service UUIDs
    std::vector<uint8_t> manufacturer_data;  ///< Manufacturer-specific data
};

/**
 * @class BLEManager
 * @brief Central BLE management class.
 *
 * Manages the Bluetooth Low Energy subsystem, including initialization,
 * connection management, and power control.
 *
 * Example:
 * @code
 *   espx::bluetooth::BLEManager ble;
 *   espx::bluetooth::BLEConfig cfg;
 *   cfg.device_name = "ESPx-Device";
 *   ble.init(cfg);
 * @endcode
 */
class BLEManager {
public:
    BLEManager();
    ~BLEManager();

    BLEManager(const BLEManager&) = delete;
    BLEManager& operator=(const BLEManager&) = delete;

    /**
     * @brief Initialize the BLE subsystem.
     * @param config BLE configuration
     * @return true if initialization succeeded
     */
    bool init(const BLEConfig& config = {});

    /**
     * @brief Deinitialize and release BLE resources.
     */
    void deinit();

    /**
     * @brief Get the current BLE state.
     * @return Current state
     */
    [[nodiscard]] BLEState state() const;

    /**
     * @brief Get the local BLE address.
     * @return BLE address string
     */
    [[nodiscard]] std::string address() const;

    /**
     * @brief Set the device name.
     * @param name New device name
     */
    void set_device_name(const std::string& name);

    /**
     * @brief Set the transmit power level.
     * @param level Power level (0-7, where 7 is maximum)
     */
    void set_tx_power(uint8_t level);

    /**
     * @brief Check if BLE is initialized and ready.
     * @return true if ready
     */
    [[nodiscard]] bool is_ready() const;

    /// Register callback for connection events
    void on_connected(std::function<void(const BLEDeviceInfo&)> callback);

    /// Register callback for disconnection events
    void on_disconnected(std::function<void(const std::string& address)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace bluetooth
}  // namespace espx
