// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace security {

/**
 * @enum KeyType
 * @brief Types of cryptographic keys.
 */
enum class KeyType {
    Symmetric,   ///< AES symmetric key
    PublicKey,   ///< RSA/EC public key
    PrivateKey,  ///< RSA/EC private key
    Certificate  ///< X.509 certificate
};

/**
 * @struct KeyInfo
 * @brief Metadata about a stored key.
 */
struct KeyInfo {
    std::string name;           ///< Key identifier
    KeyType type;               ///< Key type
    size_t size_bits = 0;       ///< Key size in bits
    uint64_t created_at = 0;    ///< Creation timestamp
    uint64_t expires_at = 0;    ///< Expiration timestamp (0 = never)
    bool exportable = false;    ///< Whether the key can be exported
};

/**
 * @class KeyStore
 * @brief Secure cryptographic key management.
 *
 * Manages cryptographic keys, certificates, and key pairs.
 * Supports key generation, import/export, and lifecycle management.
 *
 * Example:
 * @code
 *   espx::security::KeyStore store;
 *   store.init();
 *
 *   // Generate a new AES key
 *   store.generate_symmetric_key("my_aes_key", 256);
 *
 *   // Import a certificate
 *   store.import_key("server_cert", KeyType::Certificate, cert_pem);
 *
 *   // Retrieve a key
 *   auto key = store.get_key("my_aes_key");
 * @endcode
 */
class KeyStore {
public:
    KeyStore();
    ~KeyStore();

    KeyStore(const KeyStore&) = delete;
    KeyStore& operator=(const KeyStore&) = delete;

    /**
     * @brief Initialize the key store.
     * @return true if initialization succeeded
     */
    bool init();

    /**
     * @brief Generate a symmetric key.
     * @param name Key identifier
     * @param bits Key size in bits (128, 192, or 256)
     * @return true if key was generated
     */
    bool generate_symmetric_key(const std::string& name, size_t bits = 256);

    /**
     * @brief Import a key from raw data.
     * @param name Key identifier
     * @param type Key type
     * @param data Key data (raw bytes or PEM-encoded)
     * @return true if key was imported
     */
    bool import_key(const std::string& name, KeyType type,
                    const std::vector<uint8_t>& data);

    /**
     * @brief Import a key from a PEM string.
     * @param name Key identifier
     * @param type Key type
     * @param pem PEM-encoded key data
     * @return true if key was imported
     */
    bool import_key(const std::string& name, KeyType type,
                    const std::string& pem);

    /**
     * @brief Retrieve a key's raw data.
     * @param name Key identifier
     * @return Key data (empty if not found or not exportable)
     */
    [[nodiscard]] std::vector<uint8_t> get_key(const std::string& name) const;

    /**
     * @brief Get metadata about a key.
     * @param name Key identifier
     * @return Key info (name is empty if not found)
     */
    [[nodiscard]] KeyInfo get_key_info(const std::string& name) const;

    /**
     * @brief Check if a key exists.
     * @param name Key identifier
     * @return true if the key exists
     */
    [[nodiscard]] bool has_key(const std::string& name) const;

    /**
     * @brief Delete a key.
     * @param name Key identifier
     * @return true if the key was deleted
     */
    bool delete_key(const std::string& name);

    /**
     * @brief List all key names.
     * @return Vector of key identifiers
     */
    [[nodiscard]] std::vector<std::string> list_keys() const;

    /**
     * @brief Get the number of stored keys.
     * @return Key count
     */
    [[nodiscard]] size_t size() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace security
}  // namespace espx
