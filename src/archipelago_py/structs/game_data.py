from archipelago_py.structs.struct import Struct


class GameData(Struct):
    checksum: str
    item_name_to_id: dict[str, int] = {}
    location_name_to_id: dict[str, int] = {}
