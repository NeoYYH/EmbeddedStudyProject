#!/usr/bin/env python3
"""DoIP UDP discovery server for Task 1.1 Wireshark practice."""

from __future__ import annotations

import argparse
import socket

from doip_common import (
    DOIP_PORT,
    PAYLOAD_VEHICLE_IDENTIFICATION_REQUEST,
    build_vehicle_identification_response,
    payload_type_name,
)

DEFAULT_BIND = "0.0.0.0"
DEFAULT_VIN = "WVWZZZ1KZAW000000"
DEFAULT_LOGICAL_ADDRESS = 0x0E00


def handle_datagram(data: bytes, addr: tuple[str, int], sock: socket.socket) -> None:
    if len(data) < 8:
        print(f"[UDP] Short packet from {addr[0]}:{addr[1]} ({len(data)} bytes)")
        return

    payload_type = int.from_bytes(data[2:4], "big")
    print(
        f"[UDP] {addr[0]}:{addr[1]} -> {payload_type_name(payload_type)} "
        f"({len(data)} bytes)"
    )

    if payload_type != PAYLOAD_VEHICLE_IDENTIFICATION_REQUEST:
        print("[UDP] Ignored: not a Vehicle Identification Request (0x0001)")
        return

    response = build_vehicle_identification_response(
        vin=DEFAULT_VIN,
        logical_address=DEFAULT_LOGICAL_ADDRESS,
    )
    sock.sendto(response, addr)
    print(f"[UDP] Sent Vehicle Identification Response to {addr[0]}:{addr[1]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal DoIP UDP discovery server")
    parser.add_argument("--bind", default=DEFAULT_BIND, help="Bind address")
    parser.add_argument("--port", type=int, default=DOIP_PORT, help="UDP port")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.bind, args.port))

    print(f"[UDP] Listening on {args.bind}:{args.port}")
    print("[UDP] Waiting for Vehicle Identification Request (0x0001)...")

    try:
        while True:
            data, addr = sock.recvfrom(4096)
            handle_datagram(data, addr, sock)
    except KeyboardInterrupt:
        print("\n[UDP] Stopped")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
