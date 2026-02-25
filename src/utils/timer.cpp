// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/utils/timer.hpp"

#include <chrono>
#include <optional>
#include <thread>

namespace espx {
namespace utils {

struct Timer::Impl {
    using clock = std::chrono::steady_clock;
    using time_point = clock::time_point;

    bool running = false;
    time_point start_time{};
    uint64_t accumulated_us = 0;

    std::optional<std::function<void()>> callback;
    time_point target_time{};
    uint32_t interval_ms = 0;
    bool is_repeating = false;

    [[nodiscard]] uint64_t current_elapsed_us() const {
        uint64_t total = accumulated_us;
        if (running) {
            auto now = clock::now();
            auto delta = std::chrono::duration_cast<std::chrono::microseconds>(
                now - start_time);
            total += static_cast<uint64_t>(delta.count());
        }
        return total;
    }
};

Timer::Timer() : impl_(std::make_unique<Impl>()) {}
Timer::~Timer() = default;
Timer::Timer(Timer&&) noexcept = default;
Timer& Timer::operator=(Timer&&) noexcept = default;

void Timer::start() {
    impl_->start_time = Impl::clock::now();
    impl_->running = true;
}

void Timer::stop() {
    if (impl_->running) {
        auto now = Impl::clock::now();
        auto delta = std::chrono::duration_cast<std::chrono::microseconds>(
            now - impl_->start_time);
        impl_->accumulated_us += static_cast<uint64_t>(delta.count());
        impl_->running = false;
    }
}

void Timer::reset() {
    impl_->running = false;
    impl_->accumulated_us = 0;
}

bool Timer::is_running() const {
    return impl_->running;
}

uint64_t Timer::elapsed_ms() const {
    return impl_->current_elapsed_us() / 1000;
}

uint64_t Timer::elapsed_us() const {
    return impl_->current_elapsed_us();
}

double Timer::elapsed_seconds() const {
    return static_cast<double>(impl_->current_elapsed_us()) / 1'000'000.0;
}

void Timer::set_timeout(uint32_t delay_ms, std::function<void()> callback) {
    impl_->callback = std::move(callback);
    impl_->target_time = Impl::clock::now() +
        std::chrono::milliseconds(delay_ms);
    impl_->interval_ms = 0;
    impl_->is_repeating = false;
}

void Timer::set_interval(uint32_t interval_ms, std::function<void()> callback) {
    impl_->callback = std::move(callback);
    impl_->target_time = Impl::clock::now() +
        std::chrono::milliseconds(interval_ms);
    impl_->interval_ms = interval_ms;
    impl_->is_repeating = true;
}

void Timer::cancel() {
    impl_->callback.reset();
    impl_->is_repeating = false;
    impl_->interval_ms = 0;
}

void Timer::tick() {
    if (!impl_->callback) {
        return;
    }
    auto now = Impl::clock::now();
    if (now >= impl_->target_time) {
        auto cb = *impl_->callback;
        if (impl_->is_repeating) {
            impl_->target_time = now +
                std::chrono::milliseconds(impl_->interval_ms);
        } else {
            impl_->callback.reset();
        }
        cb();
    }
}

uint64_t Timer::now_ms() {
    auto now = std::chrono::steady_clock::now().time_since_epoch();
    return static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(now).count());
}

uint64_t Timer::now_us() {
    auto now = std::chrono::steady_clock::now().time_since_epoch();
    return static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(now).count());
}

void Timer::delay_ms(uint32_t ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

}  // namespace utils
}  // namespace espx
