from enum import IntEnum


class ClientStatus(IntEnum):
    """
    An enumeration containing the possible client states that may be used to inform the server in StatusUpdate.
    The MultiServer automatically sets the client state to ClientStatus.CLIENT_CONNECTED on the
    first active connection to a slot.

    :ivar CLIENT_UNKNOWN: The client is in an unknown state.
    :ivar CLIENT_CONNECTED: The client is connected to the server.
    :ivar CLIENT_READY: The client is ready to play.
    :ivar CLIENT_PLAYING: The client is currently playing the game.
    :ivar CLIENT_GOAL: The client has reached the goal of the game.

    `ClientStatus on github.com/ArchipelagoMW`_.

    .. _ClientStatus on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#clientstatus
    """

    CLIENT_UNKNOWN = 0
    CLIENT_CONNECTED = 5
    CLIENT_READY = 10
    CLIENT_PLAYING = 20
    CLIENT_GOAL = 30
