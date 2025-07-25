import asyncio
import json
from pathlib import Path

import pytest
import websockets
from websockets import ServerConnection

from archipelago_py import Client, packets, enums


@pytest.mark.asyncio
async def test_connect():

    data_folder = Path(__file__).parent / "test_connect"
    client = Client(0, host="localhost", secure=False)

    # load the test data
    client_connect_packet = (data_folder/"client_connect_packet.txt").read_text("utf-8")
    server_post_connected = (data_folder/"server_post_connected.txt").read_text("utf-8").splitlines()
    room_info = (data_folder/"room_info.txt").read_text("utf-8")

    # flags
    room_info_flag = asyncio.Event()
    connected_flag = asyncio.Event()
    print_json_join_flag = asyncio.Event()
    print_json_tutorial_flag = asyncio.Event()


    async def server_task_handler(ws: ServerConnection):
        await ws.send(room_info)

        msg = await ws.recv()
        assert msg == client_connect_packet

        for line in server_post_connected:
            await ws.send(line)

    async def on_room_info(packet: packets.RoomInfo):
        assert isinstance(packet, packets.RoomInfo)
        assert packets.RoomInfo(**json.loads(room_info[1:-2])) == packet
        room_info_flag.set()

        conn = packets.Connect(
            version=packet.version,
            tags=("AP",),
            name="Player1",  # Slot name
            game="Game_One",  # Game name
            password="123456",
            items_handling=enums.ItemHandlingFlag.OWN_WORLD | enums.ItemHandlingFlag.OTHER_WORLDS,
            slot_data=True
        )

        await client.send(conn)

    async def on_connected(packet: packets.Connected):
        assert isinstance(packet, packets.Connected)
        assert packets.Connected(**json.loads(server_post_connected[0])[0]) == packet
        connected_flag.set()

    async def on_print_json(packet: packets.PrintJSON):
        assert isinstance(packet, packets.PrintJSON)

        if packet.type == enums.PrintJSONType.JOIN:
            assert packets.PrintJSON(**json.loads(server_post_connected[1])[0]) == packet
            print_json_join_flag.set()
        elif packet.type == enums.PrintJSONType.TUTORIAL:
            assert packets.PrintJSON(**json.loads(server_post_connected[2])[0]) == packet
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