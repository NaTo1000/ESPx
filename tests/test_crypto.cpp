#include <cassert>
#include <iostream>
#include "espx/security/crypto.hpp"

using espx::security::Crypto;

int main() {
    {
        std::cout << "test sha256 empty string ... ";
        auto hash = Crypto::sha256(std::string(""));
        auto hex = Crypto::to_hex(hash);
        assert(hex == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test sha256 abc ... ";
        auto hash = Crypto::sha256(std::string("abc"));
        auto hex = Crypto::to_hex(hash);
        assert(hex == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test to_hex/from_hex round-trip ... ";
        std::vector<uint8_t> data = {0xDE, 0xAD, 0xBE, 0xEF};
        auto hex = Crypto::to_hex(data);
        assert(hex == "deadbeef");
        auto back = Crypto::from_hex(hex);
        assert(back == data);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test random_bytes length ... ";
        auto bytes = Crypto::random_bytes(32);
        assert(bytes.size() == 32);
        auto bytes2 = Crypto::random_bytes(0);
        assert(bytes2.empty());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test secure_compare ... ";
        std::vector<uint8_t> a = {1, 2, 3, 4};
        std::vector<uint8_t> b = {1, 2, 3, 4};
        std::vector<uint8_t> c = {1, 2, 3, 5};
        assert(Crypto::secure_compare(a, b));
        assert(!Crypto::secure_compare(a, c));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test hmac_sha256 ... ";
        std::vector<uint8_t> key(32, 0x0b);
        std::vector<uint8_t> data = {'H', 'i'};
        auto mac = Crypto::hmac_sha256(key, data);
        assert(mac.size() == 32);
        // Verify determinism
        auto mac2 = Crypto::hmac_sha256(key, data);
        assert(mac == mac2);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All crypto tests passed." << std::endl;
    return 0;
}
