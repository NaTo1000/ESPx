// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/gpio/sensor.hpp"

#include <chrono>
#include <mutex>
#include <random>

namespace espx {
namespace gpio {

struct Sensor::Impl {
    std::string name;
    uint8_t pin = 0;
    bool initialized = false;

    // Periodic state
    bool periodic_active = false;
    uint32_t periodic_interval_ms = 0;
    std::function<void(const SensorReading&)> periodic_cb;

    // Threshold state
    double threshold_min = 0.0;
    double threshold_max = 0.0;
    std::function<void(const SensorReading&)> threshold_cb;

    mutable std::mutex mutex;

    static uint64_t now_ms() {
        using namespace std::chrono;
        return static_cast<uint64_t>(
            duration_cast<milliseconds>(
                system_clock::now().time_since_epoch())
                .count());
    }
};

Sensor::Sensor(const std::string& name, uint8_t pin)
    : impl_(std::make_unique<Impl>()) {
    impl_->name = name;
    impl_->pin = pin;
}

Sensor::~Sensor() = default;

SensorReading Sensor::read_averaged(uint16_t count) {
    if (count == 0) count = 1;

    double sum = 0.0;
    SensorReading last{};

    for (uint16_t i = 0; i < count; ++i) {
        last = read();
        sum += last.value;
    }

    last.value = sum / static_cast<double>(count);
    return last;
}

void Sensor::start_periodic(
    uint32_t interval_ms,
    std::function<void(const SensorReading&)> callback) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->periodic_active = true;
    impl_->periodic_interval_ms = interval_ms;
    impl_->periodic_cb = std::move(callback);
}

void Sensor::stop_periodic() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->periodic_active = false;
    impl_->periodic_cb = nullptr;
}

void Sensor::set_threshold(
    double min_value, double max_value,
    std::function<void(const SensorReading&)> callback) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->threshold_min = min_value;
    impl_->threshold_max = max_value;
    impl_->threshold_cb = std::move(callback);
}

const std::string& Sensor::name() const {
    return impl_->name;
}

uint8_t Sensor::pin() const {
    return impl_->pin;
}

bool Sensor::is_initialized() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->initialized;
}

// --- TemperatureSensor ---

TemperatureSensor::TemperatureSensor(const std::string& name, uint8_t pin)
    : Sensor(name, pin) {}

TemperatureSensor::~TemperatureSensor() = default;

bool TemperatureSensor::init() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->initialized = true;
    return true;
}

SensorReading TemperatureSensor::read() {
    static thread_local std::mt19937 rng{std::random_device{}()};
    std::uniform_real_distribution<double> noise(-0.5, 0.5);

    SensorReading reading;
    reading.sensor_name = impl_->name;
    reading.unit = "\xC2\xB0""C";  // °C in UTF-8
    reading.value = 22.5 + noise(rng);
    reading.timestamp_ms = Impl::now_ms();
    reading.valid = impl_->initialized;
    return reading;
}

// --- HumiditySensor ---

HumiditySensor::HumiditySensor(const std::string& name, uint8_t pin)
    : Sensor(name, pin) {}

HumiditySensor::~HumiditySensor() = default;

bool HumiditySensor::init() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->initialized = true;
    return true;
}

SensorReading HumiditySensor::read() {
    static thread_local std::mt19937 rng{std::random_device{}()};
    std::uniform_real_distribution<double> noise(-2.0, 2.0);

    SensorReading reading;
    reading.sensor_name = impl_->name;
    reading.unit = "%";
    reading.value = 45.0 + noise(rng);
    reading.timestamp_ms = Impl::now_ms();
    reading.valid = impl_->initialized;
    return reading;
}

}  // namespace gpio
}  // namespace espx
