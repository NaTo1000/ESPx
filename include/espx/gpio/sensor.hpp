// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace gpio {

/**
 * @struct SensorReading
 * @brief A generic sensor measurement.
 */
struct SensorReading {
    std::string sensor_name;     ///< Sensor identifier
    std::string unit;            ///< Measurement unit (e.g., "°C", "%", "hPa")
    double value = 0.0;          ///< Measured value
    uint64_t timestamp_ms = 0;   ///< Reading timestamp
    bool valid = false;          ///< Whether the reading is valid
};

/**
 * @class Sensor
 * @brief Abstract base class for sensor interfaces.
 *
 * Provides a common interface for various sensors (temperature,
 * humidity, pressure, light, motion, etc.) with support for
 * periodic sampling and threshold alerts.
 *
 * Example:
 * @code
 *   espx::gpio::TemperatureSensor temp("DHT22", 4);
 *   temp.init();
 *   auto reading = temp.read();
 *   std::cout << reading.value << " " << reading.unit << std::endl;
 * @endcode
 */
class Sensor {
public:
    /**
     * @brief Construct a sensor with a name and pin.
     * @param name Sensor identifier
     * @param pin GPIO pin number
     */
    Sensor(const std::string& name, uint8_t pin);
    virtual ~Sensor();

    Sensor(const Sensor&) = delete;
    Sensor& operator=(const Sensor&) = delete;

    /**
     * @brief Initialize the sensor hardware.
     * @return true if initialization succeeded
     */
    virtual bool init() = 0;

    /**
     * @brief Take a single reading from the sensor.
     * @return Sensor reading
     */
    virtual SensorReading read() = 0;

    /**
     * @brief Take multiple readings and return the average.
     * @param count Number of readings to average
     * @return Averaged sensor reading
     */
    virtual SensorReading read_averaged(uint16_t count = 10);

    /**
     * @brief Start periodic reading at the given interval.
     * @param interval_ms Interval between readings in milliseconds
     * @param callback Called with each new reading
     */
    void start_periodic(uint32_t interval_ms,
                        std::function<void(const SensorReading&)> callback);

    /**
     * @brief Stop periodic reading.
     */
    void stop_periodic();

    /**
     * @brief Set a threshold alert.
     * @param min_value Minimum acceptable value
     * @param max_value Maximum acceptable value
     * @param callback Called when value is out of range
     */
    void set_threshold(double min_value, double max_value,
                       std::function<void(const SensorReading&)> callback);

    /// Get the sensor name
    [[nodiscard]] const std::string& name() const;

    /// Get the GPIO pin number
    [[nodiscard]] uint8_t pin() const;

    /// Check if the sensor is initialized
    [[nodiscard]] bool is_initialized() const;

protected:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

/**
 * @class TemperatureSensor
 * @brief Temperature sensor implementation (e.g., DHT22, DS18B20).
 */
class TemperatureSensor : public Sensor {
public:
    TemperatureSensor(const std::string& name, uint8_t pin);
    ~TemperatureSensor() override;

    bool init() override;
    SensorReading read() override;
};

/**
 * @class HumiditySensor
 * @brief Humidity sensor implementation.
 */
class HumiditySensor : public Sensor {
public:
    HumiditySensor(const std::string& name, uint8_t pin);
    ~HumiditySensor() override;

    bool init() override;
    SensorReading read() override;
};

}  // namespace gpio
}  // namespace espx
