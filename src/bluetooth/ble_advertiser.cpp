// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/bluetooth/ble_advertiser.hpp"

namespace espx {
namespace bluetooth {

struct BLEAdvertiser::Impl {
    AdvertiseConfig config;
    bool advertising{false};
};

BLEAdvertiser::BLEAdvertiser() : impl_(std::make_unique<Impl>()) {}
BLEAdvertiser::~BLEAdvertiser() = default;

bool BLEAdvertiser::start(const AdvertiseConfig& config) {
    impl_->config = config;
    impl_->advertising = true;
    return true;
}

void BLEAdvertiser::stop() {
    impl_->advertising = false;
}

bool BLEAdvertiser::is_advertising() const {
    return impl_->advertising;
}

void BLEAdvertiser::update_manufacturer_data(
    const std::vector<uint8_t>& manufacturer_data) {
    impl_->config.manufacturer_data = manufacturer_data;
}

void BLEAdvertiser::set_interval(uint16_t min_ms, uint16_t max_ms) {
    impl_->config.interval_min_ms = min_ms;
    impl_->config.interval_max_ms = max_ms;
}

}  // namespace bluetooth
}  // namespace espx
