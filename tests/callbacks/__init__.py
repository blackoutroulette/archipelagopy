import asyncio
from pathlib import Path
from types import MappingProxyType

import pytest
import websockets
from websockets import ServerConnection

from archipelagopy import Client, packets


class ServerClient:

    def __init__(self):
        self.stop_event = asyncio.Event()
        self.send_queue = asyncio.Queue()
        self.client = Client(0, host="localhost", secure=False)
        self.task: asyncio.Task | None = None

    async def server_task_handler(self, ws: ServerConnection):

        queue_task = asyncio.create_task(self.send_queue.get())
        stop_task = asyncio.create_task(self.stop_event.wait())
        while True:

            done, pending = await asyncio.wait(
                [queue_task, stop_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            done: asyncio.Task = next(iter(done))

            if done is queue_task:
                msg = done.result()
                await ws.send(msg)
                queue_task = asyncio.create_task(self.send_queue.get())

            elif done is stop_task:
                break

        await ws.close(code=websockets.CloseCode.NORMAL_CLOSURE)

    async def server_send(self, msg: str):
        self.send_queue.put_nowait(msg)

    async def run_server(self):
        async with websockets.serve(self.server_task_handler, "localhost", 0) as server:
            port: int = next(iter(server.sockets)).getsockname()[1]  # Get the port assigned by the OS

            self.client._addr = f"ws://localhost:{port}"
            async with self.client:
                await self.stop_event.wait()

    async def __aenter__(self):
        """
        Start the server and client.
        """
        self.task = asyncio.create_task(self.run_server())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Stop the server and client.
        """
        self.stop_event.set()
        if self.task:
            await self.task
        await self.client.stop()


@pytest.fixture(scope="module")
def test_data() -> MappingProxyType[str, str]:
    data_path = (Path(__file__).parent / "test_callbacks.txt")
    data = MappingProxyType(dict([l.split(':', 1) for l in data_path.read_text("utf-8").splitlines()]))
    assert data

    return data


async def helper_test_callback_positive(test_data, packet_type: type[packets.ServerPacket], event_func: str):
    """
    Test that the client can receive a DataPackage packet.
    """

    assert test_data

    server_client = ServerClient()
    callback_executed = asyncio.Event()

    async def on_callback(packet: packet_type):
        assert isinstance(packet, packet_type)
        callback_executed.set()

    assert hasattr(server_client.client, event_func)
    setattr(server_client.client, event_func, on_callback)

    async with server_client:
        await server_client.server_send(test_data[packet_type.__name__])
        await asyncio.wait_for(callback_executed.wait(), timeout=0.5)

    assert callback_executed.is_set()


async def helper_test_callback_negative(test_data, packet_type: type[packets.ServerPacket], event_func: str):
    """
    Test that the client can receive a DataPackage packet.
    """

    assert test_data

    server_client = ServerClient()
    callback_executed = asyncio.Event()
    packet_event = asyncio.Event()

    async def on_packet(_: packets.ServerPacket):
        packet_event.set()

    server_client.client.on_packet = on_packet

    async def on_callback(packet: packet_type):
        assert isinstance(packet, packet_type)
        callback_executed.set()

    assert hasattr(server_client.client, event_func)
    setattr(server_client.client, event_func, on_callback)

    async with server_client:
        for p in test_data:
            if p == packet_type.__name__:
                continue

            await server_client.server_send(test_data[p])
            await asyncio.wait_for(packet_event.wait(), timeout=0.5)
            packet_event.clear()

    assert not callback_executed.is_set()
