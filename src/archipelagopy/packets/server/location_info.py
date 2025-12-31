from typing import Literal

from archipelagopy.packets.server.server_packet import ServerPacket
from archipelagopy.structs.network_item import NetworkItem


class LocationInfo(ServerPacket):
    """
    Sent to clients to acknowledge a received LocationScouts packet and responds with the item in the location(s) being scouted.

    :ivar locations: Contains list of item(s) in the location(s) scouted.

    `LocationInfo on github.com/ArchipelagoMW`_.

    .. _LocationInfo on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#locationinfo
    """

    cmd: Literal["LocationInfo"] = "LocationInfo"
    locations: tuple[NetworkItem, ...]
