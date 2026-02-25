// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/network/udp_socket.hpp"

#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace espx {
namespace network {

struct UdpSocket::Impl {
    bool bound{false};
    uint16_t local_pt{0};

    std::function<void(const UdpMessage&)> on_message_cb;
    std::function<void(int, const std::string&)> on_error_cb;
};

UdpSocket::UdpSocket() : impl_(std::make_unique<Impl>()) {}
UdpSocket::~UdpSocket() = default;

bool UdpSocket::bind(uint16_t port) {
    if (impl_->bound) {
        return false;
    }
    impl_->local_pt = port;
    impl_->bound = true;
    return true;
}

int UdpSocket::send_to(const std::string& /*host*/, uint16_t /*port*/,
                        const std::vector<uint8_t>& data) {
    return static_cast<int>(data.size());
}

int UdpSocket::send_to(const std::string& /*host*/, uint16_t /*port*/,
                        const std::string& data) {
    return static_cast<int>(data.size());
}

int UdpSocket::broadcast(uint16_t port, const std::vector<uint8_t>& data) {
    return send_to("255.255.255.255", port, data);
}

bool UdpSocket::join_multicast(const std::string& /*group_ip*/) {
    return true;
}

void UdpSocket::leave_multicast(const std::string& /*group_ip*/) {
}

void UdpSocket::close() {
    impl_->bound = false;
    impl_->local_pt = 0;
}

bool UdpSocket::is_bound() const {
    return impl_->bound;
}

uint16_t UdpSocket::local_port() const {
    return impl_->local_pt;
}

void UdpSocket::on_message(
    std::function<void(const UdpMessage&)> callback) {
    impl_->on_message_cb = std::move(callback);
}

void UdpSocket::on_error(
    std::function<void(int, const std::string&)> callback) {
    impl_->on_error_cb = std::move(callback);
}

}  // namespace network
}  // namespace espx
