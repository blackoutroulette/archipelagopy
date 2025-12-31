from archipelagopy.structs.struct import Struct


class Version(Struct):
    """
    An object representing software versioning. Used in the Connect packet to allow the client to inform the server
    of the Archipelago version it supports.

    :ref: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#networkversion
    """

    major: int
    minor: int
    build: int

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.build}"
