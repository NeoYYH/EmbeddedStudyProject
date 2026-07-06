"""Minimal UDS ECU logic for Task 2 (mirrors familiar CAN UDS behavior)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

SESSION_DEFAULT = 0x01
SESSION_PROGRAMMING = 0x02
SESSION_EXTENDED = 0x03

NRC_GENERAL_REJECT = 0x10
NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUB_FUNCTION_NOT_SUPPORTED = 0x12
NRC_INCORRECT_MESSAGE_LENGTH = 0x13
NRC_CONDITIONS_NOT_CORRECT = 0x22
NRC_REQUEST_OUT_OF_RANGE = 0x31

# P2 / P2* in ms encoded as 2-byte big-endian values in 0x10 responses
P2_DEFAULT_MS = 50
P2_STAR_DEFAULT_MS = 500


@dataclass
class UdsEcuState:
    active_session: int = SESSION_DEFAULT
    security_unlocked: bool = False
    did_database: Dict[int, bytes] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.did_database:
            self.did_database = {
                0xF190: b"WVWZZZ1KZAW000000",  # VIN
                0xF186: bytes([SESSION_DEFAULT]),  # active diagnostic session
                0xF187: b"HEADLIGHT-ECU-01",  # part number demo
            }


def _negative_response(service_id: int, nrc: int) -> bytes:
    return bytes([0x7F, service_id, nrc])


def _session_name(session: int) -> str:
    names = {
        SESSION_DEFAULT: "Default",
        SESSION_PROGRAMMING: "Programming",
        SESSION_EXTENDED: "Extended",
    }
    return names.get(session, f"0x{session:02X}")


class UdsEcu:
    def __init__(self, state: Optional[UdsEcuState] = None) -> None:
        self.state = state or UdsEcuState()

    def handle(self, request: bytes) -> bytes:
        if not request:
            return _negative_response(0x00, NRC_INCORRECT_MESSAGE_LENGTH)

        sid = request[0]
        if sid == 0x10:
            return self._handle_session_control(request)
        if sid == 0x22:
            return self._handle_read_did(request)
        return _negative_response(sid, NRC_SERVICE_NOT_SUPPORTED)

    def _handle_session_control(self, request: bytes) -> bytes:
        if len(request) != 2:
            return _negative_response(0x10, NRC_INCORRECT_MESSAGE_LENGTH)

        sub_function = request[1]
        allowed = {
            SESSION_DEFAULT,
            SESSION_PROGRAMMING,
            SESSION_EXTENDED,
        }
        if sub_function not in allowed:
            return _negative_response(0x10, NRC_SUB_FUNCTION_NOT_SUPPORTED)

        if sub_function == SESSION_PROGRAMMING and not self.state.security_unlocked:
            return _negative_response(0x10, NRC_CONDITIONS_NOT_CORRECT)

        self.state.active_session = sub_function
        self.state.did_database[0xF186] = bytes([sub_function])
        return bytes([0x50, sub_function]) + P2_DEFAULT_MS.to_bytes(
            2, "big"
        ) + P2_STAR_DEFAULT_MS.to_bytes(2, "big")

    def _handle_read_did(self, request: bytes) -> bytes:
        if len(request) != 3:
            return _negative_response(0x22, NRC_INCORRECT_MESSAGE_LENGTH)

        did = (request[1] << 8) | request[2]
        if did not in self.state.did_database:
            return _negative_response(0x22, NRC_REQUEST_OUT_OF_RANGE)

        if did == 0xF187 and self.state.active_session != SESSION_EXTENDED:
            return _negative_response(0x22, NRC_CONDITIONS_NOT_CORRECT)

        data = self.state.did_database[did]
        return bytes([0x62, request[1], request[2]]) + data

    def describe_response(self, response: bytes) -> str:
        if not response:
            return "empty"
        if response[0] == 0x7F:
            return f"NRC 0x{response[2]:02X} for service 0x{response[1]:02X}"
        if response[0] == 0x50:
            p2 = int.from_bytes(response[2:4], "big")
            p2_star = int.from_bytes(response[4:6], "big")
            return (
                f"SessionControl -> {_session_name(response[1])}, "
                f"P2={p2}ms, P2*={p2_star}ms"
            )
        if response[0] == 0x62:
            did = (response[1] << 8) | response[2]
            return f"ReadDID 0x{did:04X}, data={response[3:].hex(' ').upper()}"
        return response.hex(" ").upper()
