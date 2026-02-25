#include <cassert>
#include <algorithm>
#include <iostream>
#include "espx/security/key_store.hpp"

using espx::security::KeyStore;
using espx::security::KeyType;

int main() {
    {
        std::cout << "test init ... ";
        KeyStore ks;
        assert(ks.init());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test generate_symmetric_key ... ";
        KeyStore ks;
        ks.init();
        assert(ks.generate_symmetric_key("aes256", 256));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test has_key ... ";
        KeyStore ks;
        ks.init();
        assert(!ks.has_key("mykey"));
        ks.generate_symmetric_key("mykey", 256);
        assert(ks.has_key("mykey"));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test get_key ... ";
        KeyStore ks;
        ks.init();
        ks.generate_symmetric_key("mykey", 256);
        auto data = ks.get_key("mykey");
        assert(!data.empty());
        assert(data.size() == 32);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test get_key_info ... ";
        KeyStore ks;
        ks.init();
        ks.generate_symmetric_key("mykey", 128);
        auto info = ks.get_key_info("mykey");
        assert(info.name == "mykey");
        assert(info.type == KeyType::Symmetric);
        assert(info.size_bits == 128);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test delete_key ... ";
        KeyStore ks;
        ks.init();
        ks.generate_symmetric_key("mykey", 256);
        assert(ks.delete_key("mykey"));
        assert(!ks.has_key("mykey"));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test list_keys ... ";
        KeyStore ks;
        ks.init();
        ks.generate_symmetric_key("key1", 256);
        ks.generate_symmetric_key("key2", 128);
        auto keys = ks.list_keys();
        assert(keys.size() == 2);
        assert(std::find(keys.begin(), keys.end(), "key1") != keys.end());
        assert(std::find(keys.begin(), keys.end(), "key2") != keys.end());
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All key_store tests passed." << std::endl;
    return 0;
}
