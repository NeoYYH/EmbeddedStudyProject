#!/usr/bin/env python3
"""DoIP TCP server: routing activation + diagnostic message handling."""

from __future__ import annotations

import argparse
import socket
import threading

from doip_common import (
    DOIP_PORT,
    PAYLOAD_ALIVE_CHECK_REQUEST,
    PAYLOAD_DIAGNOSTIC_MESSAGE,
    PAYLOAD_ROUTING_ACTIVATION_REQUEST,
    DoIPHeader,
    build_alive_check_response,
    build_diagnostic_positive_ack,
    build_routing_activation_response,
    hexdump,
    payload_type_name,
)

DEFAULT_BIND = "0.0.0.0"
DEFAULT_LOGICAL_ADDRESS = 0x0E00
TESTER_ADDRESS = 0x0E80


def handle_routing_activation(header: DoIPHeader) -> bytes:
    if len(header.payload) < 7:
        raise ValueError("Routing Activation Request payload too short")

    source_address = int.from_bytes(header.payload[0:2], "big")
    activation_type = header.payload[2]
    print(
        f"[TCP] Routing Activation: tester=0x{source_address:04X}, "
        f"type=0x{activation_type:02X}"
    )
    return build_routing_activation_response(
        client_logical_address=source_address,
        logical_address=DEFAULT_LOGICAL_ADDRESS,
        response_code=0x10,
    )


def handle_diagnostic_message(header: DoIPHeader) -> bytes:
    if len(header.payload) < 4:
        raise ValueError("Diagnostic Message payload too short")

    source_address = int.from_bytes(header.payload[0:2], "big")
    target_address = int.from_bytes(header.payload[2:4], "big")
    uds_payload = header.payload[4:]

    print(
        f"[TCP] Diagnostic Message: src=0x{source_address:04X}, "
        f"dst=0x{target_address:04X}, UDS={hexdump(uds_payload)}"
    )

    # Task 1 only needs to observe encapsulation; full UDS logic comes in Week 2.
    return build_diagnostic_positive_ack(
        source_address=DEFAULT_LOGICAL_ADDRESS,
        target_address=source_address,
        ack_code=0x00,
        previous_diagnostic_message=uds_payload,
    )


def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    print(f"[TCP] Client connected: {addr[0]}:{addr[1]}")
    buffer = b""

    try:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                print(f"[TCP] Client disconnected: {addr[0]}:{addr[1]}")
                break

            buffer += chunk

            while buffer:
                try:
                    header, remainder = DoIPHeader.decode(buffer)
                except ValueError:
                    break

                buffer = remainder
                print(f"[TCP] Received {payload_type_name(header.payload_type)}")

                if header.payload_type == PAYLOAD_ROUTING_ACTIVATION_REQUEST:
                    response = handle_routing_activation(header)
                elif header.payload_type == PAYLOAD_DIAGNOSTIC_MESSAGE:
                    response = handle_diagnostic_message(header)
                elif header.payload_type == PAYLOAD_ALIVE_CHECK_REQUEST:
                    response = build_alive_check_response(DEFAULT_LOGICAL_ADDRESS)
                    print("[TCP] Alive Check Request -> Response")
                else:
                    print(
                        f"[TCP] Unsupported payload type: "
                        f"0x{header.payload_type:04X}"
                    )
                    continue

                conn.sendall(response)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal DoIP TCP server")
    parser.add_argument("--bind", default=DEFAULT_BIND, help="Bind address")
    parser.add_argument("--port", type=int, default=DOIP_PORT, help="TCP port")
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.bind, args.port))
    server.listen(5)

    print(f"[TCP] Listening on {args.bind}:{args.port}")
    print("[TCP] Expect Routing Activation (0x0005) after TCP handshake")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n[TCP] Stopped")
    finally:
        server.close()


if __name__ == "__main__":
    main()
