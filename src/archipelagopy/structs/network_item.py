from archipelagopy.enums.network_item_flag import NetworkItemFlag
from archipelagopy.structs.struct import Struct


class NetworkItem(Struct):
    item: int
    location: int
    player: int
    flags: NetworkItemFlag
