import pytest

from archipelago_py import packets
from tests.callbacks import helper_test_callback_positive, helper_test_callback_negative, test_data

PACKET_CALLBACKS: list[tuple[type[packets.ServerPacket], str]] = [
    (packets.Bounced, "on_bounced"),
    (packets.Connected, "on_connected"),
    (packets.ConnectionRefused, "on_connection_refused"),
    (packets.DataPackage, "on_data_package"),
    (packets.InvalidPacket, "on_invalid_packet"),
    (packets.LocationInfo, "on_location_info"),
    (packets.PrintJSON, "on_print_json"),
    (packets.ReceivedItems, "on_received_items"),
    (packets.Retrieved, "on_retrieved"),
    (packets.RoomInfo, "on_room_info"),
    (packets.RoomUpdate, "on_room_update"),
    (packets.SetReply, "on_set_reply")
]

def id_func(callback: tuple[type[packets.ServerPacket], str]) -> str:
    return callback[1]

@pytest.mark.asyncio
@pytest.mark.parametrize("callback", PACKET_CALLBACKS, ids=id_func)
async def test_callback_positive(test_data, callback: tuple[type[packets.ServerPacket], str]):
    packet_type, callback_name = callback

    await helper_test_callback_positive(
        test_data,
        packet_type,
        callback_name
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("callback", PACKET_CALLBACKS, ids=id_func)
async def test_callback_negative(test_data, callback: tuple[type[packets.ServerPacket], str]):
    packet_type, callback_name = callback

    await helper_test_callback_negative(
        test_data,
        packet_type,
        callback_name
    )