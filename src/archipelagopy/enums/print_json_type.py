from enum import StrEnum


class PrintJSONType(StrEnum):
    """
    PrintJsonType indicates the type of the print_json packet. Different types can be handled differently
    by the client and can also contain additional arguments. When receiving an unknown or missing type,
    the data's list[JSONMessagePart] should still be displayed to the player as normal text.

    :ivar ITEM_SEND: A client received an item.
    :ivar ITEM_CHEAT: A client used the !getitem (cheat) command.
    :ivar HINT: Send when a client uses the !hint command. You need to be either connected to
     the receiver or finder slot of the hint to receive this packet.
    :ivar JOIN: A new client connected and authenticated to a slot.
    :ivar PART: A client disconnected from a slot.
    :ivar CHAT: A client sent a chat message.
    :ivar SERVER_CHAT: The server broadcasted a message.
    :ivar TUTORIAL: A client has triggered a tutorial message, such as when first connecting.
    :ivar TAGS_CHANGED: A client changed their tags.
    :ivar COMMAND_RESULT: Someone (usually the client) entered an ! command.
    :ivar ADMIN_COMMAND_RESULT: A client used the !admin command.
    :ivar GOAL: A client reached their goal.
    :ivar RELEASE: A client used the !release command.
    :ivar COLLECT: A client used the !collect command.
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
