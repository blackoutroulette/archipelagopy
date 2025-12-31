from archipelagopy.structs import GameData, Struct


class DataPackageData(Struct):
    games: dict[str, GameData]