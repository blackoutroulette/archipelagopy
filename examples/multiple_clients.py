import asyncio

import websockets

from archipelagopy import Client, enums, packets, structs
from archipelagopy.callback_interface import OnConnectExceptionUnion
from archipelagopy.structs import NetworkSlot, NetworkItem, GameData


class ItemAnnouncerClient(Client):

    # shared across all clients
    data_packages: dict[str, GameData] = {}
    game_item_id_to_name: dict[str, dict[int, str]] = {}
    game_location_id_to_name: dict[str, dict[int, str]] = {}

    def __init__(self, port: int, slot_name: str, password: str = ""):
        super().__init__(port)
        self.port: int = port
        self.slot_name: str = slot_name
        self.password: str = password
        self.slot_info: dict[int, NetworkSlot] = {}

    def data_package_is_outdated(self, game: str, checksum: str) -> bool:
        if game not in self.data_packages:
            return True
        return self.data_packages[game].checksum != checksum

    async def on_room_info(self, packet: packets.RoomInfo):

        # find all games that are outdated or not present in the data packages
        data_package_requests = [
            game
            for game, checksum
            in packet.datapackage_checksums.items()
            if self.data_package_is_outdated(game, checksum)
        ]

        # update the data packages with the checksums to avoid requesting the
        # same package multiple times from other clients
        for game in data_package_requests:
            self.data_packages[game] = GameData(
                checksum=packet.datapackage_checksums[game]
            )

        # request data packages for games that are outdated
        if data_package_requests:
            await self.send(packets.GetDataPackage(games=data_package_requests))
        else:
            await self.login()

    def create_id_to_name_mappings(self, game: str, data: GameData):
        # create item id to name mappings
        self.game_item_id_to_name[game] = {
            v: k for k, v in data.item_name_to_id.items()
        }

        # create location id to name mappings
        self.game_location_id_to_name[game] = {
            v: k for k, v in data.location_name_to_id.items()
        }

    async def login(self):
        await self.send(
            packets.Connect(
                version=structs.Version(major=6, minor=0, build=2),
                tags=["Tracker"],
                name=self.slot_name,  # slot name
                password=self.password,
                items_handling=enums.ItemHandlingFlag.OWN_WORLD | enums.ItemHandlingFlag.OTHER_WORLDS,
                slot_data=True
            )
        )

    async def on_data_package(self, packet: packets.DataPackage):
        # update the data packages with the received data
        self.data_packages.update(packet.data.games)

        # create reverse mappings for item and location IDs to names
        for game, data in packet.data.games.items():
            self.create_id_to_name_mappings(game, data)

        await self.login()

    def print(self, msg: str):
        print(f"[Lobby:{self.port}]: {msg}")

    def on_connect_error(self, error: OnConnectExceptionUnion):
        self.print("Failed to connect:", error)

    def on_connection_closed(self, close_code: websockets.CloseCode):
        self.print(f"Connection closed with code: {close_code.name}({close_code})")

    async def on_connection_refused(self, packet: packets.ConnectionRefused):
        self.print(f"Connection refused: {",".join(packet.errors)}")
        await self.stop()

    async def on_connected(self, packet: packets.Connected):
        self.slot_info.update(packet.slot_info)
        self.print(f"Logged in as: {packet.slot_info[packet.slot].name}")

    async def on_print_json(self, packet: packets.PrintJSON):
        if packet.type != enums.PrintJSONType.ITEM_SEND:
            return

        item: NetworkItem = packet.item
        receiving: int = packet.receiving
        receiver: NetworkSlot = self.slot_info[receiving]
        item_name: str = self.game_item_id_to_name[receiver.game][item.item]

        sender: NetworkSlot = self.slot_info[item.player]
        location_name: str = self.game_location_id_to_name[sender.game][item.location]

        item_importance: str = str.lower(item.flags.name)

        self.print(
            f"{receiver.name} just received their"
            f" {item_name} ({item_importance} item) from {sender.name} ({location_name})"
        )

async def main():
    # Uncomment to enable debug logging
    # import logging
    # logging.basicConfig(level=logging.DEBUG)

    clients: list[Client] = [
        ItemAnnouncerClient(port=10001, slot_name="PlayerOne", password="123456"),
        ItemAnnouncerClient(port=10002, slot_name="PlayerTwo"),
        ItemAnnouncerClient(port=10003, slot_name="PlayerThree"),
    ]

    # Start all clients concurrently
    await asyncio.gather(*[client.start() for client in clients])

    try:
        # Wait indefinitely to keep the clients running
        # This is a placeholder for your main event loop.
        await asyncio.Event().wait()
    except asyncio.exceptions.CancelledError:
        print("Stopping clients...")
        await asyncio.gather(*[client.stop() for client in clients])


if __name__ == "__main__":
    asyncio.run(main())