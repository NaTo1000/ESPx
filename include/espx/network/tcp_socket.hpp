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
 * @enum SocketState
 * @brief TCP socket connection state.
 */
enum class SocketState {
    Closed,
    Connecting,
    Connected,
    Listening,
    Error
};

/**
 * @class TcpSocket
 * @brief TCP socket for reliable network communication.
 *
 * Provides both client and server TCP socket functionality
 * with asynchronous callbacks for data reception and
 * connection state changes.
 *
 * Example (client):
 * @code
 *   espx::network::TcpSocket client;
 *   client.on_data([](const std::vector<uint8_t>& data) {
 *       std::cout << "Received " << data.size() << " bytes" << std::endl;
 *   });
 *   client.connect("192.168.1.100", 8080);
 *   client.send({0x48, 0x65, 0x6C, 0x6C, 0x6F});
 * @endcode
 *
 * Example (server):
 * @code
 *   espx::network::TcpSocket server;
 *   server.on_connection([](TcpSocket& client_sock) {
 *       client_sock.on_data([](const std::vector<uint8_t>& data) {
 *           // Handle client data
 *       });
 *   });
 *   server.listen(8080);
 * @endcode
 */
class TcpSocket {
public:
    TcpSocket();
    ~TcpSocket();

    TcpSocket(const TcpSocket&) = delete;
    TcpSocket& operator=(const TcpSocket&) = delete;
    TcpSocket(TcpSocket&&) noexcept;
    TcpSocket& operator=(TcpSocket&&) noexcept;

    /**
     * @brief Connect to a remote host.
     * @param host Hostname or IP address
     * @param port Port number
     * @param timeout_ms Connection timeout in milliseconds
     * @return true if connection was initiated
     */
    bool connect(const std::string& host, uint16_t port,
                 uint32_t timeout_ms = 5000);

    /**
     * @brief Listen for incoming connections.
     * @param port Port to listen on
     * @param backlog Maximum pending connections
     * @return true if listening started
     */
    bool listen(uint16_t port, int backlog = 5);

    /**
     * @brief Send data over the socket.
     * @param data Data to send
     * @return Number of bytes sent, or -1 on error
     */
    int send(const std::vector<uint8_t>& data);

    /**
     * @brief Send a string over the socket.
     * @param data String to send
     * @return Number of bytes sent, or -1 on error
     */
    int send(const std::string& data);

    /**
     * @brief Close the socket.
     */
    void close();

    /**
     * @brief Get the current socket state.
     * @return Current state
     */
    [[nodiscard]] SocketState state() const;

    /**
     * @brief Check if the socket is connected.
     * @return true if connected
     */
    [[nodiscard]] bool is_connected() const;

    /**
     * @brief Get the remote IP address.
     * @return IP address string
     */
    [[nodiscard]] std::string remote_address() const;

    /**
     * @brief Get the remote port.
     * @return Port number
     */
    [[nodiscard]] uint16_t remote_port() const;

    /**
     * @brief Get the local port.
     * @return Port number
     */
    [[nodiscard]] uint16_t local_port() const;

    /// Register callback for received data
    void on_data(std::function<void(const std::vector<uint8_t>&)> callback);

    /// Register callback for new connections (server mode)
    void on_connection(std::function<void(TcpSocket&)> callback);

    /// Register callback for disconnect events
    void on_disconnect(std::function<void()> callback);

    /// Register callback for errors
    void on_error(std::function<void(int error_code, const std::string& message)> callback);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace network
}  // namespace espx
