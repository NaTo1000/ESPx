#pragma once
#include <Arduino.h>

/**
 * SerialProtocol — newline-delimited JSON command/response protocol.
 *
 * Commands (send as ASCII lines, case-insensitive):
 *   SCAN_WIFI           — trigger a WiFi scan; reply: wifi_scan JSON
 *   SCAN_BLE [seconds]  — BLE scan for N seconds (default 5); reply: ble_scan JSON
 *   STATUS              — device info; reply: status JSON
 *   HELP                — list available commands
 */
namespace SerialProtocol {
    void init();
    void handleCommand();
}
