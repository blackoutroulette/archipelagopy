from typing import Literal

from archipelagopy.packets.client.client_packet import ClientPacket
from archipelagopy.structs.data_storage_operation import DataStorageOperation


class Set(ClientPacket):
    """
    Used to write data to the server's data storage, that data can then be shared across
    worlds or just saved for later. Values for keys in the data storage can be retrieved
    with a Get package, or monitored with a SetNotify package. Keys that start with _read_ cannot be set.

    :ivar key: The key to manipulate. Can never start with "_read".
    :ivar default: The default value to use in case the key has no value on the server.
    :ivar want_reply: If true, the server will send a SetReply response back to the client.
    :ivar operations: Operations to apply to the value, multiple operations can be present and
     they will be executed in order of appearance.

    `Set on github.com/ArchipelagoMW`_.

    .. _Set on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#set
    """

    cmd: Literal["Set"] = "Set"
    operations: list[DataStorageOperation]
    default: int | float
    key: str
    want_reply: bool
