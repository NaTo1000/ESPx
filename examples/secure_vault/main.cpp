// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

#include "espx/core/logger.hpp"
#include "espx/security/crypto.hpp"
#include "espx/security/key_store.hpp"
#include "espx/security/vault.hpp"
#include "espx/utils/base64.hpp"
#include "espx/utils/uuid.hpp"

static const char* TAG = "SecureVault";

using espx::core::LogLevel;

static void log_info(const std::string& msg) {
    espx::core::Logger::instance().log(LogLevel::Info, TAG, __FILE__, __LINE__, msg);
}

int main() {
    auto& logger = espx::core::Logger::instance();
    logger.set_level(LogLevel::Info);

    log_info("=== ESPx Secure Vault Example ===");

    // --- Vault: encrypted key-value storage ---
    log_info("--- Vault ---");

    espx::security::Vault vault;
    // 32-byte master key for AES-256
    if (!vault.init("ESPxMasterKey___32byteslong!!")) {
        logger.log(LogLevel::Error, TAG, __FILE__, __LINE__, "Failed to initialize vault");
        return 1;
    }
    log_info("Vault initialized");

    // Store credentials
    vault.store("wifi_ssid", "MySecureNetwork");
    vault.store("wifi_password", "SuperSecret123!");
    vault.store("api_key", "sk-abc123def456ghi789");
    vault.store("mqtt_token", "eyJhbGciOiJIUzI1NiJ9.payload.sig");

    log_info("Stored " + std::to_string(vault.size()) + " entries");

    // Retrieve and print
    std::cout << "  wifi_ssid:     " << vault.retrieve_string("wifi_ssid") << "\n";
    std::cout << "  wifi_password: " << vault.retrieve_string("wifi_password") << "\n";
    std::cout << "  api_key:       " << vault.retrieve_string("api_key") << "\n";
    std::cout << "  mqtt_token:    " << vault.retrieve_string("mqtt_token") << "\n";

    // List all keys
    std::cout << "  All keys:";
    for (const auto& k : vault.keys()) {
        std::cout << " " << k;
    }
    std::cout << "\n\n";

    // --- KeyStore: key generation and management ---
    log_info("--- KeyStore ---");

    espx::security::KeyStore store;
    if (!store.init()) {
        logger.log(LogLevel::Error, TAG, __FILE__, __LINE__, "Failed to initialize KeyStore");
        return 1;
    }

    store.generate_symmetric_key("aes_session_key", 256);
    store.generate_symmetric_key("hmac_key", 256);

    log_info("Generated " + std::to_string(store.size()) + " key(s)");

    for (const auto& name : store.list_keys()) {
        auto info = store.get_key_info(name);
        std::cout << "  Key: " << info.name
                  << "  type=" << static_cast<int>(info.type)
                  << "  bits=" << info.size_bits << "\n";
    }
    std::cout << "\n";

    // --- Crypto: SHA-256 hashing ---
    log_info("--- Crypto SHA-256 ---");

    auto hash = espx::security::Crypto::sha256("Hello, ESPx!");
    std::cout << "  SHA-256(\"Hello, ESPx!\"): "
              << espx::security::Crypto::to_hex(hash) << "\n\n";

    // --- Base64 encoding ---
    log_info("--- Base64 ---");

    std::string original = "ESPx Secure Vault Example";
    std::string encoded = espx::utils::Base64::encode(original);
    std::string decoded = espx::utils::Base64::decode_string(encoded);

    std::cout << "  Original: " << original << "\n";
    std::cout << "  Encoded:  " << encoded << "\n";
    std::cout << "  Decoded:  " << decoded << "\n";
    std::cout << "  Valid:    " << (espx::utils::Base64::is_valid(encoded) ? "yes" : "no")
              << "\n\n";

    // --- UUID generation ---
    log_info("--- UUID ---");

    for (int i = 0; i < 3; ++i) {
        auto uuid = espx::utils::UUID::generate();
        std::cout << "  UUID " << (i + 1) << ": " << uuid.to_string() << "\n";
    }
    std::cout << "\n";

    log_info("Secure vault example complete.");
    return 0;
}
