// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/core/app.hpp"

#include <atomic>
#include <chrono>
#include <mutex>
#include <thread>
#include <vector>

namespace espx {
namespace core {

struct App::Impl {
    struct PeriodicTask {
        std::string name;
        uint32_t interval_ms;
        std::function<void()> task;
        uint64_t last_run_ms;
    };

    std::string name;
    State state{State::Created};
    std::function<void()> on_ready;
    std::function<void()> on_shutdown;
    std::vector<PeriodicTask> periodic_tasks;
    std::chrono::steady_clock::time_point start_time;
    std::atomic<bool> running{false};
    std::mutex mutex;

    uint64_t elapsed_ms() const {
        auto now = std::chrono::steady_clock::now();
        return static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                now - start_time)
                .count());
    }
};

App::App(const std::string& name) : impl_(std::make_unique<Impl>()) {
    impl_->name = name;
}

App::~App() {
    if (impl_ && impl_->running) {
        stop();
    }
}

App::App(App&&) noexcept = default;
App& App::operator=(App&&) noexcept = default;

bool App::init() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (impl_->state != State::Created) {
        return false;
    }
    impl_->state = State::Initializing;
    impl_->state = State::Running;
    return true;
}

void App::run() {
    if (impl_->state == State::Created) {
        if (!init()) {
            return;
        }
    }

    impl_->start_time = std::chrono::steady_clock::now();
    impl_->running = true;
    impl_->state = State::Running;

    if (impl_->on_ready) {
        impl_->on_ready();
    }

    while (impl_->running) {
        uint64_t now_ms = impl_->elapsed_ms();

        {
            std::lock_guard<std::mutex> lock(impl_->mutex);
            for (auto& pt : impl_->periodic_tasks) {
                if (now_ms - pt.last_run_ms >= pt.interval_ms) {
                    pt.task();
                    pt.last_run_ms = now_ms;
                }
            }
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    impl_->state = State::Stopping;

    if (impl_->on_shutdown) {
        impl_->on_shutdown();
    }

    impl_->state = State::Stopped;
}

void App::stop() {
    impl_->running = false;
}

void App::on_ready(std::function<void()> callback) {
    impl_->on_ready = std::move(callback);
}

void App::on_shutdown(std::function<void()> callback) {
    impl_->on_shutdown = std::move(callback);
}

void App::add_periodic_task(const std::string& name, uint32_t interval_ms,
                            std::function<void()> task) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->periodic_tasks.push_back({name, interval_ms, std::move(task), 0});
}

const std::string& App::name() const {
    return impl_->name;
}

App::State App::state() const {
    return impl_->state;
}

uint64_t App::uptime_ms() const {
    if (!impl_->running) {
        return 0;
    }
    return impl_->elapsed_ms();
}

}  // namespace core
}  // namespace espx
