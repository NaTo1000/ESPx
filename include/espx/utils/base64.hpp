// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace espx {
namespace utils {

/**
 * @class Base64
 * @brief Base64 encoding and decoding utility.
 *
 * Provides RFC 4648 standard Base64 and URL-safe Base64 encoding.
 *
 * Example:
 * @code
 *   std::string encoded = espx::utils::Base64::encode("Hello, World!");
 *   // "SGVsbG8sIFdvcmxkIQ=="
 *
 *   std::string decoded = espx::utils::Base64::decode_string(encoded);
 *   // "Hello, World!"
 * @endcode
 */
class Base64 {
public:
    /**
     * @brief Encode a string to Base64.
     * @param input Input string
     * @return Base64-encoded string
     */
    static std::string encode(const std::string& input);

    /**
     * @brief Encode binary data to Base64.
     * @param data Input bytes
     * @return Base64-encoded string
     */
    static std::string encode(const std::vector<uint8_t>& data);

    /**
     * @brief Encode binary data to Base64.
     * @param data Pointer to data
     * @param length Data length in bytes
     * @return Base64-encoded string
     */
    static std::string encode(const uint8_t* data, size_t length);

    /**
     * @brief Decode Base64 to binary data.
     * @param encoded Base64-encoded string
     * @return Decoded bytes
     */
    static std::vector<uint8_t> decode(const std::string& encoded);

    /**
     * @brief Decode Base64 to a string.
     * @param encoded Base64-encoded string
     * @return Decoded string
     */
    static std::string decode_string(const std::string& encoded);

    /**
     * @brief Encode to URL-safe Base64 (uses - and _ instead of + and /).
     * @param input Input string
     * @return URL-safe Base64-encoded string
     */
    static std::string encode_url_safe(const std::string& input);

    /**
     * @brief Decode URL-safe Base64.
     * @param encoded URL-safe Base64-encoded string
     * @return Decoded bytes
     */
    static std::vector<uint8_t> decode_url_safe(const std::string& encoded);

    /**
     * @brief Check if a string is valid Base64.
     * @param str String to validate
     * @return true if the string is valid Base64
     */
    static bool is_valid(const std::string& str);

    /**
     * @brief Calculate the encoded length for a given input length.
     * @param input_length Input data length in bytes
     * @return Length of the Base64-encoded string
     */
    static size_t encoded_length(size_t input_length);

    /**
     * @brief Calculate the maximum decoded length for a given encoded length.
     * @param encoded_length Length of the Base64-encoded string
     * @return Maximum decoded data length
     */
    static size_t decoded_length(size_t encoded_length);

private:
    Base64() = default;
};

}  // namespace utils
}  // namespace espx
