import pytest

from archipelago_py import Client


@pytest.mark.asyncio
async def test_connection_error():
    client = Client(0)

    async def connect_monkey_patch(*args, **kwargs):
        raise ConnectionError("Simulated connection error")

    client._connect = connect_monkey_patch