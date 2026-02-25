// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

/**
 * @file espx.hpp
 * @brief Main include header for the ESPx framework.
 *
 * Include this single header to access all ESPx modules.
 */

#include "espx/core/app.hpp"
#include "espx/core/config.hpp"
#include "espx/core/event_loop.hpp"
#include "espx/core/logger.hpp"
#include "espx/wifi/wifi_manager.hpp"
#include "espx/wifi/scanner.hpp"
#include "espx/wifi/ap_mode.hpp"
#include "espx/bluetooth/ble_manager.hpp"
#include "espx/bluetooth/ble_scanner.hpp"
#include "espx/bluetooth/ble_advertiser.hpp"
#include "espx/bluetooth/gatt_server.hpp"
#include "espx/network/http_client.hpp"
#include "espx/network/http_server.hpp"
#include "espx/network/tcp_socket.hpp"
#include "espx/network/udp_socket.hpp"
#include "espx/network/dns_resolver.hpp"
#include "espx/security/vault.hpp"
#include "espx/security/crypto.hpp"
#include "espx/security/key_store.hpp"
#include "espx/ota/ota_updater.hpp"
#include "espx/gpio/pin.hpp"
#include "espx/gpio/adc.hpp"
#include "espx/gpio/sensor.hpp"
#include "espx/utils/ring_buffer.hpp"
#include "espx/utils/timer.hpp"
#include "espx/utils/uuid.hpp"
#include "espx/utils/base64.hpp"

namespace espx {

/// Library version string
constexpr const char* VERSION = "1.0.0";

/// Major version number
constexpr int VERSION_MAJOR = 1;

/// Minor version number
constexpr int VERSION_MINOR = 0;

/// Patch version number
constexpr int VERSION_PATCH = 0;

}  // namespace espx
