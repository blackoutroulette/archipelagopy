from pathlib import Path
from typing import Final

import pytest

from archipelagopy import packets
from tests.parsing import load_data, helper_test_packet_adapter, helper_test_parse_json

TEST_DATA: Final[list[tuple[type[packets.Packet], str]]] = [
    (packets.Bounced, "server/test_bounced"),
    (packets.Connected, "server/test_connected"),
    (packets.ConnectionRefused, "server/test_connection_refused"),
    (packets.DataPackage, "server/test_data_package"),
    (packets.InvalidPacket, "server/test_invalid_packet"),
    (packets.LocationInfo, "server/test_location_info"),
    (packets.ReceivedItems, "server/test_received_items"),
    (packets.Retrieved, "server/test_retrieved"),
    (packets.RoomInfo, "server/test_room_info"),
    (packets.RoomUpdate, "server/test_room_update"),
    (packets.SetReply, "server/test_set_reply"),
    (packets.Bounce, "client/test_bounce"),
    (packets.Get, "client/test_get"),
    (packets.LocationChecks, "client/test_location_checks"),
    (packets.SetNotify, "client/test_set_notify"),
    (packets.Say, "client/test_say"),
    (packets.StatusUpdate, "client/test_status_update")
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