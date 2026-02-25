// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace gpio {

/**
 * @enum ADCAttenuation
 * @brief ADC input attenuation settings.
 */
enum class ADCAttenuation {
    DB_0 = 0,    ///< 0 dB (100 mV – 950 mV)
    DB_2_5 = 1,  ///< 2.5 dB (100 mV – 1250 mV)
    DB_6 = 2,    ///< 6 dB (150 mV – 1750 mV)
    DB_11 = 3    ///< 11 dB (150 mV – 2450 mV)
};

/**
 * @enum ADCWidth
 * @brief ADC bit width resolution.
 */
enum class ADCWidth {
    Bit9 = 9,
    Bit10 = 10,
    Bit11 = 11,
    Bit12 = 12
};

/**
 * @struct ADCReading
 * @brief An ADC measurement result.
 */
struct ADCReading {
    uint8_t channel;         ///< ADC channel number
    uint16_t raw_value;      ///< Raw ADC value
    double voltage_mv;       ///< Calibrated voltage in millivolts
    uint64_t timestamp_ms;   ///< Reading timestamp
};

/**
 * @class ADC
 * @brief Analog-to-Digital Converter interface.
 *
 * Provides calibrated ADC readings with configurable attenuation,
 * resolution, and multisampling for noise reduction.
 *
 * Example:
 * @code
 *   espx::gpio::ADC adc;
 *   adc.init(0, espx::gpio::ADCAttenuation::DB_11,
 *            espx::gpio::ADCWidth::Bit12);
 *
 *   auto reading = adc.read(0);
 *   std::cout << "Voltage: " << reading.voltage_mv << " mV" << std::endl;
 *
 *   // Averaged reading for noise reduction
 *   auto avg = adc.read_averaged(0, 64);
 * @endcode
 */
class ADC {
public:
    ADC();
    ~ADC();

    ADC(const ADC&) = delete;
    ADC& operator=(const ADC&) = delete;

    /**
     * @brief Initialize an ADC channel.
     * @param channel ADC channel number (0-7)
     * @param atten Input attenuation
     * @param width Bit width resolution
     * @return true if initialization succeeded
     */
    bool init(uint8_t channel, ADCAttenuation atten = ADCAttenuation::DB_11,
              ADCWidth width = ADCWidth::Bit12);

    /**
     * @brief Read a single ADC value.
     * @param channel ADC channel
     * @return ADC reading with calibrated voltage
     */
    [[nodiscard]] ADCReading read(uint8_t channel) const;

    /**
     * @brief Read an averaged ADC value (multisampling).
     * @param channel ADC channel
     * @param samples Number of samples to average
     * @return Averaged ADC reading
     */
    [[nodiscard]] ADCReading read_averaged(uint8_t channel,
                                           uint16_t samples = 64) const;

    /**
     * @brief Read multiple channels simultaneously.
     * @param channels Vector of channel numbers
     * @return Vector of ADC readings
     */
    [[nodiscard]] std::vector<ADCReading> read_multiple(
        const std::vector<uint8_t>& channels) const;

    /**
     * @brief Calibrate the ADC for a channel.
     * @param channel ADC channel
     * @param reference_mv Known reference voltage in millivolts
     * @return true if calibration succeeded
     */
    bool calibrate(uint8_t channel, double reference_mv);

    /**
     * @brief Get the raw ADC value.
     * @param channel ADC channel
     * @return Raw ADC value (0–4095 for 12-bit)
     */
    [[nodiscard]] uint16_t raw_read(uint8_t channel) const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace gpio
}  // namespace espx
