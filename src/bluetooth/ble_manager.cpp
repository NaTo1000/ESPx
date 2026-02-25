// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/bluetooth/ble_manager.hpp"

#include <string>

namespace espx {
namespace bluetooth {

struct BLEManager::Impl {
    BLEConfig config;
    BLEState current_state{BLEState::Off};
    std::string address;

    std::function<void(const BLEDeviceInfo&)> on_connected_cb;
    std::function<void(const std::string&)> on_disconnected_cb;
};

BLEManager::BLEManager() : impl_(std::make_unique<Impl>()) {}
BLEManager::~BLEManager() = default;

bool BLEManager::init(const BLEConfig& config) {
    impl_->config = config;
    impl_->current_state = BLEState::Ready;
    impl_->address = "AA:BB:CC:DD:EE:01";
    return true;
}

void BLEManager::deinit() {
    impl_->current_state = BLEState::Off;
}

BLEState BLEManager::state() const {
    return impl_->current_state;
}

std::string BLEManager::address() const {
    return impl_->address;
}

void BLEManager::set_device_name(const std::string& name) {
    impl_->config.device_name = name;
}

void BLEManager::set_tx_power(uint8_t level) {
    impl_->config.tx_power = level;
}

bool BLEManager::is_ready() const {
    return impl_->current_state == BLEState::Ready;
}

void BLEManager::on_connected(
    std::function<void(const BLEDeviceInfo&)> callback) {
    impl_->on_connected_cb = std::move(callback);
}

void BLEManager::on_disconnected(
    std::function<void(const std::string& address)> callback) {
    impl_->on_disconnected_cb = std::move(callback);
}

}  // namespace bluetooth
}  // namespace espx
