// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <memory>
#include <sstream>
#include <string>

namespace espx {
namespace core {

/**
 * @enum LogLevel
 * @brief Severity levels for the logging system.
 */
enum class LogLevel : uint8_t {
    Trace = 0,   ///< Verbose tracing information
    Debug = 1,   ///< Debug-level messages
    Info = 2,    ///< Informational messages
    Warn = 3,    ///< Warning messages
    Error = 4,   ///< Error messages
    Fatal = 5,   ///< Fatal/critical errors
    Off = 6      ///< Disable all logging
};

/**
 * @brief Convert LogLevel to its string representation.
 * @param level The log level
 * @return String name of the log level
 */
[[nodiscard]] const char* log_level_to_string(LogLevel level);

/**
 * @brief Parse a LogLevel from a string.
 * @param str String representation (case-insensitive)
 * @return Parsed log level, defaults to Info if unrecognized
 */
[[nodiscard]] LogLevel log_level_from_string(const std::string& str);

/**
 * @class Logger
 * @brief Thread-safe structured logging system for ESPx.
 *
 * Provides tagged, leveled logging with support for multiple
 * output sinks (serial, file, network). Each logger instance
 * is associated with a tag (typically the module or class name).
 *
 * Example:
 * @code
 *   auto& logger = espx::core::Logger::instance();
 *   logger.set_level(espx::core::LogLevel::Debug);
 *
 *   ESPX_LOG_INFO("WiFi", "Connected to %s", ssid.c_str());
 *   ESPX_LOG_ERROR("BLE", "Failed to start scanner: %d", err);
 * @endcode
 */
class Logger {
public:
    /**
     * @brief Get the singleton Logger instance.
     * @return Reference to the global logger
     */
    static Logger& instance();

    /**
     * @brief Set the minimum log level.
     * @param level Messages below this level are suppressed
     */
    void set_level(LogLevel level);

    /**
     * @brief Get the current minimum log level.
     * @return Current log level
     */
    [[nodiscard]] LogLevel level() const;

    /**
     * @brief Set the minimum log level for a specific tag.
     * @param tag The tag to configure
     * @param level Minimum level for this tag
     */
    void set_tag_level(const std::string& tag, LogLevel level);

    /**
     * @brief Log a message.
     * @param level Severity level
     * @param tag Module/component tag
     * @param file Source file name (__FILE__)
     * @param line Source line number (__LINE__)
     * @param message The formatted message string
     */
    void log(LogLevel level, const char* tag, const char* file,
             int line, const std::string& message);

    /**
     * @brief Enable or disable colored output.
     * @param enabled true for ANSI color codes
     */
    void set_color_enabled(bool enabled);

    /**
     * @brief Enable or disable timestamps in output.
     * @param enabled true to include timestamps
     */
    void set_timestamp_enabled(bool enabled);

    /**
     * @brief Enable logging to a file.
     * @param filepath Path to the log file
     * @param max_size_bytes Maximum file size before rotation (0 = no limit)
     * @return true if file logging was enabled successfully
     */
    bool enable_file_logging(const std::string& filepath,
                             size_t max_size_bytes = 0);

    /**
     * @brief Disable file logging.
     */
    void disable_file_logging();

    /**
     * @brief Get the total number of messages logged.
     * @return Message count
     */
    [[nodiscard]] uint64_t message_count() const;

    /**
     * @brief Get the number of error messages logged.
     * @return Error count
     */
    [[nodiscard]] uint64_t error_count() const;

private:
    Logger();
    ~Logger();
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    struct Impl;
    std::unique_ptr<Impl> impl_;
};

// ---- Logging macros ----

/// Internal helper — do not use directly
#define ESPX_LOG(level, tag, ...)                                           \
    do {                                                                     \
        auto& _logger = ::espx::core::Logger::instance();                   \
        if (static_cast<uint8_t>(level) >=                                   \
            static_cast<uint8_t>(_logger.level())) {                         \
            std::ostringstream _oss;                                         \
            _oss << __VA_ARGS__;                                             \
            _logger.log(level, tag, __FILE__, __LINE__, _oss.str());         \
        }                                                                    \
    } while (0)

/// Log at Trace level
#define ESPX_LOG_TRACE(tag, ...) \
    ESPX_LOG(::espx::core::LogLevel::Trace, tag, __VA_ARGS__)

/// Log at Debug level
#define ESPX_LOG_DEBUG(tag, ...) \
    ESPX_LOG(::espx::core::LogLevel::Debug, tag, __VA_ARGS__)

/// Log at Info level
#define ESPX_LOG_INFO(tag, ...) \
    ESPX_LOG(::espx::core::LogLevel::Info, tag, __VA_ARGS__)

/// Log at Warn level
#define ESPX_LOG_WARN(tag, ...) \
    ESPX_LOG(::espx::core::LogLevel::Warn, tag, __VA_ARGS__)

/// Log at Error level
#define ESPX_LOG_ERROR(tag, ...) \
    ESPX_LOG(::espx::core::LogLevel::Error, tag, __VA_ARGS__)

/// Log at Fatal level
#define ESPX_LOG_FATAL(tag, ...) \
    ESPX_LOG(::espx::core::LogLevel::Fatal, tag, __VA_ARGS__)

}  // namespace core
}  // namespace espx
