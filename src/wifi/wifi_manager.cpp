// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/wifi/wifi_manager.hpp"

#include <algorithm>
#include <string>

namespace espx {
namespace wifi {

struct WiFiManager::Impl {
    WiFiConfig config;
    WiFiState current_state{WiFiState::Disconnected};
    WiFiNetworkInfo info;
    WiFiMode mode{WiFiMode::Off};
    std::string hostname;

    std::function<void(const WiFiNetworkInfo&)> on_connected_cb;
    std::function<void(int reason)> on_disconnected_cb;
    std::function<void(const std::string&)> on_got_ip_cb;
};

WiFiManager::WiFiManager() : impl_(std::make_unique<Impl>()) {}
WiFiManager::~WiFiManager() = default;

bool WiFiManager::init(WiFiMode mode) {
    impl_->mode = mode;
    return true;
}

bool WiFiManager::connect(const WiFiConfig& config) {
    impl_->config = config;
    impl_->current_state = WiFiState::Connecting;

    // Simulate successful connection
    impl_->current_state = WiFiState::Connected;

    impl_->info.ssid = config.ssid;
    impl_->info.bssid = "00:11:22:33:44:55";
    impl_->info.ip_address = "192.168.1.100";
    impl_->info.gateway = "192.168.1.1";
    impl_->info.subnet = "255.255.255.0";
    impl_->info.dns = "8.8.8.8";
    impl_->info.rssi = -45;
    impl_->info.channel = config.channel != 0 ? config.channel : 6;
    impl_->info.auth = config.auth;

    if (impl_->on_connected_cb) {
        impl_->on_connected_cb(impl_->info);
    }

    impl_->current_state = WiFiState::GotIP;

    if (impl_->on_got_ip_cb) {
        impl_->on_got_ip_cb(impl_->info.ip_address);
    }

    return true;
}

void WiFiManager::disconnect() {
    impl_->current_state = WiFiState::Disconnected;
    impl_->info = WiFiNetworkInfo{};

    if (impl_->on_disconnected_cb) {
        impl_->on_disconnected_cb(0);
    }
}

bool WiFiManager::is_connected() const {
    return impl_->current_state == WiFiState::Connected ||
           impl_->current_state == WiFiState::GotIP;
}

WiFiState WiFiManager::state() const {
    return impl_->current_state;
}

WiFiNetworkInfo WiFiManager::network_info() const {
    return impl_->info;
}

int8_t WiFiManager::rssi() const {
    return -45;
}

std::string WiFiManager::ip_address() const {
    return impl_->info.ip_address;
}

std::string WiFiManager::mac_address() const {
    return "AA:BB:CC:DD:EE:FF";
}

void WiFiManager::set_hostname(const std::string& hostname) {
    impl_->hostname = hostname;
}

void WiFiManager::on_connected(
    std::function<void(const WiFiNetworkInfo&)> callback) {
    impl_->on_connected_cb = std::move(callback);
}

void WiFiManager::on_disconnected(std::function<void(int reason)> callback) {
    impl_->on_disconnected_cb = std::move(callback);
}

void WiFiManager::on_got_ip(std::function<void(const std::string&)> callback) {
    impl_->on_got_ip_cb = std::move(callback);
}

}  // namespace wifi
}  // namespace espx
