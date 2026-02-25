#include <cassert>
#include <iostream>
#include "espx/core/event_loop.hpp"

using namespace espx::core;

static constexpr EventId TEST_EVENT = ESPX_EVENT_USER_BASE + 1;

int main() {
    auto& loop = EventLoop::instance();
    loop.reset();

    {
        std::cout << "test on/post ... ";
        int count = 0;
        auto h = loop.on(TEST_EVENT, [&](const EventData&) { ++count; });
        loop.post(TEST_EVENT, nullptr, 0, "test");
        loop.post(TEST_EVENT, nullptr, 0, "test");
        assert(count == 2);
        loop.off(h);
        std::cout << "PASS" << std::endl;
    }
    loop.reset();
    {
        std::cout << "test once ... ";
        int count = 0;
        loop.once(TEST_EVENT, [&](const EventData&) { ++count; });
        loop.post(TEST_EVENT, nullptr, 0, "test");
        loop.post(TEST_EVENT, nullptr, 0, "test");
        assert(count == 1);
        std::cout << "PASS" << std::endl;
    }
    loop.reset();
    {
        std::cout << "test off ... ";
        int count = 0;
        auto h = loop.on(TEST_EVENT, [&](const EventData&) { ++count; });
        loop.off(h);
        loop.post(TEST_EVENT, nullptr, 0, "test");
        assert(count == 0);
        std::cout << "PASS" << std::endl;
    }
    loop.reset();
    {
        std::cout << "test post_deferred/process_pending ... ";
        int count = 0;
        auto h = loop.on(TEST_EVENT, [&](const EventData&) { ++count; });
        loop.post_deferred(TEST_EVENT, nullptr, 0, "test");
        assert(count == 0);
        assert(loop.pending_count() == 1);
        loop.process_pending();
        assert(count == 1);
        assert(loop.pending_count() == 0);
        loop.off(h);
        std::cout << "PASS" << std::endl;
    }
    loop.reset();
    {
        std::cout << "test listener_count ... ";
        assert(loop.listener_count() == 0);
        auto h1 = loop.on(TEST_EVENT, [](const EventData&) {});
        auto h2 = loop.on(TEST_EVENT, [](const EventData&) {});
        assert(loop.listener_count() == 2);
        loop.off(h1);
        loop.off(h2);
        std::cout << "PASS" << std::endl;
    }
    loop.reset();
    {
        std::cout << "test reset ... ";
        loop.on(TEST_EVENT, [](const EventData&) {});
        loop.post_deferred(TEST_EVENT, nullptr, 0, "test");
        loop.reset();
        assert(loop.listener_count() == 0);
        assert(loop.pending_count() == 0);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All event_loop tests passed." << std::endl;
    return 0;
}
