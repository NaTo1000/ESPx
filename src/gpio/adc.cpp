// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/gpio/adc.hpp"

#include <chrono>
#include <map>
#include <mutex>
#include <random>

namespace espx {
namespace gpio {

struct ADC::Impl {
    struct ChannelConfig {
        ADCAttenuation atten = ADCAttenuation::DB_11;
        ADCWidth width = ADCWidth::Bit12;
        double calibration_offset = 0.0;
    };

    std::map<uint8_t, ChannelConfig> channels;
    mutable std::mutex mutex;
    mutable std::mt19937 rng{std::random_device{}()};

    static uint64_t now_ms() {
        using namespace std::chrono;
        return static_cast<uint64_t>(
            duration_cast<milliseconds>(
                system_clock::now().time_since_epoch())
                .count());
    }

    uint16_t max_raw(ADCWidth width) const {
        return static_cast<uint16_t>(
            (1u << static_cast<unsigned>(width)) - 1u);
    }

    double max_voltage_mv(ADCAttenuation atten) const {
        switch (atten) {
            case ADCAttenuation::DB_0:   return 950.0;
            case ADCAttenuation::DB_2_5: return 1250.0;
            case ADCAttenuation::DB_6:   return 1750.0;
            case ADCAttenuation::DB_11:  return 2450.0;
        }
        return 2450.0;
    }

    uint16_t simulated_raw(ADCWidth width) const {
        uint16_t max_val = max_raw(width);
        uint16_t midpoint = static_cast<uint16_t>(max_val / 2u);
        std::uniform_int_distribution<int> noise(-50, 50);
        auto val = static_cast<int>(midpoint) + noise(rng);
        if (val < 0) val = 0;
        if (val > max_val) val = max_val;
        return static_cast<uint16_t>(val);
    }
};

ADC::ADC() : impl_(std::make_unique<Impl>()) {}
ADC::~ADC() = default;

bool ADC::init(uint8_t channel, ADCAttenuation atten, ADCWidth width) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    if (channel > 7) return false;
    impl_->channels[channel] = {atten, width, 0.0};
    return true;
}

ADCReading ADC::read(uint8_t channel) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    ADCReading reading{};
    reading.channel = channel;
    reading.timestamp_ms = Impl::now_ms();

    auto it = impl_->channels.find(channel);
    if (it == impl_->channels.end()) {
        return reading;
    }

    auto& cfg = it->second;
    reading.raw_value = impl_->simulated_raw(cfg.width);

    double max_v = impl_->max_voltage_mv(cfg.atten);
    double max_r = static_cast<double>(impl_->max_raw(cfg.width));
    reading.voltage_mv =
        (static_cast<double>(reading.raw_value) / max_r) * max_v +
        cfg.calibration_offset;

    return reading;
}

ADCReading ADC::read_averaged(uint8_t channel, uint16_t samples) const {
    if (samples == 0) samples = 1;

    uint32_t raw_sum = 0;
    double voltage_sum = 0.0;

    for (uint16_t i = 0; i < samples; ++i) {
        auto r = read(channel);
        raw_sum += r.raw_value;
        voltage_sum += r.voltage_mv;
    }

    ADCReading result{};
    result.channel = channel;
    result.timestamp_ms = Impl::now_ms();
    result.raw_value =
        static_cast<uint16_t>(raw_sum / static_cast<uint32_t>(samples));
    result.voltage_mv = voltage_sum / static_cast<double>(samples);
    return result;
}

std::vector<ADCReading> ADC::read_multiple(
    const std::vector<uint8_t>& channels) const {
    std::vector<ADCReading> results;
    results.reserve(channels.size());
    for (auto ch : channels) {
        results.push_back(read(ch));
    }
    return results;
}

bool ADC::calibrate(uint8_t channel, double reference_mv) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->channels.find(channel);
    if (it == impl_->channels.end()) return false;

    auto& cfg = it->second;
    uint16_t raw = impl_->simulated_raw(cfg.width);
    double max_v = impl_->max_voltage_mv(cfg.atten);
    double max_r = static_cast<double>(impl_->max_raw(cfg.width));
    double measured_mv = (static_cast<double>(raw) / max_r) * max_v;
    cfg.calibration_offset = reference_mv - measured_mv;
    return true;
}

uint16_t ADC::raw_read(uint8_t channel) const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    auto it = impl_->channels.find(channel);
    if (it == impl_->channels.end()) return 0;
    return impl_->simulated_raw(it->second.width);
}

}  // namespace gpio
}  // namespace espx
