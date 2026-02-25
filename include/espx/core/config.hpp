// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <variant>
#include <vector>

namespace espx {
namespace core {

/**
 * @class Config
 * @brief Persistent configuration store for ESPx applications.
 *
 * Provides a hierarchical key-value store that can be serialized
 * to and from JSON. On ESP32, this is backed by NVS (Non-Volatile Storage).
 * In host mode, it persists to a local JSON file.
 *
 * Supports string, integer, floating-point, and boolean values,
 * as well as nested configuration sections.
 *
 * Example:
 * @code
 *   espx::core::Config cfg;
 *   cfg.set("wifi.ssid", "MyNetwork");
 *   cfg.set("wifi.password", "secret123");
 *   cfg.set("wifi.channel", 6);
 *   cfg.set("debug.enabled", true);
 *   cfg.save("config.json");
 * @endcode
 */
class Config {
public:
    /// Supported value types
    using Value = std::variant<std::string, int64_t, double, bool>;

    Config();
    ~Config();

    Config(const Config&);
    Config& operator=(const Config&);
    Config(Config&&) noexcept;
    Config& operator=(Config&&) noexcept;

    /**
     * @brief Set a configuration value.
     * @param key Dot-separated key path (e.g., "wifi.ssid")
     * @param value The value to store
     */
    void set(const std::string& key, const Value& value);

    /**
     * @brief Get a string value.
     * @param key Dot-separated key path
     * @param default_val Default value if key does not exist
     * @return The stored string or default_val
     */
    [[nodiscard]] std::string get_string(const std::string& key,
                                         const std::string& default_val = "") const;

    /**
     * @brief Get an integer value.
     * @param key Dot-separated key path
     * @param default_val Default value if key does not exist
     * @return The stored integer or default_val
     */
    [[nodiscard]] int64_t get_int(const std::string& key,
                                  int64_t default_val = 0) const;

    /**
     * @brief Get a double value.
     * @param key Dot-separated key path
     * @param default_val Default value if key does not exist
     * @return The stored double or default_val
     */
    [[nodiscard]] double get_double(const std::string& key,
                                    double default_val = 0.0) const;

    /**
     * @brief Get a boolean value.
     * @param key Dot-separated key path
     * @param default_val Default value if key does not exist
     * @return The stored boolean or default_val
     */
    [[nodiscard]] bool get_bool(const std::string& key,
                                bool default_val = false) const;

    /**
     * @brief Check if a key exists.
     * @param key Dot-separated key path
     * @return true if the key exists
     */
    [[nodiscard]] bool has(const std::string& key) const;

    /**
     * @brief Remove a key.
     * @param key Dot-separated key path
     * @return true if the key was removed
     */
    bool remove(const std::string& key);

    /**
     * @brief Get all keys matching a prefix.
     * @param prefix Key prefix to match (e.g., "wifi.")
     * @return Vector of matching keys
     */
    [[nodiscard]] std::vector<std::string> keys(const std::string& prefix = "") const;

    /// Remove all configuration entries
    void clear();

    /// Get the total number of entries
    [[nodiscard]] size_t size() const;

    /**
     * @brief Load configuration from a JSON file.
     * @param filepath Path to the JSON file
     * @return true if loading succeeded
     */
    bool load(const std::string& filepath);

    /**
     * @brief Save configuration to a JSON file.
     * @param filepath Path to the JSON file
     * @return true if saving succeeded
     */
    bool save(const std::string& filepath) const;

    /**
     * @brief Serialize configuration to a JSON string.
     * @return JSON representation of the config
     */
    [[nodiscard]] std::string to_json() const;

    /**
     * @brief Deserialize configuration from a JSON string.
     * @param json JSON string to parse
     * @return true if parsing succeeded
     */
    bool from_json(const std::string& json);

    /**
     * @brief Register a callback for value changes.
     * @param key Key to watch (or empty string for all changes)
     * @param callback Function called when the value changes
     */
    void on_change(const std::string& key,
                   std::function<void(const std::string&, const Value&)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace core
}  // namespace espx
