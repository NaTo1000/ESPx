// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>

namespace espx {
namespace network {

/**
 * @struct HttpRequest
 * @brief Represents an incoming HTTP request.
 */
struct HttpRequest {
    std::string method;                           ///< HTTP method (GET, POST, etc.)
    std::string path;                             ///< Request path
    std::string query_string;                     ///< Query string
    std::map<std::string, std::string> headers;   ///< Request headers
    std::map<std::string, std::string> params;    ///< URL parameters
    std::string body;                             ///< Request body
    std::string client_ip;                        ///< Client IP address
    uint16_t client_port = 0;                     ///< Client port
};

/**
 * @struct HttpServerResponse
 * @brief Response to send back to the client.
 */
struct HttpServerResponse {
    int status_code = 200;
    std::string status_text = "OK";
    std::map<std::string, std::string> headers;
    std::string body;

    /// Set the Content-Type header
    void set_content_type(const std::string& type) {
        headers["Content-Type"] = type;
    }

    /// Set a JSON response
    void json(const std::string& json_body) {
        headers["Content-Type"] = "application/json";
        body = json_body;
    }

    /// Set an HTML response
    void html(const std::string& html_body) {
        headers["Content-Type"] = "text/html; charset=utf-8";
        body = html_body;
    }

    /// Set a plain text response
    void text(const std::string& text_body) {
        headers["Content-Type"] = "text/plain; charset=utf-8";
        body = text_body;
    }

    /// Send a redirect
    void redirect(const std::string& url, int code = 302) {
        status_code = code;
        headers["Location"] = url;
    }
};

/**
 * @brief Request handler function type.
 */
using RequestHandler = std::function<void(const HttpRequest&, HttpServerResponse&)>;

/**
 * @brief Middleware function type.
 */
using Middleware = std::function<bool(const HttpRequest&, HttpServerResponse&)>;

/**
 * @struct HttpServerConfig
 * @brief Configuration for the HTTP server.
 */
struct HttpServerConfig {
    uint16_t port = 80;                ///< Listen port
    uint16_t max_connections = 8;      ///< Maximum concurrent connections
    uint32_t read_timeout_ms = 5000;   ///< Read timeout
    bool enable_cors = false;          ///< Enable CORS headers
    std::string cors_origin = "*";     ///< CORS allowed origin
    bool enable_ssl = false;           ///< Enable HTTPS
    std::string ssl_cert;              ///< SSL certificate (PEM)
    std::string ssl_key;               ///< SSL private key (PEM)
};

/**
 * @class HttpServer
 * @brief Embedded HTTP/HTTPS server.
 *
 * Lightweight HTTP server with routing, middleware support,
 * static file serving, and WebSocket upgrade capability.
 *
 * Example:
 * @code
 *   espx::network::HttpServer server;
 *
 *   server.get("/api/status", [](const HttpRequest& req, HttpServerResponse& res) {
 *       res.json(R"({"status": "ok", "uptime": 12345})");
 *   });
 *
 *   server.post("/api/config", [](const HttpRequest& req, HttpServerResponse& res) {
 *       // Process config update
 *       res.json(R"({"result": "saved"})");
 *   });
 *
 *   server.start({.port = 8080});
 * @endcode
 */
class HttpServer {
public:
    HttpServer();
    ~HttpServer();

    HttpServer(const HttpServer&) = delete;
    HttpServer& operator=(const HttpServer&) = delete;

    /**
     * @brief Start the HTTP server.
     * @param config Server configuration
     * @return true if the server started successfully
     */
    bool start(const HttpServerConfig& config = {});

    /**
     * @brief Stop the HTTP server.
     */
    void stop();

    /**
     * @brief Check if the server is running.
     * @return true if running
     */
    [[nodiscard]] bool is_running() const;

    /**
     * @brief Register a GET route handler.
     * @param path URL path pattern
     * @param handler Request handler
     */
    void get(const std::string& path, RequestHandler handler);

    /**
     * @brief Register a POST route handler.
     * @param path URL path pattern
     * @param handler Request handler
     */
    void post(const std::string& path, RequestHandler handler);

    /**
     * @brief Register a PUT route handler.
     * @param path URL path pattern
     * @param handler Request handler
     */
    void put(const std::string& path, RequestHandler handler);

    /**
     * @brief Register a DELETE route handler.
     * @param path URL path pattern
     * @param handler Request handler
     */
    void del(const std::string& path, RequestHandler handler);

    /**
     * @brief Register a route handler for any HTTP method.
     * @param method HTTP method string
     * @param path URL path pattern
     * @param handler Request handler
     */
    void route(const std::string& method, const std::string& path,
               RequestHandler handler);

    /**
     * @brief Add a middleware function.
     *
     * Middleware runs before route handlers. Return false to
     * stop processing (e.g., for authentication).
     *
     * @param middleware Middleware function
     */
    void use(Middleware middleware);

    /**
     * @brief Serve static files from a directory.
     * @param url_prefix URL prefix (e.g., "/static")
     * @param directory Filesystem directory path
     */
    void serve_static(const std::string& url_prefix,
                      const std::string& directory);

    /**
     * @brief Get the number of active connections.
     * @return Connection count
     */
    [[nodiscard]] size_t active_connections() const;

    /**
     * @brief Get total requests served.
     * @return Request count
     */
    [[nodiscard]] uint64_t total_requests() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace network
}  // namespace espx
