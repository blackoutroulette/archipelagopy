from archipelago_py.enums.hint_status import HintStatus
from archipelago_py.enums.json_message_part_type import JSONMessagePartType
from archipelago_py.structs.struct import Struct


class JSONMessagePart(Struct):
    hint_status: HintStatus | None = None
    type: JSONMessagePartType | None = None
    text: str | None = None
    color: str | None = None
    flags: int | None = None
    player: int | None = None
