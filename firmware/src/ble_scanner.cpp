#include "ble_scanner.h"
#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

namespace BLEScanner {

    static BLEScan* pBLEScan = nullptr;

    void init() {
        BLEDevice::init("ESPx");
        pBLEScan = BLEDevice::getScan();
        pBLEScan->setActiveScan(true);
        pBLEScan->setInterval(100);
        pBLEScan->setWindow(99);
    }

    String scan(int durationSec) {
        DynamicJsonDocument doc(16384);
        doc["type"]      = "ble_scan";
        doc["timestamp"] = millis();
        doc["duration"]  = durationSec;

        BLEScanResults results = pBLEScan->start(durationSec, false);
        JsonArray devices = doc.createNestedArray("devices");

        for (int i = 0; i < results.getCount(); i++) {
            BLEAdvertisedDevice d = results.getDevice(i);
            JsonObject dev = devices.createNestedObject();

            dev["address"] = d.getAddress().toString().c_str();
            dev["rssi"]    = d.getRSSI();
            dev["name"]    = d.haveName() ? d.getName().c_str() : "";

            if (d.haveManufacturerData()) {
                String hex = "";
                std::string raw = d.getManufacturerData();
                for (size_t j = 0; j < raw.size() && j < 16; j++) {
                    char buf[3];
                    sprintf(buf, "%02X", (uint8_t)raw[j]);
                    hex += buf;
                }
                dev["manufacturer_data"] = hex;
            } else {
                dev["manufacturer_data"] = "";
            }

            dev["service_uuid"] = d.haveServiceUUID()
                                  ? d.getServiceUUID().toString().c_str()
                                  : "";
        }

        pBLEScan->clearResults();

        String result;
        serializeJson(doc, result);
        return result;
    }

} // namespace BLEScanner
