// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/ota/ota_updater.hpp"

#include <mutex>

namespace espx {
namespace ota {

struct OTAUpdater::Impl {
    OTAState current_state = OTAState::Idle;
    OTAProgress current_progress;
    OTAConfig config;
    bool confirmed = false;
    std::function<void(const OTAProgress&)> progress_cb;
    std::function<void(bool, const std::string&)> complete_cb;
    mutable std::mutex mutex;

    void set_state(OTAState state, const std::string& msg,
                   uint8_t percent = 0, uint32_t downloaded = 0) {
        current_state = state;
        current_progress.state = state;
        current_progress.status_message = msg;
        current_progress.percent = percent;
        current_progress.bytes_downloaded = downloaded;
        if (progress_cb) {
            progress_cb(current_progress);
        }
    }
};

OTAUpdater::OTAUpdater() : impl_(std::make_unique<Impl>()) {}
OTAUpdater::~OTAUpdater() = default;

bool OTAUpdater::start(const OTAConfig& config) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (impl_->current_state != OTAState::Idle &&
        impl_->current_state != OTAState::Error &&
        impl_->current_state != OTAState::Complete) {
        return false;
    }

    impl_->config = config;
    uint32_t fw_size = 1024 * 512;  // simulated 512KB firmware
    impl_->current_progress.total_bytes = fw_size;

    impl_->set_state(OTAState::Checking, "Checking for update...", 0);
    impl_->set_state(OTAState::Downloading, "Downloading firmware...",
                     25, fw_size / 4);
    impl_->set_state(OTAState::Downloading, "Downloading firmware...",
                     50, fw_size / 2);
    impl_->set_state(OTAState::Downloading, "Downloading firmware...",
                     75, fw_size * 3 / 4);
    impl_->set_state(OTAState::Downloading, "Download complete",
                     100, fw_size);
    impl_->set_state(OTAState::Verifying, "Verifying firmware...", 100,
                     fw_size);
    impl_->set_state(OTAState::Installing, "Installing firmware...", 100,
                     fw_size);
    impl_->set_state(OTAState::Complete, "Update complete", 100, fw_size);

    if (impl_->complete_cb) {
        impl_->complete_cb(true, "Update installed successfully");
    }

    return true;
}

VersionInfo OTAUpdater::check_for_update(const OTAConfig& config) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    VersionInfo info;
    info.version = "2.0.0";
    info.release_notes = "Simulated update with bug fixes and improvements.";
    info.firmware_size = 1024 * 512;
    info.download_url = config.url;
    info.sha256 = "abcdef0123456789abcdef0123456789"
                  "abcdef0123456789abcdef0123456789";
    info.update_available =
        !config.current_version.empty() &&
        config.current_version != info.version;
    return info;
}

void OTAUpdater::abort() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (impl_->current_state == OTAState::Downloading ||
        impl_->current_state == OTAState::Checking) {
        impl_->set_state(OTAState::Error, "Update aborted by user");
        if (impl_->complete_cb) {
            impl_->complete_cb(false, "Update aborted by user");
        }
    }
}

OTAState OTAUpdater::state() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->current_state;
}

OTAProgress OTAUpdater::progress() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->current_progress;
}

void OTAUpdater::reboot() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    // In host mode, just reset state to Idle
    impl_->set_state(OTAState::Idle, "Rebooted (simulated)");
    impl_->confirmed = false;
}

void OTAUpdater::confirm_update() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->confirmed = true;
}

bool OTAUpdater::rollback() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (impl_->confirmed) return false;
    impl_->set_state(OTAState::Idle, "Rolled back to previous version");
    return true;
}

void OTAUpdater::on_progress(
    std::function<void(const OTAProgress&)> callback) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->progress_cb = std::move(callback);
}

void OTAUpdater::on_complete(
    std::function<void(bool success, const std::string& message)> callback) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->complete_cb = std::move(callback);
}

}  // namespace ota
}  // namespace espx
