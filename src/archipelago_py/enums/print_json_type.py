from enum import StrEnum


class PrintJSONType(StrEnum):
    """
    PrintJsonType indicates the type of the print_json packet. Different types can be handled differently
    by the client and can also contain additional arguments. When receiving an unknown or missing type,
    the data's list[JSONMessagePart] should still be displayed to the player as normal text.

    :ivar ITEM_SEND: A player received an item.
    :ivar ITEM_CHEAT: A player used the !getitem command.
    :ivar HINT: The player with the same slot which you are connected to has hinted an item. (Hints are only shown to you.)
    :ivar JOIN: A player connected.
    :ivar PART: A player disconnected.
    :ivar CHAT: A player sent a chat message.
    :ivar SERVER_CHAT: The server broadcasted a message.
    :ivar TUTORIAL: The client has triggered a tutorial message, such as when first connecting.
    :ivar TAGS_CHANGED: A player changed their tags.
    :ivar COMMAND_RESULT: Someone (usually the client) entered an ! command.
    :ivar ADMIN_COMMAND_RESULT: The client entered an !admin command.
    :ivar GOAL: A player reached their goal.
    :ivar RELEASE: A player released the remaining items in their world.
    :ivar COLLECT: A player collected the remaining items for their world.
    :ivar COUNTDOWN: The current server countdown has progressed.

    `PrintJSONType on github.com/ArchipelagoMW`_.

    .. _PrintJSONType on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#printjsontype
    """

    ITEM_SEND = "ItemSend"
    ITEM_CHEAT = "ItemCheat"
    HINT = "Hint"
    JOIN = "Join"
    PART = "Part"
    CHAT = "Chat"
    SERVER_CHAT = "ServerChat"
    TUTORIAL = "Tutorial"
    TAGS_CHANGED = "TagsChanged"
    COMMAND_RESULT = "CommandResult"
    ADMIN_COMMAND_RESULT = "AdminCommandResult"
    GOAL = "Goal"
    RELEASE = "Release"
    COLLECT = "Collect"
    COUNTDOWN = "Countdown"
