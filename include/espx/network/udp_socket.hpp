// Copyright 2024 ESPx Contributors
// Licensed under the Apache License, Version 2.0

#pragma once

#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace espx {
namespace network {

/**
 * @struct UdpMessage
 * @brief A received UDP message with sender information.
 */
struct UdpMessage {
    std::vector<uint8_t> data;   ///< Message data
    std::string sender_ip;       ///< Sender's IP address
    uint16_t sender_port = 0;    ///< Sender's port
};

/**
 * @class UdpSocket
 * @brief UDP socket for connectionless datagram communication.
 *
 * Supports unicast, broadcast, and multicast UDP communication.
 *
 * Example:
 * @code
 *   espx::network::UdpSocket udp;
 *   udp.on_message([](const UdpMessage& msg) {
 *       std::cout << "From " << msg.sender_ip << ": "
 *                 << msg.data.size() << " bytes" << std::endl;
 *   });
 *   udp.bind(5000);
 *   udp.send_to("192.168.1.255", 5000, {0x01, 0x02, 0x03});
 * @endcode
 */
class UdpSocket {
public:
    UdpSocket();
    ~UdpSocket();

    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;

    /**
     * @brief Bind to a local port to receive datagrams.
     * @param port Local port number
     * @return true if binding succeeded
     */
    bool bind(uint16_t port);

    /**
     * @brief Send a datagram to a specific host.
     * @param host Destination hostname or IP
     * @param port Destination port
     * @param data Data to send
     * @return Number of bytes sent, or -1 on error
     */
    int send_to(const std::string& host, uint16_t port,
                const std::vector<uint8_t>& data);

    /**
     * @brief Send a string datagram.
     * @param host Destination hostname or IP
     * @param port Destination port
     * @param data String to send
     * @return Number of bytes sent, or -1 on error
     */
    int send_to(const std::string& host, uint16_t port,
                const std::string& data);

    /**
     * @brief Send a broadcast datagram.
     * @param port Destination port
     * @param data Data to send
     * @return Number of bytes sent, or -1 on error
     */
    int broadcast(uint16_t port, const std::vector<uint8_t>& data);

    /**
     * @brief Join a multicast group.
     * @param group_ip Multicast group IP address
     * @return true if joined successfully
     */
    bool join_multicast(const std::string& group_ip);

    /**
     * @brief Leave a multicast group.
     * @param group_ip Multicast group IP address
     */
    void leave_multicast(const std::string& group_ip);

    /**
     * @brief Close the socket.
     */
    void close();

    /**
     * @brief Check if the socket is bound.
     * @return true if bound to a port
     */
    [[nodiscard]] bool is_bound() const;

    /**
     * @brief Get the local port.
     * @return Port number (0 if not bound)
     */
    [[nodiscard]] uint16_t local_port() const;

    /// Register callback for received messages
    void on_message(std::function<void(const UdpMessage&)> callback);

    /// Register callback for errors
    void on_error(std::function<void(int error_code, const std::string& message)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace network
}  // namespace espx
