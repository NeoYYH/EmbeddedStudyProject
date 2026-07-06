"""Minimal DoIP (ISO 13400-2) message builders for Task 1 lab exercises."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Optional

DOIP_PROTOCOL_VERSION = 0x02
DOIP_INVERSE_VERSION = 0xFD
DOIP_PORT = 13400

PAYLOAD_VEHICLE_IDENTIFICATION_REQUEST = 0x0001
PAYLOAD_VEHICLE_IDENTIFICATION_RESPONSE = 0x0002
PAYLOAD_ROUTING_ACTIVATION_REQUEST = 0x0005
PAYLOAD_ROUTING_ACTIVATION_RESPONSE = 0x0006
PAYLOAD_DIAGNOSTIC_MESSAGE = 0x8001
PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK = 0x8002
PAYLOAD_DIAGNOSTIC_MESSAGE_NEG_ACK = 0x8003
PAYLOAD_ALIVE_CHECK_REQUEST = 0x0007
PAYLOAD_ALIVE_CHECK_RESPONSE = 0x0008


@dataclass(frozen=True)
class DoIPHeader:
    payload_type: int
    payload: bytes

    def encode(self) -> bytes:
        return struct.pack(
            ">BBHI",
            DOIP_PROTOCOL_VERSION,
            DOIP_INVERSE_VERSION,
            self.payload_type,
            len(self.payload),
        ) + self.payload

    @classmethod
    def decode(cls, data: bytes) -> tuple["DoIPHeader", bytes]:
        if len(data) < 8:
            raise ValueError("DoIP header requires at least 8 bytes")

        version, inverse, payload_type, payload_len = struct.unpack(">BBHI", data[:8])
        if version != DOIP_PROTOCOL_VERSION or inverse != DOIP_INVERSE_VERSION:
            raise ValueError(
                f"Unexpected DoIP version pair: 0x{version:02X}/0x{inverse:02X}"
            )

        total = 8 + payload_len
        if len(data) < total:
            raise ValueError("Incomplete DoIP payload")

        payload = data[8:total]
        return cls(payload_type=payload_type, payload=payload), data[total:]


def payload_type_name(payload_type: int) -> str:
    names = {
        PAYLOAD_VEHICLE_IDENTIFICATION_REQUEST: "Vehicle Identification Request",
        PAYLOAD_VEHICLE_IDENTIFICATION_RESPONSE: "Vehicle Identification Response",
        PAYLOAD_ROUTING_ACTIVATION_REQUEST: "Routing Activation Request",
        PAYLOAD_ROUTING_ACTIVATION_RESPONSE: "Routing Activation Response",
        PAYLOAD_DIAGNOSTIC_MESSAGE: "Diagnostic Message",
        PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK: "Diagnostic Message Positive Ack",
        PAYLOAD_DIAGNOSTIC_MESSAGE_NEG_ACK: "Diagnostic Message Negative Ack",
        PAYLOAD_ALIVE_CHECK_REQUEST: "Alive Check Request",
        PAYLOAD_ALIVE_CHECK_RESPONSE: "Alive Check Response",
    }
    return names.get(payload_type, f"Unknown (0x{payload_type:04X})")


def build_vehicle_identification_request() -> bytes:
    return DoIPHeader(PAYLOAD_VEHICLE_IDENTIFICATION_REQUEST, b"").encode()


def build_vehicle_identification_response(
    vin: str = "WVWZZZ1KZAW000000",
    logical_address: int = 0x0E00,
    eid: bytes = b"\x00\x11\x22\x33\x44\x55",
    gid: bytes = b"\xAA\xBB\xCC\xDD\xEE\xFF",
    further_action: int = 0x00,
) -> bytes:
    if len(vin) != 17:
        raise ValueError("VIN must be exactly 17 ASCII characters")
    if len(eid) != 6 or len(gid) != 6:
        raise ValueError("EID and GID must be 6 bytes each")

    payload = (
        vin.encode("ascii")
        + struct.pack(">H", logical_address)
        + eid
        + gid
        + struct.pack("B", further_action)
    )
    return DoIPHeader(PAYLOAD_VEHICLE_IDENTIFICATION_RESPONSE, payload).encode()


def build_routing_activation_request(
    source_address: int = 0x0E00,
    activation_type: int = 0x00,
    oem_specific: bytes = b"\x00\x00\x00\x00",
) -> bytes:
    payload = (
        struct.pack(">H", source_address)
        + struct.pack("B", activation_type)
        + b"\x00\x00\x00\x00"
        + oem_specific
    )
    return DoIPHeader(PAYLOAD_ROUTING_ACTIVATION_REQUEST, payload).encode()


def build_routing_activation_response(
    client_logical_address: int,
    logical_address: int = 0x0E00,
    response_code: int = 0x10,
    oem_specific: bytes = b"\x00\x00\x00\x00",
) -> bytes:
    payload = (
        struct.pack(">H", client_logical_address)
        + struct.pack(">H", logical_address)
        + struct.pack("B", response_code)
        + oem_specific
    )
    return DoIPHeader(PAYLOAD_ROUTING_ACTIVATION_RESPONSE, payload).encode()


def build_diagnostic_message(
    source_address: int,
    target_address: int,
    uds_payload: bytes,
) -> bytes:
    payload = struct.pack(">HH", source_address, target_address) + uds_payload
    return DoIPHeader(PAYLOAD_DIAGNOSTIC_MESSAGE, payload).encode()


def build_diagnostic_positive_ack(
    source_address: int,
    target_address: int,
    ack_code: int = 0x00,
    previous_diagnostic_message: Optional[bytes] = None,
) -> bytes:
    payload = (
        struct.pack(">HHB", source_address, target_address, ack_code)
        + (previous_diagnostic_message or b"")
    )
    return DoIPHeader(PAYLOAD_DIAGNOSTIC_MESSAGE_POS_ACK, payload).encode()


def build_alive_check_request() -> bytes:
    return DoIPHeader(PAYLOAD_ALIVE_CHECK_REQUEST, b"").encode()


def build_alive_check_response(source_address: int = 0x0E00) -> bytes:
    return DoIPHeader(
        PAYLOAD_ALIVE_CHECK_RESPONSE,
        struct.pack(">H", source_address),
    ).encode()


def hexdump(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)
