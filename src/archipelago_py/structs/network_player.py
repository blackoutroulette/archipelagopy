from archipelago_py.structs.struct import Struct


class NetworkPlayer(Struct):
    """
    Denotes a player

    :ivar team: Team the player belongs to. Team numbers start at 0
    :ivar slot: The slot of the player. Slot numbers are unique per team and start
     at 1. Slot number 0 refers to the Archipelago server; this may appear in instances where the server grants the
     player an item.
    :ivar alias: Represents the player's name in current time.
    :ivar name: Is the original name used when the session was generated. This is typically distinct in
     games which require baking names into ROMs or for async games.

    `NetworkPlayer on github.com/ArchipelagoMW`_.

    .. _NetworkPlayer on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#networkplayer
    """

    team: int
    slot: int
    alias: str
    name: str
