import asyncio
from asyncio import Server

from archipelago_py import packets
from archipelago_py.callback_interface import OnConnectExceptionUnion
from archipelago_py.client import Client
from archipelago_py.enums.item_handling_flag import ItemHandlingFlag
from archipelago_py.packets import Connect

class AdvancedClient(Client):

    async def on_ready(self):
        print("Client is connected and ready")

    async def on_room_info(self, packet: packets.RoomInfo):
        packet = Connect(
            version=packet.version,
            tags=["Tracker"],
            name="Mario", # Slot name
            items_handling=ItemHandlingFlag.OWN_WORLD | ItemHandlingFlag.OTHER_WORLDS,
            slot_data=True
        )

        await self.send(packet)

    def on_connect_error(self, error: OnConnectExceptionUnion):
        print("Failed to connect:", error)

    async def on_connection_refused(self, packet: packets.ConnectionRefused):
        print("Connection refused:", packet.errors)
        await self.stop()

    async def on_connected(self, packet: packets.Connected):
        print(f"Logged in as: {packet.slot_info[packet.slot].name}")

    async def on_packet(self, packet: Server):
        print(f">> ({packet})\n")

async def my_work_task():
    """
    Example task, replace with your own asynchronous work.
    """

    while True:
        await asyncio.sleep(1)

async def runner():
    """
    Test function to run the client.
    """

    # Uncomment enable debug logging
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    async with AdvancedClient(port=12345) as client:
        my_task = asyncio.create_task(my_work_task())
        await client.wait_closed(my_task) # wait for the client to close or the task to finish

def main():
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()