from enum import StrEnum


class PacketProblemType(StrEnum):
    """
    PacketProblemType indicates the type of problem that was detected in the faulty packet,
    the known problem types are below but others may be added in the future.

    :ivar CMD: cmd argument of the faulty packet that could not be parsed correctly.
    :ivar ARGUMENTS: Arguments of the faulty packet which were not correct.

    `PacketProblemType on github.com/ArchipelagoMW`_.

    .. _PacketProblemType on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#packetproblemtype
    """
    CMD = "cmd"
    ARGUMENTS = "arguments"
