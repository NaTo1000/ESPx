// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/gpio/pin.hpp"

#include <mutex>

namespace espx {
namespace gpio {

struct Pin::Impl {
    uint8_t pin_number = 0;
    PinMode mode = PinMode::Input;
    PinState state = PinState::Low;
    uint32_t pwm_frequency = 0;
    uint8_t pwm_duty = 0;
    uint8_t pwm_resolution = 8;
    InterruptMode interrupt_mode = InterruptMode::Disabled;
    std::function<void()> interrupt_handler;
    mutable std::mutex mutex;
};

Pin::Pin(uint8_t pin_number, PinMode mode)
    : impl_(std::make_unique<Impl>()) {
    impl_->pin_number = pin_number;
    impl_->mode = mode;
}

Pin::~Pin() = default;

Pin::Pin(Pin&& other) noexcept = default;
Pin& Pin::operator=(Pin&& other) noexcept = default;

void Pin::set_mode(PinMode mode) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->mode = mode;
}

PinState Pin::read() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->state;
}

void Pin::write(PinState state) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->state = state;
}

void Pin::toggle() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->state = (impl_->state == PinState::Low)
                       ? PinState::High
                       : PinState::Low;
}

uint16_t Pin::analog_read() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    // Simulated midpoint value for host mode
    return 2048;
}

void Pin::set_pwm(uint32_t frequency, uint8_t duty, uint8_t resolution) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->pwm_frequency = frequency;
    impl_->pwm_duty = duty;
    impl_->pwm_resolution = resolution;
}

void Pin::set_pwm_duty(uint8_t duty) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->pwm_duty = duty;
}

void Pin::on_interrupt(InterruptMode mode, std::function<void()> handler) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->interrupt_mode = mode;
    impl_->interrupt_handler = std::move(handler);
}

void Pin::detach_interrupt() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->interrupt_mode = InterruptMode::Disabled;
    impl_->interrupt_handler = nullptr;
}

uint8_t Pin::pin_number() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->pin_number;
}

PinMode Pin::mode() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->mode;
}

}  // namespace gpio
}  // namespace espx
