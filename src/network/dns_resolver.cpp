// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/network/dns_resolver.hpp"

#include <map>
#include <string>
#include <utility>
#include <vector>

namespace espx {
namespace network {

struct DnsResolver::Impl {
    std::map<std::string, std::vector<DnsRecord>> cache;
    bool cache_enabled{true};
    size_t max_entries{64};
    std::string primary_dns;
    std::string secondary_dns;
};

DnsResolver::DnsResolver() : impl_(std::make_unique<Impl>()) {}
DnsResolver::~DnsResolver() = default;

std::vector<DnsRecord> DnsResolver::resolve(const std::string& hostname) {
    // Check cache first
    if (impl_->cache_enabled) {
        auto it = impl_->cache.find(hostname);
        if (it != impl_->cache.end()) {
            return it->second;
        }
    }

    // Simulated resolution
    DnsRecord record;
    record.hostname = hostname;
    record.ip_address = "93.184.216.34";
    record.ttl = 300;
    record.is_ipv6 = false;

    std::vector<DnsRecord> results{record};

    // Store in cache
    if (impl_->cache_enabled && impl_->cache.size() < impl_->max_entries) {
        impl_->cache[hostname] = results;
    }

    return results;
}

void DnsResolver::resolve_async(
    const std::string& hostname,
    std::function<void(const std::vector<DnsRecord>&)> callback) {
    auto results = resolve(hostname);
    if (callback) {
        callback(results);
    }
}

void DnsResolver::set_cache_enabled(bool enabled, size_t max_entries) {
    impl_->cache_enabled = enabled;
    impl_->max_entries = max_entries;
    if (!enabled) {
        impl_->cache.clear();
    }
}

void DnsResolver::clear_cache() {
    impl_->cache.clear();
}

size_t DnsResolver::cache_size() const {
    return impl_->cache.size();
}

void DnsResolver::set_dns_servers(const std::string& primary,
                                  const std::string& secondary) {
    impl_->primary_dns = primary;
    impl_->secondary_dns = secondary;
}

}  // namespace network
}  // namespace espx
