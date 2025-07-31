import asyncio

import pytest
import websockets

from archipelago_py import packets, Client
from archipelago_py.client import ConnectionClosedError
from tests.callbacks import ServerClient, test_data


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
@pytest.mark.parametrize("exception", [
    websockets.exceptions.InvalidURI(uri="", msg=""),
    websockets.exceptions.InvalidHandshake(),
    websockets.exceptions.InvalidProxy(proxy="", msg=""),
    ConnectionRefusedError(),
    TimeoutError(),
    OSError()
], ids=lambda e: e.__class__.__name__)
async def test_on_connect_error(exception: type[Exception]):

    client = Client(0)
    callback_executed = asyncio.Event()

    async def connect_monkey_patch(*args, **kwargs):
        raise exception

    client._connect = connect_monkey_patch

    def on_connect_error(error):
        assert error is exception
        callback_executed.set()

    client.on_connect_error = on_connect_error

    async with client:
        await asyncio.wait_for(callback_executed.wait(), timeout=1)


@pytest.mark.asyncio
@pytest.mark.parametrize("close_code", websockets.CloseCode, ids=lambda cd: cd.name)
async def test_on_connection_closed(close_code: websockets.CloseCode):

    client = Client(0, auto_reconnect=False)
    callback_executed = asyncio.Event()
    exception = ConnectionClosedError(close_code)

    async def connect_monkey_patch(*args, **kwargs):
        nonlocal exception
        raise exception

    client._connect = connect_monkey_patch

    def on_connection_closed(close_code_):
        nonlocal close_code
        assert close_code_ == close_code
        callback_executed.set()

    client.on_connection_closed = on_connection_closed

    async with client:
        await asyncio.wait_for(callback_executed.wait(), timeout=1)