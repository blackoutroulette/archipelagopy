from typing import Literal

from archipelago_py.enums.client_tag import ClientTag
from archipelago_py.packets.server.server_packet import ServerPacket


class Bounced(ServerPacket):
    """
    Sent to clients after a client requested this message be sent to them, more info in the `Bounce`_ package.
    :ivar data: The data in the Bounce package copied.
    :ivar games: Optional. Game names this message is targeting.
    :ivar tags: Optional. Client Tag this message is targeting.
    :ivar slots: Optional. Player slot IDs that this message is targeting.

    `Bounced on github.com/ArchipelagoMW`_.

    .. _Bounce:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#bounce

    .. _Bounced on github.com/ArchipelagoMW:
     https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#bounced
    """

    cmd: Literal["Bounced"] = "Bounced"
    slots: tuple[int, ...]
    data: dict | None = None
    games: tuple[str, ...] | None = None
    tags: tuple[ClientTag | str, ...] | None = None
