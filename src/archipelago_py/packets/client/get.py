from typing import Literal

from archipelago_py.packets.client.client_packet import ClientPacket


class Get(ClientPacket):
    """
    Used to request a single or multiple values from the server's data storage,
    see the Set package for how to write values to the data storage.
    A Get package will be answered with a Retrieved package.

    :ivar keys: Keys to retrieve the values for.

    `Get on github.com/ArchipelagoMW`_.

    .. _Get on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#get
    """

    cmd: Literal["Get"] = "Get"
    keys: list[str]
