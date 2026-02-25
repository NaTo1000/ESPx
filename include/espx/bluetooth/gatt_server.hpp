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
 * @struct GATTCharacteristic
 * @brief Defines a GATT characteristic.
 */
struct GATTCharacteristic {
    std::string uuid;              ///< Characteristic UUID
    std::string description;       ///< Human-readable description

    /// Permission flags
    bool readable = true;
    bool writable = false;
    bool notify = false;
    bool indicate = false;

    std::vector<uint8_t> value;    ///< Current value
    uint16_t max_length = 512;     ///< Maximum value length
};

/**
 * @struct GATTService
 * @brief Defines a GATT service with characteristics.
 */
struct GATTService {
    std::string uuid;              ///< Service UUID
    std::string description;       ///< Human-readable description
    bool primary = true;           ///< Primary or secondary service
    std::vector<GATTCharacteristic> characteristics;
};

/**
 * @class GATTServer
 * @brief BLE GATT server for exposing services and characteristics.
 *
 * Creates and manages a GATT server that exposes custom services
 * and characteristics to connected BLE clients. Supports read,
 * write, notify, and indicate operations.
 *
 * Example:
 * @code
 *   espx::bluetooth::GATTServer server;
 *
 *   GATTService svc;
 *   svc.uuid = "12345678-1234-1234-1234-123456789ABC";
 *   svc.description = "Custom Sensor Service";
 *
 *   GATTCharacteristic temp_char;
 *   temp_char.uuid = "12345678-1234-1234-1234-123456789ABD";
 *   temp_char.description = "Temperature";
 *   temp_char.readable = true;
 *   temp_char.notify = true;
 *
 *   svc.characteristics.push_back(temp_char);
 *   server.add_service(svc);
 *   server.start();
 * @endcode
 */
class GATTServer {
public:
    GATTServer();
    ~GATTServer();

    GATTServer(const GATTServer&) = delete;
    GATTServer& operator=(const GATTServer&) = delete;

    /**
     * @brief Add a GATT service.
     * @param service Service definition
     * @return true if the service was added successfully
     */
    bool add_service(const GATTService& service);

    /**
     * @brief Start the GATT server.
     * @return true if the server started successfully
     */
    bool start();

    /**
     * @brief Stop the GATT server.
     */
    void stop();

    /**
     * @brief Check if the server is running.
     * @return true if running
     */
    [[nodiscard]] bool is_running() const;

    /**
     * @brief Update a characteristic value.
     * @param service_uuid UUID of the containing service
     * @param char_uuid UUID of the characteristic
     * @param value New value
     * @return true if the value was updated
     */
    bool set_value(const std::string& service_uuid,
                   const std::string& char_uuid,
                   const std::vector<uint8_t>& value);

    /**
     * @brief Read a characteristic value.
     * @param service_uuid UUID of the containing service
     * @param char_uuid UUID of the characteristic
     * @return Current value (empty if not found)
     */
    [[nodiscard]] std::vector<uint8_t> get_value(
        const std::string& service_uuid,
        const std::string& char_uuid) const;

    /**
     * @brief Send a notification to all connected clients.
     * @param service_uuid UUID of the containing service
     * @param char_uuid UUID of the characteristic
     * @param value Data to notify
     * @return true if notification was sent
     */
    bool notify(const std::string& service_uuid,
                const std::string& char_uuid,
                const std::vector<uint8_t>& value);

    /**
     * @brief Get the number of registered services.
     * @return Service count
     */
    [[nodiscard]] size_t service_count() const;

    /// Register callback for read requests
    void on_read(std::function<void(const std::string& service_uuid,
                                    const std::string& char_uuid)> callback);

    /// Register callback for write requests
    void on_write(std::function<void(const std::string& service_uuid,
                                     const std::string& char_uuid,
                                     const std::vector<uint8_t>& value)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace bluetooth
}  // namespace espx
