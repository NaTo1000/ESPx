// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/utils/base64.hpp"

#include <array>
#include <cstddef>

namespace espx {
namespace utils {

static constexpr char kAlphabet[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static constexpr char kPadding = '=';

static std::array<int, 256> build_decode_table() {
    std::array<int, 256> table{};
    table.fill(-1);
    for (int i = 0; i < 64; ++i) {
        table[static_cast<unsigned char>(kAlphabet[i])] = i;
    }
    return table;
}

static const std::array<int, 256> kDecodeTable = build_decode_table();

std::string Base64::encode(const uint8_t* data, size_t length) {
    std::string result;
    result.reserve(encoded_length(length));

    size_t i = 0;
    while (i + 2 < length) {
        unsigned int triple =
            (static_cast<unsigned int>(data[i]) << 16) |
            (static_cast<unsigned int>(data[i + 1]) << 8) |
            static_cast<unsigned int>(data[i + 2]);
        result += kAlphabet[(triple >> 18) & 0x3F];
        result += kAlphabet[(triple >> 12) & 0x3F];
        result += kAlphabet[(triple >> 6) & 0x3F];
        result += kAlphabet[triple & 0x3F];
        i += 3;
    }

    if (i < length) {
        unsigned int val = static_cast<unsigned int>(data[i]) << 16;
        if (i + 1 < length) {
            val |= static_cast<unsigned int>(data[i + 1]) << 8;
        }
        result += kAlphabet[(val >> 18) & 0x3F];
        result += kAlphabet[(val >> 12) & 0x3F];
        if (i + 1 < length) {
            result += kAlphabet[(val >> 6) & 0x3F];
        } else {
            result += kPadding;
        }
        result += kPadding;
    }

    return result;
}

std::string Base64::encode(const std::string& input) {
    return encode(reinterpret_cast<const uint8_t*>(input.data()), input.size());
}

std::string Base64::encode(const std::vector<uint8_t>& data) {
    return encode(data.data(), data.size());
}

std::vector<uint8_t> Base64::decode(const std::string& encoded) {
    if (encoded.empty()) {
        return {};
    }

    std::vector<uint8_t> result;
    result.reserve(decoded_length(encoded.size()));

    unsigned int buffer = 0;
    int bits_collected = 0;

    for (char c : encoded) {
        if (c == kPadding) {
            break;
        }
        int val = kDecodeTable[static_cast<unsigned char>(c)];
        if (val < 0) {
            continue; // skip invalid characters
        }
        buffer = (buffer << 6) | static_cast<unsigned int>(val);
        bits_collected += 6;
        if (bits_collected >= 8) {
            bits_collected -= 8;
            result.push_back(
                static_cast<uint8_t>((buffer >> bits_collected) & 0xFF));
        }
    }

    return result;
}

std::string Base64::decode_string(const std::string& encoded) {
    auto bytes = decode(encoded);
    return std::string(bytes.begin(), bytes.end());
}

std::string Base64::encode_url_safe(const std::string& input) {
    std::string result = encode(input);
    for (auto& c : result) {
        if (c == '+') c = '-';
        else if (c == '/') c = '_';
    }
    // Strip trailing padding
    while (!result.empty() && result.back() == '=') {
        result.pop_back();
    }
    return result;
}

std::vector<uint8_t> Base64::decode_url_safe(const std::string& encoded) {
    std::string standard = encoded;
    for (auto& c : standard) {
        if (c == '-') c = '+';
        else if (c == '_') c = '/';
    }
    // Restore padding
    while (standard.size() % 4 != 0) {
        standard += '=';
    }
    return decode(standard);
}

bool Base64::is_valid(const std::string& str) {
    if (str.empty()) {
        return true;
    }

    bool padding_started = false;
    for (char c : str) {
        if (c == kPadding) {
            padding_started = true;
            continue;
        }
        if (padding_started) {
            return false; // non-padding after padding
        }
        if (kDecodeTable[static_cast<unsigned char>(c)] < 0) {
            return false;
        }
    }

    return str.size() % 4 == 0;
}

size_t Base64::encoded_length(size_t input_length) {
    return ((input_length + 2) / 3) * 4;
}

size_t Base64::decoded_length(size_t enc_length) {
    return (enc_length / 4) * 3;
}

}  // namespace utils
}  // namespace espx
