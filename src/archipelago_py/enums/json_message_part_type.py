from enum import StrEnum


class JSONMessagePartType(StrEnum):
    """
    Is used to denote the intent of the message part. This can be used to indicate special information
    which may be rendered differently depending on client. How these types are displayed in Archipelago's ALttP client
    is not the end-all be-all. Other clients may choose to interpret and display these messages differently.

    :ivar TEXT: Regular text content. Is the default type and as such may be omitted.
    :ivar PLAYER_ID: Player ID of someone on your team, should be resolved to Player Name
    :ivar PLAYER_NAME: Player Name, could be a player within a multiplayer game or from another team, not ID resolvable
    :ivar ITEM_ID: Item ID, should be resolved to Item Name
    :ivar ITEM_NAME: Item Name, not currently used over network, but supported by reference Clients.
    :ivar LOCATION_ID: Location ID, should be resolved to Location Name
    :ivar LOCATION_NAME: Location Name, not currently used over network, but supported by reference Clients.
    :ivar ENTRANCE_NAME: Entrance Name. No ID mapping exists.
    :ivar HINT_STATUS: The HintStatus of the hint. Both text and hint_status are given.
    :ivar COLOR: Regular text that should be colored. Only type that will contain color data.

    `JSONMessagePart on github.com/ArchipelagoMW`_.

    .. _JSONMessagePart on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#jsonmessagepart
    """

    TEXT = "text"
    PLAYER_ID = "player_id"
    PLAYER_NAME = "player_name"
    ITEM_ID = "item_id"
    ITEM_NAME = "item_name"
    LOCATION_ID = "location_id"
    LOCATION_NAME = "location_name"
    ENTRANCE_NAME = "entrance_name"
    HINT_STATUS = "hint_status"
    COLOR = "color"
