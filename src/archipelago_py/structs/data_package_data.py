from archipelago_py.structs import GameData, Struct


class DataPackageData(Struct):
    games: dict[str, GameData]