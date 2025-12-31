from typing import Literal

from archipelagopy.packets.client.client_packet import ClientPacket


class SetNotify(ClientPacket):
    """
    Used to register your current session for receiving all SetReply packages
    of certain keys to allow your client to keep track of changes.

    :ivar keys: Keys to receive all SetReply packages for.

    `SetNotify on github.com/ArchipelagoMW`_.

    .. _SetNotify on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#setnotify
    """

    cmd: Literal["SetNotify"] = "SetNotify"
    keys: list[str]
