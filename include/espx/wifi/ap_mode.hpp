// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace wifi {

/**
 * @struct APConfig
 * @brief Configuration for WiFi Access Point mode.
 */
struct APConfig {
    std::string ssid;                  ///< AP network name
    std::string password;              ///< AP password (empty = open)
    uint8_t channel = 1;               ///< WiFi channel (1-13)
    uint8_t max_connections = 4;       ///< Maximum simultaneous stations
    bool hidden = false;               ///< Hide the SSID
    std::string ip = "192.168.4.1";    ///< AP IP address
    std::string gateway = "192.168.4.1";
    std::string subnet = "255.255.255.0";
    bool enable_dhcp = true;           ///< Enable DHCP server
};

/**
 * @struct StationInfo
 * @brief Information about a connected station.
 */
struct StationInfo {
    std::string mac_address;   ///< MAC address of the station
    std::string ip_address;    ///< Assigned IP address
    int8_t rssi = 0;           ///< Signal strength
    uint32_t connected_time_s = 0; ///< Time since connection in seconds
};

/**
 * @class APMode
 * @brief WiFi Access Point mode manager.
 *
 * Creates and manages a WiFi access point, including DHCP server,
 * station tracking, and captive portal support.
 *
 * Example:
 * @code
 *   espx::wifi::APMode ap;
 *   espx::wifi::APConfig cfg;
 *   cfg.ssid = "ESPx-Config";
 *   cfg.password = "setup1234";
 *
 *   ap.on_station_connected([](const StationInfo& sta) {
 *       std::cout << "Station connected: " << sta.mac_address << std::endl;
 *   });
 *
 *   ap.start(cfg);
 * @endcode
 */
class APMode {
public:
    APMode();
    ~APMode();

    APMode(const APMode&) = delete;
    APMode& operator=(const APMode&) = delete;

    /**
     * @brief Start the Access Point.
     * @param config AP configuration
     * @return true if the AP was started successfully
     */
    bool start(const APConfig& config);

    /**
     * @brief Stop the Access Point.
     */
    void stop();

    /**
     * @brief Check if the AP is currently active.
     * @return true if AP is running
     */
    [[nodiscard]] bool is_active() const;

    /**
     * @brief Get list of currently connected stations.
     * @return Vector of connected station information
     */
    [[nodiscard]] std::vector<StationInfo> connected_stations() const;

    /**
     * @brief Get the number of connected stations.
     * @return Station count
     */
    [[nodiscard]] size_t station_count() const;

    /**
     * @brief Disconnect a specific station by MAC address.
     * @param mac_address MAC address of the station to disconnect
     * @return true if the station was disconnected
     */
    bool disconnect_station(const std::string& mac_address);

    /**
     * @brief Get the AP's IP address.
     * @return IP address string
     */
    [[nodiscard]] std::string ip_address() const;

    /// Register callback for station connection events
    void on_station_connected(std::function<void(const StationInfo&)> callback);

    /// Register callback for station disconnection events
    void on_station_disconnected(std::function<void(const std::string& mac)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace wifi
}  // namespace espx
