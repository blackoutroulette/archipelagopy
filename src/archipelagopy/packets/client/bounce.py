from typing import Literal

from archipelagopy.packets.client.client_packet import ClientPacket


class Bounce(ClientPacket):
    """
    Send this message to the server, tell it which clients should receive the message
    and the server will forward the message to all those targets to which any one requirement applies.

    :ivar games: Optional. Game names that should receive this message
    :ivar tags: Optional. Client tags that should receive this message
    :ivar slots: Optional. Player IDs that should receive this message
    :ivar data: Any data you want to send

    `Bounce on github.com/ArchipelagoMW`_.

    .. _Bounce on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#bounce
    """

    cmd: Literal["Bounce"] = "Bounce"
    slots: list[int]
    games: list[str] | None = None
    tags: list[str] | None = None
    data: dict | None = None
