from typing import Literal

from archipelago_py.packets.packet import Packet


class ServerPacket(Packet):
    """
    Base class for all server events. All server events should inherit from this class.
    """

    cmd: Literal["ServerPacket"] = "ServerPacket"
