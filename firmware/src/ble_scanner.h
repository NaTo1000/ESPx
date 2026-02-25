#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>

/**
 * BLEScanner — scans for nearby BLE advertisers and returns a JSON string.
 *
 * JSON shape:
 *   {
 *     "type": "ble_scan",
 *     "timestamp": <millis>,
 *     "duration": <seconds>,
 *     "devices": [
 *       { "name", "address", "rssi",
 *         "manufacturer_data" (hex, first 16 bytes),
 *         "service_uuid" }
 *     ]
 *   }
 */
namespace BLEScanner {
    /** Initialise the BLE stack. */
    void init();

    /** Perform an active BLE scan for @p durationSec seconds and return JSON. */
    String scan(int durationSec = 5);
}
