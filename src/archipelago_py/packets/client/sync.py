from typing import Literal

from archipelago_py.packets.client.client_packet import ClientPacket


class Sync(ClientPacket):
    """
    Sent to server to request a ReceivedItems packet to synchronize items. Takes no arguments.

    `Sync on github.com/ArchipelagoMW`_.

    .. _Sync on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#sync
    """

    cmd: Literal["Sync"] = "Sync"
