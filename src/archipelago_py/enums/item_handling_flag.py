from collections.abc import Iterator
from enum import IntFlag


class ItemHandlingFlag(IntFlag):
    """
    Item handling flags.

    :ivar: ItemHandlingFlag.NONE: No ReceivedItems is sent to you, ever.
    :ivar: ItemHandlingFlag.OTHER_WORLDS: Indicates you get items sent from other worlds.
    :ivar: ItemHandlingFlag.OWN_WORLD: Indicates you get items sent from your own world.
    :ivar: ItemHandlingFlag.STARTING_INVENTORY: Indicates you get your starting inventory sent.

    `ItemHandlingFlag on github.com/ArchipelagoMW`_.

    .. _ItemHandlingFlag on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#items_handling-flags
    """
    NONE = 0
    OTHER_WORLDS = 1
    OWN_WORLD = 2
    STARTING_INVENTORY = 4


def item_handling_flags_from_int(value: int) -> Iterator[ItemHandlingFlag]:
    for flag in ItemHandlingFlag:
        if value & flag.value():
            yield flag
