import asyncio
import logging
from asyncio import Server

from archipelago_py import packets
from archipelago_py.client import Client
from archipelago_py.enums.item_handling_flag import ItemHandlingFlag
from archipelago_py.packets import Connect

stop_event = asyncio.Event()

class CustomClient(Client):

    async def on_ready(self):
        print("Client is connected and ready")

    async def on_room_info(self, packet: packets.RoomInfo):
        conn = Connect(
            version=packet.version,
            tags=("Tracker",),
            name="Player1", # Slot name
            items_handling=ItemHandlingFlag.OWN_WORLD | ItemHandlingFlag.OTHER_WORLDS,
            slot_data=True
        )

        await self.send(conn)

    async def on_connection_refused(self, packet: packets.ConnectionRefused):
        print("Connection refused:", packet.errors)
        stop_event.set() # Simulate main program logic stop

    async def on_connected(self, packet: packets.Connected):
        print("Authentication successful")

    async def on_packet(self, packet: Server):
        print(">>", packet)

async def runner():
    """
    Test function to run the client.
    """
    logging.basicConfig(level=logging.INFO)

    async with CustomClient(12345):
        await stop_event.wait() # Simulate main program logic


def main():
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    main()