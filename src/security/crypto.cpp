// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/security/crypto.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <random>
#include <stdexcept>

namespace espx {
namespace security {

// --- SHA-256 implementation (public domain algorithm) ---

namespace {

constexpr std::array<uint32_t, 64> K = {{
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
}};

inline uint32_t rotr(uint32_t x, unsigned n) {
    return (x >> n) | (x << (32 - n));
}

inline uint32_t ch(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (~x & z);
}

inline uint32_t maj(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (x & z) ^ (y & z);
}

inline uint32_t sigma0(uint32_t x) {
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
}

inline uint32_t sigma1(uint32_t x) {
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
}

inline uint32_t gamma0(uint32_t x) {
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
}

inline uint32_t gamma1(uint32_t x) {
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
}

std::vector<uint8_t> sha256_compute(const uint8_t* data, size_t len) {
    uint32_t h0 = 0x6a09e667, h1 = 0xbb67ae85;
    uint32_t h2 = 0x3c6ef372, h3 = 0xa54ff53a;
    uint32_t h4 = 0x510e527f, h5 = 0x9b05688c;
    uint32_t h6 = 0x1f83d9ab, h7 = 0x5be0cd19;

    // Pre-processing: pad message
    uint64_t bit_len = static_cast<uint64_t>(len) * 8;
    size_t padded_len = len + 1;
    while (padded_len % 64 != 56) ++padded_len;
    padded_len += 8;

    std::vector<uint8_t> msg(padded_len, 0);
    std::memcpy(msg.data(), data, len);
    msg[len] = 0x80;

    // Append length in big-endian
    for (int i = 0; i < 8; ++i) {
        msg[padded_len - 1 - static_cast<size_t>(i)] =
            static_cast<uint8_t>(bit_len >> (i * 8));
    }

    // Process each 64-byte block
    for (size_t offset = 0; offset < padded_len; offset += 64) {
        std::array<uint32_t, 64> w{};
        for (int i = 0; i < 16; ++i) {
            size_t base = offset + static_cast<size_t>(i) * 4;
            w[static_cast<size_t>(i)] =
                (static_cast<uint32_t>(msg[base]) << 24) |
                (static_cast<uint32_t>(msg[base + 1]) << 16) |
                (static_cast<uint32_t>(msg[base + 2]) << 8) |
                static_cast<uint32_t>(msg[base + 3]);
        }
        for (size_t i = 16; i < 64; ++i) {
            w[i] = gamma1(w[i - 2]) + w[i - 7] +
                   gamma0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = h0, b = h1, c = h2, d = h3;
        uint32_t e = h4, f = h5, g = h6, h = h7;

        for (size_t i = 0; i < 64; ++i) {
            uint32_t t1 = h + sigma1(e) + ch(e, f, g) + K[i] + w[i];
            uint32_t t2 = sigma0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }

        h0 += a; h1 += b; h2 += c; h3 += d;
        h4 += e; h5 += f; h6 += g; h7 += h;
    }

    std::vector<uint8_t> digest(32);
    auto put32 = [&](size_t off, uint32_t v) {
        digest[off]     = static_cast<uint8_t>(v >> 24);
        digest[off + 1] = static_cast<uint8_t>(v >> 16);
        digest[off + 2] = static_cast<uint8_t>(v >> 8);
        digest[off + 3] = static_cast<uint8_t>(v);
    };
    put32(0, h0);  put32(4, h1);  put32(8, h2);   put32(12, h3);
    put32(16, h4); put32(20, h5); put32(24, h6);  put32(28, h7);

    return digest;
}

}  // namespace

// --- Public API ---

std::vector<uint8_t> Crypto::sha256(const std::vector<uint8_t>& data) {
    return sha256_compute(data.data(), data.size());
}

std::vector<uint8_t> Crypto::sha256(const std::string& data) {
    return sha256_compute(
        reinterpret_cast<const uint8_t*>(data.data()), data.size());
}

std::vector<uint8_t> Crypto::hash(HashAlgorithm /*algorithm*/,
                                  const std::vector<uint8_t>& data) {
    // In simulation mode, all algorithms dispatch to SHA-256
    return sha256(data);
}

std::vector<uint8_t> Crypto::hmac_sha256(const std::vector<uint8_t>& key,
                                         const std::vector<uint8_t>& data) {
    constexpr size_t block_size = 64;

    // If key is longer than block size, hash it
    std::vector<uint8_t> k;
    if (key.size() > block_size) {
        k = sha256(key);
    } else {
        k = key;
    }
    k.resize(block_size, 0);

    // Inner and outer padding
    std::vector<uint8_t> i_pad(block_size);
    std::vector<uint8_t> o_pad(block_size);
    for (size_t i = 0; i < block_size; ++i) {
        i_pad[i] = k[i] ^ 0x36;
        o_pad[i] = k[i] ^ 0x5c;
    }

    // Inner hash: H(i_pad || data)
    i_pad.insert(i_pad.end(), data.begin(), data.end());
    auto inner_hash = sha256(i_pad);

    // Outer hash: H(o_pad || inner_hash)
    o_pad.insert(o_pad.end(), inner_hash.begin(), inner_hash.end());
    return sha256(o_pad);
}

// XOR-based AES simulation for host mode (not real AES)
std::vector<uint8_t> Crypto::aes_encrypt(
    const std::vector<uint8_t>& plaintext,
    const std::vector<uint8_t>& key,
    const std::vector<uint8_t>& iv) {
    std::vector<uint8_t> result(plaintext.size());
    for (size_t i = 0; i < plaintext.size(); ++i) {
        result[i] = plaintext[i] ^
            key[i % key.size()] ^
            iv[i % iv.size()];
    }
    return result;
}

std::vector<uint8_t> Crypto::aes_decrypt(
    const std::vector<uint8_t>& ciphertext,
    const std::vector<uint8_t>& key,
    const std::vector<uint8_t>& iv) {
    // XOR simulation is symmetric
    return aes_encrypt(ciphertext, key, iv);
}

std::vector<uint8_t> Crypto::random_bytes(size_t count) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<unsigned> dist(0, 255);

