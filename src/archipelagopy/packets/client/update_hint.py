from typing import Literal

from archipelagopy.enums.hint_status import HintStatus
from archipelagopy.packets.client.client_packet import ClientPacket


class UpdateHint(ClientPacket):
    """
    Sent to the server to update the status of a Hint. The client must be the 'receiving_player' of the Hint, or the update fails.

    :ivar player: The ID of the player whose location is being hinted for.
    :ivar location: The ID of the location to update the hint for. If no hint exists for this location, the packet is ignored.
    :ivar status: Optional. If included, sets the status of the hint to this status. Cannot set HINT_FOUND, or change the status from HINT_FOUND.

    `UpdateHint on github.com/ArchipelagoMW`_.

    .. _UpdateHint on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#updatehint
    """

    cmd: Literal["UpdateHint"] = "UpdateHint"
    player: int
    location: int
    status: HintStatus | None = None
