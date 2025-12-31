from typing import Any, Literal

from archipelagopy.packets.server.server_packet import ServerPacket
from archipelagopy.structs.network_player import NetworkPlayer
from archipelagopy.structs.network_slot import NetworkSlot


class Connected(ServerPacket):
    """
    Sent to clients when the connection handshake is successfully completed.

    :ivar slot_data: Contains a json object for slot related data, differs per game. Empty if not required. Not
     present if slot_data in Connect is false.
    :ivar slot_info: Maps each slot to a NetworkSlot information.
    :ivar players: List denoting other players in the multiworld, whether connected or not.
    :ivar missing_location: Contains ids of remaining locations that need to be checked. Useful for trackers,
     among other things.
    :ivar checked_location: Contains ids of all locations that have been checked. Useful for trackers,
     among other things. Location ids are in the range of ± 2^53-1.
    :ivar team: Your team number. See NetworkPlayer for more info on team number.
    :ivar slot: Your slot number on your team. See NetworkPlayer for more info on the slot number.
    :ivar hint_points: Number of hint points that the current player has.

    `Connected on github.com/ArchipelagoMW`_.

    .. _Connected on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#connected
    """

    cmd: Literal["Connected"] = "Connected"
    team: int
    slot: int
    hint_points: int
    slot_info: dict[int, NetworkSlot]
    players: tuple[NetworkPlayer, ...]
    missing_location: tuple[int, ...] | None = None
    checked_location: tuple[int, ...] | None = None
    slot_data: dict[str, Any] | None = None
