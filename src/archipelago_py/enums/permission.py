from enum import IntEnum


class Permission(IntEnum):
    """
    An enumeration containing the possible command permission, for commands that may be restricted.

    :ivar DISABLED: Completely disables access to the command.
    :ivar ENABLED: Allows manual use of the command.
    :ivar GOAL: Allows manual use of the command after the goal has been completed.
    :ivar AUTO: Forces use of the command after the goal has been completed, only works for release and collect.
    :ivar AUTO_ENABLED: Forces use of the command after the goal has been completed, allows manual use any time.

    `Permission on github.com/ArchipelagoMW`_.

    .. _Permission on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#permission
    """

    DISABLED = 0
    ENABLED = 1
    GOAL = 2
    AUTO = 6
    AUTO_ENABLED = 7

    def __repr__(self):
        return self.name
