// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include <iostream>
#include <string>

#include "espx/core/logger.hpp"
#include "espx/network/http_client.hpp"
#include "espx/network/http_server.hpp"

static const char* TAG = "HttpServer";

using espx::core::LogLevel;

static void log_info(const std::string& msg) {
    espx::core::Logger::instance().log(LogLevel::Info, TAG, __FILE__, __LINE__, msg);
}

int main() {
    auto& logger = espx::core::Logger::instance();
    logger.set_level(LogLevel::Info);

    log_info("=== ESPx HTTP Server Example ===");

    // Create and configure the HTTP server
    espx::network::HttpServer server;

    // GET /api/status — returns system status
    server.get("/api/status",
        [](const espx::network::HttpRequest& /*req*/,
           espx::network::HttpServerResponse& res) {
            res.json(R"({"status":"ok","uptime":12345,"version":"1.0.0"})");
            espx::core::Logger::instance().log(
                LogLevel::Info, "HttpServer", __FILE__, __LINE__, "Handled GET /api/status");
        });

    // GET /api/config — returns current configuration
    server.get("/api/config",
        [](const espx::network::HttpRequest& /*req*/,
           espx::network::HttpServerResponse& res) {
            res.json(R"({"wifi_ssid":"MyNetwork","ble_name":"ESPx-Demo","log_level":"info"})");
            espx::core::Logger::instance().log(
                LogLevel::Info, "HttpServer", __FILE__, __LINE__, "Handled GET /api/config");
        });

    // POST /api/config — update configuration
    server.post("/api/config",
        [](const espx::network::HttpRequest& req,
           espx::network::HttpServerResponse& res) {
            espx::core::Logger::instance().log(
                LogLevel::Info, "HttpServer", __FILE__, __LINE__,
                "Handled POST /api/config, body: " + req.body);
            res.json(R"({"result":"saved"})");
        });

    // Start server on port 8080
    espx::network::HttpServerConfig srv_cfg;
    srv_cfg.port = 8080;
    srv_cfg.enable_cors = true;

    log_info("Starting HTTP server on port " + std::to_string(srv_cfg.port) + "...");
    if (!server.start(srv_cfg)) {
        logger.log(LogLevel::Warn, TAG, __FILE__, __LINE__,
                   "Server start returned false (expected in host mode)");
    }
    log_info("Server running: " + std::string(server.is_running() ? "yes" : "no"));

    // Demonstrate HttpClient making simulated requests
    log_info("--- HttpClient demo ---");

    espx::network::HttpClient client;

    auto get_resp = client.get("http://localhost:8080/api/status");
    log_info("GET /api/status -> " + std::to_string(get_resp.status_code));
    if (!get_resp.body.empty()) {
        std::cout << "  Response: " << get_resp.body << "\n";
    }

    auto post_resp = client.post(
        "http://localhost:8080/api/config",
        R"({"wifi_ssid":"NewNetwork"})",
        {{"Content-Type", "application/json"}});
    log_info("POST /api/config -> " + std::to_string(post_resp.status_code));
    if (!post_resp.body.empty()) {
        std::cout << "  Response: " << post_resp.body << "\n";
    }

    log_info("Total requests served: " + std::to_string(server.total_requests()));

    // Cleanup
    server.stop();
    log_info("HTTP server example complete.");

    return 0;
}
