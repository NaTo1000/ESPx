#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>

/**
 * WiFiScanner — scans visible 802.11 networks and returns a JSON string.
 *
 * JSON shape:
 *   {
 *     "type": "wifi_scan",
 *     "timestamp": <millis>,
 *     "networks": [
 *       { "ssid", "bssid", "rssi", "channel", "band",
 *         "frequency_mhz" (2.4 GHz only), "encryption" }
 *     ]
 *   }
 */
namespace WiFiScanner {
    /** Initialise the WiFi peripheral in station mode. */
    void init();

    /** Perform a blocking scan and return the JSON result string. */
    String scan();
}
