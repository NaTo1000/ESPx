// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace core {

/**
 * @class App
 * @brief Main application class for the ESPx framework.
 *
 * The App class serves as the central entry point for ESPx applications.
 * It manages the lifecycle of all subsystems, including WiFi, Bluetooth,
 * networking, security, and GPIO.
 *
 * Example usage:
 * @code
 *   espx::core::App app("MyESPApp");
 *   app.set_log_level(espx::core::LogLevel::Debug);
 *   app.on_ready([]() {
 *       // Application is initialized and ready
 *   });
 *   app.run();
 * @endcode
 */
class App {
public:
    /// Application state enumeration
    enum class State {
        Created,       ///< Application object created, not yet initialized
        Initializing,  ///< Subsystems are being initialized
        Running,       ///< Application is running
        Paused,        ///< Application is paused
        Stopping,      ///< Application is shutting down
        Stopped        ///< Application has been stopped
    };

    /**
     * @brief Construct a new App with the given name.
     * @param name Application name used for logging and identification
     */
    explicit App(const std::string& name);

    /// Destructor — cleans up all subsystems
    ~App();

    // Non-copyable, movable
    App(const App&) = delete;
    App& operator=(const App&) = delete;
    App(App&&) noexcept;
    App& operator=(App&&) noexcept;

    /**
     * @brief Initialize all subsystems.
     * @return true if initialization succeeded
     */
    bool init();

    /**
     * @brief Start the main application loop.
     *
     * This blocks until stop() is called or the application exits.
     */
    void run();

    /**
     * @brief Request the application to stop.
     */
    void stop();

    /**
     * @brief Register a callback invoked when the app is ready.
     * @param callback Function to call after initialization completes
     */
    void on_ready(std::function<void()> callback);

    /**
     * @brief Register a callback invoked when the app is stopping.
     * @param callback Function to call before shutdown
     */
    void on_shutdown(std::function<void()> callback);

    /**
     * @brief Register a periodic task.
     * @param name Descriptive name for the task
     * @param interval_ms Interval in milliseconds between invocations
     * @param task Function to execute periodically
     */
    void add_periodic_task(const std::string& name, uint32_t interval_ms,
                           std::function<void()> task);

    /// Get the application name
    [[nodiscard]] const std::string& name() const;

    /// Get the current application state
    [[nodiscard]] State state() const;

    /// Get uptime in milliseconds since run() was called
    [[nodiscard]] uint64_t uptime_ms() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace core
}  // namespace espx
