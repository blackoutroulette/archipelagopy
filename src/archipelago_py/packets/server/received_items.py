from typing import Literal

from archipelago_py.packets.server.server_packet import ServerPacket
from archipelago_py.structs.network_item import NetworkItem


class ReceivedItems(ServerPacket):
    """
    Sent to clients when they receive an item.

    :ivar items: The items which the client is receiving.
    :ivar index: The next empty slot in the list of items for the receiving client.

    `ReceivedItems on github.com/ArchipelagoMW`_.

    .. _ReceivedItems on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#receiveditems
    """

    cmd: Literal["ReceivedItems"] = "ReceivedItems"
    items: tuple[NetworkItem, ...]
    index: int
