from typing import Literal

from archipelagopy.packets.server.server_packet import ServerPacket


class SetReply(ServerPacket):
    """
    Sent to the client as response to a Set package when want_reply was set to true, or if the client has registered
    to receive updates for a certain key using the SetNotify package. SetReply packages are sent even
    if a Set package did not alter the value for the key.

    :ivar value: The new value for the key.
    :ivar original_value: The value the key had before it was updated. Not present on "_read" prefixed special keys.
    :ivar key: The key that was updated.
    :ivar slot: The slot that originally sent the Set package causing this change.

    `SetReply on github.com/ArchipelagoMW`_.

    .. _SetReply on github.com/ArchipelagoMW:
     https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#setreply
    """

    cmd: Literal["SetReply"] = "SetReply"
    value: int | float
    original_value: int | float
    key: str
    slot: int
