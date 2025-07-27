import asyncio
from pathlib import Path
from types import MappingProxyType

import pytest

from archipelago_py import packets
from tests.callbacks import helper_test_callback_negative, helper_test_callback_positive, ServerClient


# Todo: create test data for the callbacks and then implement all other tests

@pytest.fixture(scope="module")
def test_data() -> MappingProxyType[str, str]:
    data_path = (Path(__file__).parent / "test_callbacks.txt")
    data = MappingProxyType(dict([l.split(':', 1) for l in data_path.read_text("utf-8").splitlines()]))
    assert data

    return data


@pytest.fixture(scope="function")
def server_client():
    return ServerClient()


@pytest.mark.asyncio
async def test_on_ready(test_data, server_client):
    callback_executed = asyncio.Event()

    async def on_ready():
        callback_executed.set()

    server_client.client.on_ready = on_ready

    async with server_client:
        await asyncio.wait_for(callback_executed.wait(), timeout=0.5)

    assert callback_executed.is_set()


@pytest.mark.asyncio
async def test_on_received(test_data, server_client):
    received_event = asyncio.Event()

    async def on_received(_: packets.ServerPacket):
        received_event.set()

    server_client.client.on_received = on_received

    async with server_client:
        for p in test_data:
            await server_client.server_send(test_data[p])
            await asyncio.wait_for(received_event.wait(), timeout=0.5)
            received_event.clear()


@pytest.mark.asyncio
async def test_on_packet(test_data, server_client):
    packet_event = asyncio.Event()

    async def on_packet(_: packets.ServerPacket):
        packet_event.set()

    server_client.client.on_packet = on_packet

    async with server_client:
        for p in test_data:
            await server_client.server_send(test_data[p])
            await asyncio.wait_for(packet_event.wait(), timeout=0.5)
            packet_event.clear()


@pytest.mark.asyncio
async def test_on_bounced_positive(test_data):
    await helper_test_callback_positive(
        test_data,
        packets.Bounced,
        "on_bounced"
    )


@pytest.mark.asyncio
async def test_on_bounced_negative(test_data):
    await helper_test_callback_negative(
        test_data,
        packets.Bounced,
        "on_bounced"
    )


@pytest.mark.asyncio
async def test_on_connected(test_data):
    await helper_test_callback_positive(
        test_data,
        packets.Connected,
        "on_connected"
    )


@pytest.mark.asyncio
async def test_on_connected_negative(test_data):
    await helper_test_callback_negative(
        test_data,
        packets.Connected,
        "on_connected"
    )


@pytest.mark.asyncio
async def test_on_connection_refused(test_data):
    await helper_test_callback_positive(
        test_data,
        packets.ConnectionRefused,
        "on_connection_refused"
    )


@pytest.mark.asyncio
async def test_on_connection_refused_negative(test_data):
    await helper_test_callback_negative(
        test_data,
        packets.ConnectionRefused,
        "on_connection_refused"
    )


@pytest.mark.asyncio
async def test_on_room_update_positive(test_data):
    await helper_test_callback_positive(
        test_data,
        packets.RoomUpdate,
        "on_room_update"
    )


@pytest.mark.asyncio
async def test_on_room_update_negative(test_data):
    await helper_test_callback_negative(
        test_data,
        packets.RoomUpdate,
        "on_room_update"
    )


@pytest.mark.asyncio
async def test_on_print_json_positive(test_data):
    await helper_test_callback_positive(
        test_data,
        packets.PrintJSON,
        "on_print_json"
    )


@pytest.mark.asyncio
async def test_on_print_json_negative(test_data):
    await helper_test_callback_negative(
        test_data,
        packets.PrintJSON,
        "on_print_json"
    )


@pytest.mark.asyncio
async def test_on_data_package_positive(test_data):
    await helper_test_callback_positive(
        test_data,
        packets.DataPackage,
        "on_data_package"
    )


@pytest.mark.asyncio
async def test_on_data_package_negative(test_data):
    await helper_test_callback_negative(
        test_data,
        packets.DataPackage,
        "on_data_package"
    )
