from typing import Literal

from archipelagopy.packets.client.client_packet import ClientPacket


class LocationChecks(ClientPacket):
    """
    Sent to server to inform it of locations that the client has checked. Used to inform the server of new checks that are made, as well as to sync state.

    :ivar locations: The ids of the locations checked by the client. May contain any number of checks, even ones sent before; duplicates do not cause issues with the Archipelago server.

    `LocationChecks on github.com/ArchipelagoMW`_.

    .. _LocationChecks on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#locationchecks
    """

    cmd: Literal["LocationChecks"] = "LocationChecks"
    locations: list[int]
