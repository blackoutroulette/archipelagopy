from typing import Any, Literal

from archipelago_py.packets.server.server_packet import ServerPacket


class Retrieved(ServerPacket):
    """
    Sent to clients as a response to a `Get`_ package.

    :ivar keys: A key-value collection containing all the values for the keys requested in the Get package.

    `Retrieved on github.com/ArchipelagoMW`_.

    .. _Retrieved on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#retrieved

    .. _Get:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#get
    """

    cmd: Literal["Retrieved"] = "Retrieved"
    keys: dict[str, Any]
