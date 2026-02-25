// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/bluetooth/gatt_server.hpp"

#include <algorithm>
#include <vector>

namespace espx {
namespace bluetooth {

struct GATTServer::Impl {
    std::vector<GATTService> services;
    bool running{false};

    std::function<void(const std::string&, const std::string&)> on_read_cb;
    std::function<void(const std::string&, const std::string&,
                       const std::vector<uint8_t>&)> on_write_cb;

    GATTCharacteristic* find_characteristic(const std::string& service_uuid,
                                            const std::string& char_uuid) {
        for (auto& svc : services) {
            if (svc.uuid == service_uuid) {
                for (auto& ch : svc.characteristics) {
                    if (ch.uuid == char_uuid) {
                        return &ch;
                    }
                }
            }
        }
        return nullptr;
    }

    const GATTCharacteristic* find_characteristic(
        const std::string& service_uuid,
        const std::string& char_uuid) const {
        for (const auto& svc : services) {
            if (svc.uuid == service_uuid) {
                for (const auto& ch : svc.characteristics) {
                    if (ch.uuid == char_uuid) {
                        return &ch;
                    }
                }
            }
        }
        return nullptr;
    }
};

GATTServer::GATTServer() : impl_(std::make_unique<Impl>()) {}
GATTServer::~GATTServer() = default;

bool GATTServer::add_service(const GATTService& service) {
    impl_->services.push_back(service);
    return true;
}

bool GATTServer::start() {
    impl_->running = true;
    return true;
}

void GATTServer::stop() {
    impl_->running = false;
}

bool GATTServer::is_running() const {
    return impl_->running;
}

bool GATTServer::set_value(const std::string& service_uuid,
                           const std::string& char_uuid,
                           const std::vector<uint8_t>& value) {
    auto* ch = impl_->find_characteristic(service_uuid, char_uuid);
    if (!ch) {
        return false;
    }
    ch->value = value;

    if (impl_->on_write_cb) {
        impl_->on_write_cb(service_uuid, char_uuid, value);
    }

    return true;
}

std::vector<uint8_t> GATTServer::get_value(
    const std::string& service_uuid,
    const std::string& char_uuid) const {
    const auto* ch = impl_->find_characteristic(service_uuid, char_uuid);
    if (!ch) {
        return {};
    }

    if (impl_->on_read_cb) {
        impl_->on_read_cb(service_uuid, char_uuid);
    }

    return ch->value;
}

bool GATTServer::notify(const std::string& service_uuid,
                        const std::string& char_uuid,
                        const std::vector<uint8_t>& value) {
    auto* ch = impl_->find_characteristic(service_uuid, char_uuid);
    if (!ch || !ch->notify) {
        return false;
    }
    ch->value = value;
    return true;
}

size_t GATTServer::service_count() const {
    return impl_->services.size();
}

void GATTServer::on_read(
    std::function<void(const std::string&, const std::string&)> callback) {
    impl_->on_read_cb = std::move(callback);
}

void GATTServer::on_write(
    std::function<void(const std::string&, const std::string&,
                       const std::vector<uint8_t>&)> callback) {
    impl_->on_write_cb = std::move(callback);
}

}  // namespace bluetooth
}  // namespace espx
