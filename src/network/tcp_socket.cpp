// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/network/tcp_socket.hpp"

#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace espx {
namespace network {

struct TcpSocket::Impl {
    SocketState state{SocketState::Closed};
    std::string remote_addr;
    uint16_t remote_pt{0};
    uint16_t local_pt{0};

    std::function<void(const std::vector<uint8_t>&)> on_data_cb;
    std::function<void(TcpSocket&)> on_connection_cb;
    std::function<void()> on_disconnect_cb;
    std::function<void(int, const std::string&)> on_error_cb;
};

TcpSocket::TcpSocket() : impl_(std::make_unique<Impl>()) {}
TcpSocket::~TcpSocket() = default;

TcpSocket::TcpSocket(TcpSocket&&) noexcept = default;
TcpSocket& TcpSocket::operator=(TcpSocket&&) noexcept = default;

bool TcpSocket::connect(const std::string& host, uint16_t port,
                        uint32_t /*timeout_ms*/) {
    if (impl_->state != SocketState::Closed) {
        return false;
    }
    impl_->remote_addr = host;
    impl_->remote_pt = port;
    impl_->state = SocketState::Connected;
    return true;
}

bool TcpSocket::listen(uint16_t port, int /*backlog*/) {
    if (impl_->state != SocketState::Closed) {
        return false;
    }
    impl_->local_pt = port;
    impl_->state = SocketState::Listening;
    return true;
}

int TcpSocket::send(const std::vector<uint8_t>& data) {
    if (impl_->state != SocketState::Connected) {
        return -1;
    }
    return static_cast<int>(data.size());
}

int TcpSocket::send(const std::string& data) {
    if (impl_->state != SocketState::Connected) {
        return -1;
    }
    return static_cast<int>(data.size());
}

void TcpSocket::close() {
    impl_->state = SocketState::Closed;
    impl_->remote_addr.clear();
    impl_->remote_pt = 0;
}

SocketState TcpSocket::state() const {
    return impl_->state;
}

bool TcpSocket::is_connected() const {
    return impl_->state == SocketState::Connected;
}

std::string TcpSocket::remote_address() const {
    return impl_->remote_addr;
}

uint16_t TcpSocket::remote_port() const {
    return impl_->remote_pt;
}

uint16_t TcpSocket::local_port() const {
    return impl_->local_pt;
}

void TcpSocket::on_data(
    std::function<void(const std::vector<uint8_t>&)> callback) {
    impl_->on_data_cb = std::move(callback);
}

void TcpSocket::on_connection(std::function<void(TcpSocket&)> callback) {
    impl_->on_connection_cb = std::move(callback);
}

void TcpSocket::on_disconnect(std::function<void()> callback) {
    impl_->on_disconnect_cb = std::move(callback);
}

void TcpSocket::on_error(
    std::function<void(int, const std::string&)> callback) {
    impl_->on_error_cb = std::move(callback);
}

}  // namespace network
}  // namespace espx
