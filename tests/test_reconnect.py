import asyncio
import math

import pytest
import websockets
from websockets import ServerConnection, serve

from archipelago_py.client import Client


@pytest.mark.asyncio
async def test_reconnect_on_server_standby():
    """
    Test that the client reconnects to the server when the connection is closed.
    The test will use different close codes to ensure that the client can handle various closure scenarios.
    """

    times_connected: int = 0
    stop_event = asyncio.Event()
    Client.RECONNECT_ACCUMULATION_PERIOD = math.inf  # Ignore the accumulation period for this test
    Client._exponential_backoff = staticmethod(lambda x: 0)  # Disable exponential backoff for this test

    async def server_task_handler(ws: ServerConnection):
        nonlocal times_connected

        await asyncio.sleep(0.01)

        times_connected += 1
        if times_connected >= 2:
            stop_event.set()

        await ws.close(code=websockets.CloseCode.GOING_AWAY)

    async def run_server():
        async with serve(server_task_handler, "localhost", 0) as server:
            port: int = next(iter(server.sockets)).getsockname()[1]  # Get the port assigned by the OS

            async with Client(port, host="localhost", secure=False, auto_reconnect=True) as client:
                await stop_event.wait()

        assert client._get_reconnect_frequency() == 2

    await asyncio.wait_for(run_server(), timeout=1)

    assert times_connected == 2
    assert stop_event.is_set()


