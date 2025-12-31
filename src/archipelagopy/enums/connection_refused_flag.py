from enum import StrEnum


class ConnectionRefusedFlag(StrEnum):
    """

    :ivar INVALID_SLOT: Indicates that the sent 'name' field did not match any auth entry on the server
    :ivar INVALID_GAME: Indicates that a correctly named slot was found, but the game for it mismatched
    :ivar INCOMPATIBLE_VERSION: Indicates a version mismatch.
    :ivar INVALID_PASSWORD: Indicates the wrong, or no password when it was required, was sent.
    :ivar INVALID_ITEMS_HANDLING: Indicates a wrong value type or flag combination was sent.

    `ConnectionRefused on github.com/ArchipelagoMW`_

    .. _ConnectionRefused on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#connectionrefused
    """
    INVALID_SLOT = "InvalidSlot"
    INVALID_GAME = "InvalidGame"
    INCOMPATIBLE_VERSION = "IncompatibleVersion"
    INVALID_PASSWORD = "InvalidPassword"
    INVALID_ITEMS_HANDLING = "InvalidItemsHandling"
