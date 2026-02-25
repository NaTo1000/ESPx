// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/wifi/ap_mode.hpp"

#include <algorithm>
#include <string>
#include <vector>

namespace espx {
namespace wifi {

struct APMode::Impl {
    APConfig config;
    bool active{false};
    std::vector<StationInfo> stations;

    std::function<void(const StationInfo&)> on_station_connected_cb;
    std::function<void(const std::string& mac)> on_station_disconnected_cb;
};

APMode::APMode() : impl_(std::make_unique<Impl>()) {}
APMode::~APMode() = default;

bool APMode::start(const APConfig& config) {
    impl_->config = config;
    impl_->active = true;
    return true;
}

void APMode::stop() {
    impl_->active = false;
    impl_->stations.clear();
}

bool APMode::is_active() const {
    return impl_->active;
}

std::vector<StationInfo> APMode::connected_stations() const {
    return impl_->stations;
}

size_t APMode::station_count() const {
    return impl_->stations.size();
}

bool APMode::disconnect_station(const std::string& mac_address) {
    auto it = std::find_if(
        impl_->stations.begin(), impl_->stations.end(),
        [&mac_address](const StationInfo& s) {
            return s.mac_address == mac_address;
        });

    if (it == impl_->stations.end()) {
        return false;
    }

    impl_->stations.erase(it);

    if (impl_->on_station_disconnected_cb) {
        impl_->on_station_disconnected_cb(mac_address);
    }

    return true;
}

std::string APMode::ip_address() const {
    return impl_->config.ip;
}

void APMode::on_station_connected(
    std::function<void(const StationInfo&)> callback) {
    impl_->on_station_connected_cb = std::move(callback);
}

void APMode::on_station_disconnected(
    std::function<void(const std::string& mac)> callback) {
    impl_->on_station_disconnected_cb = std::move(callback);
}

}  // namespace wifi
}  // namespace espx
