// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/security/key_store.hpp"
#include "espx/security/crypto.hpp"

#include <chrono>
#include <map>
#include <mutex>

namespace espx {
namespace security {

struct KeyStore::Impl {
    struct StoredKey {
        KeyInfo info;
        std::vector<uint8_t> data;
    };

    bool initialized = false;
    std::map<std::string, StoredKey> keys;
    mutable std::mutex mutex;

    static uint64_t now_epoch() {
        using namespace std::chrono;
        return static_cast<uint64_t>(
            duration_cast<seconds>(
                system_clock::now().time_since_epoch())
                .count());
    }
};

KeyStore::KeyStore() : impl_(std::make_unique<Impl>()) {}
KeyStore::~KeyStore() = default;

bool KeyStore::init() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->initialized = true;
    return true;
}

bool KeyStore::generate_symmetric_key(const std::string& name, size_t bits) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (!impl_->initialized) return false;
    if (bits != 128 && bits != 192 && bits != 256) return false;

    auto data = Crypto::random_bytes(bits / 8);

    KeyInfo info;
    info.name = name;
    info.type = KeyType::Symmetric;
    info.size_bits = bits;
    info.created_at = Impl::now_epoch();
    info.expires_at = 0;
    info.exportable = true;

    impl_->keys[name] = {std::move(info), std::move(data)};
    return true;
}

bool KeyStore::import_key(const std::string& name, KeyType type,
                          const std::vector<uint8_t>& data) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (!impl_->initialized) return false;

    KeyInfo info;
    info.name = name;
    info.type = type;
    info.size_bits = data.size() * 8;
    info.created_at = Impl::now_epoch();
    info.expires_at = 0;
    info.exportable = true;

    impl_->keys[name] = {std::move(info), data};
    return true;
}

bool KeyStore::import_key(const std::string& name, KeyType type,
                          const std::string& pem) {
    std::vector<uint8_t> data(pem.begin(), pem.end());
    return import_key(name, type, data);
}

std::vector<uint8_t> KeyStore::get_key(const std::string& name) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->keys.find(name);
    if (it == impl_->keys.end()) return {};
    if (!it->second.info.exportable) return {};
    return it->second.data;
}

KeyInfo KeyStore::get_key_info(const std::string& name) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->keys.find(name);
    if (it == impl_->keys.end()) return {};
    return it->second.info;
}

bool KeyStore::has_key(const std::string& name) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->keys.count(name) > 0;
}

bool KeyStore::delete_key(const std::string& name) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->keys.erase(name) > 0;
}

std::vector<std::string> KeyStore::list_keys() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    std::vector<std::string> result;
    result.reserve(impl_->keys.size());
    for (auto& kv : impl_->keys) {
        result.push_back(kv.first);
    }
    return result;
}

size_t KeyStore::size() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->keys.size();
}

}  // namespace security
}  // namespace espx
