#include <cassert>
#include <iostream>
#include <thread>
#include "espx/utils/timer.hpp"

using espx::utils::Timer;

int main() {
    {
        std::cout << "test start/stop/elapsed_ms ... ";
        Timer t;
        t.start();
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        t.stop();
        assert(t.elapsed_ms() >= 10);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test reset ... ";
        Timer t;
        t.start();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        t.stop();
        t.reset();
        assert(t.elapsed_ms() == 0);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test now_ms ... ";
        auto ms = Timer::now_ms();
        assert(ms > 0);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test is_running ... ";
        Timer t;
        assert(!t.is_running());
        t.start();
        assert(t.is_running());
        t.stop();
        assert(!t.is_running());
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All timer tests passed." << std::endl;
    return 0;
}
