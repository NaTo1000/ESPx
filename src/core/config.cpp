// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/core/config.hpp"

#include <algorithm>
#include <fstream>
#include <mutex>
#include <sstream>

namespace espx {
namespace core {

struct Config::Impl {
    struct ChangeCallback {
        std::string key;
        std::function<void(const std::string&, const Value&)> callback;
    };

    std::map<std::string, Value> store;
    std::vector<ChangeCallback> callbacks;
    mutable std::mutex mutex;

    void notify(const std::string& key, const Value& value) {
        for (auto& cb : callbacks) {
            if (cb.key.empty() || cb.key == key) {
                cb.callback(key, value);
            }
        }
    }

    static std::string escape_json_string(const std::string& s) {
        std::string out;
        out.reserve(s.size() + 2);
        out += '"';
        for (char c : s) {
            switch (c) {
                case '"':  out += "\\\""; break;
                case '\\': out += "\\\\"; break;
                case '\b': out += "\\b";  break;
                case '\f': out += "\\f";  break;
                case '\n': out += "\\n";  break;
                case '\r': out += "\\r";  break;
                case '\t': out += "\\t";  break;
                default:   out += c;      break;
            }
        }
        out += '"';
        return out;
    }

    static std::string value_to_json(const Value& v) {
        return std::visit([](auto&& arg) -> std::string {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::string>) {
                return escape_json_string(arg);
            } else if constexpr (std::is_same_v<T, int64_t>) {
                return std::to_string(arg);
            } else if constexpr (std::is_same_v<T, double>) {
                std::ostringstream oss;
                oss << arg;
                std::string s = oss.str();
                if (s.find('.') == std::string::npos &&
                    s.find('e') == std::string::npos &&
                    s.find('E') == std::string::npos) {
                    s += ".0";
                }
                return s;
            } else if constexpr (std::is_same_v<T, bool>) {
                return arg ? "true" : "false";
            }
        }, v);
    }

    static std::string skip_ws(const std::string& s, size_t pos) {
        // returns substring starting after whitespace
        (void)s; (void)pos;
        return {};
    }

    static size_t skip_whitespace(const std::string& s, size_t pos) {
        while (pos < s.size() &&
               (s[pos] == ' ' || s[pos] == '\t' ||
                s[pos] == '\n' || s[pos] == '\r')) {
            ++pos;
        }
        return pos;
    }

    static bool parse_string(const std::string& s, size_t& pos,
                             std::string& out) {
        if (pos >= s.size() || s[pos] != '"') return false;
        ++pos;
        out.clear();
        while (pos < s.size() && s[pos] != '"') {
            if (s[pos] == '\\' && pos + 1 < s.size()) {
                ++pos;
                switch (s[pos]) {
                    case '"':  out += '"';  break;
                    case '\\': out += '\\'; break;
                    case 'b':  out += '\b'; break;
                    case 'f':  out += '\f'; break;
                    case 'n':  out += '\n'; break;
                    case 'r':  out += '\r'; break;
                    case 't':  out += '\t'; break;
                    default:   out += s[pos]; break;
                }
            } else {
                out += s[pos];
            }
            ++pos;
        }
        if (pos >= s.size()) return false;
        ++pos;  // skip closing quote
        return true;
    }

    static bool parse_value(const std::string& s, size_t& pos, Value& out) {
        pos = skip_whitespace(s, pos);
        if (pos >= s.size()) return false;

        if (s[pos] == '"') {
            std::string str;
            if (!parse_string(s, pos, str)) return false;
            out = str;
            return true;
        }
        if (s.compare(pos, 4, "true") == 0) {
            out = true;
            pos += 4;
            return true;
        }
        if (s.compare(pos, 5, "false") == 0) {
            out = false;
            pos += 5;
            return true;
        }

        // Number
        size_t start = pos;
        bool is_float = false;
        if (pos < s.size() && s[pos] == '-') ++pos;
        while (pos < s.size() && s[pos] >= '0' && s[pos] <= '9') ++pos;
        if (pos < s.size() && s[pos] == '.') {
            is_float = true;
            ++pos;
            while (pos < s.size() && s[pos] >= '0' && s[pos] <= '9') ++pos;
        }
        if (pos < s.size() && (s[pos] == 'e' || s[pos] == 'E')) {
            is_float = true;
            ++pos;
            if (pos < s.size() && (s[pos] == '+' || s[pos] == '-')) ++pos;
            while (pos < s.size() && s[pos] >= '0' && s[pos] <= '9') ++pos;
        }
        if (pos == start) return false;
        std::string num_str = s.substr(start, pos - start);
        if (is_float) {
            out = std::stod(num_str);
        } else {
            out = static_cast<int64_t>(std::stoll(num_str));
        }
        return true;
    }
};

Config::Config() : impl_(std::make_unique<Impl>()) {}
Config::~Config() = default;

Config::Config(const Config& other) : impl_(std::make_unique<Impl>()) {
    std::lock_guard<std::mutex> lock(other.impl_->mutex);
    impl_->store = other.impl_->store;
    impl_->callbacks = other.impl_->callbacks;
}

Config& Config::operator=(const Config& other) {
    if (this != &other) {
        std::lock_guard<std::mutex> lock1(impl_->mutex);
        std::lock_guard<std::mutex> lock2(other.impl_->mutex);
        impl_->store = other.impl_->store;
        impl_->callbacks = other.impl_->callbacks;
    }
    return *this;
}

Config::Config(Config&&) noexcept = default;
Config& Config::operator=(Config&&) noexcept = default;

void Config::set(const std::string& key, const Value& value) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->store[key] = value;
    impl_->notify(key, value);
}

