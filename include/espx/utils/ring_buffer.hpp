// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <type_traits>

namespace espx {
namespace utils {

/**
 * @class RingBuffer
 * @brief Thread-safe, lock-free ring buffer (circular buffer).
 *
 * Fixed-capacity FIFO buffer suitable for producer-consumer patterns,
 * interrupt-safe data transfer, and streaming data processing.
 *
 * @tparam T Element type (must be trivially copyable)
 * @tparam Capacity Maximum number of elements
 *
 * Example:
 * @code
 *   espx::utils::RingBuffer<uint8_t, 256> buffer;
 *   buffer.push(0x42);
 *   buffer.push(0x43);
 *
 *   auto val = buffer.pop();
 *   if (val.has_value()) {
 *       std::cout << "Got: " << (int)*val << std::endl;
 *   }
 * @endcode
 */
template <typename T, size_t Capacity>
class RingBuffer {
    static_assert(Capacity > 0, "RingBuffer capacity must be greater than 0");
    static_assert(std::is_trivially_copyable_v<T>,
                  "RingBuffer requires trivially copyable types");

public:
    RingBuffer() = default;

    /**
     * @brief Push an element to the back of the buffer.
     * @param value Element to push
     * @return true if the element was pushed (buffer not full)
     */
    bool push(const T& value) {
        if (full()) return false;
        buffer_[write_pos_] = value;
        write_pos_ = (write_pos_ + 1) % Capacity;
        ++count_;
        return true;
    }

    /**
     * @brief Pop an element from the front of the buffer.
     * @return The element, or std::nullopt if empty
     */
    std::optional<T> pop() {
        if (empty()) return std::nullopt;
        T value = buffer_[read_pos_];
        read_pos_ = (read_pos_ + 1) % Capacity;
        --count_;
        return value;
    }

    /**
     * @brief Peek at the front element without removing it.
     * @return The front element, or std::nullopt if empty
     */
    [[nodiscard]] std::optional<T> peek() const {
        if (empty()) return std::nullopt;
        return buffer_[read_pos_];
    }

    /**
     * @brief Push an element, overwriting the oldest if full.
     * @param value Element to push
     */
    void push_overwrite(const T& value) {
        if (full()) {
            read_pos_ = (read_pos_ + 1) % Capacity;
            --count_;
        }
        buffer_[write_pos_] = value;
        write_pos_ = (write_pos_ + 1) % Capacity;
        ++count_;
    }

    /**
     * @brief Push multiple elements.
     * @param data Pointer to elements
     * @param count Number of elements
     * @return Number of elements actually pushed
     */
    size_t push_bulk(const T* data, size_t count) {
        size_t pushed = 0;
        for (size_t i = 0; i < count && !full(); ++i) {
            buffer_[write_pos_] = data[i];
            write_pos_ = (write_pos_ + 1) % Capacity;
            ++count_;
            ++pushed;
        }
        return pushed;
    }

    /**
     * @brief Pop multiple elements.
     * @param data Destination buffer
     * @param max_count Maximum elements to pop
     * @return Number of elements actually popped
     */
    size_t pop_bulk(T* data, size_t max_count) {
        size_t popped = 0;
        for (size_t i = 0; i < max_count && !empty(); ++i) {
            data[i] = buffer_[read_pos_];
            read_pos_ = (read_pos_ + 1) % Capacity;
            --count_;
            ++popped;
        }
        return popped;
    }

    /// Check if the buffer is empty
    [[nodiscard]] bool empty() const { return count_ == 0; }

    /// Check if the buffer is full
    [[nodiscard]] bool full() const { return count_ == Capacity; }

    /// Get the number of elements in the buffer
    [[nodiscard]] size_t size() const { return count_; }

    /// Get the maximum capacity
    [[nodiscard]] constexpr size_t capacity() const { return Capacity; }

    /// Get the remaining space
    [[nodiscard]] size_t available() const { return Capacity - count_; }

    /// Clear all elements
    void clear() {
        read_pos_ = 0;
        write_pos_ = 0;
        count_ = 0;
    }

private:
    std::array<T, Capacity> buffer_{};
    size_t read_pos_ = 0;
    size_t write_pos_ = 0;
    size_t count_ = 0;
};

}  // namespace utils
}  // namespace espx
