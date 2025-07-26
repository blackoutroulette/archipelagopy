import asyncio
from pathlib import Path

import pytest
import websockets
from websockets import ServerConnection

from archipelago_py import Client


class ServerClient:

    def __init__(self):
        self.stop_event = asyncio.Event()
        self.send_queue = asyncio.Queue()
        self.client =  Client(0, host="localhost", secure=False)
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
def test_data():
    data_path = (Path(__file__).parent / "test_callbacks.txt")
    data = dict([l.split(':', 1) for l in data_path.read_text("utf-8").splitlines()])
    assert data

    return data

@pytest.fixture(scope="function")
def server_client():
    return ServerClient

@pytest.fixture(scope="function")
def callback_executed():
    return asyncio.Event()


def callback_test_decorator(raises: type[Exception] | None = None, timeout: float = 0.5):
    """
    Decorator to run the test function with the server-client setup.
    """
    def decorator(func):
        async def wrapper(test_data, server_client, callback_executed):
            callback_executed = asyncio.Event()
            server_client = ServerClient()

            await func(test_data, server_client, callback_executed)

            async with server_client:
                await asyncio.wait_for(callback_executed.wait(), timeout=timeout)
            assert callback_executed.is_set()
            server_client.stop_event.set()

        async def raises_wrapper(test_data, server_client, callback_executed):
            with pytest.raises(raises):
               await wrapper(test_data, server_client, callback_executed)

        return raises_wrapper if raises else wrapper
    return decorator
