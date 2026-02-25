#include <cassert>
#include <iostream>
#include "espx/gpio/pin.hpp"
#include "espx/gpio/adc.hpp"
#include "espx/gpio/sensor.hpp"

using namespace espx::gpio;

int main() {
    {
        std::cout << "test Pin write/read/toggle ... ";
        Pin pin(2, PinMode::Output);
        pin.write(PinState::High);
        assert(pin.read() == PinState::High);
        pin.write(PinState::Low);
        assert(pin.read() == PinState::Low);
        pin.toggle();
        assert(pin.read() == PinState::High);
        pin.toggle();
        assert(pin.read() == PinState::Low);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test ADC init/read ... ";
        ADC adc;
        assert(adc.init(0));
        auto reading = adc.read(0);
        assert(reading.raw_value <= 4095);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test TemperatureSensor ... ";
        TemperatureSensor temp("DHT22", 4);
        assert(temp.init());
        auto r = temp.read();
        assert(r.valid);
        assert(r.unit == "\xC2\xB0""C");
        assert(r.value > 10.0 && r.value < 40.0);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test HumiditySensor ... ";
        HumiditySensor hum("DHT22-H", 4);
        assert(hum.init());
        auto r = hum.read();
        assert(r.valid);
        assert(r.unit == "%");
        assert(r.value > 0.0 && r.value < 100.0);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All gpio tests passed." << std::endl;
    return 0;
}
