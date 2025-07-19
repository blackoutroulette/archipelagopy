from typing import Literal

from archipelago_py.packets.server.server_packet import ServerPacket
from archipelago_py.structs.game_data import GameData


class DataPackage(ServerPacket):
    """
    Sent to clients to provide what is known as a 'data package' which contains information to enable a client to
    most easily communicate with the Archipelago server. Contents include things like location
    id to name mappings, among others; see `Data Package Contents`_ for more info.

    :ivar data: The data package as a JSON object.

    `DataPackage on github.com/ArchipelagoMW`_.

    .. _Data Package Contents:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#data-package-contents

    .. _DataPackage on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#datapackage
    """

    cmd: Literal["DataPackage"] = "DataPackage"
    data: dict[str, GameData]
