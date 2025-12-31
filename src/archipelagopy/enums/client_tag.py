from enum import StrEnum


class ClientTag(StrEnum):
    """
    Tags are represented as a list of strings, the common client tags follow
    :ivar AP: Signifies that this client is a reference client, its usefulness is mostly in debugging to compare client behaviours more easily.
    :ivar DEATH_LINK: Client participates in the DeathLink mechanic, therefore will send and receive DeathLink bounce events.
    :ivar HINT_GAME: Indicates the client is a hint game, made to send hints instead of locations. Special join/leave message,¹ game is optional.²
    :ivar TRACKER: Indicates the client is a tracker, made to track instead of sending locations. Special join/leave message,¹ game is optional.²
    :ivar TEXT_ONLY: Indicates the client is a basic client, made to chat instead of sending locations. Special join/leave message,¹ game is optional.²
    :ivar NO_TEXT: Indicates the client does not want to receive text messages, improving performance if not needed.

    ¹: When connecting or disconnecting, the chat message shows e.g. "tracking".
    ²: Allows game to be empty or null in Connect. Game and version validation will then be skipped.

    `Tags on github.com/ArchipelagoMW`_.

    .. _Tags on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#tags
    """
    AP = "AP"
    DEATH_LINK = "DeathLink"
    HINT_GAME = "HintGame"
    TRACKER = "Tracker"
    TEXT_ONLY = "TextOnly"
    NO_TEXT = "NoText"
