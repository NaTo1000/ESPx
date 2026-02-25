// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <string>

namespace espx {
namespace utils {

/**
 * @class UUID
 * @brief UUID (Universally Unique Identifier) generator.
 *
 * Generates RFC 4122 version 4 (random) UUIDs for use as
 * unique identifiers throughout the system.
 *
 * Example:
 * @code
 *   auto id = espx::utils::UUID::generate();
 *   std::cout << "UUID: " << id.to_string() << std::endl;
 *   // Output: "550e8400-e29b-41d4-a716-446655440000"
 * @endcode
 */
class UUID {
public:
    /// Construct a nil UUID (all zeros)
    UUID();

    /**
     * @brief Generate a new random UUID (version 4).
     * @return New UUID
     */
    static UUID generate();

    /**
     * @brief Parse a UUID from a string.
     * @param str UUID string (with or without dashes)
     * @return Parsed UUID (nil if parsing failed)
     */
    static UUID from_string(const std::string& str);

    /**
     * @brief Create a UUID from raw bytes.
     * @param bytes 16-byte array
     * @return UUID
     */
    static UUID from_bytes(const uint8_t bytes[16]);

    /**
     * @brief Get the string representation.
     * @return UUID string in "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" format
     */
    [[nodiscard]] std::string to_string() const;

    /**
     * @brief Get the short string representation (no dashes).
     * @return 32-character hex string
     */
    [[nodiscard]] std::string to_short_string() const;

    /**
     * @brief Get the raw 16-byte representation.
     * @return Pointer to 16 bytes
     */
    [[nodiscard]] const uint8_t* bytes() const;

    /**
     * @brief Check if this is a nil UUID (all zeros).
     * @return true if nil
     */
    [[nodiscard]] bool is_nil() const;

    /// Equality comparison
    bool operator==(const UUID& other) const;

    /// Inequality comparison
    bool operator!=(const UUID& other) const;

    /// Less-than comparison (for use in ordered containers)
    bool operator<(const UUID& other) const;

private:
    uint8_t data_[16]{};
};

}  // namespace utils
}  // namespace espx
