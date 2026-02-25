// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>

namespace espx {
namespace ota {

/**
 * @enum OTAState
 * @brief State of the OTA update process.
 */
enum class OTAState {
    Idle,
    Checking,
    Downloading,
    Verifying,
    Installing,
    Complete,
    Error
};

/**
 * @struct OTAProgress
 * @brief Progress information during an OTA update.
 */
struct OTAProgress {
    OTAState state = OTAState::Idle;
    uint32_t bytes_downloaded = 0;  ///< Bytes downloaded so far
    uint32_t total_bytes = 0;       ///< Total firmware size
    uint8_t percent = 0;            ///< Completion percentage (0-100)
    std::string status_message;     ///< Human-readable status
};

/**
 * @struct OTAConfig
 * @brief Configuration for OTA updates.
 */
struct OTAConfig {
    std::string url;                   ///< Firmware download URL
    std::string version_url;           ///< URL to check for new versions
    std::string current_version;       ///< Current firmware version string
    bool verify_checksum = true;       ///< Verify firmware SHA-256 checksum
    std::string expected_sha256;       ///< Expected SHA-256 hash (hex string)
    bool verify_signature = false;     ///< Verify firmware digital signature
    std::string signing_cert;          ///< PEM certificate for signature verification
    uint32_t timeout_ms = 60000;       ///< Download timeout in milliseconds
    bool auto_reboot = true;           ///< Reboot after successful update
    uint32_t check_interval_ms = 0;    ///< Auto-check interval (0 = manual only)
};

/**
 * @struct VersionInfo
 * @brief Information about an available firmware version.
 */
struct VersionInfo {
    std::string version;           ///< Version string
    std::string release_notes;     ///< Release notes / changelog
    uint32_t firmware_size = 0;    ///< Firmware size in bytes
    std::string download_url;      ///< Download URL
    std::string sha256;            ///< SHA-256 checksum
    bool update_available = false; ///< Whether this is newer than current
};

/**
 * @class OTAUpdater
 * @brief Over-The-Air firmware update manager.
 *
 * Manages firmware updates over WiFi, including version checking,
 * downloading, verification, and installation.
 *
 * Example:
 * @code
 *   espx::ota::OTAUpdater updater;
 *   espx::ota::OTAConfig cfg;
 *   cfg.url = "https://firmware.example.com/latest.bin";
 *   cfg.current_version = "1.0.0";
 *   cfg.verify_checksum = true;
 *
 *   updater.on_progress([](const OTAProgress& p) {
 *       std::cout << "OTA: " << (int)p.percent << "%" << std::endl;
 *   });
 *
 *   updater.start(cfg);
 * @endcode
 */
class OTAUpdater {
public:
    OTAUpdater();
    ~OTAUpdater();

    OTAUpdater(const OTAUpdater&) = delete;
    OTAUpdater& operator=(const OTAUpdater&) = delete;

    /**
     * @brief Start the OTA update process.
     * @param config OTA configuration
     * @return true if the update process started
     */
    bool start(const OTAConfig& config);

    /**
     * @brief Check for available updates without downloading.
     * @param config OTA configuration
     * @return Version information (check update_available field)
     */
    [[nodiscard]] VersionInfo check_for_update(const OTAConfig& config);

    /**
     * @brief Abort a running OTA update.
     */
    void abort();

    /**
     * @brief Get the current OTA state.
     * @return Current state
     */
    [[nodiscard]] OTAState state() const;

    /**
     * @brief Get the current progress.
     * @return Progress information
     */
    [[nodiscard]] OTAProgress progress() const;

    /**
     * @brief Reboot the device to apply an installed update.
     */
    void reboot();

    /**
     * @brief Mark the current firmware as valid.
     *
     * Call this after a successful boot to prevent rollback.
     */
    void confirm_update();

    /**
     * @brief Rollback to the previous firmware version.
     * @return true if rollback was initiated
     */
    bool rollback();

    /// Register callback for progress updates
    void on_progress(std::function<void(const OTAProgress&)> callback);

    /// Register callback for update completion
    void on_complete(std::function<void(bool success, const std::string& message)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace ota
}  // namespace espx
