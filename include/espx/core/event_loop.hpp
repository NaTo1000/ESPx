// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>

namespace espx {
namespace core {

/**
 * @brief Event identifier type.
 */
using EventId = uint32_t;

/**
 * @brief Opaque event data passed to handlers.
 */
struct EventData {
    EventId id;               ///< Event identifier
    const void* data;         ///< Pointer to event-specific data
    size_t data_size;         ///< Size of the data in bytes
    const char* source_tag;   ///< Tag of the module that posted the event
};

/**
 * @brief Event handler callback type.
 */
using EventHandler = std::function<void(const EventData&)>;

/**
 * @brief Handle returned when registering an event listener.
 *
 * Use this to unregister the listener later.
 */
using ListenerHandle = uint64_t;

/**
 * @class EventLoop
 * @brief Asynchronous event dispatch system.
 *
 * Provides a centralized event bus where modules can post events
 * and register handlers. Supports both synchronous and deferred
 * (queued) event dispatch.
 *
 * Predefined event IDs for core system events:
 * - ESPX_EVENT_WIFI_CONNECTED      (0x1001)
 * - ESPX_EVENT_WIFI_DISCONNECTED   (0x1002)
 * - ESPX_EVENT_WIFI_SCAN_DONE      (0x1003)
 * - ESPX_EVENT_BLE_CONNECTED       (0x2001)
 * - ESPX_EVENT_BLE_DISCONNECTED    (0x2002)
 * - ESPX_EVENT_BLE_SCAN_RESULT     (0x2003)
 * - ESPX_EVENT_HTTP_REQUEST        (0x3001)
 * - ESPX_EVENT_OTA_START           (0x4001)
 * - ESPX_EVENT_OTA_PROGRESS        (0x4002)
 * - ESPX_EVENT_OTA_COMPLETE        (0x4003)
 * - ESPX_EVENT_GPIO_INTERRUPT      (0x5001)
 *
 * Example:
 * @code
 *   auto& loop = espx::core::EventLoop::instance();
 *   auto handle = loop.on(ESPX_EVENT_WIFI_CONNECTED, [](const EventData& e) {
 *       // Handle WiFi connected event
 *   });
 *   loop.post(ESPX_EVENT_WIFI_CONNECTED, nullptr, 0, "WiFi");
 * @endcode
 */
class EventLoop {
public:
    /**
     * @brief Get the singleton EventLoop instance.
     * @return Reference to the global event loop
     */
    static EventLoop& instance();

    /**
     * @brief Register a handler for a specific event.
     * @param event_id The event to listen for
     * @param handler Callback function
     * @return Handle that can be used to unregister
     */
    ListenerHandle on(EventId event_id, EventHandler handler);

    /**
     * @brief Register a one-shot handler that fires once then auto-unregisters.
     * @param event_id The event to listen for
     * @param handler Callback function
     * @return Handle that can be used to unregister before it fires
     */
    ListenerHandle once(EventId event_id, EventHandler handler);

    /**
     * @brief Register a handler for all events.
     * @param handler Callback function
     * @return Handle that can be used to unregister
     */
    ListenerHandle on_any(EventHandler handler);

    /**
     * @brief Unregister an event handler.
     * @param handle The handle returned by on() / once() / on_any()
     */
    void off(ListenerHandle handle);

    /**
     * @brief Post an event synchronously (handlers run immediately).
     * @param event_id Event identifier
     * @param data Pointer to event data (can be nullptr)
     * @param data_size Size of the data
     * @param source_tag Tag identifying the source module
     */
    void post(EventId event_id, const void* data, size_t data_size,
              const char* source_tag);

    /**
     * @brief Queue an event for deferred dispatch.
     * @param event_id Event identifier
     * @param data Pointer to event data (will be copied)
     * @param data_size Size of the data
     * @param source_tag Tag identifying the source module
     */
    void post_deferred(EventId event_id, const void* data,
                       size_t data_size, const char* source_tag);

    /**
     * @brief Process all queued deferred events.
     *
     * Call this from the main loop to dispatch queued events.
     */
    void process_pending();

    /**
     * @brief Get the number of pending deferred events.
     * @return Count of queued events
     */
    [[nodiscard]] size_t pending_count() const;

    /**
     * @brief Get the number of registered listeners.
     * @return Listener count
     */
    [[nodiscard]] size_t listener_count() const;

    /**
     * @brief Remove all listeners and pending events.
     */
    void reset();

private:
    EventLoop();
    ~EventLoop();
    EventLoop(const EventLoop&) = delete;
    EventLoop& operator=(const EventLoop&) = delete;

    struct Impl;
    std::unique_ptr<Impl> impl_;
};

// ---- Predefined System Event IDs ----

constexpr EventId ESPX_EVENT_WIFI_CONNECTED    = 0x1001;
constexpr EventId ESPX_EVENT_WIFI_DISCONNECTED = 0x1002;
constexpr EventId ESPX_EVENT_WIFI_SCAN_DONE    = 0x1003;
constexpr EventId ESPX_EVENT_WIFI_AP_START     = 0x1004;
constexpr EventId ESPX_EVENT_WIFI_AP_STOP      = 0x1005;
constexpr EventId ESPX_EVENT_WIFI_AP_STACONN   = 0x1006;

constexpr EventId ESPX_EVENT_BLE_CONNECTED     = 0x2001;
constexpr EventId ESPX_EVENT_BLE_DISCONNECTED  = 0x2002;
constexpr EventId ESPX_EVENT_BLE_SCAN_RESULT   = 0x2003;
constexpr EventId ESPX_EVENT_BLE_ADV_START     = 0x2004;
constexpr EventId ESPX_EVENT_BLE_GATT_READ     = 0x2005;
constexpr EventId ESPX_EVENT_BLE_GATT_WRITE    = 0x2006;

constexpr EventId ESPX_EVENT_HTTP_REQUEST      = 0x3001;
constexpr EventId ESPX_EVENT_HTTP_RESPONSE     = 0x3002;
constexpr EventId ESPX_EVENT_TCP_CONNECTED     = 0x3003;
constexpr EventId ESPX_EVENT_TCP_DATA          = 0x3004;
constexpr EventId ESPX_EVENT_UDP_DATA          = 0x3005;

constexpr EventId ESPX_EVENT_OTA_START         = 0x4001;
constexpr EventId ESPX_EVENT_OTA_PROGRESS      = 0x4002;
constexpr EventId ESPX_EVENT_OTA_COMPLETE      = 0x4003;
constexpr EventId ESPX_EVENT_OTA_ERROR         = 0x4004;

constexpr EventId ESPX_EVENT_GPIO_INTERRUPT    = 0x5001;
constexpr EventId ESPX_EVENT_ADC_READING       = 0x5002;
constexpr EventId ESPX_EVENT_SENSOR_DATA       = 0x5003;

constexpr EventId ESPX_EVENT_USER_BASE         = 0x8000;

}  // namespace core
}  // namespace espx
