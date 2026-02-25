// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#include "espx/core/event_loop.hpp"

#include <algorithm>
#include <cstring>
#include <map>
#include <mutex>
#include <queue>
#include <vector>

namespace espx {
namespace core {

struct EventLoop::Impl {
    struct Listener {
        ListenerHandle handle;
        EventHandler handler;
        bool once;
    };

    struct DeferredEvent {
        EventId id;
        std::vector<uint8_t> data;
        std::string source_tag;
    };

    std::map<EventId, std::vector<Listener>> listeners;
    std::vector<Listener> any_listeners;
    std::queue<DeferredEvent> deferred_queue;
    ListenerHandle next_handle{1};
    std::mutex mutex;

    void dispatch(const EventData& event) {
        // Collect handlers to invoke (copy to allow mutation during dispatch)
        std::vector<EventHandler> to_call;
        std::vector<ListenerHandle> to_remove;

        auto it = listeners.find(event.id);
        if (it != listeners.end()) {
            for (auto& listener : it->second) {
                to_call.push_back(listener.handler);
                if (listener.once) {
                    to_remove.push_back(listener.handle);
                }
            }
        }

        for (auto& listener : any_listeners) {
            to_call.push_back(listener.handler);
            if (listener.once) {
                to_remove.push_back(listener.handle);
            }
        }

        // Remove once-listeners before invoking (so re-entrant posts work)
        for (auto h : to_remove) {
            remove_listener(h);
        }

        // Invoke outside the critical path (mutex already held by caller)
        for (auto& fn : to_call) {
            fn(event);
        }
    }

    void remove_listener(ListenerHandle handle) {
        for (auto& kv : listeners) {
            auto& vec = kv.second;
            vec.erase(std::remove_if(vec.begin(), vec.end(),
                                     [handle](const Listener& l) {
                                         return l.handle == handle;
                                     }),
                      vec.end());
        }
        any_listeners.erase(
            std::remove_if(any_listeners.begin(), any_listeners.end(),
                           [handle](const Listener& l) {
                               return l.handle == handle;
                           }),
            any_listeners.end());
    }
};

EventLoop::EventLoop() : impl_(std::make_unique<Impl>()) {}
EventLoop::~EventLoop() = default;

EventLoop& EventLoop::instance() {
    static EventLoop inst;
    return inst;
}

ListenerHandle EventLoop::on(EventId event_id, EventHandler handler) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    ListenerHandle h = impl_->next_handle++;
    impl_->listeners[event_id].push_back({h, std::move(handler), false});
    return h;
}

ListenerHandle EventLoop::once(EventId event_id, EventHandler handler) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    ListenerHandle h = impl_->next_handle++;
    impl_->listeners[event_id].push_back({h, std::move(handler), true});
    return h;
}

ListenerHandle EventLoop::on_any(EventHandler handler) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    ListenerHandle h = impl_->next_handle++;
    impl_->any_listeners.push_back({h, std::move(handler), false});
    return h;
}

void EventLoop::off(ListenerHandle handle) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->remove_listener(handle);
}

void EventLoop::post(EventId event_id, const void* data, size_t data_size,
                     const char* source_tag) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    EventData event{event_id, data, data_size, source_tag};
    impl_->dispatch(event);
}

void EventLoop::post_deferred(EventId event_id, const void* data,
                              size_t data_size, const char* source_tag) {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    Impl::DeferredEvent de;
    de.id = event_id;
    if (data && data_size > 0) {
        const auto* bytes = static_cast<const uint8_t*>(data);
        de.data.assign(bytes, bytes + data_size);
    }
    de.source_tag = source_tag ? source_tag : "";
    impl_->deferred_queue.push(std::move(de));
}

void EventLoop::process_pending() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    while (!impl_->deferred_queue.empty()) {
        auto de = std::move(impl_->deferred_queue.front());
        impl_->deferred_queue.pop();

        const void* data_ptr = de.data.empty() ? nullptr : de.data.data();
        EventData event{de.id, data_ptr, de.data.size(),
                        de.source_tag.c_str()};
        impl_->dispatch(event);
    }
}

size_t EventLoop::pending_count() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    return impl_->deferred_queue.size();
}

size_t EventLoop::listener_count() const {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    size_t count = impl_->any_listeners.size();
    for (auto& kv : impl_->listeners) {
        count += kv.second.size();
    }
    return count;
}

void EventLoop::reset() {
    std::lock_guard<std::mutex> lock(impl_->mutex);
    impl_->listeners.clear();
    impl_->any_listeners.clear();
    while (!impl_->deferred_queue.empty()) {
        impl_->deferred_queue.pop();
    }
}

}  // namespace core
}  // namespace espx
