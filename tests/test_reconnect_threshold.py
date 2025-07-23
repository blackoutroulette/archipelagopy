import asyncio

import pytest
import websockets
from websockets import ServerConnection
from websockets.asyncio.server import serve

from archipelago_py import Client

class TestClient:
    def __init__(self, port: int, host: str):
        self.port = port
        self.host = host
        self.client = Client(port, host=host)
        self.connect_tries = 0
        self.server_ready = asyncio.Event()

    async def serve_handler(self, ws: ServerConnection):
        await asyncio.sleep(0.1)  # Simulate some delay before closing
        self.connect_tries += 1
        await ws.close(code=websockets.CloseCode.NORMAL_CLOSURE)

    async def server_task_handler(self):
        async with serve(self.serve_handler, self.host, self.port) as server:
            self.server_ready.set()
            await server.wait_closed()

    async def client_task_handler(self):
        await self.server_ready.wait()

        async with Client(self.port, host=self.host, secure=False) as client:
            await client.wait_closed()

@pytest.mark.asyncio
async def test_reconnect_threshold():
    """
    Test that the client stops after the server closed the connection n times in k seconds
    where n is Client.RECONNECT_THRESHOLD and k is Client.RECONNECT_ACCUMULATION_PERIOD.
    """

    test_client = TestClient(port=8765, host="localhost")
    server_task = asyncio.create_task(test_client.server_task_handler())
    client_task = asyncio.create_task(test_client.client_task_handler())

    done, pending = await asyncio.wait_for(
        asyncio.wait(
            [server_task, client_task],
            return_when=asyncio.FIRST_COMPLETED
        ),
        timeout=5
    )

    done = next(iter(done))
    await done
    pending = next(iter(pending))

    assert done is client_task
    assert pending is server_task
    assert test_client.connect_tries == Client.RECONNECT_THRESHOLD


