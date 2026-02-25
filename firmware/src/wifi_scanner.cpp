#include "wifi_scanner.h"

namespace WiFiScanner {

    static const char* encryptionTypeStr(wifi_auth_mode_t type) {
        switch (type) {
            case WIFI_AUTH_OPEN:            return "OPEN";
            case WIFI_AUTH_WEP:             return "WEP";
            case WIFI_AUTH_WPA_PSK:         return "WPA";
            case WIFI_AUTH_WPA2_PSK:        return "WPA2";
            case WIFI_AUTH_WPA_WPA2_PSK:    return "WPA/WPA2";
            case WIFI_AUTH_WPA2_ENTERPRISE: return "WPA2-ENT";
            case WIFI_AUTH_WPA3_PSK:        return "WPA3";
            default:                        return "UNKNOWN";
        }
    }

    void init() {
        WiFi.mode(WIFI_STA);
        WiFi.disconnect();
        delay(100);
    }

    String scan() {
        DynamicJsonDocument doc(16384);
        doc["type"]      = "wifi_scan";
        doc["timestamp"] = millis();

        int n = WiFi.scanNetworks();
        JsonArray networks = doc.createNestedArray("networks");

        for (int i = 0; i < n; i++) {
            JsonObject net = networks.createNestedObject();
            net["ssid"]       = WiFi.SSID(i);
            net["bssid"]      = WiFi.BSSIDstr(i);
            net["rssi"]       = WiFi.RSSI(i);
            net["channel"]    = WiFi.channel(i);
            net["encryption"] = encryptionTypeStr(WiFi.encryptionType(i));

            int ch = WiFi.channel(i);
            if (ch >= 36) {
                net["band"] = "5GHz";
            } else {
                net["band"]          = "2.4GHz";
                net["frequency_mhz"] = 2412 + (ch - 1) * 5;
            }
        }

        WiFi.scanDelete();

        String result;
        serializeJson(doc, result);
        return result;
    }

} // namespace WiFiScanner
