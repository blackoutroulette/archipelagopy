import asyncio
import threading
import time
from asyncio import AbstractEventLoop

from websockets import serve, ServerConnection

from archipelagopy import Client

import pytest

class ThreadedClient:

    def __init__(self, host: str, port: int):
        self.thread: threading.Thread | None = None
        self.loop: AbstractEventLoop | None = None
        self.stop_event: asyncio.Event | None = None
        self.task: asyncio.Task | None = None
        self.host: str = host
        self.port: int = port

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.stop_event = asyncio.Event()

        try:
            self.task = self.loop.create_task(self._main())
            self.loop.run_until_complete(self.task)
        finally:
            self.loop.close()

    async def _main(self):

        async with Client(host=self.host, port=self.port, secure=False):
            await self.stop_event.wait()

    def stop(self):
        if self.loop and not self.stop_event:
            self.loop.call_soon_threadsafe(self.stop_event.set)

            if self.thread:
                self.thread.join()

@pytest.mark.asyncio
async def test_threaded_client():
    async def server_task_handler(ws: ServerConnection):
        await ws.send('{"cmd":"PrintJSON","data":[{"text":"Now that you are connected, you can use !help to list commands to run via the server. If your client supports it, you may have additional local commands you can list with /help."}],"type":"Tutorial"}')
        async for msg in ws:
            pass

    async with serve(server_task_handler, "localhost", 0) as server:
        port: int = next(iter(server.sockets)).getsockname()[1]  # Get the port assigned by the OS

        client = ThreadedClient(host="localhost", port=port)
        client.start()

        # simulate work
        time.sleep(1)

        client.stop()
