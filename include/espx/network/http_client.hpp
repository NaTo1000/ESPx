// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace network {

/**
 * @enum HttpMethod
 * @brief HTTP request methods.
 */
enum class HttpMethod {
    GET,
    POST,
    PUT,
    PATCH,
    DELETE_,
    HEAD,
    OPTIONS
};

/**
 * @brief Convert HTTP method to string.
 */
[[nodiscard]] const char* http_method_to_string(HttpMethod method);

/**
 * @struct HttpResponse
 * @brief Represents an HTTP response.
 */
struct HttpResponse {
    int status_code = 0;                          ///< HTTP status code
    std::string status_text;                      ///< HTTP status text
    std::map<std::string, std::string> headers;   ///< Response headers
    std::string body;                             ///< Response body
    std::vector<uint8_t> body_bytes;              ///< Binary response body
    uint64_t content_length = 0;                  ///< Content-Length
    double elapsed_ms = 0.0;                      ///< Request duration in ms

    /// Check if the request was successful (2xx status)
    [[nodiscard]] bool ok() const {
        return status_code >= 200 && status_code < 300;
    }
};

/**
 * @struct HttpClientConfig
 * @brief Configuration for the HTTP client.
 */
struct HttpClientConfig {
    uint32_t timeout_ms = 10000;          ///< Request timeout
    uint32_t connect_timeout_ms = 5000;   ///< Connection timeout
    bool follow_redirects = true;         ///< Follow HTTP redirects
    uint8_t max_redirects = 5;            ///< Maximum redirect hops
    bool verify_ssl = true;               ///< Verify SSL certificates
    std::string user_agent = "ESPx/1.0";  ///< User-Agent header
    std::string ca_cert;                  ///< Custom CA certificate (PEM)
    std::string client_cert;              ///< Client certificate (PEM)
    std::string client_key;               ///< Client private key (PEM)
};

/**
 * @class HttpClient
 * @brief HTTP/HTTPS client for making web requests.
 *
 * Supports GET, POST, PUT, DELETE, and other HTTP methods
 * with SSL/TLS support, custom headers, and streaming.
 *
 * Example:
 * @code
 *   espx::network::HttpClient client;
 *
 *   auto resp = client.get("https://api.example.com/data");
 *   if (resp.ok()) {
 *       std::cout << "Response: " << resp.body << std::endl;
 *   }
 *
 *   // POST with JSON body
 *   std::map<std::string, std::string> headers = {
 *       {"Content-Type", "application/json"}
 *   };
 *   auto post_resp = client.post("https://api.example.com/data",
 *                                R"({"key": "value"})", headers);
 * @endcode
 */
class HttpClient {
public:
    explicit HttpClient(const HttpClientConfig& config = {});
    ~HttpClient();

    HttpClient(const HttpClient&) = delete;
    HttpClient& operator=(const HttpClient&) = delete;

    /**
     * @brief Perform a GET request.
     * @param url Target URL
     * @param headers Additional headers
     * @return HTTP response
     */
    [[nodiscard]] HttpResponse get(
        const std::string& url,
        const std::map<std::string, std::string>& headers = {});

    /**
     * @brief Perform a POST request.
     * @param url Target URL
     * @param body Request body
     * @param headers Additional headers
     * @return HTTP response
     */
    [[nodiscard]] HttpResponse post(
        const std::string& url,
        const std::string& body = "",
        const std::map<std::string, std::string>& headers = {});

    /**
     * @brief Perform a PUT request.
     * @param url Target URL
     * @param body Request body
     * @param headers Additional headers
     * @return HTTP response
     */
    [[nodiscard]] HttpResponse put(
        const std::string& url,
        const std::string& body = "",
        const std::map<std::string, std::string>& headers = {});

    /**
     * @brief Perform a DELETE request.
     * @param url Target URL
     * @param headers Additional headers
     * @return HTTP response
     */
    [[nodiscard]] HttpResponse del(
        const std::string& url,
        const std::map<std::string, std::string>& headers = {});

    /**
     * @brief Perform a generic HTTP request.
     * @param method HTTP method
     * @param url Target URL
     * @param body Request body (empty for GET/DELETE)
     * @param headers Additional headers
     * @return HTTP response
     */
    [[nodiscard]] HttpResponse request(
        HttpMethod method,
        const std::string& url,
        const std::string& body = "",
        const std::map<std::string, std::string>& headers = {});

    /**
     * @brief Set a default header sent with every request.
     * @param key Header name
     * @param value Header value
     */
    void set_default_header(const std::string& key, const std::string& value);

    /**
     * @brief Set HTTP Basic Auth credentials.
     * @param username Username
     * @param password Password
     */
    void set_basic_auth(const std::string& username, const std::string& password);

    /**
     * @brief Set a Bearer token for Authorization.
     * @param token Bearer token
     */
    void set_bearer_token(const std::string& token);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace network
}  // namespace espx
