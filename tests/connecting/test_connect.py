import asyncio
import json
from pathlib import Path

import pytest
import websockets
from websockets import ServerConnection

from archipelagopy import Client, packets, enums


@pytest.mark.asyncio
async def test_connect():

    client = Client(0, host="localhost", secure=False)

    # load the test data
    test_data_path = (Path(__file__).parent/"test_connect.txt")
    lines = test_data_path.read_text("utf-8").splitlines()
    test_data = dict([line.split(':', 1) for line in lines])
    assert test_data

    # flags
    room_info_flag: bool = False
    connected_flag: bool = False
    print_json_join_flag: bool = False
    print_json_tutorial_flag = asyncio.Event()


    async def server_task_handler(ws: ServerConnection):
        await ws.send(test_data["room_info"])

        msg = await ws.recv()
        assert json.loads(msg) == json.loads(test_data["connect"])

        await ws.send(test_data["connected"])
        await ws.send(test_data["join"])
        await ws.send(test_data["tutorial"])

    async def on_room_info(packet: packets.RoomInfo):
        assert isinstance(packet, packets.RoomInfo)
        assert packets.RoomInfo(**json.loads(test_data["room_info"])[0]) == packet

        nonlocal room_info_flag
        room_info_flag = True

        conn = packets.Connect(
            version=packet.version,
            tags=["AP"],
            name="Player1",  # Slot name
            game="Game_One",  # Game name
            password="123456",
            items_handling=enums.ItemHandlingFlag.OWN_WORLD | enums.ItemHandlingFlag.OTHER_WORLDS,
            slot_data=True
        )

        await client.send(conn)

    async def on_connected(packet: packets.Connected):
        assert isinstance(packet, packets.Connected)
        assert packets.Connected(**json.loads(test_data["connected"])[0]) == packet

        nonlocal connected_flag
        connected_flag = True

    async def on_print_json(packet: packets.PrintJSON):
        assert isinstance(packet, packets.PrintJSON)

        if packet.type == enums.PrintJSONType.JOIN:
            assert packets.PrintJSON(**json.loads(test_data["join"])[0]) == packet

            nonlocal print_json_join_flag
            print_json_join_flag = True

        elif packet.type == enums.PrintJSONType.TUTORIAL:
            assert packets.PrintJSON(**json.loads(test_data["tutorial"])[0]) == packet
            print_json_tutorial_flag.set()

    async def run_server():
        async with websockets.serve(server_task_handler, "localhost", 0) as server:
            port: int = next(iter(server.sockets)).getsockname()[1]  # Get the port assigned by the OS

            # monkey patch
            client._addr = f"ws://localhost:{port}"
            client.on_room_info = on_room_info
            client.on_connected = on_connected
            client.on_print_json = on_print_json

            await client.start()
            await print_json_tutorial_flag.wait()
            await client.stop()

        # check for no reconnects
        assert client._get_reconnect_frequency() == 1

    await asyncio.wait_for(run_server(), timeout=1)

    # check that all flags were set
    assert room_info_flag
    assert connected_flag
    assert print_json_join_flag
    assert print_json_tutorial_flag.is_set()