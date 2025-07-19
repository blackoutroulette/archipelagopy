from enum import IntEnum


class SlotType(IntEnum):
    """
    An enum representing the nature of a slot.

    :ivar SPECTATOR: spectator
    :ivar PLAYER: player
    :ivar GROUP: group

    `SlotType on github.com/ArchipelagoMW`_.

    .. _SlotType on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#slottype
    """

    SPECTATOR = 0
    PLAYER = 1
    GROUP = 2
