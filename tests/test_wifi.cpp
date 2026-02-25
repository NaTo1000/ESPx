#include <cassert>
#include <iostream>
#include "espx/wifi/wifi_manager.hpp"
#include "espx/wifi/scanner.hpp"
#include "espx/wifi/ap_mode.hpp"

using namespace espx::wifi;

int main() {
    {
        std::cout << "test WiFiManager init/connect ... ";
        WiFiManager mgr;
        assert(mgr.init(WiFiMode::Station));
        WiFiConfig cfg;
        cfg.ssid = "TestNet";
        cfg.password = "pass1234";
        assert(mgr.connect(cfg));
        assert(mgr.is_connected());
        assert(!mgr.ip_address().empty());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test Scanner scan_sync ... ";
        Scanner scanner;
        auto results = scanner.scan_sync();
        assert(!results.empty());
        assert(scanner.result_count() == results.size());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test APMode start/is_active/station_count ... ";
        APMode ap;
        APConfig cfg;
        cfg.ssid = "ESPx-AP";
        cfg.password = "12345678";
        assert(ap.start(cfg));
        assert(ap.is_active());
        assert(ap.station_count() == 0);
        ap.stop();
        assert(!ap.is_active());
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All wifi tests passed." << std::endl;
    return 0;
}
