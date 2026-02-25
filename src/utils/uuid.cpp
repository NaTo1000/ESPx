// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/utils/uuid.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <iomanip>
#include <random>
#include <sstream>

namespace espx {
namespace utils {

UUID::UUID() {
    std::memset(data_, 0, sizeof(data_));
}

UUID UUID::generate() {
    UUID uuid;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<unsigned int> dist(0, 255);

    for (auto& byte : uuid.data_) {
        byte = static_cast<uint8_t>(dist(gen));
    }

    // RFC 4122 version 4: set version bits
    uuid.data_[6] = static_cast<uint8_t>(0x40U | (uuid.data_[6] & 0x0FU));
    // RFC 4122 variant 1: set variant bits
    uuid.data_[8] = static_cast<uint8_t>(0x80U | (uuid.data_[8] & 0x3FU));

    return uuid;
}

static int hex_char_to_int(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return 10 + (c - 'a');
    if (c >= 'A' && c <= 'F') return 10 + (c - 'A');
    return -1;
}

UUID UUID::from_string(const std::string& str) {
    UUID uuid;
    size_t byte_index = 0;

    for (size_t i = 0; i < str.size() && byte_index < 16;) {
        if (str[i] == '-') {
            ++i;
            continue;
        }
        if (i + 1 >= str.size()) {
            return UUID(); // nil on parse failure
        }
        int hi = hex_char_to_int(str[i]);
        int lo = hex_char_to_int(str[i + 1]);
        if (hi < 0 || lo < 0) {
            return UUID(); // nil on parse failure
        }
        uuid.data_[byte_index] = static_cast<uint8_t>((hi << 4) | lo);
        ++byte_index;
        i += 2;
    }

    if (byte_index != 16) {
        return UUID(); // nil if not enough bytes
    }
    return uuid;
}

UUID UUID::from_bytes(const uint8_t bytes[16]) {
    UUID uuid;
    std::memcpy(uuid.data_, bytes, 16);
    return uuid;
}

std::string UUID::to_string() const {
    // Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    //         8-4-4-4-12
    static const char hex_chars[] = "0123456789abcdef";
    std::string result;
    result.reserve(36);

    for (int i = 0; i < 16; ++i) {
        if (i == 4 || i == 6 || i == 8 || i == 10) {
            result += '-';
        }
        result += hex_chars[(data_[i] >> 4) & 0x0F];
        result += hex_chars[data_[i] & 0x0F];
    }
    return result;
}

std::string UUID::to_short_string() const {
    static const char hex_chars[] = "0123456789abcdef";
    std::string result;
    result.reserve(32);

    for (int i = 0; i < 16; ++i) {
        result += hex_chars[(data_[i] >> 4) & 0x0F];
        result += hex_chars[data_[i] & 0x0F];
    }
    return result;
}

const uint8_t* UUID::bytes() const {
    return data_;
}

bool UUID::is_nil() const {
    for (auto byte : data_) {
        if (byte != 0) return false;
    }
    return true;
}

bool UUID::operator==(const UUID& other) const {
    return std::memcmp(data_, other.data_, 16) == 0;
}

bool UUID::operator!=(const UUID& other) const {
    return !(*this == other);
}

bool UUID::operator<(const UUID& other) const {
    return std::memcmp(data_, other.data_, 16) < 0;
}

}  // namespace utils
}  // namespace espx
