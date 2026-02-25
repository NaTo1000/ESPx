#include <cassert>
#include <iostream>
#include "espx/security/vault.hpp"

using espx::security::Vault;

int main() {
    {
        std::cout << "test init ... ";
        Vault v;
        assert(v.init("master_key_for_testing!"));
        assert(v.is_initialized());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test store/retrieve_string ... ";
        Vault v;
        v.init("master_key_for_testing!!");
        assert(v.store("password", "s3cret"));
        auto val = v.retrieve_string("password");
        assert(val == "s3cret");
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test store/retrieve binary ... ";
        Vault v;
        v.init("master_key_for_testing!!");
        std::vector<uint8_t> data = {0x01, 0x02, 0x03, 0xFF};
        assert(v.store("bindata", data));
        auto retrieved = v.retrieve("bindata");
        assert(retrieved == data);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test has ... ";
        Vault v;
        v.init("master_key_for_testing!!");
        assert(!v.has("key1"));
        v.store("key1", "val1");
        assert(v.has("key1"));
        assert(!v.has("key2"));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test remove ... ";
        Vault v;
        v.init("master_key_for_testing!!");
        v.store("key1", "val1");
        assert(v.remove("key1"));
        assert(!v.has("key1"));
        assert(!v.remove("key1"));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test keys ... ";
        Vault v;
        v.init("master_key_for_testing!!");
        v.store("a", "1");
        v.store("b", "2");
        auto k = v.keys();
        assert(k.size() == 2);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test size ... ";
        Vault v;
        v.init("master_key_for_testing!!");
        assert(v.size() == 0);
        v.store("a", "1");
        assert(v.size() == 1);
        v.store("b", "2");
        assert(v.size() == 2);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All vault tests passed." << std::endl;
    return 0;
}
