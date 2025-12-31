from enum import IntEnum


class HintStatus(IntEnum):
    """
    An enumeration containing the possible hint states.

    :ivar HINT_UNSPECIFIED: The receiving player has not specified any status.
    :ivar HINT_NO_PRIORITY: The receiving player has specified that the item is unneeded.
    :ivar HINT_AVOID: The receiving player has specified that the item is detrimental.
    :ivar HINT_PRIORITY: The receiving player has specified that the item is needed.
    :ivar HINT_FOUND: The location has been collected. Status cannot be changed once found.

    `HintStatus on github.com/ArchipelagoMW`_.

    .. _HintStatus on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#hintstatus
    """
    HINT_UNSPECIFIED = 0
    HINT_NO_PRIORITY = 10
    HINT_AVOID = 20
    HINT_PRIORITY = 30
    HINT_FOUND = 40
