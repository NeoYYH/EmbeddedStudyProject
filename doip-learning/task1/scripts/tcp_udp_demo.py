#!/usr/bin/env python3
"""Side-by-side TCP vs UDP demo for Task 1.1 transport comparison."""

from __future__ import annotations

import argparse
import socket
import threading
import time


def run_udp_server(bind: str, port: int, stop_event: threading.Event) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((bind, port))
    sock.settimeout(1.0)

    print(f"[UDP server] Listening on {bind}:{port}")
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            print(f"[UDP server] RX from {addr}: {data!r} (no handshake)")
            sock.sendto(b"UDP-ACK:" + data, addr)
        except socket.timeout:
            continue
    sock.close()


def run_tcp_server(bind: str, port: int, stop_event: threading.Event) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((bind, port))
    server.listen(1)
    server.settimeout(1.0)

    print(f"[TCP server] Listening on {bind}:{port}")
    while not stop_event.is_set():
        try:
            conn, addr = server.accept()
        except socket.timeout:
            continue

        print(f"[TCP server] Accepted {addr} after 3-way handshake")
        data = conn.recv(1024)
        print(f"[TCP server] RX: {data!r}")
        conn.sendall(b"TCP-ACK:" + data)
        conn.close()

    server.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="TCP vs UDP transport demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--udp-port", type=int, default=13401)
    parser.add_argument("--tcp-port", type=int, default=13402)
    args = parser.parse_args()

    stop_event = threading.Event()
    udp_thread = threading.Thread(
        target=run_udp_server,
        args=(args.host, args.udp_port, stop_event),
        daemon=True,
    )
    tcp_thread = threading.Thread(
        target=run_tcp_server,
        args=(args.host, args.tcp_port, stop_event),
        daemon=True,
    )

    udp_thread.start()
    tcp_thread.start()
    time.sleep(0.3)

    print("\n--- UDP client: one datagram out, one datagram back ---")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.settimeout(2.0)
        udp_sock.sendto(b"HELLO-UDP", (args.host, args.udp_port))
        print(f"[UDP client] TX HELLO-UDP -> {args.host}:{args.udp_port}")
        response = udp_sock.recv(1024)
        print(f"[UDP client] RX {response!r}")

    print("\n--- TCP client: connect handshake, then payload ---")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        print(f"[TCP client] Connecting to {args.host}:{args.tcp_port}")
        tcp_sock.connect((args.host, args.tcp_port))
        tcp_sock.sendall(b"HELLO-TCP")
        print("[TCP client] TX HELLO-TCP after handshake")
        response = tcp_sock.recv(1024)
        print(f"[TCP client] RX {response!r}")

    stop_event.set()
    udp_thread.join(timeout=2)
    tcp_thread.join(timeout=2)
    print("\nCapture this run in Wireshark with filter: tcp.port==13402 or udp.port==13401")


if __name__ == "__main__":
    main()
