#include <cassert>
#include <iostream>
#include "espx/utils/base64.hpp"

using espx::utils::Base64;

int main() {
    {
        std::cout << "test encode/decode round-trip ... ";
        std::string original = "The quick brown fox";
        std::string encoded = Base64::encode(original);
        std::string decoded = Base64::decode_string(encoded);
        assert(decoded == original);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test encode empty string ... ";
        std::string encoded = Base64::encode(std::string(""));
        assert(encoded.empty());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test encode Hello World ... ";
        std::string encoded = Base64::encode(std::string("Hello, World!"));
        assert(encoded == "SGVsbG8sIFdvcmxkIQ==");
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test decode back to original ... ";
        std::string decoded = Base64::decode_string("SGVsbG8sIFdvcmxkIQ==");
        assert(decoded == "Hello, World!");
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test URL-safe encode/decode ... ";
        std::string original = "subjects?_d";
        std::string url_enc = Base64::encode_url_safe(original);
        assert(url_enc.find('+') == std::string::npos);
        assert(url_enc.find('/') == std::string::npos);
        assert(url_enc.find('=') == std::string::npos);
        auto bytes = Base64::decode_url_safe(url_enc);
        std::string decoded(bytes.begin(), bytes.end());
        assert(decoded == original);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test is_valid ... ";
        assert(Base64::is_valid("SGVsbG8="));
        assert(Base64::is_valid(""));
        assert(!Base64::is_valid("SGVs@bG8="));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test encoded_length/decoded_length ... ";
        assert(Base64::encoded_length(0) == 0);
        assert(Base64::encoded_length(1) == 4);
        assert(Base64::encoded_length(3) == 4);
        assert(Base64::decoded_length(4) == 3);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All base64 tests passed." << std::endl;
    return 0;
}
