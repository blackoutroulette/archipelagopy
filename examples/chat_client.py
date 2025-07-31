import asyncio

import aioconsole

from archipelago_py import Client, packets, structs, enums
from archipelago_py.callback_interface import OnConnectExceptionUnion
from archipelago_py.structs import NetworkSlot


class ChatClient(Client):
    def __init__(self, port: int):
        super().__init__(port)
        self.slot_info: dict[int, NetworkSlot] = {}

    async def on_ready(self):
        print("Connected to the server.")

        await self.send(
            packets.Connect(
                version=structs.Version(major=6, minor=0, build=0),
                name="Link",  # slot name
                game="Ocarina of Time",
                password="123456",
                slot_data=True
            )
        )

    def on_connect_error(self, error: OnConnectExceptionUnion):
        print("Failed to connect:", error)

    async def on_connection_refused(self, packet: packets.ConnectionRefused):
        print(f"Connection refused: {",".join(packet.errors)}")
        await self.stop()

    async def on_connected(self, packet: packets.Connected):
        self.slot_info.update(packet.slot_info)
        print(f"Logged in as: {packet.slot_info[packet.slot].name}")

    async def on_print_json(self, packet: packets.PrintJSON):
        if packet.type != enums.PrintJSONType.CHAT:
            return

        player: NetworkSlot = self.slot_info[packet.slot]
        print(f">> {player.name}: {packet.message}")


async def input_loop(client: ChatClient):
    while True:
        msg: str = await aioconsole.ainput()
        await client.send(packets.Say(text=msg))


async def main():
    async with ChatClient(port=12345) as client:
        input_loop_task = asyncio.create_task(input_loop(client))
        await client.wait_closed(input_loop_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass