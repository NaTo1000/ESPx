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
 * @enum WiFiMode
 * @brief Operating mode for the WiFi subsystem.
 */
enum class WiFiMode {
    Off,          ///< WiFi disabled
    Station,      ///< Station (client) mode
    AccessPoint,  ///< Access Point (soft-AP) mode
    StationAP     ///< Simultaneous Station + AP mode
};

/**
 * @enum WiFiAuthMode
 * @brief Authentication modes for WiFi networks.
 */
enum class WiFiAuthMode {
    Open,
    WEP,
    WPA_PSK,
    WPA2_PSK,
    WPA_WPA2_PSK,
    WPA3_PSK,
    WPA2_Enterprise,
    Unknown
};

/**
 * @enum WiFiState
 * @brief Connection state for the WiFi station.
 */
enum class WiFiState {
    Disconnected,
    Connecting,
    Connected,
    ConnectionFailed,
    GotIP
};

/**
 * @struct WiFiConfig
 * @brief Configuration for WiFi connection.
 */
struct WiFiConfig {
    std::string ssid;             ///< Network SSID
    std::string password;         ///< Network password
    uint8_t channel = 0;          ///< Channel (0 = auto)
    WiFiAuthMode auth = WiFiAuthMode::WPA2_PSK;
    bool auto_reconnect = true;   ///< Reconnect on disconnect
    uint32_t reconnect_interval_ms = 5000;
    uint8_t max_retry = 10;       ///< Max reconnection attempts (0 = unlimited)
    std::string hostname;         ///< Device hostname on the network
    bool static_ip = false;       ///< Use static IP instead of DHCP
    std::string ip;               ///< Static IP address
    std::string gateway;          ///< Gateway address
    std::string subnet;           ///< Subnet mask
    std::string dns1;             ///< Primary DNS server
    std::string dns2;             ///< Secondary DNS server
};

/**
 * @struct WiFiNetworkInfo
 * @brief Information about a WiFi connection.
 */
struct WiFiNetworkInfo {
    std::string ssid;
    std::string bssid;
    std::string ip_address;
    std::string gateway;
    std::string subnet;
    std::string dns;
    int8_t rssi = 0;
    uint8_t channel = 0;
    WiFiAuthMode auth = WiFiAuthMode::Unknown;
};

/**
 * @class WiFiManager
 * @brief Manages WiFi station connections and IP acquisition.
 *
 * Handles connecting to WiFi networks, monitoring signal strength,
 * automatic reconnection, and IP configuration.
 *
 * Example:
 * @code
 *   espx::wifi::WiFiManager wifi;
 *   espx::wifi::WiFiConfig cfg;
 *   cfg.ssid = "MyNetwork";
 *   cfg.password = "password123";
 *
 *   wifi.on_connected([](const WiFiNetworkInfo& info) {
 *       std::cout << "Connected! IP: " << info.ip_address << std::endl;
 *   });
 *
 *   wifi.connect(cfg);
 * @endcode
 */
class WiFiManager {
public:
    WiFiManager();
    ~WiFiManager();

    WiFiManager(const WiFiManager&) = delete;
    WiFiManager& operator=(const WiFiManager&) = delete;

    /**
     * @brief Initialize the WiFi subsystem.
     * @param mode The WiFi operating mode
     * @return true if initialization succeeded
     */
    bool init(WiFiMode mode = WiFiMode::Station);

    /**
     * @brief Connect to a WiFi network.
     * @param config Connection configuration
     * @return true if connection was initiated successfully
     */
    bool connect(const WiFiConfig& config);

    /**
     * @brief Disconnect from the current network.
     */
    void disconnect();

    /**
     * @brief Check if currently connected to a network.
     * @return true if connected
     */
    [[nodiscard]] bool is_connected() const;

    /**
     * @brief Get the current WiFi state.
     * @return Current state
     */
    [[nodiscard]] WiFiState state() const;

    /**
     * @brief Get information about the current connection.
     * @return Network info (valid only when connected)
     */
    [[nodiscard]] WiFiNetworkInfo network_info() const;

    /**
     * @brief Get the current RSSI (signal strength).
     * @return RSSI in dBm
     */
    [[nodiscard]] int8_t rssi() const;

    /**
     * @brief Get the current IP address.
     * @return IP address string (empty if not connected)
     */
    [[nodiscard]] std::string ip_address() const;

    /**
     * @brief Get the MAC address.
     * @return MAC address string in "AA:BB:CC:DD:EE:FF" format
     */
    [[nodiscard]] std::string mac_address() const;

    /**
     * @brief Set the device hostname.
     * @param hostname Desired hostname
     */
    void set_hostname(const std::string& hostname);

    /// Register callback for connection events
    void on_connected(std::function<void(const WiFiNetworkInfo&)> callback);

    /// Register callback for disconnection events
    void on_disconnected(std::function<void(int reason)> callback);

    /// Register callback for IP acquisition
    void on_got_ip(std::function<void(const std::string&)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace wifi
}  // namespace espx
