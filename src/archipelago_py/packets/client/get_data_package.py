from typing import Literal

from archipelago_py.packets.client.client_packet import ClientPacket


class GetDataPackage(ClientPacket):
    """
    Requests the data package from the server. Does not require client authentication.

    :ivar games: Specifies which games to request DataPackages of from the server.
     Despite the official documentation saying this is optional, it is not.
     Leaving this list empty returns an empty dictionary from the server.

    `GetDataPackage on github.com/ArchipelagoMW`_.

    .. _GetDataPackage on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#getdatapackage
    """

    cmd: Literal["GetDataPackage"] = "GetDataPackage"
    games: list[str]

