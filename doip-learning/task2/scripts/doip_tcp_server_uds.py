#!/usr/bin/env python3
"""Task 2 DoIP TCP server with real UDS handling (0x10 / 0x22 / NRC)."""

from __future__ import annotations

import argparse
import socket
import threading

import _import_path  # noqa: F401
from doip_common import (
    DOIP_PORT,
    PAYLOAD_ALIVE_CHECK_REQUEST,
    PAYLOAD_DIAGNOSTIC_MESSAGE,
    PAYLOAD_ROUTING_ACTIVATION_REQUEST,
    DoIPHeader,
    build_alive_check_response,
    build_diagnostic_message,
    build_diagnostic_positive_ack,
    build_routing_activation_response,
    hexdump,
    payload_type_name,
)
from uds_ecu import UdsEcu

DEFAULT_BIND = "0.0.0.0"
DEFAULT_LOGICAL_ADDRESS = 0x0E00
ALLOWED_TESTER_ADDRESS = 0x0E80


def handle_routing_activation(header: DoIPHeader) -> bytes:
    source_address = int.from_bytes(header.payload[0:2], "big")
    activation_type = header.payload[2]
    print(
        f"[TCP] Routing Activation: tester=0x{source_address:04X}, "
        f"type=0x{activation_type:02X}"
    )
    if source_address != ALLOWED_TESTER_ADDRESS:
        print(f"[TCP] Rejecting unknown tester address 0x{source_address:04X}")
        return build_routing_activation_response(
            client_logical_address=source_address,
            logical_address=DEFAULT_LOGICAL_ADDRESS,
            response_code=0x00,
        )
    return build_routing_activation_response(
        client_logical_address=source_address,
        logical_address=DEFAULT_LOGICAL_ADDRESS,
        response_code=0x10,
    )


def handle_diagnostic_message(header: DoIPHeader, ecu: UdsEcu) -> list[bytes]:
    source_address = int.from_bytes(header.payload[0:2], "big")
    target_address = int.from_bytes(header.payload[2:4], "big")
    uds_request = header.payload[4:]

    print(
        f"[TCP] UDS request from 0x{source_address:04X}: {hexdump(uds_request)}"
    )

    uds_response = ecu.handle(uds_request)
    print(f"[TCP] UDS response: {hexdump(uds_response)} ({ecu.describe_response(uds_response)})")

    ack = build_diagnostic_positive_ack(
        source_address=DEFAULT_LOGICAL_ADDRESS,
        target_address=source_address,
        ack_code=0x00,
        previous_diagnostic_message=uds_request,
    )
    uds_message = build_diagnostic_message(
        source_address=DEFAULT_LOGICAL_ADDRESS,
        target_address=source_address,
        uds_payload=uds_response,
    )
    return [ack, uds_message]


def handle_client(conn: socket.socket, addr: tuple[str, int]) -> None:
    ecu = UdsEcu()
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
                    responses = [handle_routing_activation(header)]
                elif header.payload_type == PAYLOAD_DIAGNOSTIC_MESSAGE:
                    responses = handle_diagnostic_message(header, ecu)
                elif header.payload_type == PAYLOAD_ALIVE_CHECK_REQUEST:
                    responses = [build_alive_check_response(DEFAULT_LOGICAL_ADDRESS)]
                    print("[TCP] Alive Check Request -> Response")
                else:
                    print(
                        f"[TCP] Unsupported payload type: "
                        f"0x{header.payload_type:04X}"
                    )
                    continue

                for response in responses:
                    conn.sendall(response)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 2 DoIP TCP server with UDS")
    parser.add_argument("--bind", default=DEFAULT_BIND)
    parser.add_argument("--port", type=int, default=DOIP_PORT)
    args = parser.parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((args.bind, args.port))
    server.listen(5)

    print(f"[TCP] Task 2 UDS server on {args.bind}:{args.port}")
    print("[TCP] Supported UDS: 0x10 (session), 0x22 (read DID)")
    print("[TCP] Demo DIDs: F190 VIN, F186 session, F187 part no. (extended only)")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True,
            ).start()
    except KeyboardInterrupt:
        print("\n[TCP] Stopped")
    finally:
        server.close()


if __name__ == "__main__":
    main()
