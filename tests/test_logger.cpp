#include <cassert>
#include <iostream>
#include <string>
#include "espx/core/logger.hpp"

using namespace espx::core;

int main() {
    auto& logger = Logger::instance();

    {
        std::cout << "test set_level/level ... ";
        logger.set_level(LogLevel::Debug);
        assert(logger.level() == LogLevel::Debug);
        logger.set_level(LogLevel::Warn);
        assert(logger.level() == LogLevel::Warn);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test log_level_to_string/from_string ... ";
        assert(std::string(log_level_to_string(LogLevel::Error)) == "ERROR");
        assert(std::string(log_level_to_string(LogLevel::Trace)) == "TRACE");
        assert(log_level_from_string("error") == LogLevel::Error);
        assert(log_level_from_string("DEBUG") == LogLevel::Debug);
        assert(log_level_from_string("unknown") == LogLevel::Info);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test message_count ... ";
        logger.set_level(LogLevel::Trace);
        auto before = logger.message_count();
        logger.log(LogLevel::Info, "test", __FILE__, __LINE__, "hello");
        assert(logger.message_count() == before + 1);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test error_count ... ";
        logger.set_level(LogLevel::Trace);
        auto before = logger.error_count();
        logger.log(LogLevel::Info, "test", __FILE__, __LINE__, "info msg");
        assert(logger.error_count() == before);
        logger.log(LogLevel::Error, "test", __FILE__, __LINE__, "err msg");
        assert(logger.error_count() == before + 1);
        logger.log(LogLevel::Fatal, "test", __FILE__, __LINE__, "fatal msg");
        assert(logger.error_count() == before + 2);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All logger tests passed." << std::endl;
    return 0;
}
