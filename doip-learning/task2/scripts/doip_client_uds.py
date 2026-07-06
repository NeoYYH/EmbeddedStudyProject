#!/usr/bin/env python3
"""Task 2 client: discovery -> activation -> UDS 0x10/0x22 + NRC demos."""

from __future__ import annotations

import argparse
import socket
import time

import _import_path  # noqa: F401
from doip_common import (
    DOIP_PORT,
    PAYLOAD_DIAGNOSTIC_MESSAGE,
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


def send_uds_and_print(
    sock: socket.socket,
    title: str,
    uds_payload: bytes,
    expect_positive: bool = True,
) -> DoIPHeader:
    print(f"\n=== {title} ===")
    print(f"TX UDS: {hexdump(uds_payload)}")
    diagnostic = build_diagnostic_message(
        source_address=TESTER_ADDRESS,
        target_address=ECU_ADDRESS,
        uds_payload=uds_payload,
    )
    sock.sendall(diagnostic)

    ack = recv_doip_message(sock)
    print(f"RX -> {payload_type_name(ack.payload_type)}")
    if ack.payload_type != PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK:
        raise RuntimeError("Expected 0x8002 positive ack")

    response = recv_doip_message(sock)
    print(f"RX -> {payload_type_name(response.payload_type)}")
    uds_response = response.payload[4:]
    print(f"RX UDS: {hexdump(uds_response)}")

    is_positive = bool(uds_response) and uds_response[0] != 0x7F
    if expect_positive and not is_positive:
        raise RuntimeError(f"Expected positive UDS response, got {hexdump(uds_response)}")
    if not expect_positive and is_positive:
        raise RuntimeError(f"Expected NRC, got positive {hexdump(uds_response)}")
    if not expect_positive:
        print(
            f"NRC as expected: service=0x{uds_response[1]:02X}, "
            f"code=0x{uds_response[2]:02X}"
        )
    return response


def udp_discovery(host: str, port: int) -> None:
    print(f"\n=== Step 1: UDP Vehicle Discovery ({host}:{port}) ===")
    request = build_vehicle_identification_request()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3.0)
        sock.sendto(request, (host, port))
        data, addr = sock.recvfrom(4096)
    header, _ = DoIPHeader.decode(data)
    if header.payload_type != PAYLOAD_VEHICLE_IDENTIFICATION_RESPONSE:
        raise RuntimeError("Expected Vehicle Identification Response")
    vin = header.payload[:17].decode("ascii", errors="replace")
    print(f"VIN={vin}")


def run_task2_flow(host: str, port: int) -> None:
    print(f"\n=== Step 2: TCP Routing Activation ({host}:{port}) ===")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(build_routing_activation_request(source_address=TESTER_ADDRESS))
        header = recv_doip_message(sock)
        if header.payload_type != PAYLOAD_ROUTING_ACTIVATION_RESPONSE:
            raise RuntimeError("Routing activation failed")
        print(f"Routing activated, code=0x{header.payload[4]:02X}")

        send_uds_and_print(sock, "UDS 0x10 0x01 Default Session", bytes([0x10, 0x01]))
        send_uds_and_print(sock, "UDS 0x22 F190 Read VIN", bytes([0x22, 0xF1, 0x90]))
        send_uds_and_print(sock, "UDS 0x22 F186 Read Active Session", bytes([0x22, 0xF1, 0x86]))
        send_uds_and_print(
            sock,
            "UDS 0x22 F187 Read Part Number (expect NRC 0x22)",
            bytes([0x22, 0xF1, 0x87]),
            expect_positive=False,
        )
        send_uds_and_print(sock, "UDS 0x10 0x03 Extended Session", bytes([0x10, 0x03]))
        send_uds_and_print(sock, "UDS 0x22 F187 Read Part Number (now OK)", bytes([0x22, 0xF1, 0x87]))
        send_uds_and_print(
            sock,
            "UDS 0x22 FFFF Unknown DID (expect NRC 0x31)",
            bytes([0x22, 0xFF, 0xFF]),
            expect_positive=False,
        )
        send_uds_and_print(
            sock,
            "UDS 0x99 Unsupported Service (expect NRC 0x11)",
            bytes([0x99, 0x00]),
            expect_positive=False,
        )

    print("\nTask 2 client flow completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 2 DoIP + UDS client")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DOIP_PORT)
    parser.add_argument("--skip-discovery", action="store_true")
    args = parser.parse_args()

    if not args.skip_discovery:
        udp_discovery(args.host, args.port)
        time.sleep(0.3)
    run_task2_flow(args.host, args.port)


if __name__ == "__main__":
    main()
