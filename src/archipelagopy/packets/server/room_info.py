from datetime import datetime
from typing import Literal

from archipelagopy.packets.server.server_packet import ServerPacket
from archipelagopy.structs.permissions import Permissions
from archipelagopy.structs.version import Version


class RoomInfo(ServerPacket):
    """
    Sent to clients when they connect to an Archipelago server.

    :ivar version: Object denoting the version of Archipelago which the server is running.
    :ivar generator_version: Object denoting the version of Archipelago which generated the multiworld.
    :ivar permissions: Mapping of permission name to Permission, keys are: "release", "collect" and "remaining".
    :ivar datapackage_checksums: Checksum hash of the individual games' data packages the server will send.
     Used by newer clients to decide which games' caches are outdated. See Data Package Contents for more information.
     Keys are game names, values are the checksums.
    :ivar tags: Denotes special features or capabilities that the sender is capable of. Example: WebHost
    :ivar games: List of games in the multiworld.
    :ivar seed_name: Uniquely identifying name of this generation.
    :ivar time: Unix time stamp of "now". Send for time synchronization if wanted for things like the DeathLink Bounce.
    :ivar hint_cost: The percentage of total locations that need to be checked to receive a hint from the server.
    :ivar location_check_points: The amount of hint points you receive per item/location check completed.
    :ivar password: Denoted whether a password is required to join this room.

    `RoomInfo on github.com/ArchipelagoMW`_.

    .. _RoomInfo on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#roominfo
    """

    cmd: Literal["RoomInfo"] = "RoomInfo"
    version: Version
    generator_version: Version
    permissions: Permissions
    datapackage_checksums: dict[str, str]
    tags: tuple[str, ...]
    games: tuple[str, ...]
    seed_name: str
    time: datetime
    hint_cost: int
    location_check_points: int
    password: bool
