#!/usr/bin/env python3
"""Task 3 client: fault injection — bad address, alive check, reconnect."""

from __future__ import annotations

import argparse
import socket
import time

import _import_path  # noqa: F401
from doip_common import (
    DOIP_PORT,
    PAYLOAD_ALIVE_CHECK_RESPONSE,
    PAYLOAD_DIAGNOSTIC_MESSAGE,
    PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK,
    PAYLOAD_ROUTING_ACTIVATION_RESPONSE,
    DoIPHeader,
    build_alive_check_request,
    build_diagnostic_message,
    build_routing_activation_request,
    hexdump,
    payload_type_name,
)

DEFAULT_HOST = "127.0.0.1"
VALID_TESTER = 0x0E80
BAD_TESTER = 0x1234
ECU_ADDRESS = 0x0E00


def recv_doip(sock: socket.socket, timeout: float = 5.0) -> DoIPHeader:
    sock.settimeout(timeout)
    buffer = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Connection closed")
        buffer += chunk
        header, _ = DoIPHeader.decode(buffer)
        return header


def test_bad_routing_address(host: str, port: int) -> None:
    print("\n=== Task 3.1a: Wrong Source Address (expect reject 0x00) ===")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(build_routing_activation_request(source_address=BAD_TESTER))
        header = recv_doip(sock)
        if header.payload_type != PAYLOAD_ROUTING_ACTIVATION_RESPONSE:
            raise RuntimeError("Expected routing activation response")
        code = header.payload[4]
        print(f"Response code: 0x{code:02X}")
        if code != 0x00:
            raise RuntimeError(f"Expected 0x00 (denied), got 0x{code:02X}")
    print("PASS: invalid source address rejected")


def activate(sock: socket.socket, tester: int = VALID_TESTER) -> None:
    sock.sendall(build_routing_activation_request(source_address=tester))
    header = recv_doip(sock)
    if header.payload_type != PAYLOAD_ROUTING_ACTIVATION_RESPONSE:
        raise RuntimeError("No routing activation response")
    if header.payload[4] != 0x10:
        raise RuntimeError(f"Activation failed: 0x{header.payload[4]:02X}")


def test_alive_check(host: str, port: int) -> None:
    print("\n=== Task 3.1b: Alive Check Request/Response ===")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        activate(sock)
        sock.sendall(build_alive_check_request())
        header = recv_doip(sock)
        print(f"RX -> {payload_type_name(header.payload_type)}")
        if header.payload_type != PAYLOAD_ALIVE_CHECK_RESPONSE:
            raise RuntimeError("Expected Alive Check Response 0x0008")
        addr = int.from_bytes(header.payload[0:2], "big")
        print(f"ECU logical address in response: 0x{addr:04X}")
    print("PASS: alive check OK")


def test_reconnect(host: str, port: int) -> None:
    print("\n=== Task 3.1c: TCP Disconnect and Reconnect ===")
    for attempt in (1, 2):
        print(f"--- Connection attempt {attempt} ---")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            activate(sock)
            uds = bytes([0x10, 0x01])
            sock.sendall(
                build_diagnostic_message(VALID_TESTER, ECU_ADDRESS, uds)
            )
            ack = recv_doip(sock)
            if ack.payload_type != PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK:
                raise RuntimeError("Expected 0x8002 ack")
            resp = recv_doip(sock)
            if resp.payload_type != PAYLOAD_DIAGNOSTIC_MESSAGE:
                raise RuntimeError("Expected 0x8001 UDS response")
            print(f"UDS response: {hexdump(resp.payload[4:])}")
        print(f"Connection {attempt} closed")
        time.sleep(0.3)
    print("PASS: reconnect after disconnect OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Task 3 fault scenario client")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DOIP_PORT)
    args = parser.parse_args()

    test_bad_routing_address(args.host, args.port)
    test_alive_check(args.host, args.port)
    test_reconnect(args.host, args.port)
    print("\nTask 3 client flow completed successfully.")


if __name__ == "__main__":
    main()
