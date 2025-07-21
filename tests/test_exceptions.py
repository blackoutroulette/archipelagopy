import asyncio

import pytest
import websockets.exceptions

from archipelago_py.callback_interface import OnConnectExceptionUnion
from archipelago_py.client import Client


@pytest.mark.asyncio
async def test_invalid_url():

    client = Client(12345, host="/")
    exception_raised = asyncio.Event()

    def on_connect_error(error: OnConnectExceptionUnion):
        assert isinstance(error, websockets.exceptions.InvalidURI)
        nonlocal exception_raised
        exception_raised.set()

    # Assign the error handler to the client
    client.on_connect_error = on_connect_error

    await client.start()
    await asyncio.wait_for(exception_raised.wait(), 1)

    assert exception_raised.is_set()
