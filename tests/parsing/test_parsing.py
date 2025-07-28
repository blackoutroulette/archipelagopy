from pathlib import Path
from typing import Final

import pytest

from archipelago_py import packets
from tests.parsing import load_data, helper_test_packet_adapter, helper_test_parse_json

TEST_DATA: Final[list[tuple[type[packets.Packet], str]]] = [
    (packets.Bounced, "test_bounced"),
    (packets.Connected, "test_connected"),
    (packets.ConnectionRefused, "test_connection_refused"),
    (packets.DataPackage, "test_data_package"),
    (packets.InvalidPacket, "test_invalid_packet"),
    (packets.LocationInfo, "test_location_info"),
    (packets.ReceivedItems, "test_received_items"),
    (packets.Retrieved, "test_retrieved"),
    (packets.RoomInfo, "test_room_info"),
    (packets.RoomUpdate, "test_room_update"),
    (packets.SetReply, "test_set_reply"),
]

FLAT_TEST_DATA: Final[list[tuple[type[packets.Packet], tuple[Path, str]]]] = [
    (t[0], d) for t in TEST_DATA for d in load_data(Path(__file__).parent/t[1])
]

def id_func(data: tuple[type[packets.Packet], tuple[Path, str]]) -> str:
    packet_type, (path, _) = data
    return f"{packet_type.__name__}/{path.name}"

@pytest.mark.parametrize("data", FLAT_TEST_DATA, ids=id_func)
def test_model(data: tuple[type[packets.Packet], tuple[Path, str]]):
    packet_type, (_, json_data) = data
    helper_test_parse_json(json_data, packet_type)

@pytest.mark.parametrize("data", FLAT_TEST_DATA, ids=id_func)
def test_packet_adapter(data: tuple[type[packets.Packet], tuple[Path, str]]):
    packet_type, (_, json_data) = data
    helper_test_packet_adapter(json_data, packet_type)