std::string Config::get_string(const std::string& key,
                               const std::string& default_val) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->store.find(key);
    if (it == impl_->store.end()) return default_val;
    if (auto* s = std::get_if<std::string>(&it->second)) return *s;
    return default_val;
}

int64_t Config::get_int(const std::string& key, int64_t default_val) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->store.find(key);
    if (it == impl_->store.end()) return default_val;
    if (auto* v = std::get_if<int64_t>(&it->second)) return *v;
    return default_val;
}

double Config::get_double(const std::string& key, double default_val) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->store.find(key);
    if (it == impl_->store.end()) return default_val;
    if (auto* v = std::get_if<double>(&it->second)) return *v;
    return default_val;
}

bool Config::get_bool(const std::string& key, bool default_val) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->store.find(key);
    if (it == impl_->store.end()) return default_val;
    if (auto* v = std::get_if<bool>(&it->second)) return *v;
    return default_val;
}

bool Config::has(const std::string& key) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->store.count(key) > 0;
}

bool Config::remove(const std::string& key) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->store.erase(key) > 0;
}

std::vector<std::string> Config::keys(const std::string& prefix) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    std::vector<std::string> result;
    for (auto& kv : impl_->store) {
        if (prefix.empty() ||
            kv.first.compare(0, prefix.size(), prefix) == 0) {
            result.push_back(kv.first);
        }
    }
    return result;
}

void Config::clear() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->store.clear();
}

size_t Config::size() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->store.size();
}

bool Config::load(const std::string& filepath) {
    std::ifstream ifs(filepath);
    if (!ifs.is_open()) return false;
    std::string content((std::istreambuf_iterator<char>(ifs)),
                        std::istreambuf_iterator<char>());
    return from_json(content);
}

bool Config::save(const std::string& filepath) const {
    std::ofstream ofs(filepath);
    if (!ofs.is_open()) return false;
    ofs << to_json();
    return ofs.good();
}

std::string Config::to_json() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    std::ostringstream oss;
    oss << "{\n";
    size_t i = 0;
    for (auto& kv : impl_->store) {
        oss << "  " << Impl::escape_json_string(kv.first) << ": "
            << Impl::value_to_json(kv.second);
        if (++i < impl_->store.size()) oss << ",";
        oss << "\n";
    }
    oss << "}";
    return oss.str();
}

bool Config::from_json(const std::string& json) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    size_t pos = Impl::skip_whitespace(json, 0);
    if (pos >= json.size() || json[pos] != '{') return false;
    ++pos;

    std::map<std::string, Value> new_store;

    pos = Impl::skip_whitespace(json, pos);
    if (pos < json.size() && json[pos] == '}') {
        impl_->store = new_store;
        return true;
    }

    while (pos < json.size()) {
        pos = Impl::skip_whitespace(json, pos);
        std::string key;
        if (!Impl::parse_string(json, pos, key)) return false;

        pos = Impl::skip_whitespace(json, pos);
        if (pos >= json.size() || json[pos] != ':') return false;
        ++pos;

        Value val;
        if (!Impl::parse_value(json, pos, val)) return false;
        new_store[key] = val;

        pos = Impl::skip_whitespace(json, pos);
        if (pos < json.size() && json[pos] == ',') {
            ++pos;
        } else {
            break;
        }
    }

    pos = Impl::skip_whitespace(json, pos);
    if (pos >= json.size() || json[pos] != '}') return false;

    impl_->store = std::move(new_store);
    return true;
}

void Config::on_change(
    const std::string& key,
    std::function<void(const std::string&, const Value&)> callback) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->callbacks.push_back({key, std::move(callback)});
}

}  // namespace core
}  // namespace espx
