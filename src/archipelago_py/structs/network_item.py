from archipelago_py.enums.network_item_flag import NetworkItemFlag
from archipelago_py.structs.struct import Struct


class NetworkItem(Struct):
    item: int
    location: int
    player: int
    flags: NetworkItemFlag
