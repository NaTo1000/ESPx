#include <cassert>
#include <iostream>
#include "espx/utils/ring_buffer.hpp"

using espx::utils::RingBuffer;

int main() {
    {
        std::cout << "test push/pop basic ... ";
        RingBuffer<int, 4> rb;
        assert(rb.push(1));
        assert(rb.push(2));
        assert(rb.push(3));
        auto v = rb.pop();
        assert(v.has_value() && *v == 1);
        v = rb.pop();
        assert(v.has_value() && *v == 2);
        v = rb.pop();
        assert(v.has_value() && *v == 3);
        assert(!rb.pop().has_value());
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test empty/full ... ";
        RingBuffer<int, 2> rb;
        assert(rb.empty());
        assert(!rb.full());
        rb.push(1);
        rb.push(2);
        assert(rb.full());
        assert(!rb.empty());
        assert(!rb.push(3));
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test push_overwrite ... ";
        RingBuffer<int, 3> rb;
        rb.push(1);
        rb.push(2);
        rb.push(3);
        rb.push_overwrite(4);
        assert(rb.size() == 3);
        auto v = rb.pop();
        assert(v.has_value() && *v == 2);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test peek ... ";
        RingBuffer<int, 4> rb;
        assert(!rb.peek().has_value());
        rb.push(42);
        auto v = rb.peek();
        assert(v.has_value() && *v == 42);
        assert(rb.size() == 1);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test clear ... ";
        RingBuffer<int, 4> rb;
        rb.push(1);
        rb.push(2);
        rb.clear();
        assert(rb.empty());
        assert(rb.size() == 0);
        std::cout << "PASS" << std::endl;
    }
    {
        std::cout << "test capacity/size/available ... ";
        RingBuffer<int, 8> rb;
        assert(rb.capacity() == 8);
        assert(rb.size() == 0);
        assert(rb.available() == 8);
        rb.push(1);
        rb.push(2);
        assert(rb.size() == 2);
        assert(rb.available() == 6);
        std::cout << "PASS" << std::endl;
    }
    std::cout << "All ring_buffer tests passed." << std::endl;
    return 0;
}
