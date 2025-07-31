from typing import Literal

from archipelago_py.enums.item_handling_flag import ItemHandlingFlag
from archipelago_py.packets.client.client_packet import ClientPacket
from archipelago_py.structs.version import Version


class Connect(ClientPacket):
    """
    Sent by the client to initiate a connection to an Archipelago game session.

    :ivar version: An object representing the Archipelago version this client supports.
    :ivar tags: Denotes special features or capabilities that the sender is capable of.
    :ivar game: The name of the game the client is playing. Example: A Link to the Past.
    :ivar name: The player name for this client.
    :ivar items_handling: Flags configuring which items should be sent by the server.
    :ivar slot_data: If true, the Connect answer will contain slot_data
    :ivar password: If the game session requires a password, it should be passed here.
    :ivar uuid: Unique identifier for player client.

    `Connect on github.com/ArchipelagoMW`_.

    .. _Connect on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#connect
    """

    cmd: Literal["Connect"] = "Connect"
    version: Version
    name: str
    tags: list[str] = []
    items_handling: ItemHandlingFlag = ItemHandlingFlag.NONE
    game: str | None = None
    slot_data: bool = False
    password: str = ""
    uuid: str = ""
