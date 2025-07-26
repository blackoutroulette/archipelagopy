from archipelago_py import packets
from tests.callbacks import callback_test_decorator, test_data, server_client, callback_executed
import pytest

# Todo: create test data for the callbacks and then implement all other tests


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_ready(test_data, server_client, callback_executed):
    """
    Test that the client is ready to send and receive packets.
    """
    async def on_ready():
        callback_executed.set()

    server_client.client.on_ready = on_ready


@pytest.mark.asyncio
@callback_test_decorator(raises=TimeoutError)
async def test_on_ready_timeout(test_data, server_client, callback_executed):
    """
    Test that the setup will timeout if the callback_executed event is not set.
    """
    async def on_ready():
        pass

    server_client.client.on_ready = on_ready


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_received(test_data, server_client, callback_executed):
    """
    Test that the client can receive a raw packet.
    """
    async def on_received(packet: str):
        assert isinstance(packet, str)
        callback_executed.set()

    server_client.client.on_received = on_received

    await server_client.server_send(test_data["room_info"])


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_packet(test_data, server_client, callback_executed):
    """
    Test that the client can receive a packet.
    """
    async def on_packet(packet: str):
        assert isinstance(packet, packets.RoomInfo)
        callback_executed.set()

    server_client.client.on_packet = on_packet

    await server_client.server_send(test_data["room_info"])


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_bounced(test_data, server_client, callback_executed):
    """
    Test that the client can receive a Bounced packet.
    """
    async def on_bounced(packet: packets.Bounced):
        assert isinstance(packet, packets.Bounced)
        callback_executed.set()

    server_client.client.on_bounced = on_bounced

    await server_client.server_send(test_data["bounced"])


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_connected(test_data, server_client, callback_executed):
    """
    Test that the client can receive a Connected packet.
    """
    async def on_connected(packet: packets.Connected):
        assert isinstance(packet, packets.Connected)
        callback_executed.set()

    server_client.client.on_connected = on_connected

    await server_client.server_send(test_data["connected"])


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_connection_refused(test_data, server_client, callback_executed):
    """
    Test that the client can receive a ConnectionRefused packet.
    """
    async def on_connection_refused(packet: packets.ConnectionRefused):
        assert isinstance(packet, packets.ConnectionRefused)
        callback_executed.set()

    server_client.client.on_connection_refused = on_connection_refused

    await server_client.server_send(test_data["connection_refused"])


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_room_update(test_data, server_client, callback_executed):
    """
    Test that the client can receive a RoomUpdate packet.
    """
    async def on_room_update(packet: packets.RoomUpdate):
        assert isinstance(packet, packets.RoomUpdate)
        callback_executed.set()

    server_client.client.on_room_update = on_room_update

    await server_client.server_send(test_data["room_update"])


@pytest.mark.asyncio
@callback_test_decorator()
async def test_on_print_json(test_data, server_client, callback_executed):
    """
    Test that the client can receive a PrintJSON packet.
    """
    async def on_print_json(packet: packets.PrintJSON):
        assert isinstance(packet, packets.PrintJSON)
        callback_executed.set()

    server_client.client.on_print_json = on_print_json

    await server_client.server_send(test_data["print_json"])