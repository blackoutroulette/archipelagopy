from typing import Literal

from archipelagopy.enums.connection_refused_flag import ConnectionRefusedFlag
from archipelagopy.packets.server.server_packet import ServerPacket


class ConnectionRefused(ServerPacket):
    """
    Sent to clients when the server refuses connection. This is sent during the initial connection handshake.
    InvalidSlot indicates that the sent 'name' field did not match any auth entry on the server. InvalidGame indicates
    that a correctly named slot was found, but the game for it mismatched. IncompatibleVersion indicates a version
    mismatch. InvalidPassword indicates the wrong, or no password when it was required, was sent.
    InvalidItemsHandling indicates a wrong value type or flag combination was sent.

    :ivar errors: Optional. When provided, should contain any one of: InvalidSlot, InvalidGame,
     IncompatibleVersion, InvalidPassword, or InvalidItemsHandling.

    `ConnectionRefused on github.com/ArchipelagoMW`_.

    .. _ConnectionRefused on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#connectionrefused
    """

    cmd: Literal["ConnectionRefused"] = "ConnectionRefused"
    errors: tuple[ConnectionRefusedFlag, ...]
