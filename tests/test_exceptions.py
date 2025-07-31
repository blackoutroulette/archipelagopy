import asyncio

import pytest
import websockets.exceptions
from websockets import ServerConnection

from archipelago_py.client import Client


@pytest.mark.asyncio
@pytest.mark.parametrize("close_code", websockets.CloseCode, ids=lambda code: code.name)
async def test_stop_on_connection_closed(close_code: websockets.CloseCode):
    """
    Test that the client stops when auto_reconnect is False and the server closes the connection with a specific close code.
    """

    connected_event = asyncio.Event()

    async def server_task_handler(ws: ServerConnection):
        nonlocal close_code
        await asyncio.sleep(0.01)
        connected_event.set()
        await ws.close(code=close_code)

    async def run_server():
        async with websockets.serve(server_task_handler, "localhost", 0) as server:
            port: int = next(iter(server.sockets)).getsockname()[1]  # Get the port assigned by the OS

            async with Client(port, host="localhost", secure=False, auto_reconnect=False) as client:
                await client.wait_closed()

    await asyncio.wait_for(run_server(), timeout=1)
    assert connected_event.is_set()


@pytest.mark.asyncio
@pytest.mark.parametrize("exception", [
    ConnectionRefusedError(),
    websockets.exceptions.InvalidURI("", ""),
    websockets.exceptions.InvalidHandshake(),
    websockets.exceptions.InvalidProxy("", ""),
    TimeoutError(),
    OSError(),
    Exception()

], ids=lambda e: e.__class__.__name__)
async def test_stop_on_connect_error(exception: Exception):
    """
    Test that the client stops when auto_reconnect is False and an exception occurs during the connecting phase.
    """

    client = Client(0, auto_reconnect=False)
    exception_raised = asyncio.Event()

    async def connect_monkey_patch(*args, **kwargs):
        nonlocal exception_raised, exception
        exception_raised.set()
        raise exception

    client._connect = connect_monkey_patch

    async with client:
        await asyncio.wait_for(client.wait_closed(), 1)

    assert exception_raised.is_set()