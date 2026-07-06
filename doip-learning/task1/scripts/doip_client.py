#!/usr/bin/env python3
"""DoIP client: UDP discovery -> TCP routing activation -> sample UDS request."""

from __future__ import annotations

import argparse
import socket
import time

from doip_common import (
    DOIP_PORT,
    PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK,
    PAYLOAD_ROUTING_ACTIVATION_RESPONSE,
    PAYLOAD_VEHICLE_IDENTIFICATION_RESPONSE,
    DoIPHeader,
    build_diagnostic_message,
    build_routing_activation_request,
    build_vehicle_identification_request,
    hexdump,
    payload_type_name,
)

DEFAULT_HOST = "127.0.0.1"
TESTER_ADDRESS = 0x0E80
ECU_ADDRESS = 0x0E00


def recv_doip_message(sock: socket.socket, timeout: float = 5.0) -> DoIPHeader:
    sock.settimeout(timeout)
    buffer = b""

    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed before DoIP response")

        buffer += chunk
        header, _ = DoIPHeader.decode(buffer)
        return header


def udp_discovery(host: str, port: int) -> None:
    print(f"\n=== Step 1: UDP Vehicle Discovery ({host}:{port}) ===")
    request = build_vehicle_identification_request()
    print(f"TX: {hexdump(request)}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3.0)
        sock.sendto(request, (host, port))
        data, addr = sock.recvfrom(4096)

    header, _ = DoIPHeader.decode(data)
    print(f"RX from {addr[0]}:{addr[1]} -> {payload_type_name(header.payload_type)}")
    print(f"RX: {hexdump(data)}")

    if header.payload_type != PAYLOAD_VEHICLE_IDENTIFICATION_RESPONSE:
        raise RuntimeError("Expected Vehicle Identification Response (0x0002)")

    vin = header.payload[:17].decode("ascii", errors="replace")
    logical_address = int.from_bytes(header.payload[17:19], "big")
    print(f"VIN={vin}, LogicalAddress=0x{logical_address:04X}")


def tcp_session(host: str, port: int) -> None:
    print(f"\n=== Step 2: TCP Routing Activation ({host}:{port}) ===")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print("[TCP] Connecting (observe 3-way handshake in Wireshark)...")
        sock.connect((host, port))

        activation = build_routing_activation_request(source_address=TESTER_ADDRESS)
        print(f"TX Routing Activation: {hexdump(activation)}")
        sock.sendall(activation)

        header = recv_doip_message(sock)
        print(f"RX -> {payload_type_name(header.payload_type)}")
        print(f"RX: {hexdump(header.encode())}")

        if header.payload_type != PAYLOAD_ROUTING_ACTIVATION_RESPONSE:
            raise RuntimeError("Expected Routing Activation Response (0x0006)")

        response_code = header.payload[4]
        print(f"Routing Activation response code: 0x{response_code:02X}")

        print("\n=== Step 3: Diagnostic Message with UDS 0x10 0x01 ===")
        uds_payload = bytes([0x10, 0x01])
        diagnostic = build_diagnostic_message(
            source_address=TESTER_ADDRESS,
            target_address=ECU_ADDRESS,
            uds_payload=uds_payload,
        )
        print(f"TX Diagnostic Message: {hexdump(diagnostic)}")
        sock.sendall(diagnostic)

        header = recv_doip_message(sock)
        print(f"RX -> {payload_type_name(header.payload_type)}")
        print(f"RX: {hexdump(header.encode())}")

        if header.payload_type != PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK:
            raise RuntimeError("Expected Diagnostic Message Positive Ack (0x8002)")

        print("\nTask 1 client flow completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal DoIP client for Task 1")
    parser.add_argument("--host", default=DEFAULT_HOST, help="ECU / server host")
    parser.add_argument("--port", type=int, default=DOIP_PORT, help="DoIP port")
    parser.add_argument(
        "--skip-discovery",
        action="store_true",
        help="Skip UDP discovery and only run TCP flow",
    )
    args = parser.parse_args()

    if not args.skip_discovery:
        udp_discovery(args.host, args.port)
        time.sleep(0.5)

    tcp_session(args.host, args.port)


if __name__ == "__main__":
    main()
