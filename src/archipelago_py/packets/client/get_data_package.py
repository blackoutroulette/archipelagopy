from typing import Literal

from archipelago_py.packets.client.client_packet import ClientPacket


class GetDataPackage(ClientPacket):
    """
    Requests the data package from the server. Does not require client authentication.

    :ivar games: Optional. If specified, will only send back the specified data. Such as, ["Factorio"] -> Datapackage with only Factorio data.

    `GetDataPackage on github.com/ArchipelagoMW`_.

    .. _GetDataPackage on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#getdatapackage
    """

    cmd: Literal["GetDataPackage"] = "GetDataPackage"
    games: tuple[str, ...] | None = None
