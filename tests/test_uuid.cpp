#include <cassert>
#include <iostream>
#include "espx/utils/uuid.hpp"

using espx::utils::UUID;

int main() {
    {
        std::cout << "test generate non-nil ... ";
        auto id = UUID::generate();
        assert(!id.is_nil());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test to_string format ... ";
        auto id = UUID::generate();
        auto s = id.to_string();
        assert(s.size() == 36);
        assert(s[8] == '-');
        assert(s[13] == '-');
        assert(s[18] == '-');
        assert(s[23] == '-');
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test from_string round-trip ... ";
        auto id = UUID::generate();
        auto s = id.to_string();
        auto parsed = UUID::from_string(s);
        assert(parsed == id);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test two UUIDs are different ... ";
        auto a = UUID::generate();
        auto b = UUID::generate();
        assert(a != b);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test nil UUID ... ";
        UUID nil;
        assert(nil.is_nil());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test comparison operators ... ";
        auto a = UUID::generate();
        auto b = UUID::generate();
        assert(a == a);
        assert(!(a != a));
        // less-than should be consistent
        assert((a < b) || (b < a) || (a == b));
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All uuid tests passed." << std::endl;
    return 0;
}
