#include <cassert>
#include <cmath>
#include <iostream>
#include "espx/core/config.hpp"

using espx::core::Config;

int main() {
    {
        std::cout << "test set/get string, int, double, bool ... ";
        Config cfg;
        cfg.set("name", std::string("esp32"));
        cfg.set("port", static_cast<int64_t>(8080));
        cfg.set("rate", 3.14);
        cfg.set("debug", true);
        assert(cfg.get_string("name") == "esp32");
        assert(cfg.get_int("port") == 8080);
        assert(std::abs(cfg.get_double("rate") - 3.14) < 0.001);
        assert(cfg.get_bool("debug") == true);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test has ... ";
        Config cfg;
        cfg.set("key1", std::string("val"));
        assert(cfg.has("key1"));
        assert(!cfg.has("key2"));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test remove ... ";
        Config cfg;
        cfg.set("key1", std::string("val"));
        assert(cfg.remove("key1"));
        assert(!cfg.has("key1"));
        assert(!cfg.remove("key1"));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test keys with prefix ... ";
        Config cfg;
        cfg.set("wifi.ssid", std::string("net"));
        cfg.set("wifi.pass", std::string("secret"));
        cfg.set("bt.name", std::string("dev"));
        auto wifi_keys = cfg.keys("wifi.");
        assert(wifi_keys.size() == 2);
        auto all_keys = cfg.keys();
        assert(all_keys.size() == 3);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test clear ... ";
        Config cfg;
        cfg.set("a", static_cast<int64_t>(1));
        cfg.set("b", static_cast<int64_t>(2));
        cfg.clear();
        assert(cfg.size() == 0);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test size ... ";
        Config cfg;
        assert(cfg.size() == 0);
        cfg.set("x", static_cast<int64_t>(1));
        assert(cfg.size() == 1);
        cfg.set("y", static_cast<int64_t>(2));
        assert(cfg.size() == 2);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test to_json/from_json round-trip ... ";
        Config cfg;
        cfg.set("name", std::string("device"));
        cfg.set("count", static_cast<int64_t>(42));
        cfg.set("flag", true);
        auto json = cfg.to_json();

        Config cfg2;
        assert(cfg2.from_json(json));
        assert(cfg2.get_string("name") == "device");
        assert(cfg2.get_int("count") == 42);
        assert(cfg2.get_bool("flag") == true);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All config tests passed." << std::endl;
    return 0;
}
