// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>

namespace espx {
namespace utils {

/**
 * @class Timer
 * @brief High-resolution timer for scheduling and measurement.
 *
 * Provides one-shot and repeating timer functionality, as well as
 * elapsed time measurement for profiling and benchmarking.
 *
 * Example:
 * @code
 *   // Measure elapsed time
 *   espx::utils::Timer timer;
 *   timer.start();
 *   // ... do some work ...
 *   auto elapsed = timer.elapsed_ms();
 *   std::cout << "Took " << elapsed << " ms" << std::endl;
 *
 *   // Schedule a callback
 *   espx::utils::Timer repeater;
 *   repeater.set_interval(1000, []() {
 *       std::cout << "Tick!" << std::endl;
 *   });
 * @endcode
 */
class Timer {
public:
    Timer();
    ~Timer();

    Timer(const Timer&) = delete;
    Timer& operator=(const Timer&) = delete;
    Timer(Timer&&) noexcept;
    Timer& operator=(Timer&&) noexcept;

    // ---- Stopwatch functionality ----

    /**
     * @brief Start the timer (or restart if already running).
     */
    void start();

    /**
     * @brief Stop the timer.
     */
    void stop();

    /**
     * @brief Reset the timer to zero.
     */
    void reset();

    /**
     * @brief Check if the timer is currently running.
     * @return true if running
     */
    [[nodiscard]] bool is_running() const;

    /**
     * @brief Get elapsed time in milliseconds.
     * @return Elapsed milliseconds
     */
    [[nodiscard]] uint64_t elapsed_ms() const;

    /**
     * @brief Get elapsed time in microseconds.
     * @return Elapsed microseconds
     */
    [[nodiscard]] uint64_t elapsed_us() const;

    /**
     * @brief Get elapsed time in seconds (floating point).
     * @return Elapsed seconds
     */
    [[nodiscard]] double elapsed_seconds() const;

    // ---- Scheduled callbacks ----

    /**
     * @brief Schedule a one-shot callback after a delay.
     * @param delay_ms Delay in milliseconds
     * @param callback Function to call
     */
    void set_timeout(uint32_t delay_ms, std::function<void()> callback);

    /**
     * @brief Schedule a repeating callback.
     * @param interval_ms Interval in milliseconds
     * @param callback Function to call
     */
    void set_interval(uint32_t interval_ms, std::function<void()> callback);

    /**
     * @brief Cancel any scheduled callback.
     */
    void cancel();

    /**
     * @brief Process scheduled callbacks.
     *
     * Call this from the main loop to fire pending callbacks.
     */
    void tick();

    // ---- Static utilities ----

    /**
     * @brief Get the current system time in milliseconds.
     * @return Milliseconds since epoch or boot
     */
    static uint64_t now_ms();

    /**
     * @brief Get the current system time in microseconds.
     * @return Microseconds since epoch or boot
     */
    static uint64_t now_us();

    /**
     * @brief Sleep for a given number of milliseconds.
     * @param ms Milliseconds to sleep
     */
    static void delay_ms(uint32_t ms);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace utils
}  // namespace espx
