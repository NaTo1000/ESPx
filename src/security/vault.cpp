// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/security/vault.hpp"

#include <chrono>
#include <fstream>
#include <map>
#include <mutex>

namespace espx {
namespace security {

struct Vault::Impl {
    std::string master_key;
    bool initialized = false;
    std::map<std::string, VaultEntry> entries;
    mutable std::mutex mutex;

    static uint64_t now_epoch() {
        using namespace std::chrono;
        return static_cast<uint64_t>(
            duration_cast<seconds>(
                system_clock::now().time_since_epoch())
                .count());
    }

    // XOR-encode/decode with master key bytes (simulation)
    std::vector<uint8_t> xor_transform(
        const std::vector<uint8_t>& data) const {
        std::vector<uint8_t> result(data.size());
        for (size_t i = 0; i < data.size(); ++i) {
            result[i] = data[i] ^
                static_cast<uint8_t>(
                    master_key[i % master_key.size()]);
        }
        return result;
    }
};

Vault::Vault() : impl_(std::make_unique<Impl>()) {}
Vault::~Vault() = default;

bool Vault::init(const std::string& master_key) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (master_key.empty()) return false;
    impl_->master_key = master_key;
    impl_->initialized = true;
    return true;
}

bool Vault::store(const std::string& key, const std::string& value) {
    std::vector<uint8_t> bytes(value.begin(), value.end());
    return store(key, bytes);
}

bool Vault::store(const std::string& key, const std::vector<uint8_t>& data) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (!impl_->initialized) return false;

    auto now = Impl::now_epoch();
    VaultEntry entry;
    entry.key = key;
    entry.value = impl_->xor_transform(data);
    entry.encrypted = true;

    auto it = impl_->entries.find(key);
    if (it != impl_->entries.end()) {
        entry.created_at = it->second.created_at;
        entry.updated_at = now;
    } else {
        entry.created_at = now;
        entry.updated_at = now;
    }

    impl_->entries[key] = std::move(entry);
    return true;
}

std::string Vault::retrieve_string(const std::string& key) const {
    auto bytes = retrieve(key);
    return std::string(bytes.begin(), bytes.end());
}

std::vector<uint8_t> Vault::retrieve(const std::string& key) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (!impl_->initialized) return {};

    auto it = impl_->entries.find(key);
    if (it == impl_->entries.end()) return {};

    return impl_->xor_transform(it->second.value);
}

bool Vault::has(const std::string& key) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->entries.count(key) > 0;
}

bool Vault::remove(const std::string& key) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->entries.erase(key) > 0;
}

std::vector<std::string> Vault::keys() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    std::vector<std::string> result;
    result.reserve(impl_->entries.size());
    for (auto& kv : impl_->entries) {
        result.push_back(kv.first);
    }
    return result;
}

size_t Vault::size() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->entries.size();
}

void Vault::clear() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->entries.clear();
}

bool Vault::save(const std::string& filepath) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (!impl_->initialized) return false;

    std::ofstream ofs(filepath, std::ios::binary);
    if (!ofs.is_open()) return false;

    auto entry_count = impl_->entries.size();
    ofs.write(reinterpret_cast<const char*>(&entry_count),
              sizeof(entry_count));

    for (auto& kv : impl_->entries) {
        auto& e = kv.second;
        auto key_len = e.key.size();
        ofs.write(reinterpret_cast<const char*>(&key_len), sizeof(key_len));
        ofs.write(e.key.data(), static_cast<std::streamsize>(key_len));

        auto val_len = e.value.size();
        ofs.write(reinterpret_cast<const char*>(&val_len), sizeof(val_len));
        ofs.write(reinterpret_cast<const char*>(e.value.data()),
                  static_cast<std::streamsize>(val_len));

        ofs.write(reinterpret_cast<const char*>(&e.created_at),
                  sizeof(e.created_at));
        ofs.write(reinterpret_cast<const char*>(&e.updated_at),
                  sizeof(e.updated_at));
    }

    return ofs.good();
}

bool Vault::load(const std::string& filepath) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (!impl_->initialized) return false;

    std::ifstream ifs(filepath, std::ios::binary);
    if (!ifs.is_open()) return false;

    size_t entry_count = 0;
    ifs.read(reinterpret_cast<char*>(&entry_count), sizeof(entry_count));
    if (!ifs.good()) return false;

    std::map<std::string, VaultEntry> new_entries;
    for (size_t i = 0; i < entry_count; ++i) {
        VaultEntry e;

        size_t key_len = 0;
        ifs.read(reinterpret_cast<char*>(&key_len), sizeof(key_len));
        e.key.resize(key_len);
        ifs.read(&e.key[0], static_cast<std::streamsize>(key_len));

        size_t val_len = 0;
        ifs.read(reinterpret_cast<char*>(&val_len), sizeof(val_len));
        e.value.resize(val_len);
        ifs.read(reinterpret_cast<char*>(e.value.data()),
                 static_cast<std::streamsize>(val_len));

        ifs.read(reinterpret_cast<char*>(&e.created_at),
                 sizeof(e.created_at));
        ifs.read(reinterpret_cast<char*>(&e.updated_at),
                 sizeof(e.updated_at));

        if (!ifs.good()) return false;

        e.encrypted = true;
        new_entries[e.key] = std::move(e);
    }

    impl_->entries = std::move(new_entries);
    return true;
}

bool Vault::is_initialized() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->initialized;
}

}  // namespace security
}  // namespace espx
