from enum import IntFlag


class NetworkItemFlag(IntFlag):
    """
    NetworkItemFlag enum.

    :ivar COMMON: Nothing special about this item
    :ivar MINOR: If set, indicates the item can unlock logical advancement
    :ivar MAJOR: If set, indicates the item is especially useful
    :ivar TRAP: If set, indicates the item is a trap

    `NetworkItem on github.com/ArchipelagoMW`_.

    .. _NetworkItem on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#networkitem
    """

    COMMON = 0
    MINOR = 1
    MAJOR = 2
    TRAP = 4
