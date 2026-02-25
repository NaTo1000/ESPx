// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/network/http_client.hpp"

#include <chrono>
#include <map>
#include <string>

namespace espx {
namespace network {

const char* http_method_to_string(HttpMethod method) {
    switch (method) {
        case HttpMethod::GET:     return "GET";
        case HttpMethod::POST:    return "POST";
        case HttpMethod::PUT:     return "PUT";
        case HttpMethod::PATCH:   return "PATCH";
        case HttpMethod::DELETE_: return "DELETE";
        case HttpMethod::HEAD:    return "HEAD";
        case HttpMethod::OPTIONS: return "OPTIONS";
    }
    return "UNKNOWN";
}

struct HttpClient::Impl {
    HttpClientConfig config;
    std::map<std::string, std::string> default_headers;
    std::string basic_auth;
    std::string bearer_token;
};

HttpClient::HttpClient(const HttpClientConfig& config)
    : impl_(std::make_unique<Impl>()) {
    impl_->config = config;
}

HttpClient::~HttpClient() = default;

HttpResponse HttpClient::request(
    HttpMethod method,
    const std::string& url,
    const std::string& body,
    const std::map<std::string, std::string>& headers) {

    auto start = std::chrono::steady_clock::now();

    HttpResponse resp;
    resp.status_code = 200;
    resp.status_text = "OK";

    // Apply default headers
    resp.headers = impl_->default_headers;
    for (const auto& h : headers) {
        resp.headers[h.first] = h.second;
    }

    resp.headers["X-Method"] = http_method_to_string(method);
    if (!impl_->basic_auth.empty()) {
        resp.headers["Authorization"] = "Basic " + impl_->basic_auth;
    } else if (!impl_->bearer_token.empty()) {
        resp.headers["Authorization"] = "Bearer " + impl_->bearer_token;
    }

    // Echo the URL in the body (simulated)
    resp.body = url;
    if (!body.empty()) {
        resp.body += "\n" + body;
    }
    resp.content_length = static_cast<uint64_t>(resp.body.size());
    resp.body_bytes.assign(resp.body.begin(), resp.body.end());

    auto end = std::chrono::steady_clock::now();
    resp.elapsed_ms = std::chrono::duration<double, std::milli>(end - start).count();

    return resp;
}

HttpResponse HttpClient::get(
    const std::string& url,
    const std::map<std::string, std::string>& headers) {
    return request(HttpMethod::GET, url, "", headers);
}

HttpResponse HttpClient::post(
    const std::string& url,
    const std::string& body,
    const std::map<std::string, std::string>& headers) {
    return request(HttpMethod::POST, url, body, headers);
}

HttpResponse HttpClient::put(
    const std::string& url,
    const std::string& body,
    const std::map<std::string, std::string>& headers) {
    return request(HttpMethod::PUT, url, body, headers);
}

HttpResponse HttpClient::del(
    const std::string& url,
    const std::map<std::string, std::string>& headers) {
    return request(HttpMethod::DELETE_, url, "", headers);
}

void HttpClient::set_default_header(const std::string& key,
                                    const std::string& value) {
    impl_->default_headers[key] = value;
}

void HttpClient::set_basic_auth(const std::string& username,
                                const std::string& password) {
    impl_->basic_auth = username + ":" + password;
    impl_->bearer_token.clear();
}

void HttpClient::set_bearer_token(const std::string& token) {
    impl_->bearer_token = token;
    impl_->basic_auth.clear();
}

}  // namespace network
}  // namespace espx
