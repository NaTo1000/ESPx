// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/bluetooth/ble_scanner.hpp"

#include <vector>

namespace espx {
namespace bluetooth {

struct BLEScanner::Impl {
    std::vector<BLEDeviceInfo> scan_results;
    bool scanning{false};

    std::function<void(const BLEDeviceInfo&)> on_device_found_cb;
    std::function<void(const std::vector<BLEDeviceInfo>&)> on_scan_complete_cb;

    std::vector<BLEDeviceInfo> generate_simulated_devices() {
        std::vector<BLEDeviceInfo> devices;

        BLEDeviceInfo dev1;
        dev1.name = "ESPx-Sensor";
        dev1.address = "11:22:33:44:55:01";
        dev1.rssi = -42;
        dev1.connectable = true;
        devices.push_back(dev1);

        BLEDeviceInfo dev2;
        dev2.name = "ESPx-Light";
        dev2.address = "11:22:33:44:55:02";
        dev2.rssi = -58;
        dev2.connectable = true;
        devices.push_back(dev2);

        BLEDeviceInfo dev3;
        dev3.name = "ESPx-Beacon";
        dev3.address = "11:22:33:44:55:03";
        dev3.rssi = -75;
        dev3.connectable = false;
        devices.push_back(dev3);

        return devices;
    }
};

BLEScanner::BLEScanner() : impl_(std::make_unique<Impl>()) {}
BLEScanner::~BLEScanner() = default;

bool BLEScanner::start(const BLEScanConfig& /*config*/) {
    impl_->scanning = true;

    // Simulate immediate scan in host mode
    impl_->scan_results = impl_->generate_simulated_devices();
    impl_->scanning = false;

    if (impl_->on_device_found_cb) {
        for (const auto& dev : impl_->scan_results) {
            impl_->on_device_found_cb(dev);
        }
    }

    if (impl_->on_scan_complete_cb) {
        impl_->on_scan_complete_cb(impl_->scan_results);
    }

    return true;
}

void BLEScanner::stop() {
    impl_->scanning = false;
}

bool BLEScanner::is_scanning() const {
    return impl_->scanning;
}

std::vector<BLEDeviceInfo> BLEScanner::results() const {
    return impl_->scan_results;
}

size_t BLEScanner::result_count() const {
    return impl_->scan_results.size();
}

void BLEScanner::clear_results() {
    impl_->scan_results.clear();
}

void BLEScanner::on_device_found(
    std::function<void(const BLEDeviceInfo&)> callback) {
    impl_->on_device_found_cb = std::move(callback);
}

void BLEScanner::on_scan_complete(
    std::function<void(const std::vector<BLEDeviceInfo>&)> callback) {
    impl_->on_scan_complete_cb = std::move(callback);
}

}  // namespace bluetooth
}  // namespace espx
