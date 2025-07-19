from datetime import datetime
from typing import Any, Literal

from archipelago_py.packets.server.server_packet import ServerPacket
from archipelago_py.structs.network_player import NetworkPlayer
from archipelago_py.structs.network_slot import NetworkSlot
from archipelago_py.structs.permissions import Permissions
from archipelago_py.structs.version import Version


class RoomUpdate(ServerPacket):
    """
    Sent when there is a need to update information about the present game session.
    RoomUpdate may contain the same arguments from `RoomInfo`_ and, once authenticated, arguments from `Connected`_.

    :ivar version: Object denoting the version of Archipelago which the server is running.
    :ivar generator_version: Object denoting the version of Archipelago which generated the multiworld.
    :ivar permissions: Mapping of permission name to Permission, keys are: "release", "collect" and "remaining".
    :ivar datapackage_checksums: Checksum hash of the individual games' data packages the server will send.
     Used by newer clients to decide which games' caches are outdated. See Data Package Contents for more information.
    :ivar tags: Denotes special features or capabilities that the sender is capable of. Example: WebHost
    :ivar games: List of games in the multiworld.
    :ivar seed_name: Uniquely identifying name of this generation.
    :ivar time: Unix time stamp of "now". Send for time synchronization if wanted for things like the DeathLink Bounce.
    :ivar hint_cost: The percentage of total locations that need to be checked to receive a hint from the server.
    :ivar location_check_points: The amount of hint points you receive per item/location check completed.
    :ivar password: Denoted whether a password is required to join this room.
    :ivar slot_data: Contains a json object for slot related data, differs per game. Empty if not required. Not
     present if slot_data in Connect is false.
    :ivar slot_info: Maps each slot to a NetworkSlot information.
    :ivar players: Sent in the event of an alias rename. Always sends all players, whether connected or not.
    :ivar checked_location: May be a partial update, containing new locations that were checked,
     especially from a coop partner in the same slot.
    :ivar team: Your team number. See NetworkPlayer for more info on team number.
    :ivar slot: Your slot number on your team. See NetworkPlayer for more info on the slot number.
    :ivar hint_points: Number of hint points that the current player has.

    `RoomUpdate on github.com/ArchipelagoMW`_.

    .. _RoomInfo:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#roominfo

    .. _Connected:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#connected

    .. _RoomUpdate on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#receiveditems
    """

    cmd: Literal["RoomUpdate"] = "RoomUpdate"
    version: Version | None = None
    generator_version: Version | None = None
    permissions: Permissions | None = None
    datapackage_checksums: dict[str, str] | None = None
    tags: tuple[str, ...] | None = None
    games: tuple[str, ...] | None = None
    seed_name: str | None = None
    time: datetime | None = None
    hint_cost: int | None = None
    location_check_points: int | None = None
    password: bool | None = None
    slot_data: dict[str, Any] | None = None
    slot_info: dict[int, NetworkSlot] | None = None
    players: tuple[NetworkPlayer, ...] | None = None
    checked_location: tuple[int, ...] | None = None
    team: int | None = None
    slot: int | None = None
    hint_points: int | None = None
