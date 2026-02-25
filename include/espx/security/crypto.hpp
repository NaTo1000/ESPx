// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace espx {
namespace security {

/**
 * @enum HashAlgorithm
 * @brief Supported hash algorithms.
 */
enum class HashAlgorithm {
    SHA256,
    SHA384,
    SHA512,
    MD5       ///< For legacy compatibility only — not recommended
};

/**
 * @class Crypto
 * @brief Cryptographic utility functions.
 *
 * Provides symmetric encryption (AES-256-CBC, AES-256-GCM),
 * hashing (SHA-256/384/512), HMAC, and random number generation.
 * Uses a lightweight software implementation suitable for
 * embedded environments.
 *
 * Example:
 * @code
 *   // Hash a string
 *   auto hash = espx::security::Crypto::sha256("Hello, World!");
 *
 *   // Encrypt data
 *   auto key = espx::security::Crypto::random_bytes(32);
 *   auto iv = espx::security::Crypto::random_bytes(16);
 *   auto encrypted = espx::security::Crypto::aes_encrypt(plaintext, key, iv);
 *   auto decrypted = espx::security::Crypto::aes_decrypt(encrypted, key, iv);
 * @endcode
 */
class Crypto {
public:
    // ---- Hashing ----

    /**
     * @brief Compute SHA-256 hash of data.
     * @param data Input data
     * @return 32-byte hash
     */
    static std::vector<uint8_t> sha256(const std::vector<uint8_t>& data);

    /**
     * @brief Compute SHA-256 hash of a string.
     * @param data Input string
     * @return 32-byte hash
     */
    static std::vector<uint8_t> sha256(const std::string& data);

    /**
     * @brief Compute a hash using the specified algorithm.
     * @param algorithm Hash algorithm to use
     * @param data Input data
     * @return Hash bytes
     */
    static std::vector<uint8_t> hash(HashAlgorithm algorithm,
                                     const std::vector<uint8_t>& data);

    /**
     * @brief Compute HMAC-SHA256.
     * @param key HMAC key
     * @param data Input data
     * @return 32-byte HMAC
     */
    static std::vector<uint8_t> hmac_sha256(const std::vector<uint8_t>& key,
                                            const std::vector<uint8_t>& data);

    // ---- Encryption ----

    /**
     * @brief Encrypt data using AES-256-CBC.
     * @param plaintext Data to encrypt
     * @param key 32-byte encryption key
     * @param iv 16-byte initialization vector
     * @return Encrypted data (with PKCS7 padding)
     */
    static std::vector<uint8_t> aes_encrypt(const std::vector<uint8_t>& plaintext,
                                            const std::vector<uint8_t>& key,
                                            const std::vector<uint8_t>& iv);

    /**
     * @brief Decrypt data using AES-256-CBC.
     * @param ciphertext Encrypted data
     * @param key 32-byte encryption key
     * @param iv 16-byte initialization vector
     * @return Decrypted data
     */
    static std::vector<uint8_t> aes_decrypt(const std::vector<uint8_t>& ciphertext,
                                            const std::vector<uint8_t>& key,
                                            const std::vector<uint8_t>& iv);

    // ---- Random ----

    /**
     * @brief Generate cryptographically secure random bytes.
     * @param count Number of bytes to generate
     * @return Random byte vector
     */
    static std::vector<uint8_t> random_bytes(size_t count);

    /**
     * @brief Generate a random integer in [min, max].
     * @param min Minimum value (inclusive)
     * @param max Maximum value (inclusive)
     * @return Random integer
     */
    static uint32_t random_int(uint32_t min, uint32_t max);

    // ---- Encoding ----

    /**
     * @brief Convert bytes to hexadecimal string.
     * @param data Input bytes
     * @return Lowercase hex string
     */
    static std::string to_hex(const std::vector<uint8_t>& data);

    /**
     * @brief Convert hexadecimal string to bytes.
     * @param hex Hex string (with or without "0x" prefix)
     * @return Decoded bytes
     */
    static std::vector<uint8_t> from_hex(const std::string& hex);

    /**
     * @brief Constant-time comparison of two byte vectors.
     * @param a First byte vector
     * @param b Second byte vector
     * @return true if equal
     */
    static bool secure_compare(const std::vector<uint8_t>& a,
                               const std::vector<uint8_t>& b);

private:
    Crypto() = default;
};

}  // namespace security
}  // namespace espx
