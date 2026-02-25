"""
Firmware Knowledge Base
=======================
A comprehensive catalog of ESP32 firmware capabilities, patterns, libraries,
and configuration templates. Each entry describes a capability domain, its
keywords (for intent matching), a short description, code hints, and links
to relevant resources or IDF/Arduino components.
"""

# ---------------------------------------------------------------------------
# Schema for each entry:
# {
#   "id":          unique slug,
#   "title":       human-readable capability title,
#   "keywords":    list of words/phrases that signal user intent,
#   "description": plain-English explanation,
#   "use_cases":   concrete example applications,
#   "firmware": {
#       "framework": "arduino" | "esp-idf" | "both",
#       "components": [list of IDF components or Arduino libraries],
#       "snippet":    minimal code sketch,
#   },
#   "tags":        broad topic tags for grouping,
# }
# ---------------------------------------------------------------------------

FIRMWARE_KNOWLEDGE_BASE = [

    # ------------------------------------------------------------------ WiFi
    {
        "id": "wifi_sta",
        "title": "WiFi Station (STA) Mode",
        "keywords": [
            "wifi", "wi-fi", "wireless", "internet", "connect", "network",
            "station", "sta", "ssid", "password", "ip address", "dhcp",
            "online", "web", "http", "cloud",
        ],
        "description": (
            "Connect the ESP32 to an existing WiFi access point as a station. "
            "Provides full TCP/IP networking, DHCP, and internet access."
        ),
        "use_cases": [
            "Send sensor data to a cloud API",
            "Download firmware OTA updates",
            "Control device from a mobile app over the internet",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_wifi", "WiFi.h (Arduino)"],
            "snippet": (
                "#include <WiFi.h>\n"
                "WiFi.begin(\"YOUR_SSID\", \"YOUR_PASSWORD\");\n"
                "while (WiFi.status() != WL_CONNECTED) delay(500);\n"
                "Serial.println(WiFi.localIP());"
            ),
        },
        "tags": ["wifi", "networking", "connectivity"],
    },

    {
        "id": "wifi_ap",
        "title": "WiFi Access Point (AP) Mode",
        "keywords": [
            "access point", "hotspot", "ap mode", "captive portal", "provision",
            "wifi setup", "soft ap", "softap", "local network", "host",
        ],
        "description": (
            "Run the ESP32 as a WiFi access point so other devices can connect "
            "directly to it without an external router."
        ),
        "use_cases": [
            "First-time WiFi provisioning via captive portal",
            "Device-to-device communication without infrastructure",
            "Offline local control panel",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_wifi", "WiFi.h (Arduino)", "DNSServer.h"],
            "snippet": (
                "#include <WiFi.h>\n"
                "WiFi.softAP(\"ESPx_AP\", \"password123\");\n"
                "Serial.println(WiFi.softAPIP());"
            ),
        },
        "tags": ["wifi", "networking", "ap"],
    },

    {
        "id": "wifi_smart_config",
        "title": "WiFi SmartConfig / ESP-Touch Provisioning",
        "keywords": [
            "smartconfig", "esp-touch", "provisioning", "zero config",
            "auto connect", "phone setup", "mobile provision",
        ],
        "description": (
            "Allow users to configure WiFi credentials from a smartphone app "
            "using the ESP-Touch / SmartConfig protocol."
        ),
        "use_cases": [
            "Out-of-box device setup without hardcoded credentials",
            "Consumer IoT product onboarding",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_smartconfig", "WiFi.h"],
            "snippet": (
                "WiFi.beginSmartConfig();\n"
                "while (!WiFi.smartConfigDone()) { delay(500); }\n"
                "WiFi.stopSmartConfig();"
            ),
        },
        "tags": ["wifi", "provisioning", "iot"],
    },

    # ------------------------------------------------------------------ BLE
    {
        "id": "ble_server",
        "title": "Bluetooth Low Energy (BLE) GATT Server",
        "keywords": [
            "bluetooth", "ble", "gatt", "notify", "characteristic",
            "service", "beacon", "proximity", "wearable", "heart rate",
            "sensor data", "mobile app", "phone", "iOS", "android",
        ],
        "description": (
            "Expose sensor data or control endpoints over BLE using standard "
            "GATT services and characteristics."
        ),
        "use_cases": [
            "Health / fitness wearable",
            "Bluetooth-controlled robot or motor driver",
            "Low-power sensor node polled by a smartphone",
        ],
        "firmware": {
            "framework": "both",
            "components": ["bt", "NimBLE-Arduino", "BLEDevice.h"],
            "snippet": (
                "#include <BLEDevice.h>\n"
                "#include <BLEServer.h>\n"
                "BLEDevice::init(\"ESPx_BLE\");\n"
                "BLEServer *pServer = BLEDevice::createServer();\n"
                "BLEService *pService = pServer->createService(SERVICE_UUID);\n"
                "BLECharacteristic *pChar = pService->createCharacteristic(\n"
                "    CHAR_UUID, BLECharacteristic::PROPERTY_READ | PROPERTY_NOTIFY);\n"
                "pService->start();"
            ),
        },
        "tags": ["bluetooth", "ble", "wireless", "connectivity"],
    },

    {
        "id": "ble_scanner",
        "title": "BLE Scanner / iBeacon Detection",
        "keywords": [
            "ble scan", "beacon", "ibeacon", "eddystone", "indoor positioning",
            "asset tracking", "presence detection", "bluetooth scan",
        ],
        "description": (
            "Scan for nearby BLE advertisements to detect beacons, track assets, "
            "or implement indoor positioning."
        ),
        "use_cases": [
            "Indoor asset tracking",
            "Presence / occupancy detection",
            "Smart home entry triggers",
        ],
        "firmware": {
            "framework": "both",
            "components": ["bt", "BLEScan.h"],
            "snippet": (
                "BLEScan *pScan = BLEDevice::getScan();\n"
                "pScan->setActiveScan(true);\n"
                "BLEScanResults results = pScan->start(5);\n"
                "for (int i=0;i<results.getCount();i++) {\n"
                "    Serial.println(results.getDevice(i).toString().c_str());\n"
                "}"
            ),
        },
        "tags": ["bluetooth", "ble", "scanning"],
    },

    # ----------------------------------------------------------------- MQTT
    {
        "id": "mqtt_client",
        "title": "MQTT Pub/Sub Client",
        "keywords": [
            "mqtt", "publish", "subscribe", "broker", "topic", "message",
            "home assistant", "node-red", "iot hub", "telemetry",
            "command", "event driven", "lightweight protocol",
        ],
        "description": (
            "Publish sensor readings and subscribe to command topics over MQTT, "
            "the dominant lightweight IoT messaging protocol."
        ),
        "use_cases": [
            "Home automation with Home Assistant",
            "Industrial telemetry to MQTT broker",
            "Fleet management via centralised broker",
        ],
        "firmware": {
            "framework": "both",
            "components": ["PubSubClient", "esp-mqtt (IDF)"],
            "snippet": (
                "#include <PubSubClient.h>\n"
                "WiFiClient wc; PubSubClient mqtt(wc);\n"
                "mqtt.setServer(\"broker.local\", 1883);\n"
                "mqtt.connect(\"esp32_client\");\n"
                "mqtt.publish(\"sensors/temp\", \"23.5\");\n"
                "mqtt.subscribe(\"cmd/relay\");"
            ),
        },
        "tags": ["mqtt", "networking", "iot", "protocol"],
    },

    # ----------------------------------------------------------------- HTTP
    {
        "id": "http_server",
        "title": "Embedded HTTP / REST API Server",
        "keywords": [
            "http server", "web server", "rest api", "api", "endpoint",
            "dashboard", "browser", "curl", "json", "webpage", "ui",
            "control panel", "local web", "esp_http_server",
        ],
        "description": (
            "Host a lightweight HTTP server on the ESP32 to serve web pages, "
            "REST API endpoints, or a configuration dashboard."
        ),
        "use_cases": [
            "Browser-based device dashboard",
            "REST API for mobile app integration",
            "Firmware configuration over HTTP",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_http_server", "WebServer.h (Arduino)", "ESPAsyncWebServer"],
            "snippet": (
                "#include <WebServer.h>\n"
                "WebServer server(80);\n"
                "server.on(\"/\", [](){\n"
                "    server.send(200, \"text/html\", \"<h1>ESPx</h1>\");\n"
                "});\n"
                "server.begin();"
            ),
        },
        "tags": ["http", "networking", "web", "api"],
    },

    {
        "id": "https_client",
        "title": "Secure HTTPS Client (TLS/SSL)",
        "keywords": [
            "https", "tls", "ssl", "secure", "certificate", "api call",
            "post request", "get request", "openweathermap", "rest client",
            "secure cloud", "mbedtls",
        ],
        "description": (
            "Make secure HTTPS requests to cloud APIs using the built-in "
            "mbedTLS stack, including certificate validation."
        ),
        "use_cases": [
            "Post data to AWS IoT / Azure IoT Hub over HTTPS",
            "Fetch weather or stock data from public APIs",
            "Secure OTA firmware download",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_http_client", "HTTPClient.h", "mbedtls"],
            "snippet": (
                "#include <HTTPClient.h>\n"
                "#include <WiFiClientSecure.h>\n"
                "WiFiClientSecure client;\n"
                "client.setCACert(root_ca);\n"
                "HTTPClient https;\n"
                "https.begin(client, \"https://api.example.com/data\");\n"
                "int code = https.GET();"
            ),
        },
        "tags": ["https", "networking", "security", "api"],
    },

    # ------------------------------------------------------------------ OTA
    {
        "id": "ota_update",
        "title": "Over-the-Air (OTA) Firmware Updates",
        "keywords": [
            "ota", "over the air", "update", "firmware update", "remote update",
            "deploy", "flash", "upgrade", "rollback", "partition", "delta ota",
        ],
        "description": (
            "Update device firmware wirelessly over WiFi, with support for "
            "rollback on failed updates using dual-partition schemes."
        ),
        "use_cases": [
            "Deploy bug fixes without physical access",
            "Staged fleet-wide firmware rollouts",
            "Self-healing devices with rollback",
        ],
        "firmware": {
            "framework": "both",
            "components": ["app_update", "esp_https_ota", "ArduinoOTA"],
            "snippet": (
                "#include <ArduinoOTA.h>\n"
                "ArduinoOTA.setHostname(\"espx-device\");\n"
                "ArduinoOTA.onProgress([](unsigned int p, unsigned int t){\n"
                "    Serial.printf(\"OTA: %u%%\\n\", (p*100)/t);\n"
                "});\n"
                "ArduinoOTA.begin();\n"
                "// In loop(): ArduinoOTA.handle();"
            ),
        },
        "tags": ["ota", "update", "maintenance"],
    },

    # ---------------------------------------------------------------- Sensors
    {
        "id": "temperature_humidity",
        "title": "Temperature & Humidity Sensing (DHT / SHT / BME)",
        "keywords": [
            "temperature", "humidity", "dht11", "dht22", "sht30", "sht31",
            "bme280", "bme680", "climate", "weather station", "hvac",
            "thermostat", "ambient", "air quality",
        ],
        "description": (
            "Read temperature and relative humidity from common I²C or 1-Wire "
            "sensors. BME series additionally provides pressure and VOC data."
        ),
        "use_cases": [
            "Smart thermostat",
            "Greenhouse climate monitor",
            "Weather station node",
        ],
        "firmware": {
            "framework": "both",
            "components": ["DHT sensor library", "Adafruit BME280", "SHT31 library"],
            "snippet": (
                "#include <DHT.h>\n"
                "DHT dht(4, DHT22);\n"
                "dht.begin();\n"
                "float t = dht.readTemperature();\n"
                "float h = dht.readHumidity();"
            ),
        },
        "tags": ["sensor", "environmental", "i2c", "1-wire"],
    },

    {
        "id": "imu_motion",
        "title": "IMU / Motion Sensing (MPU-6050 / ICM-42688)",
        "keywords": [
            "imu", "accelerometer", "gyroscope", "motion", "tilt", "orientation",
            "gesture", "fall detection", "mpu6050", "mpu9250", "icm42688",
            "6dof", "9dof", "ahrs", "quaternion", "angle",
        ],
        "description": (
            "Read 6-axis or 9-axis inertial data, compute orientation using "
            "AHRS algorithms (Mahony, Madgwick), and detect gestures or falls."
        ),
        "use_cases": [
            "Drone / robot stabilisation",
            "Wearable fall detection",
            "Game controller gesture input",
        ],
        "firmware": {
            "framework": "both",
            "components": ["MPU6050 library", "Adafruit ICM series", "MahonyAHRS"],
            "snippet": (
                "#include <MPU6050.h>\n"
                "MPU6050 mpu;\n"
                "mpu.initialize();\n"
                "int16_t ax,ay,az,gx,gy,gz;\n"
                "mpu.getMotion6(&ax,&ay,&az,&gx,&gy,&gz);"
            ),
        },
        "tags": ["sensor", "motion", "imu", "i2c"],
    },

    {
        "id": "distance_ranging",
        "title": "Distance / Ranging Sensors (HC-SR04 / VL53L0X / TF-Luna)",
        "keywords": [
            "distance", "ranging", "ultrasonic", "lidar", "tof", "time of flight",
            "hc-sr04", "vl53l0x", "proximity", "obstacle", "collision",
            "robot navigation", "parking sensor",
        ],
        "description": (
            "Measure distance using ultrasonic or ToF laser sensors. "
            "Ultrasonic covers 2 cm–4 m; ToF LiDAR covers 2 cm–12 m."
        ),
        "use_cases": [
            "Obstacle avoidance robot",
            "Smart parking indicator",
            "Liquid level measurement",
        ],
        "firmware": {
            "framework": "both",
            "components": ["NewPing", "Adafruit VL53L0X", "vl53l0x-esp-idf"],
            "snippet": (
                "#include <NewPing.h>\n"
                "NewPing sonar(TRIG_PIN, ECHO_PIN, 200);\n"
                "unsigned int dist = sonar.ping_cm();\n"
                "Serial.printf(\"Distance: %u cm\\n\", dist);"
            ),
        },
        "tags": ["sensor", "distance", "ultrasonic", "lidar"],
    },

    {
        "id": "adc_analog",
        "title": "Analog Sensor Reading (ADC)",
        "keywords": [
            "analog", "adc", "voltage", "potentiometer", "light sensor", "ldr",
            "soil moisture", "ph sensor", "gas sensor", "mq2", "mq135",
            "current sensor", "acs712", "raw reading",
        ],
        "description": (
            "Read 12-bit ADC values from ESP32 GPIO pins (with attenuation config) "
            "for analog sensors like LDR, soil moisture, gas detectors, etc."
        ),
        "use_cases": [
            "Soil moisture alert for plant watering",
            "Gas / smoke alarm",
            "Battery voltage monitor",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_adc_cal (IDF)", "analogRead() (Arduino)"],
            "snippet": (
                "analogSetAttenuation(ADC_11db);\n"
                "int raw = analogRead(34);\n"
                "float voltage = raw * (3.3f / 4095.0f);\n"
                "Serial.printf(\"%.2f V\\n\", voltage);"
            ),
        },
        "tags": ["sensor", "adc", "analog"],
    },

    {
        "id": "camera_vision",
        "title": "Camera & Computer Vision (ESP32-CAM / OV2640)",
        "keywords": [
            "camera", "photo", "image", "video", "stream", "face detection",
            "qr code", "barcode", "esp32-cam", "ov2640", "jpeg", "snapshot",
            "surveillance", "doorbell", "vision", "opencv",
        ],
        "description": (
            "Capture JPEG images or stream MJPEG video using the ESP32-CAM module "
            "with the OV2640 sensor. Includes face detection examples."
        ),
        "use_cases": [
            "WiFi surveillance camera",
            "Smart doorbell with snapshot to MQTT",
            "QR / barcode scanner kiosk",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp32-camera", "esp_camera.h"],
            "snippet": (
                "#include \"esp_camera.h\"\n"
                "camera_config_t config = { /* pin definitions */ };\n"
                "esp_camera_init(&config);\n"
                "camera_fb_t *fb = esp_camera_fb_get();\n"
                "// fb->buf, fb->len contain JPEG data\n"
                "esp_camera_fb_return(fb);"
            ),
        },
        "tags": ["camera", "vision", "media", "image"],
    },

    # --------------------------------------------------------------- Display
    {
        "id": "oled_display",
        "title": "OLED Display (SSD1306 / SH1106 via I²C / SPI)",
        "keywords": [
            "oled", "display", "screen", "ssd1306", "sh1106", "i2c display",
            "show text", "draw", "pixel", "dashboard", "status display",
            "128x64", "u8g2",
        ],
        "description": (
            "Drive monochrome OLED displays to show sensor readings, status "
            "messages, or simple graphics with the U8g2 or Adafruit SSD1306 library."
        ),
        "use_cases": [
            "Portable sensor display",
            "Device status / IP address screen",
            "Mini game console",
        ],
        "firmware": {
            "framework": "both",
            "components": ["U8g2", "Adafruit SSD1306", "Adafruit GFX"],
            "snippet": (
                "#include <U8g2lib.h>\n"
                "U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0);\n"
                "u8g2.begin();\n"
                "u8g2.clearBuffer();\n"
                "u8g2.setFont(u8g2_font_ncenB08_tr);\n"
                "u8g2.drawStr(0, 20, \"ESPx Ready\");\n"
                "u8g2.sendBuffer();"
            ),
        },
        "tags": ["display", "oled", "i2c", "ui"],
    },

    {
        "id": "tft_display",
        "title": "TFT / LCD Colour Display (ILI9341 / ST7789)",
        "keywords": [
            "tft", "lcd", "colour display", "color display", "ili9341", "st7789",
            "ili9488", "touch screen", "graphics", "sprite", "lvgl",
            "gui", "240x240", "320x240",
        ],
        "description": (
            "Drive colour TFT LCD panels over SPI with TFT_eSPI or LVGL for "
            "rich graphical user interfaces including touch input."
        ),
        "use_cases": [
            "Graphical instrument cluster",
            "Touch-screen control panel",
            "Data logger with chart display",
        ],
        "firmware": {
            "framework": "both",
            "components": ["TFT_eSPI", "LVGL", "Adafruit ILI9341"],
            "snippet": (
                "#include <TFT_eSPI.h>\n"
                "TFT_eSPI tft;\n"
                "tft.init();\n"
                "tft.setRotation(1);\n"
                "tft.fillScreen(TFT_BLACK);\n"
                "tft.setTextColor(TFT_GREEN);\n"
                "tft.drawString(\"ESPx\", 10, 10, 4);"
            ),
        },
        "tags": ["display", "tft", "lcd", "gui", "spi"],
    },

    # -------------------------------------------------------------- Protocol
    {
        "id": "i2c_bus",
        "title": "I²C Bus Master (Scan, Read, Write)",
        "keywords": [
            "i2c", "i2c scan", "wire", "sda", "scl", "slave address",
            "register read", "sensor bus", "multiple sensors",
        ],
        "description": (
            "Initialise the I²C bus, scan for connected devices, and "
            "read/write registers on I²C peripherals."
        ),
        "use_cases": [
            "Multi-sensor node on a single bus",
            "EEPROM data storage",
            "Real-time clock (RTC) module",
        ],
        "firmware": {
            "framework": "both",
            "components": ["Wire.h", "i2c_master (IDF)"],
            "snippet": (
                "#include <Wire.h>\n"
                "Wire.begin(SDA_PIN, SCL_PIN);\n"
                "// Scan\n"
                "for(uint8_t addr=1;addr<127;addr++){\n"
                "    Wire.beginTransmission(addr);\n"
                "    if(Wire.endTransmission()==0)\n"
                "        Serial.printf(\"Found: 0x%02X\\n\",addr);\n"
                "}"
            ),
        },
        "tags": ["i2c", "protocol", "bus"],
    },

    {
        "id": "spi_bus",
        "title": "SPI Bus (Master / Slave)",
        "keywords": [
            "spi", "mosi", "miso", "sck", "cs", "chip select", "sd card",
            "flash memory", "high speed", "dma", "vspi", "hspi",
        ],
        "description": (
            "Configure the ESP32 SPI controller as master or slave for high-speed "
            "peripheral communication (displays, SD cards, ADC chips, etc.)."
        ),
        "use_cases": [
            "SD card data logging",
            "High-resolution ADC / DAC",
            "RF module (LoRa, NRF24)",
        ],
        "firmware": {
            "framework": "both",
            "components": ["SPI.h", "spi_master (IDF)"],
            "snippet": (
                "#include <SPI.h>\n"
                "SPI.begin(SCK, MISO, MOSI, CS);\n"
                "digitalWrite(CS, LOW);\n"
                "SPI.transfer(0xAB);\n"
                "digitalWrite(CS, HIGH);"
            ),
        },
        "tags": ["spi", "protocol", "bus"],
    },

    {
        "id": "uart_serial",
        "title": "UART / Serial Communication",
        "keywords": [
            "uart", "serial", "rs232", "rs485", "modbus", "gps", "nmea",
            "at commands", "gsm", "sim800", "sim7600", "baud rate",
            "hardware serial", "softwareserial",
        ],
        "description": (
            "Use one of the three hardware UART ports to communicate with GPS "
            "modules, GSM modems, RS-485 devices, or any serial peripheral."
        ),
        "use_cases": [
            "GPS tracking (NMEA parsing)",
            "GSM / LTE modem for cellular IoT",
            "Modbus RTU industrial sensor",
        ],
        "firmware": {
            "framework": "both",
            "components": ["HardwareSerial", "TinyGPS++", "ModbusMaster"],
            "snippet": (
                "Serial2.begin(9600, SERIAL_8N1, RX2, TX2);\n"
                "while(Serial2.available()){\n"
                "    char c = Serial2.read();\n"
                "    Serial.print(c);\n"
                "}"
            ),
        },
        "tags": ["uart", "serial", "protocol", "gps"],
    },

    {
        "id": "lora_wan",
        "title": "LoRa / LoRaWAN Long-Range Radio",
        "keywords": [
            "lora", "lorawan", "long range", "915mhz", "868mhz", "sx1276",
            "sx1278", "heltec", "ttgo lora", "the things network", "ttn",
            "low power wide area", "lpwan", "chirpstack",
        ],
        "description": (
            "Transmit small data payloads over kilometres using LoRa radio. "
            "LoRaWAN connects to public/private networks like The Things Network."
        ),
        "use_cases": [
            "Remote agriculture / livestock monitoring",
            "Smart city sensor mesh",
            "Asset tracking in areas without cellular",
        ],
        "firmware": {
            "framework": "both",
            "components": ["LoRa library", "LMIC / arduino-lmic", "RadioLib"],
            "snippet": (
                "#include <LoRa.h>\n"
                "LoRa.begin(915E6);\n"
                "LoRa.beginPacket();\n"
                "LoRa.print(\"Hello LoRa\");\n"
                "LoRa.endPacket();"
            ),
        },
        "tags": ["lora", "lorawan", "radio", "lpwan"],
    },

    {
        "id": "espnow",
        "title": "ESP-NOW Peer-to-Peer Mesh",
        "keywords": [
            "esp-now", "espnow", "peer to peer", "p2p", "mesh", "broadcast",
            "no router", "direct link", "fast pairing", "latency",
            "multi-device", "swarm",
        ],
        "description": (
            "Use Espressif's ESP-NOW protocol for ultra-low-latency direct "
            "communication between ESP32/ESP8266 devices without WiFi infrastructure."
        ),
        "use_cases": [
            "RC car / drone controller",
            "Wireless sensor mesh without router",
            "Button → action bridge across rooms",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_now.h", "esp-now (Arduino)"],
            "snippet": (
                "#include <esp_now.h>\n"
                "#include <WiFi.h>\n"
                "WiFi.mode(WIFI_STA);\n"
                "esp_now_init();\n"
                "esp_now_peer_info_t peer = {};\n"
                "memcpy(peer.peer_addr, broadcastAddress, 6);\n"
                "esp_now_add_peer(&peer);\n"
                "esp_now_send(broadcastAddress, data, sizeof(data));"
            ),
        },
        "tags": ["espnow", "wireless", "mesh", "p2p"],
    },

    # ------------------------------------------------------------ Power Mgmt
    {
        "id": "deep_sleep",
        "title": "Deep Sleep & Ultra-Low Power Modes",
        "keywords": [
            "deep sleep", "low power", "battery", "sleep mode", "wake up",
            "ulp", "rtc", "timer wakeup", "gpio wakeup", "power saving",
            "coin cell", "energy harvest", "hibernate",
        ],
        "description": (
            "Put the ESP32 into deep sleep (as low as 10 µA) with configurable "
            "wake sources: timer, GPIO, touch pad, ULP co-processor, or ext1 pin."
        ),
        "use_cases": [
            "Battery-powered sensor that wakes every 60 s",
            "Door/window sensor waking on magnetic contact",
            "Solar-powered remote node",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_sleep.h", "esp32/deep_sleep"],
            "snippet": (
                "esp_sleep_enable_timer_wakeup(60 * 1000000ULL); // 60 s\n"
                "esp_deep_sleep_start();"
            ),
        },
        "tags": ["power", "sleep", "battery", "low-power"],
    },

    # ----------------------------------------------------------------- RTOS
    {
        "id": "freertos_tasks",
        "title": "FreeRTOS Multi-tasking",
        "keywords": [
            "freertos", "rtos", "task", "multitask", "thread", "queue",
            "semaphore", "mutex", "priority", "concurrent", "parallel",
            "non blocking", "task scheduler",
        ],
        "description": (
            "Create multiple FreeRTOS tasks pinned to specific cores to run "
            "WiFi, sensor reading, and display rendering concurrently."
        ),
        "use_cases": [
            "Sensor task on core 0, WiFi task on core 1",
            "Real-time motor control alongside data logging",
            "Responsive UI while doing heavy computation",
        ],
        "firmware": {
            "framework": "both",
            "components": ["freertos", "FreeRTOS.h"],
            "snippet": (
                "void sensorTask(void *param) {\n"
                "    while(1) { readSensor(); vTaskDelay(100/portTICK_PERIOD_MS); }\n"
                "}\n"
                "xTaskCreatePinnedToCore(sensorTask,\"Sensor\",4096,NULL,1,NULL,0);"
            ),
        },
        "tags": ["freertos", "rtos", "multitasking"],
    },

    # --------------------------------------------------------- Storage / NVS
    {
        "id": "nvs_storage",
        "title": "Non-Volatile Storage (NVS / Preferences)",
        "keywords": [
            "nvs", "preferences", "persistent", "save settings", "eeprom",
            "config store", "retain", "flash storage", "key value",
            "remember", "store value",
        ],
        "description": (
            "Persist configuration data, calibration values, or counters to "
            "flash across resets using the NVS (key-value) partition."
        ),
        "use_cases": [
            "Save WiFi credentials after provisioning",
            "Remember last device state on power-loss",
            "Firmware rollout counter",
        ],
        "firmware": {
            "framework": "both",
            "components": ["nvs_flash", "Preferences.h"],
            "snippet": (
                "#include <Preferences.h>\n"
                "Preferences prefs;\n"
                "prefs.begin(\"app\", false);\n"
                "prefs.putString(\"ssid\", \"MyNetwork\");\n"
                "String s = prefs.getString(\"ssid\", \"\");\n"
                "prefs.end();"
            ),
        },
        "tags": ["storage", "nvs", "flash", "persistence"],
    },

    {
        "id": "sd_card",
        "title": "SD Card Data Logging",
        "keywords": [
            "sd card", "sdcard", "file", "log", "csv", "data logger",
            "fat", "fat32", "spiffs", "littlefs", "file system",
            "store data", "record",
        ],
        "description": (
            "Mount an SD card over SPI and log structured data (CSV, JSON) "
            "to files using the Arduino SD library or ESP-IDF FAT VFS."
        ),
        "use_cases": [
            "Field data logger for environmental monitoring",
            "Flight recorder / black box",
            "Time-series data buffer before cloud upload",
        ],
        "firmware": {
            "framework": "both",
            "components": ["SD.h", "SD_MMC.h", "fatfs (IDF)"],
            "snippet": (
                "#include <SD.h>\n"
                "SD.begin(CS_PIN);\n"
                "File f = SD.open(\"/log.csv\", FILE_APPEND);\n"
                "f.printf(\"%lu,%.2f\\n\", millis(), temperature);\n"
                "f.close();"
            ),
        },
        "tags": ["storage", "sd", "logging", "filesystem"],
    },

    # --------------------------------------------------------------- Motors
    {
        "id": "dc_motor_pwm",
        "title": "DC Motor Control (PWM / L298N / DRV8833)",
        "keywords": [
            "dc motor", "motor", "pwm", "l298n", "l293d", "drv8833",
            "speed control", "direction", "robot", "drive", "wheels",
            "h-bridge", "motor driver",
        ],
        "description": (
            "Generate LEDC PWM signals to control DC motor speed and direction "
            "through common H-bridge driver ICs."
        ),
        "use_cases": [
            "Two-wheel differential robot",
            "Conveyor belt speed control",
            "Fan speed regulation",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_ledc.h", "ledcWrite (Arduino)"],
            "snippet": (
                "ledcSetup(0, 20000, 8);   // ch0, 20kHz, 8-bit\n"
                "ledcAttachPin(MOTOR_PIN, 0);\n"
                "ledcWrite(0, 128);        // 50% duty = half speed"
            ),
        },
        "tags": ["motor", "pwm", "actuator", "robot"],
    },

    {
        "id": "servo_motor",
        "title": "Servo Motor Control",
        "keywords": [
            "servo", "servo motor", "angle", "position", "pan tilt", "robotic arm",
            "sg90", "mg996", "esp32servo", "pwm servo",
        ],
        "description": (
            "Generate 50 Hz PWM servo signals using the LEDC peripheral to "
            "position standard or continuous-rotation servos."
        ),
        "use_cases": [
            "Pan-tilt camera gimbal",
            "Robotic arm joint",
            "Door lock actuator",
        ],
        "firmware": {
            "framework": "both",
            "components": ["ESP32Servo library", "ledc_set_duty"],
            "snippet": (
                "#include <ESP32Servo.h>\n"
                "Servo myServo;\n"
                "myServo.attach(SERVO_PIN);\n"
                "myServo.write(90); // move to 90 degrees"
            ),
        },
        "tags": ["servo", "motor", "actuator", "pwm"],
    },

    {
        "id": "stepper_motor",
        "title": "Stepper Motor Control (A4988 / TMC2209)",
        "keywords": [
            "stepper", "stepper motor", "cnc", "3d printer", "a4988",
            "drv8825", "tmc2209", "steps", "microstep", "precise movement",
            "linear actuator",
        ],
        "description": (
            "Drive stepper motors for precise positioning in CNC machines, "
            "3D printers, or robotic axes using step/dir interfaces."
        ),
        "use_cases": [
            "CNC router axis controller",
            "Camera slider / dolly",
            "Automated valve or valve actuator",
        ],
        "firmware": {
            "framework": "both",
            "components": ["FastAccelStepper", "AccelStepper"],
            "snippet": (
                "#include <FastAccelStepper.h>\n"
                "FastAccelStepperEngine engine;\n"
                "engine.init();\n"
                "FastAccelStepper *stepper = engine.stepperConnectToPin(STEP_PIN);\n"
                "stepper->setDirectionPin(DIR_PIN);\n"
                "stepper->setSpeedInHz(1000);\n"
                "stepper->setAcceleration(500);\n"
                "stepper->move(3200);"
            ),
        },
        "tags": ["stepper", "motor", "cnc", "actuator"],
    },

    # ------------------------------------------------------- Home Automation
    {
        "id": "home_assistant_esphome",
        "title": "Home Assistant Integration (ESPHome / MQTT Discovery)",
        "keywords": [
            "home assistant", "hass", "ha", "esphome", "smart home",
            "automation", "mqtt discovery", "entity", "switch", "sensor entity",
            "lovelace", "dashboard",
        ],
        "description": (
            "Integrate the ESP32 with Home Assistant via ESPHome YAML firmware "
            "or native MQTT discovery, exposing sensors and controls as HA entities."
        ),
        "use_cases": [
            "Smart plug with energy monitoring",
            "DIY multi-sensor (temp/hum/motion) node",
            "Custom light controller",
        ],
        "firmware": {
            "framework": "both",
            "components": ["ESPHome", "PubSubClient (MQTT discovery)"],
            "snippet": (
                "# ESPHome YAML snippet\n"
                "sensor:\n"
                "  - platform: dht\n"
                "    pin: GPIO4\n"
                "    model: DHT22\n"
                "    temperature:\n"
                "      name: \"Room Temperature\"\n"
                "    humidity:\n"
                "      name: \"Room Humidity\""
            ),
        },
        "tags": ["home-automation", "esphome", "mqtt", "ha"],
    },

    # -------------------------------------------------------------- Security
    {
        "id": "secure_boot_flash_encrypt",
        "title": "Secure Boot & Flash Encryption",
        "keywords": [
            "secure boot", "flash encryption", "security", "trusted", "tamper",
            "production firmware", "signing", "key", "efuse", "sbv2",
        ],
        "description": (
            "Enable Secure Boot V2 and flash encryption to prevent unauthorised "
            "firmware execution and protect intellectual property."
        ),
        "use_cases": [
            "Commercial product IP protection",
            "Prevent firmware extraction from devices in the field",
            "Compliance with security certification requirements",
        ],
        "firmware": {
            "framework": "esp-idf",
            "components": ["esp_secure_boot", "nvs_encryption", "eFuse"],
            "snippet": (
                "# Enable in sdkconfig:\n"
                "CONFIG_SECURE_BOOT=y\n"
                "CONFIG_SECURE_BOOT_SIGNING_KEY=\"secure_boot_signing_key.pem\"\n"
                "CONFIG_FLASH_ENCRYPTION_ENABLED=y"
            ),
        },
        "tags": ["security", "production", "encryption"],
    },

    # ----------------------------------------------------------- Audio/Media
    {
        "id": "audio_i2s",
        "title": "Audio Playback & Recording (I²S / DAC)",
        "keywords": [
            "audio", "sound", "speaker", "microphone", "i2s", "dac", "adc audio",
            "mp3", "wav", "beep", "tone", "voice", "tts", "record",
            "inmp441", "max98357", "pcm5102",
        ],
        "description": (
            "Stream digital audio over I²S to an amplifier + speaker, or capture "
            "audio from a MEMS microphone for voice recognition or recording."
        ),
        "use_cases": [
            "Voice assistant / wake-word detection",
            "Audio alert / alarm system",
            "Bluetooth speaker (A2DP sink)",
        ],
        "firmware": {
            "framework": "both",
            "components": ["ESP8266Audio / ESP32-audioI2S", "driver/i2s.h"],
            "snippet": (
                "#include <Audio.h>\n"
                "Audio audio;\n"
                "audio.setPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);\n"
                "audio.setVolume(15);\n"
                "audio.connecttoFS(SD, \"/music.mp3\");\n"
                "// In loop(): audio.loop();"
            ),
        },
        "tags": ["audio", "i2s", "media", "voice"],
    },

    # ---------------------------------------------------------- Mesh Network
    {
        "id": "wifi_mesh",
        "title": "WiFi Mesh Network (painlessMesh / ESP-MESH)",
        "keywords": [
            "mesh", "wifi mesh", "esp-mesh", "painlessmesh", "self healing",
            "multi hop", "node", "decentralised", "scalable network",
            "building automation", "large area",
        ],
        "description": (
            "Create a self-healing, multi-hop mesh network of ESP32 nodes using "
            "ESP-MESH or the painlessMesh library for large-scale deployments."
        ),
        "use_cases": [
            "Building-wide sensor network",
            "Smart street lighting mesh",
            "Disaster-resilient communication grid",
        ],
        "firmware": {
            "framework": "both",
            "components": ["painlessMesh", "esp_mesh.h (IDF)"],
            "snippet": (
                "#include <painlessMesh.h>\n"
                "painlessMesh mesh;\n"
                "mesh.init(MESH_PREFIX, MESH_PASSWORD, MESH_PORT);\n"
                "mesh.onReceive([](uint32_t from, String &msg){\n"
                "    Serial.printf(\"From %u: %s\\n\", from, msg.c_str());\n"
                "});\n"
                "// In loop(): mesh.update();"
            ),
        },
        "tags": ["mesh", "wifi", "networking", "iot"],
    },

    # ------------------------------------------------------- Machine Learning
    {
        "id": "edge_ml",
        "title": "Edge Machine Learning (TensorFlow Lite / Edge Impulse)",
        "keywords": [
            "machine learning", "ml", "ai", "tensorflow", "tflite",
            "edge impulse", "neural network", "inference", "classification",
            "anomaly detection", "keyword spotting", "tinyml", "model",
        ],
        "description": (
            "Run TensorFlow Lite Micro or Edge Impulse models on-device for "
            "keyword spotting, gesture recognition, or anomaly detection."
        ),
        "use_cases": [
            "Wake-word detection ('Hey ESPx')",
            "Vibration anomaly detection for predictive maintenance",
            "Image classification with ESP32-S3 PSRAM",
        ],
        "firmware": {
            "framework": "both",
            "components": ["tensorflow/lite/micro", "Edge Impulse SDK"],
            "snippet": (
                "#include <EloquentTinyML.h>\n"
                "Eloquent::TinyML::TfLite<NUM_IN, NUM_OUT, TENSOR_ARENA_SZ> ml;\n"
                "ml.begin(model_data);\n"
                "float input[] = {0.5f, 1.2f};\n"
                "float result = ml.predict(input);"
            ),
        },
        "tags": ["ml", "ai", "tinyml", "inference"],
    },

    # ---------------------------------------------------------- Time / Clock
    {
        "id": "ntp_rtc",
        "title": "Real-Time Clock (NTP Sync / DS3231)",
        "keywords": [
            "time", "clock", "rtc", "ntp", "timestamp", "date", "schedule",
            "cron", "ds3231", "ds1307", "timezone", "drift", "epoch",
        ],
        "description": (
            "Synchronise device time via NTP over WiFi, or use a hardware RTC "
            "module (DS3231) for accurate timekeeping without internet access."
        ),
        "use_cases": [
            "Timestamped sensor logs",
            "Scheduled relay (alarm clock style)",
            "Off-grid time-keeping with backup battery RTC",
        ],
        "firmware": {
            "framework": "both",
            "components": ["esp_sntp.h", "RTClib", "time.h"],
            "snippet": (
                "configTime(0, 0, \"pool.ntp.org\");\n"
                "struct tm ti;\n"
                "getLocalTime(&ti);\n"
                "Serial.printf(\"%04d-%02d-%02d %02d:%02d:%02d\\n\",\n"
                "    ti.tm_year+1900, ti.tm_mon+1, ti.tm_mday,\n"
                "    ti.tm_hour, ti.tm_min, ti.tm_sec);"
            ),
        },
        "tags": ["time", "rtc", "ntp", "scheduling"],
    },

    # ------------------------------------------------------ Touch / Input
    {
        "id": "capacitive_touch",
        "title": "Capacitive Touch Sensing",
        "keywords": [
            "touch", "capacitive", "touchpad", "button", "no button",
            "fingertip", "touch sensor", "wake touch", "touch key",
        ],
        "description": (
            "Use the ESP32's built-in capacitive touch peripherals (T0–T9 pins) "
            "to create touch buttons or wake the device from deep sleep."
        ),
        "use_cases": [
            "Touch-sensitive lamp switch",
            "Keypad without physical buttons",
            "Sleep-wake trigger from touch",
        ],
        "firmware": {
            "framework": "both",
            "components": ["touch_pad (IDF)", "touchRead() (Arduino)"],
            "snippet": (
                "int val = touchRead(T0); // GPIO4\n"
                "if (val < 30) Serial.println(\"Touched!\");\n\n"
                "// Deep-sleep wake on touch:\n"
                "esp_sleep_enable_touchpad_wakeup();\n"
                "esp_deep_sleep_start();"
            ),
        },
        "tags": ["touch", "input", "gpio", "sleep"],
    },

    # ------------------------------------------------------ Firmware Mapping
    {
        "id": "firmware_partitions",
        "title": "Custom Partition Table & Firmware Mapping",
        "keywords": [
            "partition", "partition table", "firmware map", "ota partition",
            "nvs partition", "spiffs", "littlefs", "custom layout",
            "flash layout", "app partition",
        ],
        "description": (
            "Define a custom partition table CSV to allocate flash regions for "
            "dual OTA app slots, NVS, SPIFFS/LittleFS, and custom data partitions."
        ),
        "use_cases": [
            "Dual-OTA with safe rollback",
            "Large filesystem for web assets",
            "Separate encrypted data partition",
        ],
        "firmware": {
            "framework": "esp-idf",
            "components": ["partition_table", "esptool.py"],
            "snippet": (
                "# partitions.csv\n"
                "# Name,   Type, SubType,  Offset,  Size\n"
                "nvs,      data, nvs,      0x9000,  0x5000\n"
                "otadata,  data, ota,      0xe000,  0x2000\n"
                "app0,     app,  ota_0,    0x10000, 0x1E0000\n"
                "app1,     app,  ota_1,    0x1F0000,0x1E0000\n"
                "spiffs,   data, spiffs,   0x3D0000,0x30000"
            ),
        },
        "tags": ["partition", "firmware", "flash", "ota"],
    },
]
