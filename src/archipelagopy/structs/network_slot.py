from archipelagopy.enums.slot_type import SlotType
from archipelagopy.structs.struct import Struct


class NetworkSlot(Struct):
    """
    An object representing static information about a slot.

    :ivar type: The type of the slot, which can be a player, spectator, or group.
    :ivar group_members: A list of slot IDs that are members of the group. Only populated if type == group
    :ivar name: The name of the player or group.
    :ivar game: The game that the slot is playing.

    :ref: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#networkslot
    """

    type: SlotType
    group_members: tuple[int, ...]
    name: str
    game: str
