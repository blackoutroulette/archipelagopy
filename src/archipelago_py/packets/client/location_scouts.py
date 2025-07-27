from typing import Literal

from archipelago_py.enums.location_scout_hint import LocationScoutHint
from archipelago_py.packets.client.client_packet import ClientPacket


class LocationScouts(ClientPacket):
    """
    Sent to the server to retrieve the items that are on a specified list of locations. The server will respond with a LocationInfo packet containing the items located in the scouted locations. Fully remote clients without a patch file may use this to "place" items onto their in-game locations, most commonly to display their names or item classifications before/upon pickup.
    LocationScouts can also be used to inform the server of locations the client has seen, but not checked. This creates a hint as if the player had run !hint_location on a location, but without deducting hint points. This is useful in cases where an item appears in the game world, such as 'ledge items' in A Link to the Past. To do this, set the create_as_hint parameter to a non-zero value.

    :ivar locations: The ids of the locations seen by the client. May contain any number of locations, even ones sent before; duplicates do not cause issues with the Archipelago server.
    :ivar create_as_hint: If non-zero, the scouted locations get created and broadcasted as a player-visible hint. If 2 only new hints are broadcast, however this does not remove them from the LocationInfo reply.

    `LocationScouts on github.com/ArchipelagoMW`_.

    .. _LocationScouts on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#locationscouts
    """

    cmd: Literal["LocationScouts"] = "LocationScouts"
    locations: list[int]
    create_as_hint: LocationScoutHint
