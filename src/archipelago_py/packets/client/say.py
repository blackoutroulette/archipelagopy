from typing import Literal

from archipelago_py.packets.client.client_packet import ClientPacket


class Say(ClientPacket):
    """
    Basic chat command which sends text to the server to be distributed to other clients.

    :ivar text: Text to send to others.

    `Say on github.com/ArchipelagoMW`_.

    .. _Say on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#say
    """

    cmd: Literal["Say"] = "Say"
    text: str
