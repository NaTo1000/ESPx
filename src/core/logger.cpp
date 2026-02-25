// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/core/logger.hpp"

#include <algorithm>
#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>

namespace espx {
namespace core {

const char* log_level_to_string(LogLevel level) {
    switch (level) {
        case LogLevel::Trace: return "TRACE";
        case LogLevel::Debug: return "DEBUG";
        case LogLevel::Info:  return "INFO";
        case LogLevel::Warn:  return "WARN";
        case LogLevel::Error: return "ERROR";
        case LogLevel::Fatal: return "FATAL";
        case LogLevel::Off:   return "OFF";
    }
    return "UNKNOWN";
}

LogLevel log_level_from_string(const std::string& str) {
    std::string lower;
    lower.resize(str.size());
    std::transform(str.begin(), str.end(), lower.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });

    if (lower == "trace") return LogLevel::Trace;
    if (lower == "debug") return LogLevel::Debug;
    if (lower == "info")  return LogLevel::Info;
    if (lower == "warn" || lower == "warning") return LogLevel::Warn;
    if (lower == "error") return LogLevel::Error;
    if (lower == "fatal") return LogLevel::Fatal;
    if (lower == "off")   return LogLevel::Off;
    return LogLevel::Info;
}

// ANSI color codes
static const char* level_color(LogLevel level) {
    switch (level) {
        case LogLevel::Trace: return "\033[90m";      // dark gray
        case LogLevel::Debug: return "\033[36m";      // cyan
        case LogLevel::Info:  return "\033[32m";      // green
        case LogLevel::Warn:  return "\033[33m";      // yellow
        case LogLevel::Error: return "\033[31m";      // red
        case LogLevel::Fatal: return "\033[1;31m";    // bold red
        case LogLevel::Off:   return "";
    }
    return "";
}

static const char* color_reset() {
    return "\033[0m";
}

struct Logger::Impl {
    LogLevel global_level{LogLevel::Info};
    std::map<std::string, LogLevel> tag_levels;
    bool color_enabled{true};
    bool timestamp_enabled{true};
    uint64_t message_count{0};
    uint64_t error_count{0};
    std::ofstream file_stream;
    size_t max_file_size{0};
    std::string log_filepath;
    std::mutex mutex;
    std::chrono::steady_clock::time_point start_time{
        std::chrono::steady_clock::now()};

    LogLevel effective_level(const char* tag) const {
        if (tag) {
            auto it = tag_levels.find(tag);
            if (it != tag_levels.end()) {
                return it->second;
            }
        }
        return global_level;
    }
};

Logger::Logger() : impl_(std::make_unique<Impl>()) {}
Logger::~Logger() = default;

Logger& Logger::instance() {
    static Logger inst;
    return inst;
}

void Logger::set_level(LogLevel level) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->global_level = level;
}

LogLevel Logger::level() const {
    return impl_->global_level;
}

void Logger::set_tag_level(const std::string& tag, LogLevel level) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->tag_levels[tag] = level;
}

void Logger::log(LogLevel level, const char* tag, const char* file,
                 int line, const std::string& message) {
    std::lock_guard<std::mutex> lock(impl_->mutex);

    if (static_cast<uint8_t>(level) <
        static_cast<uint8_t>(impl_->effective_level(tag))) {
        return;
    }

    ++impl_->message_count;
    if (level >= LogLevel::Error) {
        ++impl_->error_count;
    }

    std::ostringstream oss;

    // Timestamp
    if (impl_->timestamp_enabled) {
        auto now = std::chrono::steady_clock::now();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                      now - impl_->start_time)
                      .count();
        oss << "[" << ms << "ms] ";
    }

    // Level
    const char* lvl_str = log_level_to_string(level);
    oss << "[" << lvl_str << "] ";

    // Tag
    if (tag && std::strlen(tag) > 0) {
        oss << "[" << tag << "] ";
    }

    // Message
    oss << message;

    // File and line
    if (file) {
        const char* basename = std::strrchr(file, '/');
        if (!basename) basename = std::strrchr(file, '\\');
        if (basename) ++basename; else basename = file;
        oss << " (" << basename << ":" << line << ")";
    }

    std::string formatted = oss.str();

    // Console output
    if (impl_->color_enabled) {
        std::cout << level_color(level) << formatted << color_reset()
                  << std::endl;
    } else {
        std::cout << formatted << std::endl;
    }

    // File output
    if (impl_->file_stream.is_open()) {
        impl_->file_stream << formatted << "\n";
        impl_->file_stream.flush();
    }
}

void Logger::set_color_enabled(bool enabled) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->color_enabled = enabled;
}

void Logger::set_timestamp_enabled(bool enabled) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->timestamp_enabled = enabled;
}

bool Logger::enable_file_logging(const std::string& filepath,
                                 size_t max_size_bytes) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (impl_->file_stream.is_open()) {
        impl_->file_stream.close();
    }
    impl_->file_stream.open(filepath, std::ios::app);
    if (!impl_->file_stream.is_open()) {
        return false;
    }
    impl_->log_filepath = filepath;
    impl_->max_file_size = max_size_bytes;
    return true;
}

void Logger::disable_file_logging() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (impl_->file_stream.is_open()) {
        impl_->file_stream.close();
    }
    impl_->log_filepath.clear();
}

uint64_t Logger::message_count() const {
    return impl_->message_count;
}

uint64_t Logger::error_count() const {
    return impl_->error_count;
}

}  // namespace core
}  // namespace espx
