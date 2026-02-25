// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/wifi/scanner.hpp"

#include <algorithm>
#include <vector>

namespace espx {
namespace wifi {

struct Scanner::Impl {
    std::vector<ScanResult> scan_results;
    bool scanning{false};
    std::function<void(const std::vector<ScanResult>&)> on_scan_done_cb;

    std::vector<ScanResult> generate_simulated_results() {
        std::vector<ScanResult> results;

        results.push_back({"HomeNetwork", "AA:BB:CC:DD:EE:01", -30, 1,
                           WiFiAuthMode::WPA2_PSK, false});
        results.push_back({"OfficeWiFi", "AA:BB:CC:DD:EE:02", -55, 6,
                           WiFiAuthMode::WPA_WPA2_PSK, false});
        results.push_back({"GuestNet", "AA:BB:CC:DD:EE:03", -65, 11,
                           WiFiAuthMode::WPA3_PSK, false});
        results.push_back({"CafeHotspot", "AA:BB:CC:DD:EE:04", -72, 3,
                           WiFiAuthMode::Open, false});
        results.push_back({"Neighbor5G", "AA:BB:CC:DD:EE:05", -80, 36,
                           WiFiAuthMode::WPA2_PSK, true});

        std::sort(results.begin(), results.end());
        return results;
    }
};

Scanner::Scanner() : impl_(std::make_unique<Impl>()) {}
Scanner::~Scanner() = default;

bool Scanner::scan_async(const ScanConfig& /*config*/) {
    impl_->scanning = true;

    // Simulate immediate scan completion in host mode
    impl_->scan_results = impl_->generate_simulated_results();
    impl_->scanning = false;

    if (impl_->on_scan_done_cb) {
        impl_->on_scan_done_cb(impl_->scan_results);
    }

    return true;
}

std::vector<ScanResult> Scanner::scan_sync(const ScanConfig& /*config*/) {
    impl_->scanning = true;
    impl_->scan_results = impl_->generate_simulated_results();
    impl_->scanning = false;
    return impl_->scan_results;
}

bool Scanner::is_scanning() const {
    return impl_->scanning;
}

std::vector<ScanResult> Scanner::results() const {
    return impl_->scan_results;
}

size_t Scanner::result_count() const {
    return impl_->scan_results.size();
}

void Scanner::on_scan_done(
    std::function<void(const std::vector<ScanResult>&)> callback) {
    impl_->on_scan_done_cb = std::move(callback);
}

}  // namespace wifi
}  // namespace espx
