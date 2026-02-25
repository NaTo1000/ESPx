// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>

namespace espx {
namespace gpio {

/**
 * @enum PinMode
 * @brief GPIO pin operating modes.
 */
enum class PinMode {
    Input,          ///< Digital input
    Output,         ///< Digital output
    InputPullUp,    ///< Input with internal pull-up resistor
    InputPullDown,  ///< Input with internal pull-down resistor
    OpenDrain,      ///< Open-drain output
    Analog          ///< Analog input (ADC)
};

/**
 * @enum PinState
 * @brief Digital pin logic levels.
 */
enum class PinState {
    Low = 0,
    High = 1
};

/**
 * @enum InterruptMode
 * @brief GPIO interrupt trigger modes.
 */
enum class InterruptMode {
    Disabled,    ///< No interrupt
    Rising,      ///< Trigger on rising edge
    Falling,     ///< Trigger on falling edge
    Change,      ///< Trigger on any edge
    Low,         ///< Trigger while low
    High         ///< Trigger while high
};

/**
 * @class Pin
 * @brief GPIO pin control.
 *
 * Provides digital I/O, interrupt handling, PWM output, and
 * analog reading for ESP32 GPIO pins.
 *
 * Example:
 * @code
 *   espx::gpio::Pin led(2, espx::gpio::PinMode::Output);
 *   led.write(espx::gpio::PinState::High);
 *
 *   espx::gpio::Pin button(0, espx::gpio::PinMode::InputPullUp);
 *   button.on_interrupt(espx::gpio::InterruptMode::Falling, []() {
 *       // Button pressed!
 *   });
 *
 *   espx::gpio::Pin pwm_pin(5, espx::gpio::PinMode::Output);
 *   pwm_pin.set_pwm(1000, 128);  // 1kHz, 50% duty cycle
 * @endcode
 */
class Pin {
public:
    /**
     * @brief Construct a GPIO pin.
     * @param pin_number GPIO pin number
     * @param mode Pin operating mode
     */
    Pin(uint8_t pin_number, PinMode mode = PinMode::Input);
    ~Pin();

    Pin(const Pin&) = delete;
    Pin& operator=(const Pin&) = delete;
    Pin(Pin&&) noexcept;
    Pin& operator=(Pin&&) noexcept;

    /**
     * @brief Set the pin mode.
     * @param mode New pin mode
     */
    void set_mode(PinMode mode);

    /**
     * @brief Read the digital pin state.
     * @return Current pin state
     */
    [[nodiscard]] PinState read() const;

    /**
     * @brief Write a digital value to the pin.
     * @param state Pin state to set
     */
    void write(PinState state);

    /**
     * @brief Toggle the pin state (High <-> Low).
     */
    void toggle();

    /**
     * @brief Read the analog value (10-bit ADC).
     * @return ADC value (0–4095 on ESP32)
     */
    [[nodiscard]] uint16_t analog_read() const;

    /**
     * @brief Set up PWM output.
     * @param frequency PWM frequency in Hz
     * @param duty Duty cycle (0–255)
     * @param resolution PWM resolution in bits (1–16, default 8)
     */
    void set_pwm(uint32_t frequency, uint8_t duty, uint8_t resolution = 8);

    /**
     * @brief Update PWM duty cycle.
     * @param duty New duty cycle (0–255)
     */
    void set_pwm_duty(uint8_t duty);

    /**
     * @brief Attach an interrupt handler.
     * @param mode Interrupt trigger mode
     * @param handler Callback function
     */
    void on_interrupt(InterruptMode mode, std::function<void()> handler);

    /**
     * @brief Detach the interrupt handler.
     */
    void detach_interrupt();

    /// Get the pin number
    [[nodiscard]] uint8_t pin_number() const;

    /// Get the current pin mode
    [[nodiscard]] PinMode mode() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace gpio
}  // namespace espx
