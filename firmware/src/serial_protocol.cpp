#include "serial_protocol.h"
#include "wifi_scanner.h"
#include "ble_scanner.h"

namespace SerialProtocol {

    static String inputBuffer = "";

    void init() { /* nothing yet */ }

    static void processCommand(const String& raw) {
        String cmd = raw;
        cmd.trim();
        cmd.toUpperCase();

        if (cmd == "SCAN_WIFI") {
            Serial.println(F("{\"type\":\"status\",\"message\":\"Scanning WiFi...\"}"));
            Serial.println(WiFiScanner::scan());

        } else if (cmd.startsWith("SCAN_BLE")) {
            int duration = 5;
            int spaceIdx = cmd.indexOf(' ');
            if (spaceIdx > 0) {
                int v = cmd.substring(spaceIdx + 1).toInt();
                if (v >= 1 && v <= 30) duration = v;
            }
            Serial.println(F("{\"type\":\"status\",\"message\":\"Scanning BLE...\"}"));
            Serial.println(BLEScanner::scan(duration));

        } else if (cmd == "STATUS") {
            Serial.println(
                "{\"type\":\"status\",\"fw_version\":\"1.0.0\","
                "\"uptime_ms\":" + String(millis()) +
                ",\"free_heap\":"  + String(ESP.getFreeHeap()) + "}");

        } else if (cmd == "HELP") {
            Serial.println(
                F("{\"type\":\"help\",\"commands\":"
                  "[\"SCAN_WIFI\",\"SCAN_BLE [seconds]\",\"STATUS\",\"HELP\"]}"));

        } else if (cmd.length() > 0) {
            Serial.println("{\"type\":\"error\",\"message\":\"Unknown command: " + cmd + "\"}");
        }
    }

    void handleCommand() {
        while (Serial.available()) {
            char c = (char)Serial.read();
            if (c == '\n' || c == '\r') {
                if (inputBuffer.length() > 0) {
                    processCommand(inputBuffer);
                    inputBuffer = "";
                }
            } else {
                inputBuffer += c;
            }
        }
    }

} // namespace SerialProtocol
