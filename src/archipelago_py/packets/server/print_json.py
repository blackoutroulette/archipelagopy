from typing import Literal

from archipelago_py.enums.print_json_type import PrintJSONType
from archipelago_py.packets.server.server_packet import ServerPacket
from archipelago_py.structs.json_message_part import JSONMessagePart
from archipelago_py.structs.network_item import NetworkItem


class PrintJSON(ServerPacket):
    """
    Sent to clients purely to display a message to the player. While various message types provide additional
    arguments, clients only need to evaluate the data argument to construct the human-readable message text.
    All other arguments may be ignored safely.

    :ivar type: PrintJsonType of this message (optional).
    :ivar data: Textual content of this message.
    :ivar tags: Tags of the triggering player.
    :ivar item: Source player's ID, location ID, item ID and item flags.
    :ivar message: Original chat message without sender prefix.
    :ivar receiving: Destination player's ID.
    :ivar team: Team of the triggering player.
    :ivar slot: Slot of the triggering player.
    :ivar countdown: Amount of seconds remaining on the countdown.
    :ivar found: Whether the location hinted for was checked.

    `print_json on github.com/ArchipelagoMW`_.

    .. _PrintJSON on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#printjson
    """

    cmd: Literal["PrintJSON"] = "PrintJSON"
    data: list[JSONMessagePart]
    type: PrintJSONType | None = None
    tags: list[str] | None = None
    item: NetworkItem | None = None
    message: str | None = None
    receiving: int | None = None
    team: int | None = None
    slot: int | None = None
    countdown: int | None = None
    found: bool | None = None
