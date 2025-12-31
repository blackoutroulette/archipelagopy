from typing import Literal

from archipelagopy.enums.item_handling_flag import ItemHandlingFlag
from archipelagopy.packets.client.client_packet import ClientPacket


class ConnectUpdate(ClientPacket):
    """
    Update arguments from the Connect package, currently only updating tags and items_handling is supported.

    :ivar tags: Denotes special features or capabilities that the sender is capable of
    :ivar items_handling: Flags configuring which items should be sent by the server.

    `ConnectUpdate on github.com/ArchipelagoMW`_.

    .. _ConnectUpdate on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#connectupdate
    """

    cmd: Literal["ConnectUpdate"] = "ConnectUpdate"
    tags: list[str]
    items_handling: ItemHandlingFlag
