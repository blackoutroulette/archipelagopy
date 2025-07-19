from enum import IntEnum


class LocationScoutHint(IntEnum):
    """
    Enum for location scout hints.

    :ivar NO_HINT: No hint is broadcasted.
    :ivar ALL: All hints are broadcasted.
    :ivar ONLY_NEW: Only new hints are broadcasted, however this does not remove them from the LocationInfo reply.

    `LocationScoutHint on github.com/ArchipelagoMW`_.

    .. _LocationScoutHint on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#arguments-16
    """

    NO_HINT = 0
    ALL = 1
    ONLY_NEW = 2
