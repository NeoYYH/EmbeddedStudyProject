#!/usr/bin/env python3
"""Quick unit checks for Task 2 UDS ECU logic."""

from uds_ecu import UdsEcu


def test_session_and_did_flow() -> None:
    ecu = UdsEcu()

    resp = ecu.handle(bytes([0x10, 0x01]))
    assert resp[0] == 0x50 and resp[1] == 0x01

    resp = ecu.handle(bytes([0x22, 0xF1, 0x90]))
    assert resp[0] == 0x62 and b"WVW" in resp

    resp = ecu.handle(bytes([0x22, 0xF1, 0x87]))
    assert resp == bytes([0x7F, 0x22, 0x22])

    resp = ecu.handle(bytes([0x10, 0x03]))
    assert resp[0] == 0x50 and resp[1] == 0x03

    resp = ecu.handle(bytes([0x22, 0xF1, 0x87]))
    assert resp[0] == 0x62

    resp = ecu.handle(bytes([0x22, 0xFF, 0xFF]))
    assert resp == bytes([0x7F, 0x22, 0x31])

    resp = ecu.handle(bytes([0x99]))
    assert resp == bytes([0x7F, 0x99, 0x11])

    print("uds_ecu tests passed")


if __name__ == "__main__":
    test_session_and_did_flow()
