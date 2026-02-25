// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace network {

/**
 * @struct DnsRecord
 * @brief A DNS resolution result.
 */
struct DnsRecord {
    std::string hostname;     ///< Queried hostname
    std::string ip_address;   ///< Resolved IP address
    uint32_t ttl = 0;         ///< Time-to-live in seconds
    bool is_ipv6 = false;     ///< Whether this is an IPv6 address
};

/**
 * @class DnsResolver
 * @brief DNS name resolution utility.
 *
 * Resolves hostnames to IP addresses with caching support.
 * Supports both synchronous and asynchronous resolution.
 *
 * Example:
 * @code
 *   espx::network::DnsResolver dns;
 *   auto records = dns.resolve("www.example.com");
 *   for (const auto& r : records) {
 *       std::cout << r.hostname << " -> " << r.ip_address << std::endl;
 *   }
 * @endcode
 */
class DnsResolver {
public:
    DnsResolver();
    ~DnsResolver();

    DnsResolver(const DnsResolver&) = delete;
    DnsResolver& operator=(const DnsResolver&) = delete;

    /**
     * @brief Resolve a hostname synchronously.
     * @param hostname Hostname to resolve
     * @return Vector of DNS records
     */
    [[nodiscard]] std::vector<DnsRecord> resolve(const std::string& hostname);

    /**
     * @brief Resolve a hostname asynchronously.
     * @param hostname Hostname to resolve
     * @param callback Called with the results
     */
    void resolve_async(const std::string& hostname,
                       std::function<void(const std::vector<DnsRecord>&)> callback);

    /**
     * @brief Enable or disable the DNS cache.
     * @param enabled true to enable caching
     * @param max_entries Maximum cache entries
     */
    void set_cache_enabled(bool enabled, size_t max_entries = 64);

    /**
     * @brief Clear the DNS cache.
     */
    void clear_cache();

    /**
     * @brief Get the number of cached entries.
     * @return Cache size
     */
    [[nodiscard]] size_t cache_size() const;

    /**
     * @brief Set custom DNS server addresses.
     * @param primary Primary DNS server IP
     * @param secondary Secondary DNS server IP (optional)
     */
    void set_dns_servers(const std::string& primary,
                         const std::string& secondary = "");

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace network
}  // namespace espx
