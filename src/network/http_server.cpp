// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/network/http_server.hpp"

#include <map>
#include <string>
#include <vector>

namespace espx {
namespace network {

struct HttpServer::Impl {
    HttpServerConfig config;
    bool running{false};
    std::map<std::string, RequestHandler> routes;
    std::vector<Middleware> middlewares;
    std::map<std::string, std::string> static_mappings;
    size_t active_conns{0};
    uint64_t total_reqs{0};
};

HttpServer::HttpServer() : impl_(std::make_unique<Impl>()) {}
HttpServer::~HttpServer() = default;

bool HttpServer::start(const HttpServerConfig& config) {
    if (impl_->running) {
        return false;
    }
    impl_->config = config;
    impl_->running = true;
    return true;
}

void HttpServer::stop() {
    impl_->running = false;
    impl_->active_conns = 0;
}

bool HttpServer::is_running() const {
    return impl_->running;
}

void HttpServer::get(const std::string& path, RequestHandler handler) {
    route("GET", path, std::move(handler));
}

void HttpServer::post(const std::string& path, RequestHandler handler) {
    route("POST", path, std::move(handler));
}

void HttpServer::put(const std::string& path, RequestHandler handler) {
    route("PUT", path, std::move(handler));
}

void HttpServer::del(const std::string& path, RequestHandler handler) {
    route("DELETE", path, std::move(handler));
}

void HttpServer::route(const std::string& method, const std::string& path,
                       RequestHandler handler) {
    std::string key = method + ":" + path;
    impl_->routes[key] = std::move(handler);
}

void HttpServer::use(Middleware middleware) {
    impl_->middlewares.push_back(std::move(middleware));
}

void HttpServer::serve_static(const std::string& url_prefix,
                              const std::string& directory) {
    impl_->static_mappings[url_prefix] = directory;
}

size_t HttpServer::active_connections() const {
    return impl_->active_conns;
}

uint64_t HttpServer::total_requests() const {
    return impl_->total_reqs;
}

}  // namespace network
}  // namespace espx
