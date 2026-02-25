// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace security {

/**
 * @struct VaultEntry
 * @brief A stored vault entry with metadata.
 */
struct VaultEntry {
    std::string key;              ///< Entry key/name
    std::vector<uint8_t> value;   ///< Encrypted value
    uint64_t created_at = 0;     ///< Creation timestamp (UNIX epoch)
    uint64_t updated_at = 0;     ///< Last update timestamp
    bool encrypted = true;        ///< Whether the value is encrypted
};

/**
 * @class Vault
 * @brief Secure key-value storage with encryption.
 *
 * Provides encrypted persistent storage for sensitive data such as
 * passwords, API keys, certificates, and tokens. On ESP32, this
 * uses NVS with flash encryption. In host mode, it uses AES-256
 * encryption on a local file.
 *
 * Example:
 * @code
 *   espx::security::Vault vault;
 *   vault.init("my_master_key_32chars!!");
 *
 *   vault.store("wifi_password", "supersecret123");
 *   vault.store("api_key", "sk-abc123def456");
 *
 *   auto password = vault.retrieve_string("wifi_password");
 *   std::cout << "WiFi password: " << password << std::endl;
 * @endcode
 */
class Vault {
public:
    Vault();
    ~Vault();

    Vault(const Vault&) = delete;
    Vault& operator=(const Vault&) = delete;

    /**
     * @brief Initialize the vault with a master key.
     * @param master_key Master encryption key (must be 16, 24, or 32 bytes)
     * @return true if initialization succeeded
     */
    bool init(const std::string& master_key);

    /**
     * @brief Store a string value.
     * @param key Entry key
     * @param value Value to store
     * @return true if stored successfully
     */
    bool store(const std::string& key, const std::string& value);

    /**
     * @brief Store binary data.
     * @param key Entry key
     * @param data Data to store
     * @return true if stored successfully
     */
    bool store(const std::string& key, const std::vector<uint8_t>& data);

    /**
     * @brief Retrieve a string value.
     * @param key Entry key
     * @return Decrypted string value (empty if not found)
     */
    [[nodiscard]] std::string retrieve_string(const std::string& key) const;

    /**
     * @brief Retrieve binary data.
     * @param key Entry key
     * @return Decrypted data (empty if not found)
     */
    [[nodiscard]] std::vector<uint8_t> retrieve(const std::string& key) const;

    /**
     * @brief Check if a key exists in the vault.
     * @param key Entry key
     * @return true if the key exists
     */
    [[nodiscard]] bool has(const std::string& key) const;

    /**
     * @brief Remove an entry from the vault.
     * @param key Entry key
     * @return true if the entry was removed
     */
    bool remove(const std::string& key);

    /**
     * @brief List all keys in the vault.
     * @return Vector of key names
     */
    [[nodiscard]] std::vector<std::string> keys() const;

    /**
     * @brief Get the number of entries.
     * @return Entry count
     */
    [[nodiscard]] size_t size() const;

    /// Remove all entries
    void clear();

    /**
     * @brief Save the vault to persistent storage.
     * @param filepath Path to save to
     * @return true if saved successfully
     */
    bool save(const std::string& filepath) const;

    /**
     * @brief Load the vault from persistent storage.
     * @param filepath Path to load from
     * @return true if loaded successfully
     */
    bool load(const std::string& filepath);

    /**
     * @brief Check if the vault is initialized.
     * @return true if initialized
     */
    [[nodiscard]] bool is_initialized() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace security
}  // namespace espx
