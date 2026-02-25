#include <Arduino.h>
#include "wifi_scanner.h"
#include "ble_scanner.h"
#include "serial_protocol.h"

void setup() {
    Serial.begin(115200);
    Serial.println(F("{\"type\":\"boot\",\"message\":\"ESPx starting...\"}"));

    WiFiScanner::init();
    BLEScanner::init();
    SerialProtocol::init();

    Serial.println(F("{\"type\":\"boot\",\"message\":\"ESPx ready — send HELP for commands\"}"));
}

void loop() {
    SerialProtocol::handleCommand();
    delay(10);
}