    std::vector<uint8_t> result(count);
    for (size_t i = 0; i < count; ++i) {
        result[i] = static_cast<uint8_t>(dist(gen));
    }
    return result;
}

uint32_t Crypto::random_int(uint32_t min, uint32_t max) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint32_t> dist(min, max);
    return dist(gen);
}

std::string Crypto::to_hex(const std::vector<uint8_t>& data) {
    static const char hex_chars[] = "0123456789abcdef";
    std::string result;
    result.reserve(data.size() * 2);
    for (uint8_t byte : data) {
        result += hex_chars[(byte >> 4) & 0x0f];
        result += hex_chars[byte & 0x0f];
    }
    return result;
}

std::vector<uint8_t> Crypto::from_hex(const std::string& hex) {
    std::string input = hex;
    if (input.size() >= 2 && input[0] == '0' &&
        (input[1] == 'x' || input[1] == 'X')) {
        input = input.substr(2);
    }

    std::vector<uint8_t> result;
    result.reserve(input.size() / 2);

    auto hex_val = [](char c) -> uint8_t {
        if (c >= '0' && c <= '9') return static_cast<uint8_t>(c - '0');
        if (c >= 'a' && c <= 'f') return static_cast<uint8_t>(c - 'a' + 10);
        if (c >= 'A' && c <= 'F') return static_cast<uint8_t>(c - 'A' + 10);
        return 0;
    };

    for (size_t i = 0; i + 1 < input.size(); i += 2) {
        result.push_back(
            static_cast<uint8_t>((hex_val(input[i]) << 4) |
                                  hex_val(input[i + 1])));
    }
    return result;
}

bool Crypto::secure_compare(const std::vector<uint8_t>& a,
                            const std::vector<uint8_t>& b) {
    if (a.size() != b.size()) return false;

    volatile uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<uint8_t>(a[i] ^ b[i]);
    }
    return diff == 0;
}

}  // namespace security
}  // namespace espx
